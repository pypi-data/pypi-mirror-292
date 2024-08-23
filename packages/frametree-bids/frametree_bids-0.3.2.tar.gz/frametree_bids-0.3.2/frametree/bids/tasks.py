from __future__ import annotations
import attrs
from copy import copy
import tempfile
import logging
import typing as ty
import shutil
import shlex
from pathlib import Path
from pydra import Workflow
from pydra.engine.task import ShellCommandTask
from pydra.engine.specs import (
    ShellSpec,
    SpecInfo,
    ShellOutSpec,
)
from pydra.engine.environments import Docker, Native
from frametree.core import __version__
from frametree.core.frameset import FrameSet
from fileformats.core import FileSet
from fileformats.generic import Directory
from frametree.common import Clinical
from frametree.bids.store import JsonEdit
from frametree.core.serialize import (
    ClassResolver,
    ObjectListConverter,
)
from frametree.core.utils import func_task
from .store import Bids

logger = logging.getLogger("frametree")


@attrs.define(kw_only=True)
class BidsInput:

    name: str
    path: str
    datatype: FileSet = attrs.field(converter=ClassResolver(FileSet))


@attrs.define(kw_only=True)
class BidsOutput:

    name: str
    datatype: FileSet = attrs.field(converter=ClassResolver(FileSet))
    path: ty.Optional[str] = None


logger = logging.getLogger("frametree")


def bids_app(
    name: str,
    inputs: ty.List[ty.Union[BidsInput, ty.Dict[str, str]]],
    outputs: ty.List[ty.Union[BidsOutput, ty.Dict[str, str]]],
    executable: str = "",  # Use entrypoint of container,
    container_image: ty.Optional[str] = None,
    parameters: ty.Dict[str, type] = None,
    row_frequency: ty.Union[Clinical, str] = Clinical.session,
    container_type: str = "docker",
    dataset: ty.Optional[ty.Union[str, Path, FrameSet]] = None,
    app_output_dir: ty.Optional[Path] = None,
    app_work_dir: ty.Optional[Path] = None,
    json_edits: ty.List[ty.Tuple[str, str]] = None,
) -> Workflow:
    """Creates a Pydra workflow which takes file inputs, maps them to
    a BIDS dataset, executes a BIDS app, and then extracts the
    the derivatives that were stored back in the BIDS dataset by the app

    Parameters
    ----------
    name : str
        Name of the workflow/BIDS app. Will be used to name the 'derivatives'
        sub-directory where the app outputs are stored
    inputs : list[ty.Union[AppField, ty.Dict[str, str]]]
        The inputs to be inserted into the BIDS dataset. Should be a list of tuples
        consisting of the the path the file/directory should be stored within a BIDS subject/session,
        e.g. anat/T1w, func/bold, and the DataFormat class it should be stored in, e.g.
        fileformats.medimage.NiftiGzX.
    outputs : list[ty.Union[AppField, ty.Dict[str, str]]]
        The outputs to be extracted from the derivatives directory. Should be a list of tuples
        consisting of the the path the file/directory is saved by the app within a BIDS subject/session,
        e.g. freesurfer/recon-all, and the DataFormat class it is stored in,
    executable : str, optional
        Name of the executable within the image to run (i.e. the entrypoint of the image).
        Required when extending the base image and launching FrameTree within it. Defaults to
        empty string, i.e. the entrypoint of the BIDS app container image
    container_image : str, optional
        Name of the BIDS app image to wrap
    parameters : ty.Dict[str, type], optional
        a list of parameters of the app (i.e. CLI flags) to be exposed to the user
        mapped to their data type.
    row_frequency : Clinical, optional
        Frequency to run the app at, i.e. per-"session" or per-"dataset"
    container_type : str, optional
        The virtualisation method to run the main app task, can be one of
        'docker' or 'singularity'
    dataset : str or FrameSet, optional
        The dataset to run the BIDS app on. If a string or Path is provided
        then a new BIDS dataset is created at that location with a single
        subject (sub-DEFAULT). If nothing is provided then a dataset is
        created in a temporary directory.
    app_output_dir : Path, optional
        file system path where the app outputs will be written before being
        copied to the dataset directory
    app_work_dir: Path, optional
        the directory used to run the app within. Can be used to avoid overly long path
        lengths that can occur running nested workflows (e.g. fmriprep)
    json_edits: ty.List[ty.Tuple[str, str]]
        Ad-hoc edits to JSON side-cars that are fixed during the configuration
        of the app, i.e. not passed as an input. Input JSON edits are appended
        to these fixed

    Returns
    -------
    pydra.Workflow
        A Pydra workflow
    """
    if parameters is None:
        parameters = {}
    if app_output_dir is None:
        app_output_dir = Path(tempfile.mkdtemp())
    else:
        app_output_dir = Path(app_output_dir)
        app_output_dir.mkdir(parents=True, exist_ok=True)
    if app_work_dir is None:
        app_work_dir = Path(tempfile.mkdtemp())
    else:
        app_work_dir = Path(app_work_dir)
        app_work_dir.mkdir(parents=True, exist_ok=True)

    if json_edits is None:
        json_edits = []

    if isinstance(row_frequency, str):
        row_frequency = Clinical[row_frequency]

    # Create BIDS dataset to hold translated data
    if dataset is None:
        dataset = Path(tempfile.mkdtemp()) / "frametree_bids_dataset"
    if not isinstance(dataset, FrameSet):
        dataset = Bids().create_dataset(
            id=dataset,
            name=name + "_dataset",
            leaves=[(DEFAULT_BIDS_ID,)],
            metadata={
                "authors": [
                    f"Auto-generated by FrameTree {__version__}",
                    "Dummy second author",
                ]
            },
        )
        wf_kwargs = {"id": DEFAULT_BIDS_ID}
    else:
        wf_kwargs = {}

    # Convert from JSON format inputs/outputs to tuples with resolved data formats
    inputs = ObjectListConverter(BidsInput)(inputs)
    outputs = ObjectListConverter(BidsOutput)(outputs)

    # Ensure output paths all start with 'derivatives
    input_names = [i.name for i in inputs]
    output_names = [o.name for o in outputs]

    input_spec = set(["id", "flags", "json_edits"] + input_names + list(parameters))

    wf = Workflow(name=name, input_spec=list(input_spec), **wf_kwargs)

    # # Check id startswith 'sub-' as per BIDS
    # wf.add(bidsify_id(name="bidsify_id", id=wf.lzin.id))

    # Can't use a decorated function as we need to allow for dynamic
    # arguments
    wf.add(
        func_task(
            to_bids,
            in_fields=(
                [
                    ("row_frequency", Clinical),
                    ("inputs", ty.List[BidsInput]),
                    ("dataset", ty.Union[FrameSet, str]),
                    ("id", str),
                    ("json_edits", str),
                    ("fixed_json_edits", ty.List[ty.Tuple[str, str]]),
                ]
                + [(i, ty.Union[str, Path]) for i in input_names]
            ),
            out_fields=[
                ("frameset", FrameSet),
                ("completed", bool),
            ],
            name="to_bids",
            row_frequency=row_frequency,
            inputs=inputs,
            dataset=dataset,
            id=wf.lzin.id,
            json_edits=wf.lzin.json_edits,
            fixed_json_edits=json_edits,
            **{i: getattr(wf.lzin, i) for i in input_names},
        )
    )

    # dataset_path=Path(dataset.id),
    # output_dir=app_output_dir,
    # parameters={p: type(p) for p in parameters},
    # id=wf.bidsify_id.lzout.no_prefix,

    input_fields = copy(BIDS_APP_INPUTS)

    for param in parameters.items():
        argstr = f"--{param}"
        if type(param) is not bool:
            argstr += " %s"
        input_fields.append(
            (
                param,
                type(param),
                {"help_string": f"Optional parameter {param}", "argstr": argstr},
            )
        )

    kwargs = {p: getattr(wf.lzin, p) for p in parameters}

    # If 'image' is None, don't use any virtualisation (i.e. assume we are running from "inside" the
    # container or extension of it)
    if container_image is None:
        app_output_path = str(app_output_dir)
        environment = Native()
    else:
        environment = Docker(container_image)
        app_output_path = CONTAINER_DERIV_PATH

    if row_frequency == Clinical.session:
        analysis_level = "participant"
        kwargs["participant_label"] = wf.lzin.id  # wf.bidsify_id.lzout.no_prefix
    else:
        analysis_level = "group"

    main_task = ShellCommandTask(
        name="bids_app",
        input_spec=SpecInfo(name="Input", fields=input_fields, bases=(ShellSpec,)),
        output_spec=SpecInfo(
            name="Output", fields=BIDS_APP_OUTPUTS, bases=(ShellOutSpec,)
        ),
        dataset_path=dataset.id,
        output_path=str(app_output_path),
        work_dir=str(app_work_dir),
        analysis_level=analysis_level,
        executable=executable,
        environment=environment,
        flags=wf.lzin.flags,
        setup_completed=wf.to_bids.lzout.completed,
        **kwargs,
    )

    if container_image is not None:
        main_task.bindings = {
            # str(dataset.id): (CONTAINER_DATASET_PATH, "ro"),
            str(app_output_dir): (CONTAINER_DERIV_PATH, "rw"),
        }

    wf.add(main_task)

    wf.add(
        func_task(
            extract_bids,
            in_fields=[
                ("dataset", FrameSet),
                ("row_frequency", Clinical),
                ("app_name", str),
                ("output_dir", Path),
                ("outputs", ty.List[BidsOutput]),
                ("id", str),
                ("app_completed", bool),
            ],
            out_fields=[(o, str) for o in output_names],
            name="extract_bids",
            app_name=name,
            # We pass dataset object modified by to_bids rather than initial one passed
            # to the bids_app method
            dataset=wf.to_bids.lzout.frameset,
            output_dir=app_output_dir,
            row_frequency=row_frequency,
            outputs=outputs,
            id=wf.lzin.id,  # wf.bidsify_id.lzout.out,
            app_completed=wf.bids_app.lzout.completed,
        )
    )

    for output_name in output_names:
        wf.set_output((output_name, getattr(wf.extract_bids.lzout, output_name)))

    return wf


# For running
CONTAINER_DERIV_PATH = "/frametree_bids_outputs"
CONTAINER_DATASET_PATH = "/frametree_bids_dataset"

DEFAULT_BIDS_ID = "DEFAULT"


# @mark.task
# @mark.annotate({"return": {"out": str, "no_prefix": str}})
# def bidsify_id(id):
#     if id == attrs.NOTHING:
#         id = DEFAULT_BIDS_ID
#     else:
#         id = re.sub(r"[^a-zA-Z0-9]", "", id)
#         if not id.startswith("sub-"):
#             id = "sub-" + id
#     return id, id[len("sub-") :]


def to_bids(
    row_frequency, inputs, dataset, id, json_edits, fixed_json_edits, **input_values
):
    """Takes generic inptus and stores them within a BIDS dataset"""
    # Update the Bids store with the JSON edits requested by the user
    je_args = shlex.split(json_edits) if json_edits else []
    dataset.store.json_edits = JsonEdit.attr_converter(
        fixed_json_edits + list(zip(je_args[::2], je_args[1::2]))
    )
    for inpt in inputs:
        dataset.add_sink(inpt.name, inpt.datatype, path=inpt.path)
    row = dataset.row(row_frequency, id)
    with dataset.store.connection:
        for inpt_name, inpt_value in input_values.items():
            if inpt_value is attrs.NOTHING:
                logger.warning("No input provided for '%s' input", inpt_name)
                continue
            row[inpt_name] = inpt_value
    return (dataset, True)


def extract_bids(
    dataset: FrameSet,
    row_frequency: Clinical,
    app_name: str,
    output_dir: Path,
    outputs: ty.List[ty.Tuple[str, type]],
    id: str,
    app_completed: bool,
):
    """Selects the items from the dataset corresponding to the input
    sources and retrieves them from the store to a cache on
    the host

    Parameters
    ----------
    dataset : FrameSet
    row_frequency : Clinical
    output_dir : Path
    outputs : ty.List[ty.Tuple[str, type]]
    id : str
        id of the row to be processed
    app_completed : bool
        a dummy field produced by the main BIDS app task on output, to ensure
        'extract_bids' is run after the app has completed.
    """
    # Copy output dir into BIDS dataset
    shutil.copytree(
        output_dir, Path(dataset.id) / "derivatives" / app_name / ("sub-" + id)
    )
    output_paths = []
    row = dataset.row(row_frequency, id)
    for output in outputs:
        if output.path:
            path = output.path
        else:
            path = ""  # whole directory
        path += "@" + app_name
        dataset.add_sink(
            output.name,
            output.datatype,
            path=path,
        )
    with dataset.store.connection:
        for output in outputs:
            output_paths.append(row[output.name])
    return tuple(output_paths) if len(outputs) > 1 else output_paths[0]


BIDS_APP_INPUTS = [
    (
        "dataset_path",
        Directory,  # Needs to be path for internal container paths
        {
            "help_string": "Path to BIDS dataset in the container",
            "position": 1,
            "mandatory": True,
            "argstr": "'{dataset_path}'",
        },
    ),
    (
        "output_path",
        Path,
        {
            "help_string": "Directory where outputs will be written in the container",
            "position": 2,
            "argstr": "'{output_path}'",
        },
    ),
    (
        "analysis_level",
        str,
        {
            "help_string": "The analysis level the app will be run at",
            "position": 3,
            "argstr": "",
        },
    ),
    (
        "participant_label",
        str,
        {
            "help_string": "The IDs to include in the analysis",
            "argstr": "--participant-label ",
            "position": 4,
        },
    ),
    (
        "flags",
        str,
        {
            "help_string": "Additional flags to pass to the app",
            "argstr": "",
            "position": -1,
        },
    ),
    (
        "work_dir",
        Path,
        {
            "help_string": "Directory where the nipype temporary working directories will be stored",
            "argstr": "--work-dir '{work_dir}'",
        },
    ),
    (
        "setup_completed",
        bool,
        {
            "help_string": "Dummy field to ensure that the BIDS dataset construction completes first"
        },
    ),
]

BIDS_APP_OUTPUTS = [
    (
        "completed",
        bool,
        {
            "help_string": "a simple flag to indicate app has completed",
            "callable": lambda: True,
        },
    )
]
