from pathlib import Path

import pytest
from click.testing import CliRunner
from kedro.pipeline import Pipeline
from kedro.pipeline import node

from kedro_argo.cli import clean_name
from kedro_argo.cli import commands
from kedro_argo.cli import get_deps_dict
from kedro_argo.cli import get_source_template_filename
from kedro_argo.cli import get_tags
from kedro_argo.cli import transform_parameters


def identity(x):
    return x


@pytest.fixture
def mock_pipe():
    mock_node1 = node(identity, "a", "b")
    mock_node2 = node(identity, "b", "c")
    mock_pipe = Pipeline([mock_node1, mock_node2])
    return mock_pipe


@pytest.fixture
def mock_named_pipe():
    mock_node1 = node(identity, "a", "b", name="step_1", tags=["argo.image.what"])
    mock_node2 = node(identity, "b", "c", name="step_2", tags=["argo.huh"])
    mock_named_pipe = Pipeline([mock_node1, mock_node2])
    return mock_named_pipe


def test_main():
    runner = CliRunner()
    result = runner.invoke(commands, [])

    assert result.exit_code == 0


def test_transform_parameters():
    parameters = {"a": 1, "b": "c"}
    expected_pretty_params = [
        {"name": "a", "default": 1, "caption": "a"},
        {"name": "b", "default": "c", "caption": "b"},
    ]
    assert transform_parameters(parameters) == expected_pretty_params


def test_get_deps_dict(mock_named_pipe):
    dependencies = mock_named_pipe.node_dependencies
    deps_dict = get_deps_dict(dependencies)
    expected_deps_dict = [
        {"node": "step_1", "name": "step-1", "dep": []},
        {"node": "step_2", "name": "step-2", "dep": ["step-1"]},
    ]
    assert type(deps_dict) == list
    assert len(dependencies) == len(deps_dict)
    assert deps_dict == expected_deps_dict


def test_clean_name():
    dirty_name = "hi_there[ a ] -> [b]"
    cleaned_name = clean_name(dirty_name)
    expected_name = "hi-there-a-b"
    assert cleaned_name == expected_name


def test_get_tags(mock_named_pipe):
    tags = get_tags(mock_named_pipe)
    expected_tags = {"step_1": {"argo.image.what"}, "step_2": {"argo.huh"}}
    assert type(tags) == dict
    assert tags == expected_tags


def test_source_template_filename():
    source_file = get_source_template_filename()
    assert Path(source_file).exists()
