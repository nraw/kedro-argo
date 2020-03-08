from pathlib import Path

import pytest
from click.testing import CliRunner
from kedro.pipeline import Pipeline
from kedro.pipeline import node

from kedro_argo.cli import commands
from kedro_argo.cli import get_deps_dict
from kedro_argo.cli import get_source_template_filename
from kedro_argo.cli import get_tags


@pytest.fixture
def mock_pipe():
    def identity(x):
        return x

    mock_node1 = node(identity, "a", "b")
    mock_node2 = node(identity, "b", "c")
    mock_pipe = Pipeline([mock_node1, mock_node2])
    return mock_pipe


@pytest.fixture
def mock_named_pipe():
    def identity(x):
        return x

    mock_node1 = node(identity, "a", "b", name="step_1", tags=["argo.image.what"])
    mock_node2 = node(identity, "b", "c", name="step_2", tags=["argo.huh"])
    mock_named_pipe = Pipeline([mock_node1, mock_node2])
    return mock_named_pipe


def test_main():
    runner = CliRunner()
    result = runner.invoke(commands, [])

    assert result.exit_code == 0


def test_get_deps_dict(mock_pipe):
    dependencies = mock_pipe.node_dependencies
    deps_dict = get_deps_dict(dependencies)
    expected_deps_dict = [
        {"name": "identity([a]) -> [b]", "dep": "[]"},
        {"name": "identity([b]) -> [c]", "dep": "['identity([a]) -> [b]']"},
    ]
    assert type(deps_dict) == list
    assert len(dependencies) == len(deps_dict)
    assert deps_dict == expected_deps_dict


def test_get_tags(mock_named_pipe):
    tags = get_tags(mock_named_pipe)
    expected_tags = {"step_1": {"argo.image.what"}, "step_2": {"argo.huh"}}
    assert type(tags) == dict
    assert tags == expected_tags


def test_source_template_filename():
    source_file = get_source_template_filename()
    assert Path(source_file).exists()
