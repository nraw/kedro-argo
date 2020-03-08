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
@click.argument("templates_folder", default="templates")
@click.option("--force-template", default=False)
def argokedro(image, templates_folder, force_template):
    """Creates an argo pipeline yaml
    - https://get-ytt.io/#playground
    """
    pc = cli.get_project_context()
    pipeline = pc.pipeline
    dependencies = pipeline.node_dependencies
    deps_dict = get_deps_dict(dependencies)
    tags = get_tags(pipeline)
    tagged_deps_dict = update_deps_dict_with_tags(deps_dict, tags)
    yaml_pipe = generate_yaml(tagged_deps_dict, image)
    save_yaml(yaml_pipe, templates_folder)
    copy_template(templates_folder, force_template)
    logging.info("Templates saved in `templates` folder")
    click.secho(FINISHED_MESSAGE)


def get_deps_dict(dependencies):
    deps_dict = [
        {
            "name": key.name,
            "clean_name": clean_name(key.name),
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
        node_tags = tags[dep_dict["name"]]
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


def generate_yaml(deps_dict, image):
    pipe_dict = {"steps": deps_dict, "image": image}
    yaml_pipe = yaml.safe_dump(pipe_dict)
    yaml_pipe = "#@data/values\n---\n" + yaml_pipe
    return yaml_pipe


def save_yaml(yaml_pipe, templates_folder):
    Path(templates_folder).mkdir(parents=True, exist_ok=True)
    Path(templates_folder + "/kedro.yaml").write_text(yaml_pipe)


def copy_template(templates_folder, force_template):
    template_filename = "argo_template.yaml"
    source_file = get_source_template_filename(template_filename)
    target_file = Path(templates_folder) / template_filename
    if not target_file.exists() or force_template:
        shutil.copy2(str(source_file), str(templates_folder))


def get_source_template_filename(template_filename="argo_template.yaml"):
    source_file_relative = Path("templates") / template_filename
    source_file = pkg_resources.resource_filename(__name__, str(source_file_relative))
    return source_file


FINISHED_MESSAGE = """
You can now run:

$ ytt -f templates > argo.yaml

or if you prefer in Docker:

$ docker run --rm -it --name ytt -v $(pwd)/templates:/templates gerritk/ytt:latest -f /templates > argo.yaml

and finally

$ argo submit --watch argo.yaml
"""
