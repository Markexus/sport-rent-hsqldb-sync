import csv
import re
from datetime import datetime

UNICODE_ESCAPE_PATTERN = re.compile(r"\\u([0-9a-fA-F]{4})")


def split_insert_values(statement: str, prefix: str) -> list[str]:
    values_text = statement.removeprefix(prefix).removesuffix(")")
    return next(csv.reader([values_text], delimiter=",", quotechar="'"))


def parse_timestamp(value: str) -> datetime | None:
    if value == "NULL":
        return None
    return datetime.fromisoformat(value)


def parse_optional_int(value: str) -> int | None:
    if value == "NULL":
        return None
    return int(value)


def parse_optional_text(value: str) -> str | None:
    if value == "NULL":
        return None
    return UNICODE_ESCAPE_PATTERN.sub(
        lambda match: chr(int(match.group(1), 16)),
        value,
    )
