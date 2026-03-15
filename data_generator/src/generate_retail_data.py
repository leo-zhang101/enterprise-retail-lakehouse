"""
Generate synthetic Australian retail data for local development and testing.

Creates relationally consistent datasets: products, stores, customers, promotions,
sales_transactions, inventory_snapshots.

Usage:
    python -m data_generator.src.generate_retail_data
    python -m data_generator.src.generate_retail_data --n-sales 100000 --output data/raw
"""

import argparse
import random
import sys
from datetime import datetime, time, timedelta
from pathlib import Path

# Ensure shared package is importable when run from project root
_project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_project_root / "shared" / "src"))

import pandas as pd
from faker import Faker

from retail_lakehouse.config.settings import get_settings
from retail_lakehouse.utils.logging_utils import get_logger

from data_generator.src.config import GeneratorConfig

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Product seed data: (category, subcategory) -> product names, brands, price range
# -----------------------------------------------------------------------------

PRODUCT_SEED: dict[str, dict[str, tuple[list[str], list[str], tuple[float, float]]]] = {
    "Grocery": {
        "Dairy": (
            ["Full Cream Milk 2L", "Skim Milk 2L", "Greek Yogurt 500g", "Natural Yogurt 1kg",
             "Cheddar Cheese 500g", "Butter 250g", "Cream 300ml", "Cottage Cheese 200g"],
            ["Devondale", "Pauls", "Dairy Farmers", "Bega", "Mainland", "Liddells"],
            (2.50, 12.00),
        ),
        "Bakery": (
            ["White Bread Loaf", "Wholemeal Bread", "Sourdough Loaf", "Multigrain Rolls 6pk",
             "Croissant", "Muffin Blueberry", "Banana Bread", "Baguette"],
            ["Tip Top", "Helga's", "Bakers Delight", "Coles", "Woolworths"],
            (1.80, 8.50),
        ),
        "Produce": (
            ["Bananas 1kg", "Apples 1kg", "Oranges 1kg", "Carrots 1kg", "Broccoli",
             "Lettuce", "Tomatoes 500g", "Potatoes 2kg", "Onions 1kg", "Avocado"],
            ["Fresh", "Coles", "Woolworths", "Harris Farm"],
            (1.50, 15.00),
        ),
        "Pantry": (
            ["Pasta 500g", "Rice 1kg", "Olive Oil 750ml", "Tomato Sauce 500g",
             "Baked Beans 420g", "Cereal 500g", "Oats 1kg", "Honey 500g"],
            ["San Remo", "SunRice", "Cobram Estate", "Heinz", "Kellogg's", "Uncle Tobys"],
            (2.00, 18.00),
        ),
        "Frozen": (
            ["Frozen Peas 500g", "Frozen Mixed Vegetables 1kg", "Ice Cream 2L",
             "Frozen Pizza", "Frozen Chips 1kg", "Frozen Berries 500g"],
            ["Birds Eye", "McCain", "Peters", "Dr Oetker", "Coles", "Woolworths"],
            (3.00, 14.00),
        ),
        "Beverages": (
            ["Orange Juice 2L", "Cola 1.25L", "Sparkling Water 1L", "Coffee Beans 250g",
             "Tea Bags 100pk", "Sports Drink 600ml", "Mineral Water 24pk"],
            ["Berri", "Coca-Cola", "Mount Franklin", "Lavazza", "Twinings", "Powerade"],
            (2.50, 25.00),
        ),
    },
    "General Merchandise": {
        "Home": (
            ["Storage Box Medium", "Kettle", "Kitchen Towels 2pk", "Clothes Pegs 50pk",
             "Dish Brush", "Trash Bags 30pk", "Aluminium Foil", "Food Wrap"],
            ["Kmart", "Target", "Big W", "IKEA", "Glad", "Reynolds"],
            (4.00, 45.00),
        ),
        "Electronics": (
            ["USB Charging Cable", "Power Bank 10000mAh", "Bluetooth Speaker",
             "Phone Holder", "HDMI Cable", "Screen Protector", "Earbuds"],
            ["Belkin", "Anker", "JBL", "Samsung", "Apple", "Kmart"],
            (12.00, 120.00),
        ),
        "Toys": (
            ["Building Blocks Set", "Board Game", "Puzzle 500pc", "Action Figure",
             "Stuffed Toy", "Art Supplies Kit", "Outdoor Ball"],
            ["LEGO", "Hasbro", "Mattel", "Kmart", "Target", "Big W"],
            (8.00, 80.00),
        ),
        "Stationery": (
            ["Notebook A4", "Pen Pack 10", "Sticky Notes", "Highlighters 5pk",
             "Scissors", "Stapler", "Filing Folder", "Whiteboard Markers"],
            ["Officeworks", "Staedtler", "Bic", "3M", "Kmart"],
            (2.50, 35.00),
        ),
    },
    "Health & Beauty": {
        "Skincare": (
            ["Face Cleanser", "Moisturiser 50ml", "Sunscreen SPF50", "Serum 30ml",
             "Face Mask", "Lip Balm", "Hand Cream", "Eye Cream"],
            ["Sukin", "Nivea", "Cetaphil", "La Roche-Posay", "CeraVe", "QV"],
            (5.00, 55.00),
        ),
        "Haircare": (
            ["Shampoo 400ml", "Conditioner 400ml", "Hair Gel", "Dry Shampoo",
             "Hair Oil", "Styling Spray", "Hair Mask"],
            ["Pantene", "Herbal Essences", "OGX", "Schwarzkopf", "L'Oreal"],
            (4.00, 35.00),
        ),
        "Personal Care": (
            ["Toothpaste", "Mouthwash", "Deodorant", "Razor 4pk", "Shaving Gel",
             "Body Lotion", "Soap Bar 3pk", "Cotton Pads 100pk"],
            ["Colgate", "Listerine", "Dove", "Gillette", "Nivea", "Swisse"],
            (3.00, 25.00),
        ),
    },
    "Apparel": {
        "Men": (
            ["Men's T-Shirt", "Men's Polo Shirt", "Men's Shorts", "Men's Jeans",
             "Men's Hoodie", "Men's Jacket", "Men's Socks 3pk", "Men's Belt"],
            ["Bonds", "Hanes", "Levi's", "Nike", "Adidas", "Kmart", "Target"],
            (15.00, 120.00),
        ),
        "Women": (
            ["Women's T-Shirt", "Women's Blouse", "Women's Leggings", "Women's Dress",
             "Women's Cardigan", "Women's Socks 3pk", "Women's Scarf"],
            ["Bonds", "Kmart", "Target", "Cotton On", "Sportsgirl"],
            (12.00, 95.00),
        ),
        "Kids": (
            ["Kids T-Shirt", "Kids Shorts", "Kids Hoodie", "Kids Socks 3pk",
             "Kids Pyjamas", "Kids Dress", "Kids Leggings"],
            ["Bonds", "Kmart", "Target", "Big W", "Best & Less"],
            (8.00, 55.00),
        ),
        "Footwear": (
            ["Thongs", "Sandals", "Sneakers", "Slip-On Shoes", "School Shoes"],
            ["Havaianas", "Kmart", "Target", "Nike", "Skechers"],
            (15.00, 180.00),
        ),
    },
}

# -----------------------------------------------------------------------------
# Australian store locations: (city, state)
# -----------------------------------------------------------------------------

AU_STORE_LOCATIONS = [
    ("Melbourne", "VIC"), ("Sydney", "NSW"), ("Brisbane", "QLD"), ("Perth", "WA"),
    ("Adelaide", "SA"), ("Hobart", "TAS"), ("Canberra", "ACT"), ("Darwin", "NT"),
    ("Geelong", "VIC"), ("Newcastle", "NSW"), ("Gold Coast", "QLD"), ("Fremantle", "WA"),
    ("Wollongong", "NSW"), ("Ballarat", "VIC"), ("Bendigo", "VIC"), ("Cairns", "QLD"),
    ("Parramatta", "NSW"), ("Penrith", "NSW"), ("Logan", "QLD"), ("Toowoomba", "QLD"),
]

AU_STORE_SUFFIXES = [
    "CBD", "Central", "North", "South", "East", "West", "Plaza", "Square",
    "Metro", "Express", "Supercentre", "Regional",
]

# Australian postcode ranges by state (4-digit, realistic)
AU_POSTCODE_RANGES: dict[str, tuple[int, int]] = {
    "NSW": (2000, 2999),
    "VIC": (3000, 3999),
    "QLD": (4000, 4999),
    "SA": (5000, 5999),
    "WA": (6000, 6999),
    "TAS": (7000, 7999),
    "NT": (800, 999),   # formatted as 0800-0999
    "ACT": (2600, 2920),
}

# -----------------------------------------------------------------------------
# Promotion campaign names
# -----------------------------------------------------------------------------

PROMOTION_NAMES = [
    "Weekend Sale", "Summer Clearance", "Member Discount Week", "Back to School",
    "EOFY Sale", "Winter Warmers", "Spring Special", "Christmas Sale",
    "New Year Sale", "Flash Sale", "Buy One Get One", "Half Price",
    "Clearance Event", "Loyalty Bonus", "End of Season", "Midweek Special",
]

# -----------------------------------------------------------------------------
# Loyalty tiers
# -----------------------------------------------------------------------------

LOYALTY_TIERS = ("Bronze", "Silver", "Gold", "Platinum")


# -----------------------------------------------------------------------------
# Generation helpers
# -----------------------------------------------------------------------------

def _ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _trading_hours_datetime(sale_date: datetime.date, fake: Faker) -> datetime:
    """Return a datetime within store trading hours (07:00–22:00) on sale_date."""
    hour = fake.random_int(min=7, max=21)
    minute = fake.random_int(min=0, max=59)
    return datetime.combine(sale_date, time(hour, minute))


def generate_products(cfg: GeneratorConfig, fake: Faker) -> pd.DataFrame:
    """Generate products with realistic Australian retail names and price ranges."""
    rows = []
    product_idx = 0
    flat_seed = [
        (cat, subcat, names, brands, (lo, hi))
        for cat, subcats in PRODUCT_SEED.items()
        for subcat, (names, brands, (lo, hi)) in subcats.items()
    ]
    for i in range(cfg.n_products):
        cat, subcat, names, brands, (price_lo, price_hi) = flat_seed[i % len(flat_seed)]
        name = names[product_idx % len(names)]
        brand = brands[(product_idx // len(names)) % len(brands)]
        unit_price = round(fake.random.uniform(price_lo, price_hi), 2)
        cost = round(unit_price * fake.random.uniform(0.35, 0.65), 2) if i % 2 else None
        rows.append({
            "product_id": f"PRD-{i + 1:06d}",
            "product_name": name,
            "category": cat,
            "subcategory": subcat,
            "brand": brand,
            "unit_price_aud": unit_price,
            "cost_aud": cost,
            "created_at": fake.date_time_this_year().isoformat(),
        })
        product_idx += 1
    return pd.DataFrame(rows)


def _postcode_for_state(state: str, fake: Faker) -> str:
    """Return a plausible Australian postcode for the given state."""
    lo, hi = AU_POSTCODE_RANGES.get(state, (2000, 2999))
    n = fake.random_int(min=lo, max=hi)
    return f"{n:04d}" if n < 1000 else str(n)


def generate_stores(cfg: GeneratorConfig, fake: Faker) -> pd.DataFrame:
    """Generate stores with realistic Australian locations and branch names."""
    rows = []
    for i in range(cfg.n_stores):
        city, state = AU_STORE_LOCATIONS[i % len(AU_STORE_LOCATIONS)]
        suffix = AU_STORE_SUFFIXES[(i // len(AU_STORE_LOCATIONS)) % len(AU_STORE_SUFFIXES)]
        store_name = f"{city} {suffix}"
        rows.append({
            "store_id": f"STR-{i + 1:05d}",
            "store_name": store_name,
            "city": city,
            "state": state,
            "postcode": _postcode_for_state(state, fake),
            "address": fake.street_address(),
            "created_at": fake.date_time_this_year().isoformat(),
        })
    return pd.DataFrame(rows)


def generate_customers(cfg: GeneratorConfig, fake: Faker) -> pd.DataFrame:
    """Generate customers with controlled loyalty tiers. Non-enrolled use Guest."""
    rows = []
    for i in range(cfg.n_customers):
        is_enrolled = fake.random.random() > 0.10
        loyalty_tier = fake.random_element(LOYALTY_TIERS) if is_enrolled else "Guest"
        email = fake.email()
        rows.append({
            "customer_id": f"CUS-{i + 1:06d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": email,
            "loyalty_tier": loyalty_tier,
            "created_at": fake.date_time_this_year().isoformat(),
        })
    return pd.DataFrame(rows)


def generate_promotions(cfg: GeneratorConfig, fake: Faker) -> pd.DataFrame:
    """Generate promotions with realistic campaign names and valid date ranges."""
    rows = []
    for i in range(cfg.n_promotions):
        name = PROMOTION_NAMES[i % len(PROMOTION_NAMES)]
        if i >= len(PROMOTION_NAMES):
            name = f"{name} {i // len(PROMOTION_NAMES) + 1}"
        discount_type = fake.random_element(["PERCENT", "FIXED"])
        if discount_type == "PERCENT":
            discount_value = round(fake.random.uniform(5, 25), 2)
        else:
            discount_value = round(fake.random.uniform(2, 15), 2)
        start = fake.date_between(start_date="-1y", end_date="today")
        end = fake.date_between(start_date=start, end_date="+3m")
        rows.append({
            "promotion_id": f"PROM-{i + 1:05d}",
            "promotion_name": name,
            "discount_type": discount_type,
            "discount_value": discount_value,
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "created_at": fake.date_time_this_year().isoformat(),
        })
    return pd.DataFrame(rows)


def _apply_promotion_discount(
    unit_price: float, quantity: int, discount_type: str, discount_value: float
) -> float:
    """
    Calculate discount_aud from promotion rule.

    Rules:
    - PERCENT: discount = subtotal × (value / 100)
    - FIXED: discount_value is per unit; total = min(value × quantity, subtotal)
    - Total discount never exceeds order subtotal.
    """
    subtotal = unit_price * quantity
    if discount_type == "PERCENT":
        discount = subtotal * (discount_value / 100)
    else:
        # FIXED: per-unit discount; cap at subtotal
        discount = min(discount_value * quantity, subtotal)
    return round(discount, 2)


def generate_sales(
    cfg: GeneratorConfig,
    fake: Faker,
    products: pd.DataFrame,
    stores: pd.DataFrame,
    customers: pd.DataFrame,
    promotions: pd.DataFrame,
) -> pd.DataFrame:
    """Generate sales with valid promotion dates, calculated discounts, and trading hours."""
    product_ids = products["product_id"].tolist()
    store_ids = stores["store_id"].tolist()
    enrolled_customers = customers[customers["loyalty_tier"] != "Guest"]["customer_id"].tolist()

    promos = promotions.copy()
    promos["start_date_dt"] = pd.to_datetime(promos["start_date"])
    promos["end_date_dt"] = pd.to_datetime(promos["end_date"])

    rows = []
    for i in range(cfg.n_sales):
        product_id = fake.random_element(product_ids)
        store_id = fake.random_element(store_ids)
        is_guest = fake.random.random() < cfg.guest_sale_ratio
        customer_id = None if is_guest else fake.random_element(enrolled_customers)

        product = products[products["product_id"] == product_id].iloc[0]
        unit_price = float(product["unit_price_aud"])
        quantity = fake.random_int(min=1, max=10)

        sale_date = fake.date_between(start_date="-1y", end_date="today")
        sale_date_str = sale_date.strftime("%Y-%m-%d")

        # Only assign promotion if sale_date falls within promotion window
        sale_ts_pd = pd.Timestamp(sale_date)
        valid_promos = promos[
            (promos["start_date_dt"] <= sale_ts_pd) & (promos["end_date_dt"] >= sale_ts_pd)
        ]
        if len(valid_promos) > 0 and fake.random.random() < 0.35:
            promo = valid_promos.sample(1).iloc[0]
            promotion_id = promo["promotion_id"]
            discount_aud = _apply_promotion_discount(
                unit_price, quantity,
                promo["discount_type"], float(promo["discount_value"]),
            )
        else:
            promotion_id = None
            discount_aud = 0.0

        sale_ts = _trading_hours_datetime(sale_date, fake)

        rows.append({
            "sale_id": f"SAL-{i + 1:08d}",
            "product_id": product_id,
            "store_id": store_id,
            "customer_id": customer_id,
            "promotion_id": promotion_id,
            "quantity": quantity,
            "unit_price_aud": unit_price,
            "discount_aud": discount_aud,
            "sale_date": sale_date_str,
            "sale_timestamp": sale_ts.isoformat(),
        })
    return pd.DataFrame(rows)


def _inventory_qty_by_category(category: str, fake: Faker) -> int:
    """Return realistic quantity_on_hand by category."""
    ranges = {
        "Grocery": (20, 200),
        "General Merchandise": (5, 80),
        "Health & Beauty": (10, 80),
        "Apparel": (5, 50),
    }
    lo, hi = ranges.get(category, (5, 100))
    return fake.random_int(min=lo, max=hi)


def generate_inventory_snapshots(
    cfg: GeneratorConfig,
    fake: Faker,
    products: pd.DataFrame,
    stores: pd.DataFrame,
) -> pd.DataFrame:
    """Generate one row per (product_id, store_id, snapshot_date) with realistic quantities."""
    product_list = products.to_dict("records")
    store_ids = stores["store_id"].tolist()

    n_days = cfg.n_inventory_snapshots_per_product_store
    n_combos = min(
        len(product_list) * len(store_ids),
        cfg.max_inventory_product_store_pairs,
    )

    # Sample product-store pairs (deterministic with seed)
    rng = random.Random(cfg.seed)
    pairs: list[tuple[dict, str]] = []
    seen = set()
    attempts = 0
    while len(pairs) < n_combos and attempts < n_combos * 2:
        p = rng.choice(product_list)
        s = rng.choice(store_ids)
        key = (p["product_id"], s)
        if key not in seen:
            seen.add(key)
            pairs.append((p, s))
        attempts += 1

    rows = []
    snapshot_id = 0
    base_date = datetime.now().date() - timedelta(days=n_days)

    for product, store_id in pairs:
        category = product["category"]
        for d in range(n_days):
            snapshot_date = base_date + timedelta(days=d)
            qty = _inventory_qty_by_category(category, fake)
            created_at = datetime.combine(snapshot_date, time(23, 59, 0))
            rows.append({
                "snapshot_id": f"INV-{snapshot_id + 1:08d}",
                "product_id": product["product_id"],
                "store_id": store_id,
                "quantity_on_hand": qty,
                "snapshot_date": snapshot_date.strftime("%Y-%m-%d"),
                "created_at": created_at.isoformat(),
            })
            snapshot_id += 1

    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# Main flow
# -----------------------------------------------------------------------------

def run(config: GeneratorConfig) -> None:
    """Generate all entities and write to data/raw/<entity>/."""
    fake = Faker("en_AU")
    Faker.seed(config.seed)
    random.seed(config.seed)

    output_dir = Path(config.output_dir)
    if not output_dir.is_absolute():
        settings = get_settings()
        output_dir = settings["project_root"] / output_dir

    logger.info("Generating retail data (seed=%d)", config.seed)
    logger.info("Output: %s", output_dir)

    logger.info("Generating products (%d rows)...", config.n_products)
    products = generate_products(config, fake)
    out = output_dir / "products"
    _ensure_output_dir(out)
    products.to_csv(out / "products.csv", index=False)
    logger.info("  -> %s/products.csv", out)

    logger.info("Generating stores (%d rows)...", config.n_stores)
    stores = generate_stores(config, fake)
    out = output_dir / "stores"
    _ensure_output_dir(out)
    stores.to_csv(out / "stores.csv", index=False)
    logger.info("  -> %s/stores.csv", out)

    logger.info("Generating customers (%d rows)...", config.n_customers)
    customers = generate_customers(config, fake)
    out = output_dir / "customers"
    _ensure_output_dir(out)
    customers.to_csv(out / "customers.csv", index=False)
    logger.info("  -> %s/customers.csv", out)

    logger.info("Generating promotions (%d rows)...", config.n_promotions)
    promotions = generate_promotions(config, fake)
    out = output_dir / "promotions"
    _ensure_output_dir(out)
    promotions.to_csv(out / "promotions.csv", index=False)
    logger.info("  -> %s/promotions.csv", out)

    logger.info("Generating sales_transactions (%d rows)...", config.n_sales)
    sales = generate_sales(config, fake, products, stores, customers, promotions)
    out = output_dir / "sales_transactions"
    _ensure_output_dir(out)
    sales.to_csv(out / "sales_transactions.csv", index=False)
    logger.info("  -> %s/sales_transactions.csv", out)

    logger.info("Generating inventory_snapshots...")
    inventory = generate_inventory_snapshots(config, fake, products, stores)
    out = output_dir / "inventory_snapshots"
    _ensure_output_dir(out)
    inventory.to_csv(out / "inventory_snapshots.csv", index=False)
    logger.info("  -> %s/inventory_snapshots.csv (%d rows)", out, len(inventory))

    logger.info("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic Australian retail data")
    parser.add_argument("--n-stores", type=int, default=100)
    parser.add_argument("--n-products", type=int, default=5_000)
    parser.add_argument("--n-customers", type=int, default=50_000)
    parser.add_argument("--n-promotions", type=int, default=500)
    parser.add_argument("--n-sales", type=int, default=500_000)
    parser.add_argument("--n-inventory-days", type=int, default=30)
    parser.add_argument("--max-inventory-pairs", type=int, default=50_000)
    parser.add_argument("--guest-ratio", type=float, default=0.15)
    parser.add_argument("--output", type=str, default="data/raw")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    config = GeneratorConfig(
        n_stores=args.n_stores,
        n_products=args.n_products,
        n_customers=args.n_customers,
        n_promotions=args.n_promotions,
        n_sales=args.n_sales,
        n_inventory_snapshots_per_product_store=args.n_inventory_days,
        max_inventory_product_store_pairs=args.max_inventory_pairs,
        guest_sale_ratio=args.guest_ratio,
        output_dir=Path(args.output),
        seed=args.seed,
    )
    run(config)


if __name__ == "__main__":
    main()
