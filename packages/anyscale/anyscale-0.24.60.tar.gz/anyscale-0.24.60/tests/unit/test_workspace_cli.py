import os
import subprocess
from typing import Dict, Generator, Optional, Tuple, Union
import uuid

import click
from click.testing import CliRunner
import pytest

from anyscale._private.sdk import _LAZY_SDK_SINGLETONS
from anyscale.commands.workspace_commands_v2 import (
    create,
    run_command,
    ssh,
    start,
    status,
    terminate,
    wait,
)
from anyscale.workspace.commands import _WORKSPACE_SDK_SINGLETON_KEY
from anyscale.workspace.models import WorkspaceConfig, WorkspaceState


def _get_test_file_path(subpath: str) -> str:
    return os.path.join(os.path.dirname(__file__), "test_files/", subpath)


EMPTY_CONFIG_PATH = _get_test_file_path("workspace_config_files/empty.yaml")
MINIMAL_CONFIG_PATH = _get_test_file_path("workspace_config_files/minimal.yaml")
FULL_CONFIG_PATH = _get_test_file_path("workspace_config_files/full.yaml")
UNRECOGNIZED_OPTION_CONFIG_PATH = _get_test_file_path(
    "workspace_config_files/unrecognized_option.yaml"
)

FULL_CONFIG_SCHEDULE_NAME = "test-name-from-file"


class FakeWorkspaceSDK:
    def __init__(self):
        self._created_workspaces: Dict[str, WorkspaceConfig] = {}
        self._workspace_status = {}

    def _resolve_to_workspace_model(
        self,
        *,
        id: Optional[str] = None,  # noqa: A002
        name: Optional[str] = None,
        cloud: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Tuple[str, WorkspaceConfig]:
        workspace_config = None
        workspace_id = None
        if id is not None:
            workspace_config = self._created_workspaces.get(id)
            workspace_id = id
        elif name is not None:
            for key, config in self._created_workspaces.items():
                if (
                    config.name == name
                    and (cloud is None or config.cloud == cloud)
                    and (project is None or config.project == project)
                ):
                    workspace_config = config
                    workspace_id = key
                    break
        assert workspace_id is not None, "Workspace was not found."
        if workspace_config is None:
            raise RuntimeError("Workspace was not found.")
        return workspace_id, workspace_config

    def create(self, config: WorkspaceConfig) -> str:
        assert isinstance(config, WorkspaceConfig)
        id = str(uuid.uuid4())  # noqa: A001
        self._created_workspaces[id] = config
        self._workspace_status[id] = WorkspaceState.TERMINATED
        return id

    def start(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,  # noqa: A002
        cloud: Optional[str] = None,
        project: Optional[str] = None,
    ) -> str:
        workspace_id, _ = self._resolve_to_workspace_model(
            name=name, id=id, cloud=cloud, project=project
        )
        self._workspace_status[workspace_id] = WorkspaceState.RUNNING
        return workspace_id

    def terminate(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,  # noqa: A002
        cloud: Optional[str] = None,
        project: Optional[str] = None,
    ) -> str:
        workspace_id, _ = self._resolve_to_workspace_model(
            name=name, id=id, cloud=cloud, project=project
        )
        self._workspace_status[workspace_id] = WorkspaceState.TERMINATED
        return workspace_id

    def status(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,  # noqa: A002
        cloud: Optional[str] = None,
        project: Optional[str] = None,
    ) -> str:
        workspace_id, _ = self._resolve_to_workspace_model(
            name=name, id=id, cloud=cloud, project=project
        )
        return self._workspace_status[workspace_id]

    def wait(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,  # noqa: A002
        cloud: Optional[str] = None,
        project: Optional[str] = None,
        timeout_s: float = 5,
        state: Union[str, WorkspaceState] = WorkspaceState.RUNNING,
    ):
        workspace_id, _ = self._resolve_to_workspace_model(
            name=name, id=id, cloud=cloud, project=project
        )
        target_state = WorkspaceState.validate(state)
        current_status = self._workspace_status[workspace_id]

        if current_status != target_state:
            raise TimeoutError(f"Workspace did not reach state {target_state} in time.")

    def generate_ssh_config_file(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,  # noqa: A002
        cloud: Optional[str] = None,
        project: Optional[str] = None,
        ssh_config_path: Optional[str] = None,
    ) -> Tuple[str, str]:
        _, model = self._resolve_to_workspace_model(
            name=name, id=id, cloud=cloud, project=project
        )
        assert model.name is not None
        return model.name, f"{ssh_config_path}/ssh_config"

    def run_command(
        self,
        *,
        id: Optional[str] = None,  # noqa: A002
        name: Optional[str] = None,
        cloud: Optional[str] = None,
        project: Optional[str] = None,
        command: str,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        workspace_id, _ = self._resolve_to_workspace_model(
            name=name, id=id, cloud=cloud, project=project
        )
        print(f"Running command {command} for {workspace_id}")
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=f"Output for {workspace_id} and {command}".encode("utf-8"),
            stderr=b"",
        )

    def get_default_dir_name(
        self,
        *,
        id: Optional[str] = None,  # noqa: A002
        name: Optional[str] = None,
        cloud: Optional[str] = None,
        project: Optional[str] = None,
    ) -> str:
        workspace_id, _ = self._resolve_to_workspace_model(
            name=name, id=id, cloud=cloud, project=project
        )
        return "/home/ray/default"


@pytest.fixture()
def fake_workspace_sdk() -> Generator[FakeWorkspaceSDK, None, None]:
    fake_workspace_sdk = FakeWorkspaceSDK()
    _LAZY_SDK_SINGLETONS[_WORKSPACE_SDK_SINGLETON_KEY] = fake_workspace_sdk
    try:
        yield fake_workspace_sdk
    finally:
        del _LAZY_SDK_SINGLETONS[_WORKSPACE_SDK_SINGLETON_KEY]


def _assert_error_message(result: click.testing.Result, *, message: str):
    assert result.exit_code != 0
    assert message in result.stdout


class TestCreate:
    def test_missing_arg(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create)
        _assert_error_message(result, message="Workspace name must be configured")

    def test_config_file_not_found(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", "missing_config.yaml"])
        _assert_error_message(
            result, message="Error: Config file 'missing_config.yaml' not found.",
        )

    @pytest.mark.parametrize(
        "config_file_arg", [MINIMAL_CONFIG_PATH, FULL_CONFIG_PATH],
    )
    def test_basic(self, fake_workspace_sdk, config_file_arg):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", config_file_arg])
        assert result.exit_code == 0, result.stdout
        assert len(fake_workspace_sdk._created_workspaces) == 1

    def test_override_name(self, fake_workspace_sdk):
        runner = CliRunner()
        name = "test-different-name"
        result = runner.invoke(create, ["--name", name, "-f", FULL_CONFIG_PATH])
        assert result.exit_code == 0
        assert result.exit_code == 0, result.stdout
        assert len(fake_workspace_sdk._created_workspaces) == 1

        workspace_config = list(fake_workspace_sdk._created_workspaces.values())[0]
        assert workspace_config.name == name


class TestStart:
    def test_missing_arg(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        result = runner.invoke(start)
        _assert_error_message(
            result, message="Error: One of '--name' and '--id' must be provided.\n"
        )

    def test_start_with_id(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        # Start the workspace
        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]

        result = runner.invoke(start, ["--id", workspace_id])
        assert result.exit_code == 0, result.stdout
        assert (
            fake_workspace_sdk._workspace_status[workspace_id] == WorkspaceState.RUNNING
        )

    def test_start_with_name(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        # Start the workspace
        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]
        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name
        result = runner.invoke(start, ["--name", workspace_name])
        assert result.exit_code == 0, result.stdout
        assert (
            fake_workspace_sdk._workspace_status[workspace_id] == WorkspaceState.RUNNING
        )

    def test_invalid_args(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]
        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name

        result = runner.invoke(start, ["--name", workspace_name, "--id", workspace_id])
        _assert_error_message(
            result, message="Only one of '--name' and '--id' can be provided."
        )


class TestTerminate:
    def test_missing_arg(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        result = runner.invoke(terminate)
        _assert_error_message(
            result, message="Error: One of '--name' and '--id' must be provided.\n"
        )

    def test_terminate_with_id(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        # Terminate the workspace
        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]

        result = runner.invoke(terminate, ["--id", workspace_id])
        assert result.exit_code == 0, result.stdout
        assert (
            fake_workspace_sdk._workspace_status[workspace_id]
            == WorkspaceState.TERMINATED
        )

    def test_terminate_with_name(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        # Terminate the workspace
        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]
        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name
        result = runner.invoke(terminate, ["--name", workspace_name])
        assert result.exit_code == 0, result.stdout
        assert (
            fake_workspace_sdk._workspace_status[workspace_id]
            == WorkspaceState.TERMINATED
        )

    def test_invalid_args(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]
        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name

        result = runner.invoke(
            terminate, ["--name", workspace_name, "--id", workspace_id]
        )
        _assert_error_message(
            result, message="Only one of '--name' and '--id' can be provided."
        )


class TestStatus:
    def test_missing_arg(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        result = runner.invoke(status)
        _assert_error_message(
            result, message="Error: One of '--name' and '--id' must be provided.\n"
        )

    def test_status_with_id(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]

        result = runner.invoke(status, ["--id", workspace_id])
        assert result.exit_code == 0, result.stdout
        assert (
            fake_workspace_sdk._workspace_status[workspace_id]
            == WorkspaceState.TERMINATED
        )

    def test_status_with_name(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]
        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name
        result = runner.invoke(status, ["--name", workspace_name])
        assert result.exit_code == 0, result.stdout
        assert (
            fake_workspace_sdk._workspace_status[workspace_id]
            == WorkspaceState.TERMINATED
        )

    def test_invalid_args(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]
        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name

        result = runner.invoke(status, ["--name", workspace_name, "--id", workspace_id])
        _assert_error_message(
            result, message="Only one of '--name' and '--id' can be provided."
        )


class TestWait:
    def test_missing_arg(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        result = runner.invoke(wait)
        _assert_error_message(
            result, message="Error: One of '--name' and '--id' must be provided.\n"
        )

    def test_wait_with_id(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]

        result = runner.invoke(
            wait, ["--id", workspace_id, "--state", WorkspaceState.TERMINATED]
        )
        assert result.exit_code == 0, result.stdout
        assert (
            fake_workspace_sdk._workspace_status[workspace_id]
            == WorkspaceState.TERMINATED
        )

    def test_wait_with_name(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]
        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name
        result = runner.invoke(
            wait, ["--name", workspace_name, "--state", WorkspaceState.TERMINATED]
        )
        assert result.exit_code == 0, result.stdout
        assert (
            fake_workspace_sdk._workspace_status[workspace_id]
            == WorkspaceState.TERMINATED
        )

    def test_invalid_args(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]
        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name

        result = runner.invoke(wait, ["--name", workspace_name, "--id", workspace_id])
        _assert_error_message(
            result, message="Only one of '--name' and '--id' can be provided."
        )


class TestSSH:
    def test_missing_arg(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        result = runner.invoke(ssh)
        _assert_error_message(
            result, message="Error: One of '--name' and '--id' must be provided.\n"
        )

    def test_ssh_with_id(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]

        # start it
        result = runner.invoke(start, ["--id", workspace_id])
        assert result.exit_code == 0, result.stdout

        result = runner.invoke(ssh, ["--id", workspace_id, "--command", "ls"])
        assert result.exit_code == 0, result.stdout

    def test_ssh_with_name(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]
        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name

        # start it
        result = runner.invoke(start, ["--id", workspace_id])
        assert result.exit_code == 0, result.stdout

        result = runner.invoke(ssh, ["--name", workspace_name])
        assert result.exit_code == 0, result.stdout

    def test_invalid_args(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]
        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name

        result = runner.invoke(ssh, ["--name", workspace_name, "--id", workspace_id])
        _assert_error_message(
            result, message="Only one of '--name' and '--id' can be provided."
        )

    def test_with_ssh_args(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]

        # start it
        result = runner.invoke(start, ["--id", workspace_id])
        assert result.exit_code == 0, result.stdout

        result = runner.invoke(
            ssh, ["--id", workspace_id, "--", "-l", "9000:localhost:9000"]
        )
        assert result.exit_code == 0, result.stdout


class TestRunCommand:
    def test_missing_arg(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]

        # start it
        result = runner.invoke(start, ["--id", workspace_id])
        assert result.exit_code == 0, result.stdout

        result = runner.invoke(ssh)
        _assert_error_message(
            result, message="Error: One of '--name' and '--id' must be provided.\n"
        )

    def test_run_command_with_id(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]

        # start it
        result = runner.invoke(start, ["--id", workspace_id])
        assert result.exit_code == 0, result.stdout

        result = runner.invoke(run_command, ["--id", workspace_id, "ls"])
        assert result.exit_code == 0, result.stdout
        assert "ls" in result.stdout

    def test_run_command_with_name(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name
        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]

        # start it
        result = runner.invoke(start, ["--id", workspace_id])
        assert result.exit_code == 0, result.stdout

        result = runner.invoke(run_command, ["--name", workspace_name, "ls"])
        assert result.exit_code == 0, result.stdout
        assert "ls" in result.stdout

    def test_invalid_args(self, fake_workspace_sdk):
        runner = CliRunner()
        result = runner.invoke(create, ["-f", MINIMAL_CONFIG_PATH])
        assert result.exit_code == 0, result.stdout

        workspace_id = list(fake_workspace_sdk._created_workspaces.keys())[0]
        workspace_name = list(fake_workspace_sdk._created_workspaces.values())[0].name

        result = runner.invoke(
            run_command, ["--name", workspace_name, "--id", workspace_id, "ls"]
        )
        _assert_error_message(
            result, message="Only one of '--name' and '--id' can be provided."
        )
