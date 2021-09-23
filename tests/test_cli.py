from pathlib import Path

import mock
from click.testing import CliRunner, Result

from tickit.cli import main


def test_cli_set_loggging_level():
    runner: CliRunner = CliRunner()
    with mock.patch("logging.basicConfig") as mock_basicConfig:
        result: Result = runner.invoke(main, args=["--log-level", "INFO"])
        assert result.exit_code == 0
        mock_basicConfig.assert_called_with(level="INFO")


def test_component_command():
    runner: CliRunner = CliRunner()

    test_config_path: str = (
        (Path(__file__).parent / "../examples/configs/sunk-trampoline.yaml")
        .resolve()
        .__str__()
    )

    with mock.patch("asyncio.run") as run_patch:
        result: Result = runner.invoke(
            main, args=["component", "rand_tramp", test_config_path]
        )
        assert result.exit_code == 0

    run_patch.assert_called()


def test_scheduler():
    runner: CliRunner = CliRunner()

    test_config_path: str = (
        (Path(__file__).parent / "../examples/configs/sunk-trampoline.yaml")
        .resolve()
        .__str__()
    )

    with mock.patch("asyncio.run") as run_patch:
        result: Result = runner.invoke(main, args=["scheduler", test_config_path])
        assert result.exit_code == 0

    run_patch.assert_called()


def test_all():
    runner: CliRunner = CliRunner()

    test_config_path: str = (
        (Path(__file__).parent / "../examples/configs/sunk-trampoline.yaml")
        .resolve()
        .__str__()
    )

    with mock.patch("asyncio.run") as run_patch:
        result: Result = runner.invoke(main, args=["all", test_config_path])
        assert result.exit_code == 0

    run_patch.assert_called()
