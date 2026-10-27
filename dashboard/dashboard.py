from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


st.set_page_config(
    page_title="Analisis E-Commerce",
    page_icon="📊",
    layout="wide",
)

DATA_DIR = Path(__file__).resolve().parent.parent / "E-Commerce Public Dataset"


@st.cache_data
def load_data():
    orders = pd.read_csv(DATA_DIR / "orders_dataset.csv")
    payments = pd.read_csv(DATA_DIR / "order_payments_dataset.csv")
    customers = pd.read_csv(DATA_DIR / "customers_dataset.csv")
    items = pd.read_csv(DATA_DIR / "order_items_dataset.csv")
    products = pd.read_csv(DATA_DIR / "products_dataset.csv")

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )
    orders = orders.dropna(subset=["order_purchase_timestamp"]).drop_duplicates(
        subset=["order_id"]
    )

    payments_by_order = payments.groupby("order_id", as_index=False)[
        "payment_value"
    ].sum()
    items_with_category = items.merge(
        products[["product_id", "product_category_name"]],
        on="product_id",
        how="left",
    )
    return orders, payments_by_order, customers, items_with_category


orders, payments_by_order, customers, items = load_data()

st.title("📊 Analisis Data E-Commerce")
st.caption(
    "Jelajahi tren pembayaran, kategori produk, dan karakteristik pelanggan "
    "berdasarkan data transaksi."
)

st.sidebar.header("Filter Periode")
min_date = orders["order_purchase_timestamp"].min().date()
max_date = orders["order_purchase_timestamp"].max().date()
date_range = st.sidebar.date_input(
    "Tanggal pembelian",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date = end_date = min_date
else:
    start_date = end_date = date_range

period_orders = orders.loc[
    orders["order_purchase_timestamp"].dt.date.between(start_date, end_date)
].copy()

if period_orders.empty:
    st.warning("Tidak ada transaksi pada periode yang dipilih.")
    st.stop()

period_payments = period_orders[["order_id"]].merge(
    payments_by_order,
    on="order_id",
    how="left",
)
period_items = items.merge(
    period_orders[["order_id"]],
    on="order_id",
    how="inner",
)
period_customers = period_orders.merge(
    customers[["customer_id", "customer_unique_id"]],
    on="customer_id",
    how="left",
)

total_revenue = period_payments["payment_value"].sum()
total_orders = period_orders["order_id"].nunique()
total_customers = period_customers["customer_unique_id"].nunique()
total_products = period_items["product_id"].nunique()

st.subheader("Ringkasan Periode")
metric_cols = st.columns(4)
metric_cols[0].metric("Total Pembayaran", f"R$ {total_revenue:,.2f}")
metric_cols[1].metric("Jumlah Pesanan", f"{total_orders:,}")
metric_cols[2].metric("Pelanggan Unik", f"{total_customers:,}")
metric_cols[3].metric("Produk Berbeda", f"{total_products:,}")

st.divider()
st.subheader("Tren Pembayaran Bulanan")
monthly_data = period_orders[["order_id", "order_purchase_timestamp"]].merge(
    payments_by_order,
    on="order_id",
    how="left",
)
monthly_data["Bulan"] = (
    monthly_data["order_purchase_timestamp"].dt.to_period("M").astype(str)
)
monthly_revenue = (
    monthly_data.groupby("Bulan", as_index=False)["payment_value"]
    .sum()
    .sort_values("Bulan")
)

fig, ax = plt.subplots(figsize=(12, 4))
sns.lineplot(
    data=monthly_revenue,
    x="Bulan",
    y="payment_value",
    marker="o",
    ax=ax,
)
ax.set_xlabel("Bulan")
ax.set_ylabel("Total pembayaran (R$)")
ax.tick_params(axis="x", rotation=45)
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

left_col, right_col = st.columns(2)
with left_col:
    st.subheader("Kategori Produk Teratas")
    category_data = period_items.assign(
        product_category_name=period_items["product_category_name"].fillna(
            "Tidak diketahui"
        )
    )
    top_categories = (
        category_data.groupby("product_category_name")["price"]
        .sum()
        .nlargest(10)
        .sort_values()
        .reset_index()
    )
    top_categories = top_categories.rename(
        columns={
            "product_category_name": "Kategori",
            "price": "Nilai item",
        }
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=top_categories,
        x="Nilai item",
        y="Kategori",
        color="#4C78A8",
        ax=ax,
    )
    ax.set_xlabel("Total harga item (R$)")
    ax.set_ylabel("")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption(
        "Grafik kategori menjumlahkan harga item, bukan nilai pembayaran order, "
        "agar satu order tidak terhitung berulang pada setiap item."
    )

with right_col:
    st.subheader("Segmentasi Pelanggan (RFM)")
    customer_orders = period_customers.merge(
        period_payments,
        on="order_id",
        how="left",
    )
    rfm = (
        customer_orders.groupby("customer_unique_id", as_index=False)
        .agg(
            recency=("order_purchase_timestamp", lambda dates: (
                period_orders["order_purchase_timestamp"].max() - dates.max()
            ).days),
            frequency=("order_id", "nunique"),
            monetary=("payment_value", "sum"),
        )
        .dropna(subset=["customer_unique_id"])
    )

    if rfm.empty:
        st.info("Data pelanggan tidak tersedia untuk periode ini.")
    else:
        score_bins = [0, 0.2, 0.4, 0.6, 0.8, 1]
        score_labels = [1, 2, 3, 4, 5]
        for column, score_column in (
            ("recency", "R"),
            ("frequency", "F"),
            ("monetary", "M"),
        ):
            percentile = rfm[column].rank(method="first", pct=True)
            score = pd.cut(
                percentile,
                bins=score_bins,
                labels=score_labels,
                include_lowest=True,
            ).astype(int)
            rfm[score_column] = 6 - score if score_column == "R" else score
        rfm["RFM Score"] = rfm[["R", "F", "M"]].sum(axis=1)
        spending_rank = rfm["RFM Score"].rank(method="first", pct=True)
        rfm["Segmen"] = "Low Value"
        rfm.loc[spending_rank >= 0.25, "Segmen"] = "Medium Value"
        rfm.loc[spending_rank >= 0.75, "Segmen"] = "High Value"
        segment_order = ["High Value", "Medium Value", "Low Value"]
        segment_counts = (
            rfm["Segmen"]
            .value_counts()
            .reindex(segment_order, fill_value=0)
            .rename_axis("Segmen")
            .reset_index(name="Jumlah pelanggan")
        )
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(
            segment_counts["Segmen"],
            segment_counts["Jumlah pelanggan"],
            color=["#2A9D8F", "#E9C46A", "#E76F51"],
        )
        ax.set_xlabel("")
        ax.set_ylabel("Jumlah pelanggan")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        with st.expander("Lihat ringkasan segmen pelanggan"):
            segment_summary = (
                rfm.groupby("Segmen", as_index=False)
                .agg(
                    pelanggan=("customer_unique_id", "count"),
                    rata_rata_recency_hari=("recency", "mean"),
                    frekuensi_pesanan=("frequency", "mean"),
                    total_pembayaran=("monetary", "sum"),
                )
                .set_index("Segmen")
                .reindex(segment_order)
                .dropna(how="all")
                .reset_index()
            )
            st.dataframe(segment_summary, hide_index=True)
        with st.expander("Lihat skor RFM pelanggan"):
            st.dataframe(
                rfm[
                    [
                        "customer_unique_id",
                        "recency",
                        "frequency",
                        "monetary",
                        "R",
                        "F",
                        "M",
                        "RFM Score",
                        "Segmen",
                    ]
                ],
                hide_index=True,
            )
