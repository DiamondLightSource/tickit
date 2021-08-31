from typing import List

import pytest
from immutables import Map
from mock import AsyncMock, MagicMock

from tickit.core.management.event_router import Inverse_Wiring_Struct, InverseWiring
from tickit.core.management.ticker import Ticker
from tickit.core.typedefs import Changes, ComponentID, Input, IoId, Output, SimTime


@pytest.fixture
def inverse_wiring_struct() -> Inverse_Wiring_Struct:
    return {
        ComponentID("Mid1"): {
            IoId("Mid1<1"): (ComponentID("Out1"), IoId("Out1>1")),
            IoId("Mid1<2"): (ComponentID("Ext1"), IoId("Ext1>1")),
        },
        ComponentID("In1"): {
            IoId("In1<1"): (ComponentID("Mid1"), IoId("Mid1>1")),
            IoId("In1<2"): (ComponentID("Ext1"), IoId("Ext1>1")),
        },
    }


@pytest.fixture
def inverse_wiring(inverse_wiring_struct: Inverse_Wiring_Struct) -> InverseWiring:
    return InverseWiring(inverse_wiring_struct)


@pytest.fixture
async def ticker(inverse_wiring: InverseWiring) -> Ticker:
    return Ticker(inverse_wiring, AsyncMock())


def test_ticker_components_returns_components(ticker: Ticker):
    assert {
        ComponentID("In1"),
        ComponentID("Mid1"),
        ComponentID("Out1"),
        ComponentID("Ext1"),
    } == ticker.components


def test_ticker_collate_inputs_collates_inputs(ticker: Ticker):
    assert Input(
        ComponentID("Target"),
        SimTime(100),
        Changes(Map({"TargetOne": 42, "TargetTwo": 3.14})),
    ) == ticker.collate_inputs(
        {
            Input(ComponentID("Target"), SimTime(100), Changes(Map({"TargetOne": 42}))),
            Input(
                ComponentID("Target"), SimTime(100), Changes(Map({"TargetTwo": 3.14}))
            ),
            Input(
                ComponentID("Other"), SimTime(100), Changes(Map({"TargetOne": "wrong"}))
            ),
            Input(
                ComponentID("Target"), SimTime(200), Changes(Map({"TargetOne": False}))
            ),
        },
        ComponentID("Target"),
        SimTime(100),
    )


@pytest.mark.asyncio
async def test_ticker_schedule_possible_updates_schedules_only_possible(ticker: Ticker):
    ticker.time = SimTime(42)
    ticker.inputs = set()
    ticker.to_update = {ComponentID("Out1"): None, ComponentID("Mid1"): None}
    ticker.update_component = AsyncMock()
    await ticker.schedule_possible_updates()
    ticker.update_component.assert_called_once_with(
        Input(ComponentID("Out1"), SimTime(42), Changes(Map()))
    )


@pytest.mark.asyncio
async def test_ticker_schedule_possible_updates_passes_inputs(ticker: Ticker):
    ticker.time = SimTime(42)
    ticker.inputs = {
        Input(ComponentID("Out1"), SimTime(42), Changes(Map({"TestChange": 3.14})))
    }
    ticker.to_update = {ComponentID("Out1"): None}
    ticker.update_component = AsyncMock()
    await ticker.schedule_possible_updates()
    ticker.update_component.assert_called_once_with(
        Input(ComponentID("Out1"), SimTime(42), Changes(Map({"TestChange": 3.14})))
    )


@pytest.mark.asyncio
async def test_ticker_propagate_raises_unexpected_output(ticker: Ticker):
    ticker.time = SimTime(42)
    ticker.to_update = {ComponentID("Out1"): None}
    with pytest.raises(AssertionError):
        await ticker.propagate(
            Output(ComponentID("Mid1"), SimTime(42), Changes(Map()), None)
        )


@pytest.mark.asyncio
async def test_ticker_propagate_raises_unexpected_time(ticker: Ticker):
    ticker.time = SimTime(42)
    ticker.to_update = {ComponentID("Out1"): None}
    with pytest.raises(AssertionError):
        await ticker.propagate(
            Output(ComponentID("Out1"), SimTime(64), Changes(Map()), None)
        )


@pytest.mark.asyncio
async def test_ticker_propagate_schedules_next(ticker: Ticker):
    ticker.time = SimTime(42)
    ticker.inputs = set()
    ticker.to_update = {ComponentID("Out1"): None, ComponentID("Mid1"): None}
    ticker.update_component = AsyncMock()
    await ticker.propagate(
        Output(ComponentID("Out1"), SimTime(42), Changes(Map()), None)
    )
    ticker.update_component.assert_called_once_with(
        Input(ComponentID("Mid1"), SimTime(42), Changes(Map()))
    )


@pytest.mark.asyncio
async def test_ticker_propagate_sets_finished_once_complete(ticker: Ticker):
    ticker.time = SimTime(42)
    ticker.inputs = set()
    ticker.to_update = {ComponentID("Out1"): None}
    ticker.update_component = AsyncMock()
    await ticker.propagate(
        Output(ComponentID("Out1"), SimTime(42), Changes(Map()), None)
    )
    assert ticker.finished.is_set()


@pytest.mark.asyncio
async def test_ticker_start_tick_sets_time(ticker: Ticker):
    await ticker._start_tick(SimTime(42), set())
    assert SimTime(42) == ticker.time


@pytest.mark.asyncio
async def test_ticker_start_tick_sets_empty_inputs(ticker: Ticker):
    await ticker._start_tick(SimTime(42), set())
    assert set() == ticker.inputs


@pytest.mark.asyncio
async def test_ticker_start_tick_adds_root_component_dependents_to_to_update(
    ticker: Ticker,
):
    await ticker._start_tick(SimTime(42), {ComponentID("Mid1")})
    assert {ComponentID("Mid1"): None, ComponentID("In1"): None} == ticker.to_update


@pytest.mark.asyncio
async def test_ticker_call_starts_tick(ticker: Ticker):
    ticker.finished.set()
    ticker._start_tick = MagicMock(ticker._start_tick)  # type: ignore
    await ticker(SimTime(42), set())
    ticker._start_tick.assert_called_once()


@pytest.mark.asyncio
async def test_ticker_call_schedules_possible_updates(ticker: Ticker):
    ticker.finished.set()
    ticker.schedule_possible_updates = MagicMock(  # type: ignore
        ticker.schedule_possible_updates
    )
    await ticker(SimTime(42), set())
    ticker.schedule_possible_updates.assert_called_once()


@pytest.mark.asyncio
async def test_ticker_does_tick(ticker: Ticker):
    updates: List[Input] = list()

    async def update_component(input: Input) -> None:
        updates.append(input)
        await ticker.propagate(Output(input.target, input.time, Changes(Map()), None))

    ticker.update_component = update_component
    await ticker(SimTime(42), {ComponentID("Ext1")})
    assert [
        Input(ComponentID("Ext1"), SimTime(42), Changes(Map())),
        Input(ComponentID("Mid1"), SimTime(42), Changes(Map())),
        Input(ComponentID("In1"), SimTime(42), Changes(Map())),
    ] == updates
