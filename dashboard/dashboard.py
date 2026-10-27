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


# Memuat data utama dari folder dataset dan menyiapkan kolom tanggal serta gabungan data.
@st.cache_data
def load_data():
    # Membaca lima tabel yang diperlukan untuk analisis pesanan, pembayaran, pelanggan, dan produk.
    orders = pd.read_csv(DATA_DIR / "orders_dataset.csv")
    payments = pd.read_csv(DATA_DIR / "order_payments_dataset.csv")
    customers = pd.read_csv(DATA_DIR / "customers_dataset.csv")
    items = pd.read_csv(DATA_DIR / "order_items_dataset.csv")
    products = pd.read_csv(DATA_DIR / "products_dataset.csv")

    # Mengubah tanggal menjadi format waktu; nilai tanggal yang tidak valid akan dijadikan kosong.
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )
    # Menghapus pesanan tanpa tanggal valid dan duplikat agar satu pesanan hanya muncul sekali.
    orders = orders.dropna(subset=["order_purchase_timestamp"]).drop_duplicates(
        subset=["order_id"]
    )

    # Menjumlahkan seluruh metode pembayaran agar setiap pesanan memiliki satu nilai total.
    payments_by_order = payments.groupby("order_id", as_index=False)[
        "payment_value"
    ].sum()
    # Menambahkan nama kategori produk ke setiap item untuk analisis kategori.
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

# Panel filter di sidebar agar pengguna bisa membatasi data berdasarkan tahun dan tanggal.
st.sidebar.header("Filter Periode")
selected_year = st.sidebar.radio(
    "Pilih tahun",
    options=["Semua tahun", 2016, 2017, 2018],
    horizontal=True,
)

min_date = orders["order_purchase_timestamp"].min().date()
max_date = orders["order_purchase_timestamp"].max().date()
date_range = st.sidebar.date_input(
    "Tanggal pembelian",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Menangani input rentang tanggal agar tetap valid walau user memilih satu hari atau dua tanggal.
if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date = end_date = min_date
else:
    start_date = end_date = date_range

# Membuat mask untuk memfilter transaksi sesuai rentang tanggal dan tahun yang dipilih.
date_mask = orders["order_purchase_timestamp"].dt.date.between(
    start_date, end_date
)
if selected_year != "Semua tahun":
    date_mask &= orders["order_purchase_timestamp"].dt.year.eq(selected_year)

period_orders = orders.loc[date_mask].copy()

# Jika hasil filter kosong, dashboard akan berhenti agar tidak menampilkan angka yang bias.
if period_orders.empty:
    st.warning("Tidak ada transaksi pada periode yang dipilih.")
    st.stop()

# Menghitung ukuran ringkasan periode untuk KPI dan analisis lanjutan.
# Menggabungkan pembayaran per pesanan agar transaksi yang memiliki beberapa pembayaran tidak terhitung ganda.
period_payments = period_orders[["order_id"]].merge(
    payments_by_order,
    on="order_id",
    how="left",
)
# Menyaring item dari pesanan terpilih untuk menjaga analisis produk sesuai periode.
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

# Menghitung metrik utama berdasarkan data yang sudah dibatasi oleh filter periode.
total_revenue = period_payments["payment_value"].sum()
total_orders = period_orders["order_id"].nunique()
total_customers = period_customers["customer_unique_id"].nunique()
total_products = period_items["product_id"].nunique()

st.subheader("Ringkasan Periode")
# KPI utama menampilkan gambaran cepat performa bisnis pada periode aktif.
metric_cols = st.columns(4)
metric_cols[0].metric("Total Pembayaran", f"R$ {total_revenue:,.2f}")
metric_cols[1].metric("Jumlah Pesanan", f"{total_orders:,}")
metric_cols[2].metric("Pelanggan Unik", f"{total_customers:,}")
metric_cols[3].metric("Produk Berbeda", f"{total_products:,}")

st.divider()
# Grafik ini menunjukkan perubahan total pendapatan dari bulan ke bulan.
st.subheader("Tren Pembayaran Bulanan")
monthly_data = period_orders[["order_id", "order_purchase_timestamp"]].merge(
    payments_by_order,
    on="order_id",
    how="left",
)
monthly_data["Bulan"] = (
    monthly_data["order_purchase_timestamp"].dt.to_period("M").astype(str)
)
# Menjumlahkan pembayaran per bulan untuk ditampilkan sebagai tren.
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
    # Analisis kategori membantu melihat produk mana yang paling banyak menyumbang nilai transaksi.
    st.subheader("Kategori Produk Teratas")
    category_data = period_items.assign(
        product_category_name=period_items["product_category_name"].fillna(
            "Tidak diketahui"
        )
    )
    # Memilih 10 kategori dengan nilai item terbesar, lalu mengurutkannya untuk grafik batang.
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
    # Segmentasi RFM mengelompokkan pelanggan berdasarkan recency, frequency, dan monetary value.
    st.subheader("Segmentasi Pelanggan (RFM)")
    customer_orders = period_customers.merge(
        period_payments,
        on="order_id",
        how="left",
    )
    # Menghitung RFM per pelanggan: jarak hari dari transaksi terakhir, jumlah pesanan, dan total pembayaran.
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
        # Membagi peringkat persentil menjadi lima skor; recency dibalik agar nilai lebih rendah mendapat skor lebih tinggi.
        score_bins = [0, 0.2, 0.4, 0.6, 0.8, 1]
        score_labels = [1, 2, 3, 4, 5]
        for column, score_column in (
            ("recency", "R"),
            ("frequency", "F"),
            ("monetary", "M"),
        ):
            # Mengubah nilai menjadi skor kuintil agar metrik yang skalanya berbeda dapat dibandingkan.
            percentile = rfm[column].rank(method="first", pct=True)
            score = pd.cut(
                percentile,
                bins=score_bins,
                labels=score_labels,
                include_lowest=True,
            ).astype(int)
            rfm[score_column] = 6 - score if score_column == "R" else score
        # Menjumlahkan skor R, F, dan M; pelanggan dengan skor lebih tinggi berada di peringkat atas.
        rfm["RFM Score"] = rfm[["R", "F", "M"]].sum(axis=1)
        spending_rank = rfm["RFM Score"].rank(method="first", pct=True)
        # Membagi pelanggan menjadi tiga segmen berdasarkan peringkat skor RFM.
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
