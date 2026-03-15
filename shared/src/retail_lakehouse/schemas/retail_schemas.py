"""
Python schema metadata for retail entities.

Used for validation, data generation, and Spark schema inference.
"""

from typing import Any

# Column: (dtype, nullable, description)
ENTITY_SCHEMAS: dict[str, list[tuple[str, str, bool, str]]] = {
    "products": [
        ("product_id", "string", False, "Unique product identifier"),
        ("product_name", "string", False, "Product display name"),
        ("category", "string", False, "Product category"),
        ("subcategory", "string", True, "Product subcategory"),
        ("brand", "string", True, "Brand name"),
        ("unit_price_aud", "float", False, "Unit price in AUD"),
        ("cost_aud", "float", True, "Cost in AUD"),
        ("created_at", "string", True, "Record creation timestamp"),
    ],
    "stores": [
        ("store_id", "string", False, "Unique store identifier"),
        ("store_name", "string", False, "Store display name"),
        ("city", "string", False, "City"),
        ("state", "string", False, "State/territory"),
        ("postcode", "string", True, "Postcode"),
        ("address", "string", True, "Street address"),
        ("created_at", "string", True, "Record creation timestamp"),
    ],
    "customers": [
        ("customer_id", "string", False, "Unique customer identifier"),
        ("first_name", "string", False, "First name"),
        ("last_name", "string", False, "Last name"),
        ("email", "string", True, "Email address"),
        ("loyalty_tier", "string", True, "Loyalty tier (Bronze, Silver, Gold)"),
        ("created_at", "string", True, "Record creation timestamp"),
    ],
    "promotions": [
        ("promotion_id", "string", False, "Unique promotion identifier"),
        ("promotion_name", "string", False, "Promotion display name"),
        ("discount_type", "string", False, "PERCENT or FIXED"),
        ("discount_value", "float", False, "Discount amount or percentage"),
        ("start_date", "string", False, "Promotion start date (YYYY-MM-DD)"),
        ("end_date", "string", False, "Promotion end date (YYYY-MM-DD)"),
        ("created_at", "string", True, "Record creation timestamp"),
    ],
    "sales_transactions": [
        ("sale_id", "string", False, "Unique sale identifier"),
        ("product_id", "string", False, "FK to products"),
        ("store_id", "string", False, "FK to stores"),
        ("customer_id", "string", True, "FK to customers (nullable for guest)"),
        ("promotion_id", "string", True, "FK to promotions (nullable if no promo)"),
        ("quantity", "int", False, "Quantity sold"),
        ("unit_price_aud", "float", False, "Unit price at time of sale"),
        ("discount_aud", "float", True, "Discount applied in AUD"),
        ("sale_date", "string", False, "Sale date (YYYY-MM-DD)"),
        ("sale_timestamp", "string", True, "Sale datetime"),
    ],
    "inventory_snapshots": [
        ("snapshot_id", "string", False, "Unique snapshot identifier"),
        ("product_id", "string", False, "FK to products"),
        ("store_id", "string", False, "FK to stores"),
        ("quantity_on_hand", "int", False, "Quantity in stock"),
        ("snapshot_date", "string", False, "Snapshot date (YYYY-MM-DD)"),
        ("created_at", "string", True, "Record creation timestamp"),
    ],
}


def get_entity_columns(entity: str) -> list[str]:
    """Return column names for an entity."""
    if entity not in ENTITY_SCHEMAS:
        raise ValueError(f"Unknown entity: {entity}")
    return [col[0] for col in ENTITY_SCHEMAS[entity]]


def get_entity_dtypes(entity: str) -> dict[str, str]:
    """Return column name -> dtype mapping for an entity."""
    if entity not in ENTITY_SCHEMAS:
        raise ValueError(f"Unknown entity: {entity}")
    return {col[0]: col[1] for col in ENTITY_SCHEMAS[entity]}
