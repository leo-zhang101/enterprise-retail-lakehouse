"""
Configuration for the retail data generator.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class GeneratorConfig:
    """Configurable row counts and paths for synthetic data generation."""

    # Row counts (MVP defaults)
    n_stores: int = 100
    n_products: int = 5_000
    n_customers: int = 50_000
    n_promotions: int = 500
    n_sales: int = 500_000
    n_inventory_snapshots_per_product_store: int = 30

    # Sales: % of transactions without customer (guest)
    guest_sale_ratio: float = 0.15

    # Inventory: max product-store pairs to generate (keeps size manageable)
    max_inventory_product_store_pairs: int = 50_000

    # Output
    output_dir: Path = Path("data/raw")
    seed: int = 42

    def __post_init__(self) -> None:
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
