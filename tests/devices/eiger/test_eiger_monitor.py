import json

import aiohttp
import pytest

from tickit.devices.eiger.monitor.eiger_monitor import EigerMonitor


@pytest.fixture
def filewriter() -> EigerMonitor:
    return EigerMonitor()


def test_eiger_monitor_constructor():
    EigerMonitor()


@pytest.mark.asyncio
@pytest.mark.parametrize("tickit_task", ["examples/configs/eiger.yaml"], indirect=True)
async def test_eiger_monitor_system(tickit_task):

    url = "http://0.0.0.0:8081/monitor/api/1.8.0/"

    async with aiohttp.ClientSession() as session:

        async with session.get(url + "config/mode") as resp:
            assert "enabled" == json.loads(str(await resp.text()))["value"]

        async with session.get(url + "status/error") as resp:
            assert [] == json.loads(str(await resp.text()))["value"]
