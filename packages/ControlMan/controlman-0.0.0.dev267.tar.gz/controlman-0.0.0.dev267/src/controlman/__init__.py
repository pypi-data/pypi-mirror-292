"""ControlMan

The control center manager for RepoDynamics template repositories.
"""

from pathlib import Path as _Path

import pyserials as _ps
from gittidy import Git as _Git


from controlman import const, exception
from controlman import data_validator as _data_validator
from controlman import _file_util
from controlman.center_manager import CenterManager


# TODO: Remove after adding versioningit
__release__ = "1.0"


def manager(
    repo: _Git | _Path | str,
    data_before: _ps.NestedDict | None = None,
    data_main: _ps.NestedDict | None = None,
    github_token: str | None = None,
    future_versions: dict[str, str] | None = None,
    control_center_path: str | None = None,
):
    if isinstance(repo, (str, _Path)):
        repo = _Git(path=repo)
    if not data_before:
        if control_center_path:
            cc_path = repo.repo_path / control_center_path
            if not cc_path.is_dir():
                raise ValueError(f"Invalid control center path '{cc_path}'")
            data_before = _ps.NestedDict({})
        else:
            data_before = from_json_file(repo_path=repo.repo_path)
            cc_path = repo.repo_path / data_before["control.path"]
    else:
        cc_path = repo.repo_path / data_before["control.path"]
    data_main = data_main or _ps.NestedDict({})
    return CenterManager(
        git_manager=repo,
        cc_path=cc_path,
        data_before=data_before,
        data_main=data_main,
        github_token=github_token,
        future_versions=future_versions,
    )


def from_json_file(
    repo_path: str | _Path,
    filepath: str = const.FILEPATH_METADATA,
    validate: bool = True,
) -> _ps.NestedDict:
    """Load control center data from the full JSON file.

    Parameters
    ----------
    repo_path : str | _Path
        Path to the repository root.
    filepath : str, default: controlman.const.FILEPATH_METADATA
        Relative path to the JSON file in the repository.
    validate : bool, default: True
        Validate the data against the schema.

    Raises
    ------
    controlman.exception.ControlManFileReadError
        If the file cannot be read.
    """
    data_dict = _file_util.read_data_from_file(
        path=_Path(repo_path) / filepath,
        base_path=repo_path,
        extension="json",
        raise_errors=True,
    )
    if validate:
        _data_validator.validate(data=data_dict)
    return _ps.NestedDict(data_dict)


def from_json_file_at_commit(
    git_manager: _Git,
    commit_hash: str,
    filepath: str = const.FILEPATH_METADATA,
    validate: bool = True,
) -> _ps.NestedDict:
    data_str = git_manager.file_at_hash(
        commit_hash=commit_hash,
        path=filepath,
    )
    return from_json_string(data=data_str, validate=validate)


def from_json_string(
    data: str,
    validate: bool = True,
) -> _ps.NestedDict:
    """Load control center data from the full JSON string.

    Parameters
    ----------
    data : str
        JSON data string.
    validate : bool, default: True
        Validate the data against the schema.

    Raises
    ------
    controlman.exception.ControlManFileReadError
        If the data cannot be read.
    """
    data_dict = _file_util.read_datafile_from_string(
        data=data,
        extension="json",
        raise_errors=True,
    )
    if validate:
        _data_validator.validate(data=data_dict)
    return _ps.NestedDict(data_dict)
