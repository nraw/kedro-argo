import logging
import re
import shutil
from pathlib import Path

import click
import pkg_resources
import yaml
from kedro import cli


@click.group(name="ARGO")
def commands():
    """ Kedro plugin for transforming kedro pipelines to argo pipelines """
    pass


@commands.command("argo")
@click.argument("image", required=True)
@click.option("-t", "--templates_folder", default="templates")
@click.option("--ytt", default=False)
@click.option("-n", "--namespace", default="")
def argokedro(image, templates_folder, ytt, namespace):
    """Creates an argo pipeline yaml
    - https://get-ytt.io/#playground
    """
    pc = cli.get_project_context()
    pipeline = pc.pipeline
    project_name = pc.project_name
    parameters = pc.catalog.load("parameters")
    pretty_params = transform_parameters(parameters)
    dependencies = pipeline.node_dependencies
    deps_dict = get_deps_dict(dependencies)
    tags = get_tags(pipeline)
    tagged_deps_dict = update_deps_dict_with_tags(deps_dict, tags)
    kedro_dict = {
        "tasks": tagged_deps_dict,
        "image": image,
        "project_name": project_name,
        "parameters": pretty_params,
        "namespace": namespace,
    }
    kedro_yaml = generate_yaml(kedro_dict)
    if ytt:
        kedro_yaml = ytt_add_values_part(kedro_yaml)
        copy_template(templates_folder, ytt)
        logging.info(f"YTT template saved in {templates_folder} folder")
    save_yaml(kedro_yaml, templates_folder)
    logging.info(f"Kedro template saved in {templates_folder} folder")
    if ytt:
        click.secho(FINISHED_MESSAGE_YTT)


def transform_parameters(parameters):
    pretty_params = [
        {"name": key, "default": value, "caption": key}
        for key, value in parameters.items()
    ]
    return pretty_params


def get_deps_dict(dependencies):
    deps_dict = [
        {
            "node": key.name,
            "name": clean_name(key.name),
            "dep": [clean_name(val.name) for val in vals],
        }
        for key, vals in dependencies.items()
    ]
    return deps_dict


def clean_name(name):
    clean_name = re.sub(r"[\W_]+", "-", name).strip("-")
    return clean_name


def get_tags(pipeline):
    nodes = pipeline.nodes
    tags = {node.name: node.tags for node in nodes}
    return tags


def update_deps_dict_with_tags(deps_dict, tags):
    for dep_dict in deps_dict:
        node_tags = tags[dep_dict["node"]]
        tag_dict = parse_tags(node_tags)
        dep_dict.update(tag_dict)
    return deps_dict


def parse_tags(node_tags, sep="."):
    if node_tags:
        split_tags = [tag.split(sep) for tag in node_tags]
        split_tags = [
            [tag[0], sep.join(tag[1:-1]), tag[-1]]
            for tag in split_tags
            if len(tag) > 2 and tag[0] == "argo"
        ]
        tag_dict = {tag[1]: tag[2] for tag in split_tags}
        return tag_dict
    else:
        return {}


def generate_yaml(kedro_dict):
    kedro_yaml = yaml.safe_dump(kedro_dict)
    return kedro_yaml


def ytt_add_values_part(kedro_yaml):
    kedro_yaml = "#@data/values\n---\n" + kedro_yaml
    return kedro_yaml


def save_yaml(kedro_yaml, templates_folder):
    Path(templates_folder).mkdir(parents=True, exist_ok=True)
    Path(templates_folder + "/kedro.yaml").write_text(kedro_yaml)


def copy_template(templates_folder, ytt):
    if ytt:
        Path(templates_folder).mkdir(parents=True, exist_ok=True)
        template_filename = "argo_template.yaml"
        source_file = get_source_template_filename(template_filename)
        target_file = Path(templates_folder) / template_filename
        if not target_file.exists():
            shutil.copy2(str(source_file), str(templates_folder))


def get_source_template_filename(template_filename="argo_template.yaml"):
    source_file_relative = Path("templates") / template_filename
    source_file = pkg_resources.resource_filename(__name__, str(source_file_relative))
    return source_file


FINISHED_MESSAGE_YTT = """
You can now run:

$ ytt -f templates > argo.yaml

or if you prefer in Docker:

$ docker run --rm -it --name ytt -v $(pwd)/templates:/templates gerritk/ytt:latest -f /templates > argo.yaml

and finally

$ argo submit --watch argo.yaml
"""
