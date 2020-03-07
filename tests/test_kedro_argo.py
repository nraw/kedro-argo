
from click.testing import CliRunner

from kedro_argo.cli import commands


def test_main():
    runner = CliRunner()
    result = runner.invoke(commands, [])

    assert result.exit_code == 0
