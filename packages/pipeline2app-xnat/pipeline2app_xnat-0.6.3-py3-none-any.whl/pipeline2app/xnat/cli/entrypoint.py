import click
from pipeline2app.core.command import entrypoint_opts
from pipeline2app.xnat import XnatApp
from .base import xnat_group


@xnat_group.command(
    name="cs-entrypoint",
    help="""Loads a dataset, or creates one it is not already present, then applies and
launches a pipeline in a single command. To be used within the command configuration
of an XNAT Container Service ready Docker image.

ADDRESS string containing the nickname of the data store, the ID of the
dataset (e.g. XNAT project ID or file-system directory) and the dataset's name
in the format <store-nickname>//<dataset-id>[@<dataset-name>]

""",
)
@click.argument("address")
@entrypoint_opts.data_columns
@entrypoint_opts.parameterisation
@entrypoint_opts.execution
@entrypoint_opts.debugging
@entrypoint_opts.dataset_config
def cs_entrypoint(
    address,
    spec_path,
    **kwargs,
):

    image_spec = XnatApp.load(spec_path)

    image_spec.command.execute(
        address,
        **kwargs,
    )
