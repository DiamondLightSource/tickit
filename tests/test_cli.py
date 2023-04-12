import subprocess
from typing import Iterable

import pytest
from click.testing import CliRunner, Result
from mock import Mock, patch
from mock.mock import create_autospec

from tickit import __version__
from tickit.cli import main
from tickit.core.components.component import ComponentConfig
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.typedefs import ComponentID, ComponentPort, PortID


def test_cli_version():
    cmd = ["tickit", "--version"]
    assert (
        subprocess.check_output(cmd).decode().strip()
        == f"tickit, version {__version__}"
    )


@pytest.fixture
def patch_logging() -> Iterable[Mock]:
    with patch("tickit.cli.logging", autospec=True) as mock:
        yield mock


@pytest.fixture
def patch_run_all_forever() -> Iterable[Mock]:
    with patch("tickit.cli.run_all_forever", autospec=True) as mock:
        yield mock


@pytest.fixture
def patch_asyncio() -> Iterable[Mock]:
    with patch("tickit.cli.asyncio", autospec=True) as mock:
        yield mock


@pytest.fixture
def patch_read_configs() -> Iterable[Mock]:
    with patch("tickit.cli.read_configs", autospec=True) as mock:
        mock_config = create_autospec(ComponentConfig, instance=True)
        mock_config.name = "fake_device"
        mock_config.inputs = {
            PortID("42"),
            ComponentPort(ComponentID("foo"), PortID("24")),
        }
        mock.return_value = [mock_config]
        yield mock


def test_cli_set_logging_level(
    patch_logging: Mock,
):
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(main, args=["--log-level", "INFO"])
    assert result.exit_code == 0
    patch_logging.basicConfig.assert_called_with(level="INFO")


def test_component_command(
    patch_run_all_forever: Mock,
    patch_read_configs: Mock,
    event_loop,
):
    runner: CliRunner = CliRunner()

    result: Result = runner.invoke(
        main, args=["component", "fake_device", "path/to/fake_device.yaml"]
    )

    assert result.exit_code == 0
    patch_run_all_forever.assert_called_once()


@pytest.fixture
def patch_master_scheduler_run_forever_method() -> Iterable[Mock]:
    with patch.object(MasterScheduler, "run_forever", autospec=True) as mock:
        yield mock


def test_scheduler(
    patch_read_configs: Mock,
    patch_master_scheduler_run_forever_method: Mock,
    event_loop,
):
    runner: CliRunner = CliRunner()

    result: Result = runner.invoke(main, args=["scheduler", "path/to/fake_device.yaml"])

    assert result.exit_code == 0
    patch_master_scheduler_run_forever_method.assert_awaited_once()


def test_all(
    patch_read_configs: Mock,
    patch_master_scheduler_run_forever_method: Mock,
    event_loop,
):
    runner: CliRunner = CliRunner()

    result: Result = runner.invoke(main, args=["all", "path/to/fake_device.yaml"])

    assert result.exit_code == 0
    patch_master_scheduler_run_forever_method.assert_awaited_once()
