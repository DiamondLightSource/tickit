import asyncio
import signal
import sys
from subprocess import PIPE, STDOUT, Popen

import pytest
import pytest_asyncio

from tickit.core.management.event_router import InverseWiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.runner import run_all_forever
from tickit.core.state_interfaces.state_interface import get_interface
from tickit.utils.configuration.loading import read_configs


# https://docs.pytest.org/en/latest/example/parametrize.html#indirect-parametrization
@pytest.fixture
def tickit_process(request):
    """Subprocess that runs ``tickit all <config_path>``."""
    config_path: str = request.param
    proc = Popen(
        [sys.executable, "-m", "tickit", "all", config_path],
        stdout=PIPE,
        stderr=STDOUT,
        text=True,
    )
    # Wait for IOC to be up
    while True:
        if "complete" in proc.stdout.readline():
            break
    yield proc
    proc.send_signal(signal.SIGINT)
    print(proc.communicate()[0])


@pytest_asyncio.fixture
async def tickit_task(request):
    """Task that runs ``tickit all <config_path>``."""
    config_path: str = request.param
    configs = read_configs(config_path)
    inverse_wiring = InverseWiring.from_component_configs(configs)
    scheduler = MasterScheduler(inverse_wiring, *get_interface("internal"))
    t = asyncio.Task(
        run_all_forever(
            [c().run_forever(*get_interface("internal")) for c in configs]
            + [scheduler.run_forever()]
        )
    )
    # TODO: would like to await all_servers_running() here
    await asyncio.sleep(0.5)
    yield t
    tasks = asyncio.tasks.all_tasks()
    for task in tasks:
        task.cancel()
    try:
        await t
    except asyncio.CancelledError:
        pass


@pytest.fixture
def event_loop():
    """Manage instance of event loop for runner test cases."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
