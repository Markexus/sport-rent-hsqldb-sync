from collections.abc import Iterable

from sport_rent_hsqldb_sync.models import HsqldbDatabaseState
from sport_rent_hsqldb_sync.parsing.abstract_position import (
    ABSTRACT_POSITION_DELETE_PREFIX,
    ABSTRACT_POSITION_INSERT_PREFIX,
    ABSTRACT_POSITION_STATEMENT_PREFIXES,
    parse_abstract_position_delete,
    parse_abstract_position_insert,
)
from sport_rent_hsqldb_sync.parsing.reservation_position import (
    RESERVATION_POSITION_DELETE_PREFIX,
    RESERVATION_POSITION_INSERT_PREFIX,
    RESERVATION_POSITION_STATEMENT_PREFIXES,
    parse_reservation_position_delete,
    parse_reservation_position_insert,
)

SUPPORTED_STATEMENT_PREFIXES = (
    *RESERVATION_POSITION_STATEMENT_PREFIXES,
    *ABSTRACT_POSITION_STATEMENT_PREFIXES,
)


def parse_database_script(lines: Iterable[str]) -> HsqldbDatabaseState:
    database_state = HsqldbDatabaseState(
        reservation_positions={},
        abstract_positions={},
    )

    for raw_line in lines:
        statement = raw_line.strip()

        if statement.startswith(SUPPORTED_STATEMENT_PREFIXES):
            _apply_statement(statement, database_state)

    return database_state


def apply_committed_log_changes(
    database_state: HsqldbDatabaseState,
    lines: Iterable[str],
) -> HsqldbDatabaseState:
    updated_state = HsqldbDatabaseState(
        reservation_positions=database_state.reservation_positions.copy(),
        abstract_positions=database_state.abstract_positions.copy(),
    )
    pending_statements: list[str] = []

    for raw_line in lines:
        statement = raw_line.strip()

        if statement == "COMMIT":
            for pending_statement in pending_statements:
                _apply_statement(pending_statement, updated_state)

            pending_statements.clear()
            continue

        if statement.startswith(SUPPORTED_STATEMENT_PREFIXES):
            pending_statements.append(statement)

    return updated_state


def _apply_statement(
    statement: str,
    database_state: HsqldbDatabaseState,
) -> None:
    if statement.startswith(RESERVATION_POSITION_INSERT_PREFIX):
        reservation_position = parse_reservation_position_insert(statement)
        database_state.reservation_positions[
            reservation_position.source_position_id
        ] = reservation_position
    elif statement.startswith(RESERVATION_POSITION_DELETE_PREFIX):
        source_position_id = parse_reservation_position_delete(statement)
        database_state.reservation_positions.pop(source_position_id, None)
    elif statement.startswith(ABSTRACT_POSITION_INSERT_PREFIX):
        abstract_position = parse_abstract_position_insert(statement)
        database_state.abstract_positions[abstract_position.source_position_id] = (
            abstract_position
        )
    elif statement.startswith(ABSTRACT_POSITION_DELETE_PREFIX):
        source_position_id = parse_abstract_position_delete(statement)
        database_state.abstract_positions.pop(source_position_id, None)
