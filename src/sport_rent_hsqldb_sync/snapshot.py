from dataclasses import dataclass
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory

from sport_rent_hsqldb_sync.models import HsqldbDatabaseState
from sport_rent_hsqldb_sync.parsing.database import (
    apply_committed_log_changes,
    parse_database_script,
)

SNAPSHOT_FILE_SUFFIXES = (
    ".script",
    ".log",
    ".properties",
)


@dataclass(frozen=True)
class FileState:
    exists: bool
    size: int | None
    modified_at_ns: int | None


@dataclass(frozen=True)
class SnapshotFilesState:
    script: FileState
    log: FileState
    properties: FileState


class SnapshotChangedDuringCopyError(RuntimeError):
    pass


def load_consistent_snapshot(database_path: Path) -> HsqldbDatabaseState:
    before = get_snapshot_files_state(database_path)

    with TemporaryDirectory(prefix="sport-rent-hsqldb-") as temporary_directory:
        copied_database_path = _copy_snapshot_files(
            database_path,
            Path(temporary_directory),
        )

        after = get_snapshot_files_state(database_path)

        if before != after:
            raise SnapshotChangedDuringCopyError(
                "HSQLDB files changed while creating the snapshot"
            )

        return load_snapshot(copied_database_path)


def _copy_snapshot_files(
    database_path: Path,
    destination_directory: Path,
) -> Path:
    destination_directory.mkdir(parents=True, exist_ok=True)
    copied_database_path = destination_directory / database_path.name

    for suffix in SNAPSHOT_FILE_SUFFIXES:
        source_path = database_path.with_suffix(suffix)

        if not source_path.exists():
            continue

        destination_path = copied_database_path.with_suffix(suffix)
        copy2(source_path, destination_path)

    return copied_database_path


def get_snapshot_files_state(database_path: Path) -> SnapshotFilesState:
    return SnapshotFilesState(
        script=get_file_state(database_path.with_suffix(".script")),
        log=get_file_state(database_path.with_suffix(".log")),
        properties=get_file_state(database_path.with_suffix(".properties")),
    )


def load_snapshot(database_path: Path) -> HsqldbDatabaseState:
    script_path = database_path.with_suffix(".script")
    log_path = database_path.with_suffix(".log")

    with script_path.open(encoding="utf-8") as script:
        database_state = parse_database_script(script)

    if not log_path.exists():
        return database_state

    with log_path.open(encoding="utf-8") as log:
        return apply_committed_log_changes(database_state, log)


def get_file_state(path: Path) -> FileState:
    try:
        stat = path.stat()
    except FileNotFoundError:
        return FileState(
            exists=False,
            size=None,
            modified_at_ns=None,
        )

    return FileState(
        exists=True,
        size=stat.st_size,
        modified_at_ns=stat.st_mtime_ns,
    )
