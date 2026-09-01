from pathlib import Path
from shutil import copyfile

import pytest

import sport_rent_hsqldb_sync.snapshot as snapshot_module
from sport_rent_hsqldb_sync.snapshot import (
    SnapshotChangedDuringCopyError,
    _copy_snapshot_files,
    get_snapshot_files_state,
    load_consistent_snapshot,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_loads_consistent_snapshot(tmp_path: Path) -> None:
    database_path = tmp_path / "source" / "rental"
    database_path.parent.mkdir()
    copyfile(
        FIXTURES / "reservation_baseline.script",
        database_path.with_suffix(".script"),
    )
    copyfile(
        FIXTURES / "reservation_insert.log",
        database_path.with_suffix(".log"),
    )

    database_state = load_consistent_snapshot(database_path)

    assert set(database_state.reservation_positions) == {1001, 1002}


def test_rejects_snapshot_when_source_changes_during_copy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "source" / "rental"
    database_path.parent.mkdir()
    copyfile(
        FIXTURES / "reservation_baseline.script",
        database_path.with_suffix(".script"),
    )
    original_copy = snapshot_module._copy_snapshot_files

    def copy_then_change_source(
        source_database_path: Path,
        destination_directory: Path,
    ) -> Path:
        copied_database_path = original_copy(
            source_database_path,
            destination_directory,
        )
        source_database_path.with_suffix(".log").write_bytes(b"COMMIT\n")
        return copied_database_path

    monkeypatch.setattr(
        snapshot_module,
        "_copy_snapshot_files",
        copy_then_change_source,
    )

    with pytest.raises(SnapshotChangedDuringCopyError):
        load_consistent_snapshot(database_path)


def test_copies_snapshot_files(tmp_path: Path) -> None:
    database_path = tmp_path / "source" / "rental"
    database_path.parent.mkdir()
    expected_contents = {
        ".script": b"script contents",
        ".log": b"log contents",
        ".properties": b"modified=yes",
    }
    for suffix, contents in expected_contents.items():
        database_path.with_suffix(suffix).write_bytes(contents)

    copied_database_path = _copy_snapshot_files(
        database_path,
        tmp_path / "destination",
    )

    assert copied_database_path == tmp_path / "destination" / "rental"
    for suffix, contents in expected_contents.items():
        assert copied_database_path.with_suffix(suffix).read_bytes() == contents


def test_copy_snapshot_files_allows_missing_log(tmp_path: Path) -> None:
    database_path = tmp_path / "source" / "rental"
    database_path.parent.mkdir()
    database_path.with_suffix(".script").write_bytes(b"script contents")

    copied_database_path = _copy_snapshot_files(
        database_path,
        tmp_path / "destination",
    )

    assert copied_database_path.with_suffix(".script").exists()
    assert not copied_database_path.with_suffix(".log").exists()


def test_snapshot_files_state_reports_missing_files(tmp_path: Path) -> None:
    state = get_snapshot_files_state(tmp_path / "rental")

    assert state.script.exists is False
    assert state.log.exists is False
    assert state.properties.exists is False


def test_snapshot_files_state_detects_log_appearance(tmp_path: Path) -> None:
    database_path = tmp_path / "rental"
    before = get_snapshot_files_state(database_path)

    log_contents = b"COMMIT\n"
    database_path.with_suffix(".log").write_bytes(log_contents)
    after = get_snapshot_files_state(database_path)

    assert before != after
    assert before.log.exists is False
    assert after.log.exists is True
    assert after.log.size == len(log_contents)


def test_snapshot_files_state_detects_script_change(tmp_path: Path) -> None:
    database_path = tmp_path / "rental"
    script_path = database_path.with_suffix(".script")
    script_path.write_text("old\n", encoding="utf-8")
    before = get_snapshot_files_state(database_path)

    script_path.write_text("new script contents\n", encoding="utf-8")
    after = get_snapshot_files_state(database_path)

    assert before != after
    assert before.script.size != after.script.size
