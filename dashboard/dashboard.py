from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Set konfigurasi halaman Streamlit
st.set_page_config(
    page_title="E-Commerce Data Analysis Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Function untuk memuat data
@st.cache_data
def load_data():
    # Mengambil jalur folder tempat dashboard.py berada
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "main_data.csv")
    
    df = pd.read_csv(file_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
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

# Header Dashboard
st.title("🛒 E-Commerce Data Analysis Dashboard")
st.markdown(f"**Periode Data:** {start_date} s/d {end_date}")

st.markdown("---")

# ==========================================
# 1. PERHITUNGAN & SEGMENTASI RFM GABUNGAN
# ==========================================
recent_date = filtered_df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

rfm_df = filtered_df.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (recent_date - x.max()).days,
    'order_id': 'count',
    'price': 'sum'
}).reset_index()

rfm_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']

# Skor 1-5 menggunakan rank(method='first') agar terdistribusi merata
rfm_df['r_score'] = pd.qcut(rfm_df['recency'].rank(method='first'), q=5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm_df['f_score'] = pd.qcut(rfm_df['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm_df['m_score'] = pd.qcut(rfm_df['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

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

# ==========================================
# METRICS UTAMA (METRIC CARDS)
# ==========================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Pelanggan", f"{rfm_df['customer_id'].nunique():,}")
with col2:
    st.metric("Rata-rata Recency", f"{rfm_df['recency'].mean():.1f} Hari")
with col3:
    st.metric("Rata-rata Frequency", f"{rfm_df['frequency'].mean():.2f} Transaksi")
with col4:
    st.metric("Total Revenue", f"Rp {rfm_df['monetary'].sum():,.2f}")

st.markdown("---")

# ==========================================
# 2. GRAFIK SEGMENTASI & KONTRIBUSI REVENUE
# ==========================================
st.subheader("👥 Segmentasi Pelanggan berdasarkan Analisis RFM")

rfm_summary = rfm_df.groupby('customer_segment').agg(
    jumlah_pelanggan=('customer_id', 'count'),
    avg_recency=('recency', 'mean'),
    avg_frequency=('frequency', 'mean'),
    total_monetary=('monetary', 'sum'),
    avg_monetary=('monetary', 'mean')
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

with col_right:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        x='customer_segment', 
        y='total_monetary', 
        data=rfm_summary, 
        palette='Greens_r',
        hue='customer_segment',
        legend=False,
        ax=ax
    )
    ax.set_title("Total Revenue (Monetary) per Segmen Pelanggan", fontsize=14)
    ax.set_xlabel("Segmen Pelanggan", fontsize=11)
    ax.set_ylabel("Total Revenue (Rp)", fontsize=11)
    st.pyplot(fig)

# ==========================================
# 3. TABEL RINGKASAN RFM
# ==========================================
st.subheader("📊 Tabel Ringkasan Metrik RFM per Segmen")

# Rename kolom agar rapi dibaca di dashboard
tabel_tampil = rfm_summary.rename(columns={
    'customer_segment': 'Segmen Pelanggan',
    'jumlah_pelanggan': 'Jumlah Pelanggan',
    'avg_recency': 'Rata-rata Recency (Hari)',
    'avg_frequency': 'Rata-rata Frequency',
    'total_monetary': 'Total Monetary (Rp)',
    'avg_monetary': 'Rata-rata Monetary (Rp)'
})

st.dataframe(
    tabel_tampil.style.format({
        'Jumlah Pelanggan': '{:,}',
        'Rata-rata Recency (Hari)': '{:.1f}',
        'Rata-rata Frequency': '{:.2f}',
        'Total Monetary (Rp)': 'Rp {:,.2f}',
        'Rata-rata Monetary (Rp)': 'Rp {:,.2f}'
    }),
    use_container_width=True
)

st.caption("Dashboard Analisis Data E-Commerce — Proyek Akhir Dicoding")