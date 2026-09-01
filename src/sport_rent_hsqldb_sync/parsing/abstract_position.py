from sport_rent_hsqldb_sync.models import HsqldbAbstractPosition
from sport_rent_hsqldb_sync.parsing.values import (
    parse_optional_text,
    split_insert_values,
)

ABSTRACT_POSITION_INSERT_PREFIX = "INSERT INTO ABSTRACTPOSITION VALUES("
ABSTRACT_POSITION_DELETE_PREFIX = "DELETE FROM ABSTRACTPOSITION WHERE ID="
ABSTRACT_POSITION_STATEMENT_PREFIXES = (
    ABSTRACT_POSITION_INSERT_PREFIX,
    ABSTRACT_POSITION_DELETE_PREFIX,
)


def parse_abstract_position_insert(statement: str) -> HsqldbAbstractPosition:
    values = split_insert_values(statement, ABSTRACT_POSITION_INSERT_PREFIX)
    return HsqldbAbstractPosition(
        source_position_id=int(values[0]),
        source_name=parse_optional_text(values[1]),
    )


def parse_abstract_position_delete(statement: str) -> int:
    source_position_id = statement.removeprefix(
        ABSTRACT_POSITION_DELETE_PREFIX
    ).removesuffix(";")
    return int(source_position_id)
