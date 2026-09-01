from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HsqldbReservationPosition:
    source_position_id: int
    begin_at: datetime | None
    end_at: datetime | None
    source_rent_object_id: int | None
    source_status: int | None


@dataclass(frozen=True)
class HsqldbAbstractPosition:
    source_position_id: int
    source_name: str | None


@dataclass
class HsqldbDatabaseState:
    reservation_positions: dict[int, HsqldbReservationPosition]
    abstract_positions: dict[int, HsqldbAbstractPosition]


@dataclass(frozen=True)
class HsqldbItemIdentity:
    source_name: str
    product_name: str
    inventory_code: str | None


@dataclass(frozen=True)
class HsqldbReservation:
    source_position_id: int
    begin_at: datetime | None
    end_at: datetime | None
    source_rent_object_id: int | None
    source_status: int | None
    item: HsqldbItemIdentity | None
