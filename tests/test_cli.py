from pathlib import Path

import mock
import pytest
from click.testing import CliRunner, Result
from mock.mock import AsyncMock


@pytest.fixture
def mock_run_all_forever():
    with mock.patch("tickit.cli.run_all_forever") as mock_run_all_forever:
        yield mock_run_all_forever


def test_cli_set_loggging_level():
    from tickit.cli import main

    runner: CliRunner = CliRunner()
    with mock.patch("logging.basicConfig") as mock_basicConfig:
        result: Result = runner.invoke(main, args=["--log-level", "INFO"])
        assert result.exit_code == 0
        mock_basicConfig.assert_called_with(level="INFO")


def test_component_command(mock_run_all_forever: AsyncMock):
    from tickit.cli import main

    runner: CliRunner = CliRunner()

    test_config_path: str = (
        (Path(__file__).parent / "../examples/configs/sunk-trampoline.yaml")
        .resolve()
        .__str__()
    )

    result: Result = runner.invoke(
        main, args=["component", "rand_tramp", test_config_path]
    )
    assert result.exit_code == 0

    mock_run_all_forever.assert_called_once()


def test_scheduler(mock_run_all_forever: AsyncMock):
    from tickit.cli import main

    runner: CliRunner = CliRunner()

    test_config_path: str = (
        (Path(__file__).parent / "../examples/configs/sunk-trampoline.yaml")
        .resolve()
        .__str__()
    )

    result: Result = runner.invoke(main, args=["scheduler", test_config_path])
    assert result.exit_code == 0

    mock_run_all_forever.assert_awaited_once()


def test_all(mock_run_all_forever: AsyncMock):
    from tickit.cli import main

    runner: CliRunner = CliRunner()

    test_config_path: str = (
        (Path(__file__).parent / "../examples/configs/sunk-trampoline.yaml")
        .resolve()
        .__str__()
    )

    result: Result = runner.invoke(main, args=["all", test_config_path])
    assert result.exit_code == 0

    mock_run_all_forever.assert_awaited_once()
