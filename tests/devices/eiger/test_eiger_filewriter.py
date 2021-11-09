import json

import aiohttp
import pytest

from tickit.devices.eiger.filewriter.eiger_filewriter import EigerFileWriter


@pytest.fixture
def filewriter() -> EigerFileWriter:
    return EigerFileWriter()


def test_eiger_filewriter_constructor():
    EigerFileWriter()


@pytest.mark.asyncio
@pytest.mark.parametrize("tickit_task", ["examples/configs/eiger.yaml"], indirect=True)
async def test_eiger_filewriter_system(tickit_task):

    url = "http://0.0.0.0:8081/filewriter/api/1.8.0/"

    async with aiohttp.ClientSession() as session:

        async with session.get(url + "config/mode") as resp:
            assert "enabled" == json.loads(str(await resp.text()))["value"]

        async with session.get(url + "status/state") as resp:
            assert "ready" == json.loads(str(await resp.text()))["value"]
