import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Enterprise Retail Lakehouse Dashboard", layout="wide")

st.title("Enterprise Retail Lakehouse Dashboard")
st.caption("Demo business dashboard for store sales, product performance, and promotion effectiveness")

# -------------------------------------------------------------------
# Demo datasets
# -------------------------------------------------------------------

store_sales_daily = pd.DataFrame({
    "sale_date": ["2024-03-10", "2024-03-11", "2024-03-12", "2024-03-13", "2024-03-14"],
    "store_name": ["Melbourne Central", "Melbourne Central", "Melbourne Central", "Melbourne Central", "Melbourne Central"],
    "state": ["VIC", "VIC", "VIC", "VIC", "VIC"],
    "sales_amount": [12500, 13200, 14150, 13800, 14920],
    "transactions": [240, 255, 270, 262, 281]
})

product_performance = pd.DataFrame({
    "product_name": ["Protein Bar", "Greek Yogurt", "Cold Brew", "Almond Milk", "Granola"],
    "category": ["Snacks", "Dairy", "Beverages", "Dairy", "Breakfast"],
    "revenue": [18200, 15400, 16800, 12100, 11350],
    "units_sold": [920, 770, 840, 605, 550]
})

promotion_effectiveness = pd.DataFrame({
    "promotion_name": ["Weekend 10% Off", "Buy 2 Get 1", "Member Discount", "Easter Promo"],
    "channel": ["In-store", "Online", "Loyalty", "In-store"],
    "promo_revenue": [25200, 19800, 17600, 21400],
    "conversion_rate": [0.18, 0.14, 0.22, 0.17]
})

# -------------------------------------------------------------------
# KPI Row
# -------------------------------------------------------------------

total_sales = int(store_sales_daily["sales_amount"].sum())
total_transactions = int(store_sales_daily["transactions"].sum())
top_product = product_performance.sort_values("revenue", ascending=False).iloc[0]["product_name"]
avg_conversion = round(promotion_effectiveness["conversion_rate"].mean() * 100, 2)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Transactions", f"{total_transactions:,}")
col3.metric("Top Product", top_product)
col4.metric("Avg Promotion Conversion", f"{avg_conversion}%")

st.divider()

# -------------------------------------------------------------------
# Sales Trend
# -------------------------------------------------------------------

st.subheader("Store Sales Trend")

sales_chart = (
    alt.Chart(store_sales_daily)
    .mark_line(point=True)
    .encode(
        x=alt.X("sale_date:N", title="Sale Date"),
        y=alt.Y("sales_amount:Q", title="Sales Amount"),
        tooltip=["sale_date", "store_name", "sales_amount", "transactions"]
    )
    .properties(height=320)
)

st.altair_chart(sales_chart, use_container_width=True)

# -------------------------------------------------------------------
# Product Performance
# -------------------------------------------------------------------

st.subheader("Top Product Performance")

product_chart = (
    alt.Chart(product_performance)
    .mark_bar()
    .encode(
        x=alt.X("product_name:N", sort="-y", title="Product"),
        y=alt.Y("revenue:Q", title="Revenue"),
        color="category:N",
        tooltip=["product_name", "category", "revenue", "units_sold"]
    )
    .properties(height=320)
)

st.altair_chart(product_chart, use_container_width=True)

# -------------------------------------------------------------------
# Promotion Effectiveness
# -------------------------------------------------------------------

st.subheader("Promotion Effectiveness")

promo_chart = (
    alt.Chart(promotion_effectiveness)
    .mark_bar()
    .encode(
        x=alt.X("promotion_name:N", title="Promotion"),
        y=alt.Y("promo_revenue:Q", title="Promotion Revenue"),
        color="channel:N",
        tooltip=["promotion_name", "channel", "promo_revenue", "conversion_rate"]
    )
    .properties(height=320)
)

st.altair_chart(promo_chart, use_container_width=True)

# -------------------------------------------------------------------
# Data Preview
# -------------------------------------------------------------------

st.subheader("Sample Mart Preview")

tab1, tab2, tab3 = st.tabs(["Store Sales Daily", "Product Performance", "Promotion Effectiveness"])

with tab1:
    st.dataframe(store_sales_daily, use_container_width=True)

with tab2:
    st.dataframe(product_performance, use_container_width=True)

with tab3:
    st.dataframe(promotion_effectiveness, use_container_width=True)
