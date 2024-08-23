from pathlib import Path
import pytest
from conftest import (
    TEST_XNAT_DATASET_BLUEPRINTS,
    TestXnatDatasetBlueprint,
    ScanBP,
    FileBP,
    access_dataset,
)
from pipeline2app.xnat.image import XnatApp
from pipeline2app.xnat.command import XnatCommand
from pipeline2app.xnat.deploy import (
    install_and_launch_xnat_cs_command,
)
from fileformats.medimage import NiftiGzX, NiftiGzXBvec


PIPELINE_NAME = "test-concatenate"


@pytest.fixture(params=["func", "bids_app"], scope="session")
def run_spec(
    command_spec,
    bids_command_spec,
    xnat_repository,
    xnat_archive_dir,
    request,
    nifti_sample_dir,
    mock_bids_app_image,
    run_prefix,
):
    spec = {}
    if request.param == "func":
        spec["build"] = {
            "org": "pipeline2app-tests",
            "name": "concatenate-xnat-cs",
            "version": {
                "package": "1.0",
            },
            "title": "A pipeline to test Pydra2App's deployment tool",
            "command": command_spec,
            "authors": [{"name": "Some One", "email": "some.one@an.email.org"}],
            "docs": {
                "info_url": "http://concatenate.readthefakedocs.io",
            },
            "readme": "This is a test README",
            "registry": "a.docker.registry.io",
            "packages": {
                "system": ["git", "vim"],
                "pip": [
                    "pipeline2app",
                    "pipeline2app-xnat",
                    "fileformats",
                    "fileformats-medimage",
                    "pydra",
                ],
            },
        }
        blueprint = TEST_XNAT_DATASET_BLUEPRINTS["concatenate_test"]
        project_id = run_prefix + "concatenate_test"
        blueprint.make_dataset(
            store=xnat_repository,
            dataset_id=project_id,
        )
        spec["dataset"] = access_dataset(
            project_id, "cs", xnat_repository, xnat_archive_dir
        )
        spec["params"] = {"duplicates": 2}
    elif request.param == "bids_app":
        bids_command_spec["configuration"]["executable"] = "/launch.sh"
        spec["build"] = {
            "org": "pipeline2app-tests",
            "name": "bids-app-xnat-cs",
            "version": {
                "package": "1.0",
            },
            "title": "A pipeline to test wrapping of BIDS apps",
            "base_image": {
                "name": mock_bids_app_image,
                "package_manager": "apt",
            },
            "packages": {
                "system": ["git", "vim"],
                "pip": [
                    "fileformats",
                    "fileformats-medimage",
                    "fileformats-medimage-extras",
                    "frametree-bids",
                    "frametree-xnat",
                    "pydra",
                    "pipeline2app",
                    "pipeline2app-xnat",
                ],
            },
            "command": bids_command_spec,
            "authors": [
                {"name": "Some One Else", "email": "some.oneelse@an.email.org"}
            ],
            "docs": {
                "info_url": "http://a-bids-app.readthefakedocs.io",
            },
            "readme": "This is another test README for BIDS app image",
            "registry": "another.docker.registry.io",
        }
        blueprint = TestXnatDatasetBlueprint(
            dim_lengths=[1, 1, 1],
            scans=[
                ScanBP(
                    "anat/T1w",
                    [
                        FileBP(
                            path="NiftiGzX",
                            datatype=NiftiGzX,
                            filenames=["anat/T1w.nii.gz", "anat/T1w.json"],
                        )
                    ],
                ),
                ScanBP(
                    "anat/T2w",
                    [
                        FileBP(
                            path="NiftiGzX",
                            datatype=NiftiGzX,
                            filenames=["anat/T2w.nii.gz", "anat/T2w.json"],
                        )
                    ],
                ),
                ScanBP(
                    "dwi/dwi",
                    [
                        FileBP(
                            path="NiftiGzXBvec",
                            datatype=NiftiGzXBvec,
                            filenames=[
                                "dwi/dwi.nii.gz",
                                "dwi/dwi.json",
                                "dwi/dwi.bvec",
                                "dwi/dwi.bval",
                            ],
                        )
                    ],
                ),
            ],
        )
        project_id = run_prefix + "xnat_cs_bids_app"
        blueprint.make_dataset(
            store=xnat_repository,
            dataset_id=project_id,
            source_data=nifti_sample_dir,
        )
        spec["dataset"] = access_dataset(
            project_id, "cs", xnat_repository, xnat_archive_dir
        )
        spec["params"] = {}
    else:
        assert False, f"unrecognised request param '{request.param}'"
    return spec


def test_xnat_cs_pipeline(xnat_repository, run_spec, run_prefix, work_dir):
    """Tests the complete XNAT deployment pipeline by building and running a
    container"""

    # Retrieve test dataset and build and command specs from fixtures
    build_spec = run_spec["build"]
    dataset = run_spec["dataset"]
    params = run_spec["params"]
    blueprint = dataset.__annotations__["blueprint"]

    # Append run_prefix to command name to avoid clash with previous test runs
    build_spec["name"] = "xnat-cs-test" + run_prefix

    image_spec = XnatApp(**build_spec)

    image_spec.make(
        build_dir=work_dir,
        pipeline2app_install_extras=["test"],
        use_local_packages=True,
        for_localhost=True,
    )

    # We manually set the command in the test XNAT instance as commands are
    # loaded from images when they are pulled from a registry and we use
    # the fact that the container service test XNAT instance shares the
    # outer Docker socket. Since we build the pipeline image with the same
    # socket there is no need to pull it.
    xnat_command = image_spec.command.make_json()

    launch_inputs = {}

    for inpt, scan in zip(xnat_command["inputs"], blueprint.scans):
        launch_inputs[XnatCommand.path2xnatname(inpt["name"])] = scan.name

    for pname, pval in params.items():
        launch_inputs[pname] = pval

    with xnat_repository.connection:

        xlogin = xnat_repository.connection

        test_xsession = next(iter(xlogin.projects[dataset.id].experiments.values()))

        workflow_id, status, out_str = install_and_launch_xnat_cs_command(
            command_json=xnat_command,
            project_id=dataset.id,
            session_id=test_xsession.id,
            inputs=launch_inputs,
            xlogin=xlogin,
        )

        assert status == "Complete", f"Workflow {workflow_id} failed.\n{out_str}"

        for deriv in blueprint.derivatives:
            assert [
                Path(f).name for f in test_xsession.resources[deriv.path].files
            ] == deriv.filenames
