from pathlib import Path
from shutil import copyfile

import pytest

from sport_rent_hsqldb_sync.parsing.database import (
    apply_committed_log_changes,
    parse_database_script,
)
from sport_rent_hsqldb_sync.parsing.reservation_position import (
    parse_reservation_position_insert,
)
from sport_rent_hsqldb_sync.snapshot import load_snapshot

FIXTURES = Path(__file__).parent / "fixtures"


def test_loads_snapshot_from_script_and_log(tmp_path: Path) -> None:
    database_path = tmp_path / "rental"
    copyfile(
        FIXTURES / "reservation_baseline.script",
        database_path.with_suffix(".script"),
    )
    copyfile(
        FIXTURES / "reservation_insert.log",
        database_path.with_suffix(".log"),
    )

    database_state = load_snapshot(database_path)

    assert set(database_state.reservation_positions) == {1001, 1002}
    assert set(database_state.abstract_positions) == {1001}


def test_loads_snapshot_without_log(tmp_path: Path) -> None:
    database_path = tmp_path / "rental"
    copyfile(
        FIXTURES / "reservation_baseline.script",
        database_path.with_suffix(".script"),
    )

    database_state = load_snapshot(database_path)

    assert set(database_state.reservation_positions) == {1001}
    assert set(database_state.abstract_positions) == {1001}


def test_load_snapshot_requires_script(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_snapshot(tmp_path / "missing")


def test_parses_reservation_from_script() -> None:
    with (FIXTURES / "reservation_baseline.script").open(encoding="utf-8") as script:
        database_state = parse_database_script(script)

    assert set(database_state.reservation_positions) == {1001}

    reservation_position = database_state.reservation_positions[1001]
    assert reservation_position.source_position_id == 1001
    assert reservation_position.begin_at is not None
    assert reservation_position.begin_at.isoformat() == "2026-09-01T10:00:00"
    assert reservation_position.end_at is not None
    assert reservation_position.end_at.isoformat() == "2026-09-05T18:00:00"
    assert reservation_position.source_rent_object_id == 3001
    assert reservation_position.source_status == 1

    abstract_position = database_state.abstract_positions[1001]
    assert abstract_position.source_position_id == 1001
    assert abstract_position.source_name == "Rower testowy Trek 3001"


def test_parses_null_reservation_status() -> None:
    statement = (
        "INSERT INTO RESERVATIONPOSITION VALUES(1001,NULL,NULL,NULL,NULL,NULL,"
        "NULL,0,NULL,0.22,NULL,NULL,NULL,NULL,NULL,NULL,NULL)"
    )

    reservation_position = parse_reservation_position_insert(statement)

    assert reservation_position.source_status is None


def test_applies_log_insert_after_commit() -> None:
    with (FIXTURES / "reservation_baseline.script").open(encoding="utf-8") as script:
        database_state = parse_database_script(script)

    with (FIXTURES / "reservation_insert.log").open(encoding="utf-8") as log:
        updated_state = apply_committed_log_changes(database_state, log)

    assert set(updated_state.reservation_positions) == {1001, 1002}
    assert updated_state.reservation_positions[1002].source_rent_object_id == 3002
    assert updated_state.reservation_positions[1002].source_status == 1


def test_applies_reservation_and_abstract_position_from_one_commit() -> None:
    with (FIXTURES / "reservation_baseline.script").open(encoding="utf-8") as script:
        database_state = parse_database_script(script)

    with (FIXTURES / "reservation_with_abstract_position_insert.log").open(
        encoding="utf-8"
    ) as log:
        updated_state = apply_committed_log_changes(database_state, log)

    assert set(updated_state.reservation_positions) == {1001, 1002}
    assert set(updated_state.abstract_positions) == {1001, 1002}
    assert (
        updated_state.abstract_positions[1002].source_name
        == "Uprząż wspinaczkowa 10563"
    )


def test_ignores_log_insert_without_commit() -> None:
    with (FIXTURES / "reservation_baseline.script").open(encoding="utf-8") as script:
        database_state = parse_database_script(script)

    with (FIXTURES / "reservation_insert.log").open(encoding="utf-8") as log:
        log_without_commit = (line for line in log if line.strip() != "COMMIT")
        updated_state = apply_committed_log_changes(
            database_state,
            log_without_commit,
        )

    assert updated_state == database_state


def test_applies_log_delete_after_commit() -> None:
    with (FIXTURES / "reservation_baseline.script").open(encoding="utf-8") as script:
        database_state = parse_database_script(script)

    with (FIXTURES / "reservation_insert.log").open(encoding="utf-8") as log:
        database_state = apply_committed_log_changes(database_state, log)

    assert set(database_state.reservation_positions) == {1001, 1002}

    with (FIXTURES / "reservation_delete.log").open(encoding="utf-8") as log:
        database_state = apply_committed_log_changes(database_state, log)

    assert set(database_state.reservation_positions) == {1001}


def test_ignores_log_delete_without_commit() -> None:
    with (FIXTURES / "reservation_baseline.script").open(encoding="utf-8") as script:
        database_state = parse_database_script(script)

    with (FIXTURES / "reservation_insert.log").open(encoding="utf-8") as log:
        database_state = apply_committed_log_changes(database_state, log)

    assert set(database_state.reservation_positions) == {1001, 1002}

    with (FIXTURES / "reservation_delete.log").open(encoding="utf-8") as log:
        log_without_commit = (line for line in log if line.strip() != "COMMIT")
        updated_state = apply_committed_log_changes(
            database_state,
            log_without_commit,
        )

    assert set(updated_state.reservation_positions) == {1001, 1002}


def test_applies_delete_and_insert_as_committed_update() -> None:
    with (FIXTURES / "reservation_baseline.script").open(encoding="utf-8") as script:
        database_state = parse_database_script(script)

    with (FIXTURES / "reservation_update.log").open(encoding="utf-8") as log:
        updated_state = apply_committed_log_changes(database_state, log)

    assert set(updated_state.reservation_positions) == {1001}

    original = database_state.reservation_positions[1001]
    updated = updated_state.reservation_positions[1001]

    assert original.end_at is not None
    assert original.end_at.isoformat() == "2026-09-05T18:00:00"
    assert updated.end_at is not None
    assert updated.end_at.isoformat() == "2026-09-06T18:00:00"


def test_applies_multiple_committed_transactions_from_one_log() -> None:
    with (FIXTURES / "reservation_baseline.script").open(encoding="utf-8") as script:
        database_state = parse_database_script(script)

    with (FIXTURES / "reservation_insert_then_delete.log").open(
        encoding="utf-8"
    ) as log:
        updated_state = apply_committed_log_changes(database_state, log)

    assert set(updated_state.reservation_positions) == {1001}


def test_ignores_truncated_transaction_after_complete_commit() -> None:
    with (FIXTURES / "reservation_baseline.script").open(encoding="utf-8") as script:
        database_state = parse_database_script(script)

    with (FIXTURES / "reservation_committed_then_truncated.log").open(
        encoding="utf-8"
    ) as log:
        updated_state = apply_committed_log_changes(database_state, log)

    assert set(updated_state.reservation_positions) == {1001, 1002}


def test_preserves_change_order_inside_transaction() -> None:
    with (FIXTURES / "reservation_baseline.script").open(encoding="utf-8") as script:
        database_state = parse_database_script(script)

    with (FIXTURES / "reservation_insert_then_delete_same_transaction.log").open(
        encoding="utf-8"
    ) as log:
        updated_state = apply_committed_log_changes(database_state, log)

    assert set(updated_state.reservation_positions) == {1001}
