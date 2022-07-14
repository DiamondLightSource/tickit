import asyncio

import pytest
from aioca import caget, caput


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tickit_process", ["examples/configs/multi-ioc.yaml"], indirect=True
)
async def test_femto_system(tickit_process):
    assert (await caget("FEMTO:GAIN_RBV")) == 2.5
    current = await caget("FEMTO:CURRENT")
    assert 100 * 2.5 <= current < 200 * 2.5
    await caput("FEMTO:GAIN", 0.01)
    await asyncio.sleep(0.5)
    assert (await caget("FEMTO:GAIN_RBV")) == 0.01
    current = await caget("FEMTO:CURRENT")
    assert 100 * 0.01 <= current < 200 * 0.01

    async def toggle(expected: bool):
        assert (await caget("PNEUMATIC:FILTER_RBV")) != expected
        await caput("PNEUMATIC:FILTER", expected)
        await asyncio.sleep(0.8)
        assert (await caget("PNEUMATIC:FILTER_RBV")) == expected

    await toggle(True)
    await toggle(False)
