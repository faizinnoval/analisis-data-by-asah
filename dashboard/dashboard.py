import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set konfigurasi halaman Streamlit
st.set_page_config(
    page_title="E-Commerce Data Analysis Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Function untuk memuat data
# The cached DataFrame is only read below; resource caching avoids serializing it.
@st.cache_resource
def load_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "main_data.csv")

    required_columns = {
        "order_id",
        "customer_id",
        "order_purchase_timestamp",
        "order_item_id",
        "price",
        "product_category_name",
        "payment_sequential",
        "payment_value",
    }
    df = pd.read_csv(
        file_path,
        usecols=lambda column: column in required_columns,
    )
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            "Kolom yang diperlukan tidak tersedia di dashboard/main_data.csv: "
            + ", ".join(sorted(missing_columns))
        )

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"], errors="coerce"
    )
    df = df.dropna(subset=["order_purchase_timestamp"])
    return df


main_df = load_data()

# Sidebar - Filter Rentang Tanggal
st.sidebar.header("Filter Data")
st.sidebar.caption("Pilih tahun")
years = [2016, 2017, 2018]
if "selected_year" not in st.session_state:
    st.session_state.selected_year = None

year_columns = st.sidebar.columns(len(years))
for year, column in zip(years, year_columns):
    if column.button(
        str(year),
        key=f"year_{year}",
        type="primary" if st.session_state.selected_year == year else "secondary"
    ):
        st.session_state.selected_year = year

if st.session_state.selected_year is None:
    date_df = main_df
else:
    date_df = main_df[
        main_df['order_purchase_timestamp'].dt.year == st.session_state.selected_year
    ]

min_date = date_df['order_purchase_timestamp'].min().date()
max_date = date_df['order_purchase_timestamp'].max().date()

start_date, end_date = st.sidebar.date_input(
    label='Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date],
    key=f"date_range_{st.session_state.selected_year or 'all'}"
)

# Filter Dataset berdasarkan tanggal yang dipilih
filtered_df = date_df[
    (date_df['order_purchase_timestamp'].dt.date >= start_date) & 
    (date_df['order_purchase_timestamp'].dt.date <= end_date)
]

if filtered_df.empty:
    st.warning("Tidak ada data pada rentang tanggal yang dipilih.")
    st.stop()

# main_data.csv menggabungkan item dan pembayaran; deduplikasi mencegah
# penghitungan berulang ketika satu order memiliki beberapa pembayaran.
filtered_items = filtered_df[
    [
        "order_id",
        "customer_id",
        "order_purchase_timestamp",
        "order_item_id",
        "price",
        "product_category_name",
    ]
].drop_duplicates(
    subset=["order_id", "order_item_id"]
)
filtered_payments = filtered_df[
    [
        "order_id",
        "customer_id",
        "order_purchase_timestamp",
        "payment_sequential",
        "payment_value",
    ]
].drop_duplicates(
    subset=["order_id", "payment_sequential"]
)

# Header Dashboard
st.title("🛒 E-Commerce Data Analysis Dashboard")
st.markdown(f"**Periode Data:** {start_date} s/d {end_date}")

st.markdown("---")

# METRICS UTAMA (METRIC CARDS)
recent_date = filtered_items['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

rfm_df = filtered_items.groupby("customer_id").agg(
    last_purchase=("order_purchase_timestamp", "max"),
    frequency=("order_id", "nunique"),
    monetary=("price", "sum"),
).reset_index()

rfm_df["recency"] = (recent_date - rfm_df["last_purchase"]).dt.days
rfm_df = rfm_df.drop(columns="last_purchase")
payment_by_customer = filtered_payments.groupby("customer_id")["payment_value"].sum()
rfm_df["payment_value"] = rfm_df["customer_id"].map(payment_by_customer).fillna(0)
total_payments = filtered_payments["payment_value"].sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Pelanggan", f"{rfm_df['customer_id'].nunique():,}")
with col2:
    st.metric("Rata-rata Recency", f"{rfm_df['recency'].mean():.1f} Hari")
with col3:
    st.metric("Rata-rata Frequency", f"{rfm_df['frequency'].mean():.2f} Pesanan")
with col4:
    st.metric("Total Pembayaran", f"R$ {total_payments:,.2f}")

st.markdown("---")

# 1. PERTANYAAN 1: TREN PENDAPATAN & KATEGORI PRODUK
st.header("📈 Pertanyaan 1: Tren Pendapatan & Performa Kategori Produk")

col_trend, col_cat = st.columns(2)

with col_trend:
    monthly_revenue = (
        filtered_payments.assign(
            order_month=filtered_payments["order_purchase_timestamp"]
            .dt.to_period("M")
            .astype(str)
        )
        .groupby("order_month")["payment_value"]
        .sum()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(
        data=monthly_revenue,
        x="order_month",
        y="payment_value",
        marker="o",
        color="#1f77b4",
        ax=ax
    )
    ax.set_title("Tren Pendapatan Bulanan", fontsize=14)
    ax.set_xlabel("Bulan", fontsize=11)
    ax.set_ylabel("Total Pembayaran (R$)", fontsize=11)
    ax.tick_params(axis="x", labelrotation=45)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_cat:
    category_revenue = (
        filtered_items.groupby(
            filtered_items["product_category_name"].fillna(
                "Kategori tidak diketahui"
            )
        )["price"]
        .sum()
        .rename_axis("product_category_name")
        .reset_index(name="price")
    )
    top_categories = category_revenue.sort_values(
        by="price", ascending=False
    ).head(5)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=top_categories,
        x="price",
        y="product_category_name",
        palette="Blues_r",
        hue="product_category_name",
        legend=False,
        ax=ax
    )
    ax.set_title("Top 5 Kategori Berdasarkan Total Harga Item", fontsize=14)
    ax.set_xlabel("Total Harga Item (R$)", fontsize=11)
    ax.set_ylabel("Kategori Produk", fontsize=11)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.markdown("---")

# 2. PERTANYAAN 2: SEGMENTASI RFM & REVENUE
st.header("👥 Pertanyaan 2: Segmentasi Pelanggan Berdasarkan Analisis RFM")

# Skor 1-5 berdasarkan peringkat agar tetap dapat dihitung pada sampel kecil.
rfm_df["r_score"] = 6 - np.ceil(rfm_df["recency"].rank(method="first", pct=True) * 5)
rfm_df["f_score"] = np.ceil(rfm_df["frequency"].rank(method="first", pct=True) * 5)
rfm_df["m_score"] = np.ceil(rfm_df["monetary"].rank(method="first", pct=True) * 5)

rfm_df['rfm_score'] = rfm_df['r_score'] + rfm_df['f_score'] + rfm_df['m_score']

# Segmentasi Pelanggan
def segment_customer(score):
    if score >= 11:
        return 'High Value'
    elif score >= 7:
        return 'Medium Value'
    else:
        return 'Low Value'

rfm_df['customer_segment'] = rfm_df['rfm_score'].apply(segment_customer)

rfm_summary = rfm_df.groupby('customer_segment').agg(
    jumlah_pelanggan=('customer_id', 'count'),
    avg_recency=('recency', 'mean'),
    avg_frequency=('frequency', 'mean'),
    total_monetary=('monetary', 'sum'),
    avg_monetary=('monetary', 'mean'),
    total_payment_value=('payment_value', 'sum')
).reset_index()

# Urutkan segmen
segment_order = ['High Value', 'Medium Value', 'Low Value']
rfm_summary['customer_segment'] = pd.Categorical(rfm_summary['customer_segment'], categories=segment_order, ordered=True)
rfm_summary = rfm_summary.sort_values('customer_segment')

col_left, col_right = st.columns(2)

with col_left:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        x='customer_segment', 
        y='jumlah_pelanggan', 
        data=rfm_summary, 
        palette='Blues_r',
        hue='customer_segment',
        legend=False,
        ax=ax
    )
    ax.set_title("Jumlah Pelanggan per Segmen RFM", fontsize=14)
    ax.set_xlabel("Segmen Pelanggan", fontsize=11)
    ax.set_ylabel("Jumlah Pelanggan", fontsize=11)
    st.pyplot(fig)
    plt.close(fig)

with col_right:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        x='customer_segment', 
        y='total_payment_value',
        data=rfm_summary, 
        palette='Greens_r',
        hue='customer_segment',
        legend=False,
        ax=ax
    )
    ax.set_title("Total Pembayaran per Segmen Pelanggan", fontsize=14)
    ax.set_xlabel("Segmen Pelanggan", fontsize=11)
    ax.set_ylabel("Total Pembayaran (R$)", fontsize=11)
    st.pyplot(fig)
    plt.close(fig)

# 3. TABEL RINGKASAN RFM
st.subheader("📊 Tabel Ringkasan Metrik RFM per Segmen")

tabel_tampil = rfm_summary.rename(columns={
    'customer_segment': 'Segmen Pelanggan',
    'jumlah_pelanggan': 'Jumlah Pelanggan',
    'avg_recency': 'Rata-rata Recency (Hari)',
    'avg_frequency': 'Rata-rata Frequency (Pesanan)',
    'total_monetary': 'Total Monetary (Harga Item, R$)',
    'avg_monetary': 'Rata-rata Monetary (Harga Item, R$)',
    'total_payment_value': 'Total Pembayaran (R$)'
})

st.dataframe(
    tabel_tampil.style.format({
        'Jumlah Pelanggan': '{:,}',
        'Rata-rata Recency (Hari)': '{:.1f}',
        'Rata-rata Frequency (Pesanan)': '{:.2f}',
        'Total Monetary (Harga Item, R$)': 'R$ {:,.2f}',
        'Rata-rata Monetary (Harga Item, R$)': 'R$ {:,.2f}',
        'Total Pembayaran (R$)': 'R$ {:,.2f}'
    }),
    use_container_width=True
)

st.caption(
    "Pembayaran dihitung satu kali per urutan pembayaran; harga item dihitung "
    "satu kali per item pesanan. Nilai mata uang sumber adalah real Brasil (BRL)."
)