"""
Reusable constants for the retail lakehouse platform.
"""

# Entity names (used for paths, table names, etc.)
ENTITIES = (
    "products",
    "stores",
    "customers",
    "promotions",
    "sales_transactions",
    "inventory_snapshots",
)

# MinIO bucket names (Medallion architecture)
BUCKETS = {
    "raw": "raw",
    "bronze": "bronze",
    "silver": "silver",
    "gold": "gold",
}

# PostgreSQL schema names
SCHEMAS = {
    "staging": "staging",
    "marts": "marts",
}

# Default date partition format
DATE_PARTITION_FORMAT = "yyyy-MM-dd"

# Australia/Melbourne timezone
AUSTRALIA_MELBOURNE_TZ = "Australia/Melbourne"
