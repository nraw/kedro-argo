"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mkedro_argo` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``kedro_argo.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``kedro_argo.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import os
import pathlib
import shutil

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
@click.argument("templates_folder")
def argokedro(image, templates_folder="templates"):
    """Creates argo pipeline
    https://get-ytt.io/#playground
    """
    pc = cli.get_project_context()
    dependencies = pc.pipeline.node_dependencies
    deps_dict = [
        {"name": key.name, "dep": str([val.name for val in vals])}
        for key, vals in dependencies.items()
    ]
    nodes = pc.pipeline.nodes
    tags = {node.name: node.tags for node in nodes}
    yaml_pipe = generate_yaml(deps_dict, tags, image)
    save_yamls(yaml_pipe, templates_folder)
    print(yaml_pipe)


def generate_yaml(deps_dict, tags, image):
    for dep_dict in deps_dict:
        node_tags = tags[dep_dict["name"]]
        tag_dict = parse_tags(node_tags)
        dep_dict.update(tag_dict)
    pipe_dict = {"steps": deps_dict, "image": image}
    yaml_pipe = yaml.dump(pipe_dict).replace("'", "")
    yaml_pipe = "#@data/values\n---\n" + yaml_pipe
    return yaml_pipe


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


def save_yamls(yaml_pipe, templates_folder):
    os.mkdir(templates_folder)
    kedro_yaml_file = os.path.join(templates_folder, "kedro.yaml")
    pathlib.Path(kedro_yaml_file).write_text(yaml_pipe)
    path = "templates/argo_template.yaml"
    template_file = pkg_resources.resource_filename(__name__, path)
    shutil.copy2(template_file, templates_folder)
