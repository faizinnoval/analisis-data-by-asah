# Analisis Data E-Commerce

Proyek ini mengeksplorasi data transaksi e-commerce untuk melihat tren pembayaran, kategori produk dengan nilai item tertinggi, dan karakteristik pelanggan. Hasil analisis tersedia dalam notebook dan dashboard interaktif berbasis Streamlit.

## Pertanyaan Bisnis

1. Bagaimana tren total pembayaran per bulan selama 2016–2018, dan kategori produk apa yang memiliki total harga item tertinggi?
2. Bagaimana pelanggan tersegmentasi berdasarkan **Recency**, **Frequency**, dan **Monetary (RFM)**, serta berapa jumlah pelanggan dan total pembayaran pada setiap segmen?

## Isi Proyek

- [`Proyek_Analisis_Data.ipynb`](./Proyek_Analisis_Data.ipynb): notebook eksplorasi dan analisis data.
- [`dashboard/dashboard.py`](./dashboard/dashboard.py): aplikasi dashboard interaktif.
- [`E-Commerce Public Dataset/`](./E-Commerce%20Public%20Dataset/): file CSV lokal yang dibaca dashboard.
- [`requirements.txt`](./requirements.txt): daftar dependensi Python.

Struktur file utama:

```text
.
├── E-Commerce Public Dataset/
│   ├── customers_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── orders_dataset.csv
│   └── products_dataset.csv
├── dashboard/
│   ├── dashboard.py
│   └── main_data.csv
├── Proyek_Analisis_Data.ipynb
├── requirements.txt
├── README.md
└── url.txt
```

Dashboard membaca data gabungan dari `dashboard/main_data.csv`. Notebook mengambil file sumber dari [repository dataset di GitHub](https://github.com/faizinnoval/E-Commerce-Public-Dataset), sehingga memerlukan koneksi internet saat memuat data. Lima CSV di folder `E-Commerce Public Dataset` merupakan data sumber lokal dan tidak dibaca langsung oleh dashboard.

## Dashboard Online

Buka [Dashboard Analisis E-Commerce](https://em7uns4wrdxbyszda3hzxt.streamlit.app/). Pilih tahun dan rentang tanggal melalui sidebar untuk memperbarui ringkasan, grafik, dan segmentasi. Jika aplikasi sedang tidak aktif, tunggu hingga Streamlit selesai memulainya kembali.

## Menjalankan Dashboard Secara Lokal

Pastikan Python sudah terpasang dan file `dashboard/main_data.csv` tersedia. Jalankan perintah berikut di PowerShell dari folder utama proyek:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run dashboard/dashboard.py
```

Streamlit akan menampilkan alamat lokal dashboard di terminal dan biasanya membuka halaman tersebut di browser. Jika aktivasi virtual environment tidak tersedia atau diblokir, jalankan instalasi dan dashboard menggunakan interpreter di `.venv` secara langsung:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run dashboard/dashboard.py
```

## Fitur Dashboard

- Memfilter data berdasarkan tahun 2016, 2017, atau 2018, lalu memilih rentang tanggal. Jika belum memilih tahun, seluruh periode data digunakan.
- Menampilkan total pelanggan, rata-rata Recency dan Frequency, serta total pembayaran pada periode terpilih.
- Menampilkan tren pembayaran per bulan dan lima kategori dengan total harga item tertinggi.
- Mengelompokkan pelanggan ke segmen RFM, lalu membandingkan jumlah pelanggan dan total pembayaran untuk setiap segmen.
- Menampilkan tabel ringkasan segmen yang mencakup jumlah pelanggan, rata-rata Recency dan Frequency, Monetary berbasis harga item, serta total pembayaran.
- Menampilkan pesan yang jelas jika rentang tanggal yang dipilih tidak memiliki data.

## Definisi dan Perhitungan

- **Pelanggan**: jumlah `customer_id` unik pada data yang sudah difilter.
- **Recency**: jumlah hari antara tanggal pembelian terakhir pelanggan dalam periode terpilih dan satu hari setelah tanggal pembelian terakhir dalam periode tersebut. Semakin kecil nilainya, semakin baru pembelian pelanggan.
- **Frequency**: jumlah `order_id` unik pelanggan dalam periode terpilih.
- **Monetary RFM**: jumlah `price` untuk setiap item pesanan unik pelanggan. Nilai ini menjumlahkan harga item, bukan `payment_value`.
- **Total pembayaran**: jumlah `payment_value` unik berdasarkan kombinasi `order_id` dan `payment_sequential`. Deduplikasi ini mencegah nilai pembayaran berulang akibat bentuk data gabungan pada `main_data.csv`.
- **Kategori produk**: peringkat dihitung dari jumlah `price` item pesanan unik, bukan dari pembayaran order yang dapat mencakup beberapa kategori.
- **Tren bulanan**: menjumlahkan pembayaran unik berdasarkan bulan pembelian.
- **Skor RFM**: setiap komponen diberi skor 1–5 berdasarkan peringkat pelanggan. Skor Recency dibalik (Recency lebih rendah mendapat skor lebih tinggi), sedangkan Frequency dan Monetary tidak dibalik. Peringkat berurutan digunakan ketika nilai sama dan tetap dapat menghasilkan skor pada sampel kecil.
- **Segmen pelanggan**: jumlah skor R, F, dan M menghasilkan skor 3–15. Skor 11–15 masuk **High Value**, skor 7–10 **Medium Value**, dan skor di bawah 7 **Low Value**.
- Nilai uang pada dataset sumber menggunakan real Brasil (BRL); label `R$` pada dashboard hanya menampilkan mata uang sumber dan tidak mengonversi nilainya.

## Membaca Hasil

Mulailah dengan memilih tahun dan rentang tanggal yang ingin dianalisis. Grafik tren menunjukkan perubahan total pembayaran bulanan, sedangkan grafik kategori membandingkan total harga item pada lima kategori teratas. Untuk segmentasi, gunakan grafik jumlah pelanggan dan pembayaran per segmen; tabel juga membedakan Monetary berbasis harga item dari total pembayaran.

Segmen dibentuk dari skor gabungan relatif terhadap data yang sedang difilter, bukan batas nilai bisnis yang tetap. Hasil segmentasi bersifat deskriptif dan tidak dengan sendirinya menjelaskan penyebab perilaku pelanggan.
