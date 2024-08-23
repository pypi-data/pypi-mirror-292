from __future__ import annotations
import sys
from pathlib import Path
import json
import attrs
from neurodocker.reproenv import DockerRenderer
from frametree.xnat import XnatViaCS
from frametree.core.serialize import ClassResolver, ObjectConverter
from frametree.core.store import Store
from pipeline2app.core.image import App
from .command import XnatCommand


@attrs.define(kw_only=True)
class XnatApp(App):

    PIP_DEPENDENCIES = (
        "pipeline2app-xnat",
        "fileformats-medimage",
        "fileformats-medimage-extras",
    )

    command: XnatCommand = attrs.field(
        converter=ObjectConverter(
            XnatCommand
        )  # Change the command type to XnatCommand subclass
    )

    def construct_dockerfile(
        self,
        build_dir: Path,
        for_localhost: bool = False,
        **kwargs,
    ):
        """Creates a Docker image containing one or more XNAT commands ready
        to be installed in XNAT's container service plugin

        Parameters
        ----------
        build_dir : Path
            the directory to build the docker image within, i.e. where to write
            Dockerfile and supporting files to be copied within the image
        for_localhost : bool
            whether to create the container so that it will work with the test
            XNAT configuration (i.e. hard-coding the XNAT server IP)
        **kwargs:
            Passed on to super `construct_dockerfile` method

        Returns
        -------
        DockerRenderer
            the Neurodocker renderer
        Path
            path to build directory
        """

        dockerfile = super().construct_dockerfile(build_dir, **kwargs)

        xnat_command = self.command.make_json()

        # Copy the generated XNAT commands inside the container for ease of reference
        self.copy_command_ref(dockerfile, xnat_command, build_dir)

        self.save_store_config(dockerfile, build_dir, for_localhost=for_localhost)

        # Convert XNAT command label into string that can by placed inside the
        # Docker label
        commands_label = json.dumps([xnat_command]).replace("$", r"\$")

        self.add_labels(
            dockerfile,
            {"org.nrg.commands": commands_label, "maintainer": self.authors[0].email},
        )

        return dockerfile

    def add_entrypoint(self, dockerfile: DockerRenderer, build_dir: Path):
        pass  # Don't need to add entrypoint as the command line is specified in the command JSON

    def copy_command_ref(self, dockerfile: DockerRenderer, xnat_command, build_dir):
        """Copy the generated command JSON within the Docker image for future reference

        Parameters
        ----------
        dockerfile : DockerRenderer
            Neurodocker renderer to build
        xnat_command : ty.Dict[str, Any]
            XNAT command to write to file within the image for future reference
        build_dir : Path
            path to build directory
        """
        # Copy command JSON inside dockerfile for ease of reference
        with open(build_dir / "xnat_command.json", "w") as f:
            json.dump(xnat_command, f, indent="    ")
        dockerfile.copy(
            source=["./xnat_command.json"], destination="/xnat_command.json"
        )

    def save_store_config(
        self, dockerfile: DockerRenderer, build_dir: Path, for_localhost=False
    ):
        """Save a configuration for a XnatViaCS store.

        Parameters
        ----------
        dockerfile : DockerRenderer
            Neurodocker renderer to build
        build_dir : Path
            the build directory to save supporting files
        for_localhost : bool
            whether the target XNAT is using the local test configuration, in which
            case the server location will be hard-coded rather than rely on the
            XNAT_HOST environment variable passed to the container by the XNAT CS
        """
        xnat_cs_store_entry = {
            "class": "<" + ClassResolver.tostr(XnatViaCS, strip_prefix=False) + ">"
        }
        if for_localhost:
            if sys.platform == "linux":
                ip_address = "172.17.0.1"  # Linux + GH Actions
            else:
                ip_address = "host.docker.internal"  # Mac/Windows local debug
            xnat_cs_store_entry["server"] = "http://" + ip_address + ":8080"
        Store.save_configs(
            {"xnat-cs": xnat_cs_store_entry}, config_path=build_dir / "stores.yaml"
        )
        dockerfile.run(command="mkdir -p /root/.pipeline2app")
        dockerfile.run(command=f"mkdir -p {str(XnatViaCS.CACHE_DIR)}")
        dockerfile.copy(
            source=["./stores.yaml"],
            destination=self.IN_DOCKER_FRAMETREE_HOME_DIR + "/stores.yaml",
        )
