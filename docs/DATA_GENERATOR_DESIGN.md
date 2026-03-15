# Data Generator — Revised Design

## Discount Calculation Rules (Sales)

| Rule | Implementation |
|------|----------------|
| **promotion_id = null** | discount_aud = 0 |
| **discount_type = PERCENT** | discount_aud = round(unit_price × quantity × (discount_value / 100), 2) |
| **discount_type = FIXED** | discount_aud = round(min(discount_value × quantity, unit_price × quantity), 2) |
| **FIXED semantics** | discount_value is per-unit; total discount capped at order subtotal |
| **Consistency** | discount_aud is fully determined by quantity, unit_price_aud, promotion discount_type, promotion discount_value |

---

## 1. Products

| Change | Implementation |
|--------|-----------------|
| **Product names** | Category-specific product name pools (e.g. Grocery/Dairy: Full Cream Milk 2L, Greek Yogurt 500g) |
| **Categories** | Grocery (Dairy, Bakery, Produce, Pantry, Frozen, Beverages), General Merchandise (Home, Electronics, Toys, Stationery), Health & Beauty (Skincare, Haircare, Personal Care), Apparel (Men, Women, Kids, Footwear) |
| **Brands** | Australian retail brands per category (e.g. Grocery: Devondale, Pauls, Tip Top; H&B: Sukin, Nivea, L'Oreal) |
| **Price ranges** | Grocery: 1.50–25 AUD; Health & Beauty: 3–55 AUD; Apparel: 12–180 AUD; Electronics/General: 15–350 AUD |

## 2. Stores

| Change | Implementation |
|--------|-----------------|
| **Locations** | Fixed AU city/state pairs: Melbourne/VIC, Sydney/NSW, Brisbane/QLD, Perth/WA, Adelaide/SA, Hobart/TAS, Canberra/ACT, Darwin/NT |
| **Store names** | "{City} {Suffix}" e.g. Melbourne CBD, Sydney Parramatta, Brisbane West, Perth North |

## 3. Promotions

| Change | Implementation |
|--------|-----------------|
| **Names** | Realistic campaigns: Weekend Sale, Summer Clearance, Member Discount Week, Back to School, EOFY Sale, etc. |
| **Discount** | PERCENT: 5–25%; FIXED: 2–15 AUD |
| **Date ranges** | Valid start_date ≤ end_date |

## 4. Sales Transactions

| Change | Implementation |
|--------|-----------------|
| **Promotion assignment** | Only assign promotion_id when sale_date ∈ [promotion.start_date, promotion.end_date] |
| **discount_aud** | Derived from promotion: PERCENT → unit_price × quantity × (value/100); FIXED → min(value × quantity, unit_price × quantity); null promo → 0 |
| **sale_timestamp** | Within trading hours 07:00–22:00 (Australia/Melbourne) |
| **customer_id** | ~15% null (guest/anonymous) |

## 5. Inventory Snapshots

| Change | Implementation |
|--------|-----------------|
| **Uniqueness** | One row per (product_id, store_id, snapshot_date) |
| **created_at** | Same day as snapshot_date, end-of-day (e.g. 23:59) |
| **quantity_on_hand** | Category-based: Grocery 20–200, H&B 10–80, Apparel 5–50, Electronics 2–25 |

## 6. Customers

| Change | Implementation |
|--------|-----------------|
| **loyalty_tier** | Controlled: Bronze, Silver, Gold, Platinum; ~10% None (non-enrolled) |
| **email** | Most have email; None only for non-enrolled |
