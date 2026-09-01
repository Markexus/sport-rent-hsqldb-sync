import pytest

from sport_rent_hsqldb_sync.item_identity import extract_item_identity


@pytest.mark.parametrize(
    ("source_name", "expected_product_name", "expected_inventory_code"),
    [
        (
            "Narty Dynafit LT 88 172 10803",
            "Narty Dynafit LT 88 172",
            "10803",
        ),
        (
            "Kije Dynafit/004",
            "Kije Dynafit",
            "004",
        ),
        (
            "abc lawinowe 00115",
            "abc lawinowe",
            "00115",
        ),
        (
            "ROWER NS BIKES E-FINE 2 S",
            "ROWER NS BIKES E-FINE 2 S",
            None,
        ),
        (
            "Rower dziecięcy 20",
            "Rower dziecięcy 20",
            None,
        ),
    ],
)
def test_extracts_item_identity(
    source_name: str,
    expected_product_name: str,
    expected_inventory_code: str | None,
) -> None:
    identity = extract_item_identity(source_name)

    assert identity.source_name == source_name
    assert identity.product_name == expected_product_name
    assert identity.inventory_code == expected_inventory_code


def test_normalizes_whitespace_without_changing_source_name() -> None:
    source_name = "  Lonża  EDELRID Cable Kit VI 10531  "

    identity = extract_item_identity(source_name)

    assert identity.source_name == source_name
    assert identity.product_name == "Lonża EDELRID Cable Kit VI"
    assert identity.inventory_code == "10531"


def test_handles_blank_source_name() -> None:
    identity = extract_item_identity("   ")

    assert identity.source_name == "   "
    assert identity.product_name == ""
    assert identity.inventory_code is None
