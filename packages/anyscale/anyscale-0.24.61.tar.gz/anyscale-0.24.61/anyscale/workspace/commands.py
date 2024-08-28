from typing import Any, Dict, Optional, Tuple

from anyscale._private.sdk import sdk_command
from anyscale.workspace._private.workspace_sdk import PrivateWorkspaceSDK
from anyscale.workspace.models import WorkspaceConfig, WorkspaceState


_WORKSPACE_SDK_SINGLETON_KEY = "workspace_sdk"

_CREATE_EXAMPLE = """
import anyscale
from anyscale.workspace.models import WorkspaceConfig

anyscale.workspace.create(
    WorkspaceConfig(
        name="my-workspace",
        idle_termination_minutes=120,
    ),
)
"""

_CREATE_ARG_DOCSTRINGS = {"config": "The config for defining the workspace."}
_WAIT_TIMEOUT_SECONDS = 1800.0


@sdk_command(
    _WORKSPACE_SDK_SINGLETON_KEY,
    PrivateWorkspaceSDK,
    doc_py_example=_CREATE_EXAMPLE,
    arg_docstrings=_CREATE_ARG_DOCSTRINGS,
)
def create(config: WorkspaceConfig, *, _sdk: PrivateWorkspaceSDK) -> str:
    """Create a workspace.

    Returns the id of the created workspace.
    """
    return _sdk.create(config)


_START_EXAMPLE = """
import anyscale

anyscale.workspace.start(
    name="my-workspace",
)
"""

_START_ARG_DOCSTRINGS = {
    "name": "Name of the workspace.",
    "id": "Unique ID of the workspace",
    "cloud": "The Anyscale Cloud to run this workload on. If not provided, the organization default will be used (or, if running in a workspace, the cloud of the workspace).",
    "project": "Named project to use for the workspace. If not provided, the default project for the cloud will be used (or, if running in a workspace, the project of the workspace).",
}


@sdk_command(
    _WORKSPACE_SDK_SINGLETON_KEY,
    PrivateWorkspaceSDK,
    doc_py_example=_START_EXAMPLE,
    arg_docstrings=_START_ARG_DOCSTRINGS,
)
def start(
    *,
    name: Optional[str] = None,
    id: Optional[str] = None,  # noqa: A002
    cloud: Optional[str] = None,
    project: Optional[str] = None,
    _sdk: PrivateWorkspaceSDK,
) -> str:
    """Start a workspace.

    Returns the id of the started workspace.
    """
    return _sdk.start(name=name, id=id, cloud=cloud, project=project)


_TERMINATE_EXAMPLE = """
import anyscale

anyscale.workspace.terminate(
    name="my-workspace",
)
"""

_TERMINATE_ARG_DOCSTRINGS = {
    "name": "Name of the workspace.",
    "id": "Unique ID of the workspace",
    "cloud": "The Anyscale Cloud to run this workload on. If not provided, the organization default will be used (or, if running in a workspace, the cloud of the workspace).",
    "project": "Named project to use for the workspace. If not provided, the default project for the cloud will be used (or, if running in a workspace, the project of the workspace).",
}


@sdk_command(
    _WORKSPACE_SDK_SINGLETON_KEY,
    PrivateWorkspaceSDK,
    doc_py_example=_TERMINATE_EXAMPLE,
    arg_docstrings=_TERMINATE_ARG_DOCSTRINGS,
)
def terminate(
    *,
    name: Optional[str] = None,
    id: Optional[str] = None,  # noqa: A002
    cloud: Optional[str] = None,
    project: Optional[str] = None,
    _sdk: PrivateWorkspaceSDK,
) -> str:
    """Terminate a workspace.

    Returns the id of the terminated workspace.
    """
    return _sdk.terminate(name=name, id=id, cloud=cloud, project=project)


_STATUS_EXAMPLE = """
import anyscale

status = anyscale.workspace.status(
    name="my-workspace",
)
"""

_STATUS_ARG_DOCSTRINGS = {
    "name": "Name of the workspace.",
    "id": "Unique ID of the workspace",
    "cloud": "The Anyscale Cloud to run this workload on. If not provided, the organization default will be used (or, if running in a workspace, the cloud of the workspace).",
    "project": "Named project to use for the workspace. If not provided, the default project for the cloud will be used (or, if running in a workspace, the project of the workspace).",
}


@sdk_command(
    _WORKSPACE_SDK_SINGLETON_KEY,
    PrivateWorkspaceSDK,
    doc_py_example=_STATUS_EXAMPLE,
    arg_docstrings=_STATUS_ARG_DOCSTRINGS,
)
def status(
    *,
    name: Optional[str] = None,
    id: Optional[str] = None,  # noqa: A002
    cloud: Optional[str] = None,
    project: Optional[str] = None,
    _sdk: PrivateWorkspaceSDK,
) -> str:
    """Get the status of a workspace.

    Returns the status of the workspace.
    """
    return _sdk.status(name=name, id=id, cloud=cloud, project=project)


_WAIT_EXAMPLE = """
import anyscale

anyscale.workspace.wait(
    name="my-workspace",
)
"""

_WAIT_ARG_DOCSTRINGS = {
    "name": "Name of the workspace.",
    "id": "Unique ID of the workspace",
    "cloud": "The Anyscale Cloud to run this workload on. If not provided, the organization default will be used (or, if running in a workspace, the cloud of the workspace).",
    "project": "Named project to use for the workspace. If not provided, the default project for the cloud will be used (or, if running in a workspace, the project of the workspace).",
    "timeout_s": "The maximum time to wait for the workspace to reach a terminal state.",
    "state": "The desired terminal state to wait for, defaults to RUNNING.",
}


@sdk_command(
    _WORKSPACE_SDK_SINGLETON_KEY,
    PrivateWorkspaceSDK,
    doc_py_example=_WAIT_EXAMPLE,
    arg_docstrings=_WAIT_ARG_DOCSTRINGS,
)
def wait(
    *,
    name: Optional[str] = None,
    id: Optional[str] = None,  # noqa: A002
    cloud: Optional[str] = None,
    project: Optional[str] = None,
    timeout_s: float = _WAIT_TIMEOUT_SECONDS,
    state: str = WorkspaceState.RUNNING,
    _sdk: PrivateWorkspaceSDK,
) -> str:
    """Wait for a workspace to reach a terminal state.

    Returns the status of the workspace.
    """
    return _sdk.wait(
        name=name,
        id=id,
        cloud=cloud,
        project=project,
        timeout_s=timeout_s,
        state=state,
    )


_GENERATE_SSH_CONFIG_FILE_EXAMPLE = """
import anyscale
import subprocess

host_name, config_file = anyscale.workspace.generate_ssh_config_file(
    name="my-workspace",
)

# run an ssh command using the generated config file
subprocess.run(["ssh", "-F", config_path, host_name, "ray --version"])
"""

_GENERATE_SSH_CONFIG_FILE_ARG_DOCSTRINGS = {
    "name": "Name of the workspace.",
    "id": "Unique ID of the workspace",
    "cloud": "The Anyscale Cloud to run this workload on. If not provided, the organization default will be used (or, if running in a workspace, the cloud of the workspace).",
    "project": "Named project to use for the workspace. If not provided, the default project for the cloud will be used (or, if running in a workspace, the project of the workspace).",
    "ssh_config_path": "The directory to write the generated config file to.",
}


@sdk_command(
    _WORKSPACE_SDK_SINGLETON_KEY,
    PrivateWorkspaceSDK,
    doc_py_example=_GENERATE_SSH_CONFIG_FILE_EXAMPLE,
    arg_docstrings=_GENERATE_SSH_CONFIG_FILE_ARG_DOCSTRINGS,
)
def generate_ssh_config_file(
    *,
    name: Optional[str] = None,
    id: Optional[str] = None,  # noqa: A002
    cloud: Optional[str] = None,
    project: Optional[str] = None,
    ssh_config_path: Optional[str] = None,
    _sdk: PrivateWorkspaceSDK,
) -> Tuple[str, str]:
    """Generate an SSH config file for a workspace.

    Returns the hostname and path to the generated config file.
    """
    return _sdk.generate_ssh_config_file(
        name=name, id=id, cloud=cloud, project=project, ssh_config_path=ssh_config_path,
    )


_RUN_COMMAND_EXAMPLE = """
import anyscale

process = anyscale.workspace.run_command(
    name="my-workspace",
    command="ray_version",
    capture_output=True,
    text=True,
)
print(process.stdout)
"""

_RUN_COMMAND_ARG_DOCSTRINGS = {
    "name": "Name of the workspace.",
    "id": "Unique ID of the workspace",
    "cloud": "The Anyscale Cloud to run this workload on. If not provided, the organization default will be used (or, if running in a workspace, the cloud of the workspace).",
    "project": "Named project to use for the workspace. If not provided, the default project for the cloud will be used (or, if running in a workspace, the project of the workspace).",
    "command": "The command to run.",
    "kwargs": "Additional arguments to pass to subprocess.run.",
}


@sdk_command(
    _WORKSPACE_SDK_SINGLETON_KEY,
    PrivateWorkspaceSDK,
    doc_py_example=_RUN_COMMAND_EXAMPLE,
    arg_docstrings=_RUN_COMMAND_ARG_DOCSTRINGS,
)
def run_command(
    *,
    name: Optional[str] = None,
    id: Optional[str] = None,  # noqa: A002
    cloud: Optional[str] = None,
    project: Optional[str] = None,
    command: str,
    _sdk: PrivateWorkspaceSDK,
    **kwargs: Dict[str, Any],
):
    """Run a command in a workspace.

    Returns a subprocess.CompletedProcess object.
    """
    return _sdk.run_command(
        name=name, id=id, cloud=cloud, project=project, command=command, **kwargs,
    )
