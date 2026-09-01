import re

from sport_rent_hsqldb_sync.models import HsqldbItemIdentity

SLASH_INVENTORY_CODE_PATTERN = re.compile(
    r"^(?P<product_name>.+?)/(?P<inventory_code>\d+)$"
)

SPACE_INVENTORY_CODE_PATTERN = re.compile(
    r"^(?P<product_name>.+?)\s+(?P<inventory_code>\d{5})$"
)


def extract_item_identity(source_name: str) -> HsqldbItemIdentity:
    normalized_name = " ".join(source_name.split())
    match = SLASH_INVENTORY_CODE_PATTERN.fullmatch(normalized_name)
    if match is None:
        match = SPACE_INVENTORY_CODE_PATTERN.fullmatch(normalized_name)
    if match is None:
        return HsqldbItemIdentity(
            source_name=source_name,
            product_name=normalized_name,
            inventory_code=None,
        )

    return HsqldbItemIdentity(
        source_name=source_name,
        product_name=match.group("product_name"),
        inventory_code=match.group("inventory_code"),
    )
