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

Dashboard membaca lima file CSV lokal dari folder `E-Commerce Public Dataset`. Notebook mengambil file yang sama dari [repository dataset di GitHub](https://github.com/faizinnoval/E-Commerce-Public-Dataset), sehingga memerlukan koneksi internet saat memuat data. File `dashboard/main_data.csv` tidak digunakan oleh dashboard.

## Dashboard Online

Buka [Dashboard Analisis E-Commerce](https://em7uns4wrdxbyszda3hzxt.streamlit.app/). Pilih tahun dan rentang tanggal melalui sidebar untuk memperbarui ringkasan, grafik, dan segmentasi. Jika aplikasi sedang tidak aktif, tunggu hingga Streamlit selesai memulainya kembali.

## Menjalankan Dashboard Secara Lokal

Pastikan Python sudah terpasang dan semua file dataset berada di lokasi seperti pada struktur proyek di atas. Jalankan perintah berikut di PowerShell dari folder utama proyek:

```powershell
py -m venv .venv
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

- Memfilter data berdasarkan tahun (semua tahun, 2016, 2017, atau 2018) dan rentang tanggal.
- Menampilkan total pembayaran, jumlah pesanan, pelanggan unik, dan produk berbeda pada periode terpilih.
- Menggambarkan tren total pembayaran per bulan.
- Menampilkan 10 kategori teratas berdasarkan jumlah harga item.
- Menampilkan jumlah pelanggan per segmen RFM, ringkasan segmen, dan skor RFM setiap pelanggan.

Pilih **Semua tahun** dan rentang tanggal penuh untuk melihat seluruh periode yang tersedia.

## Definisi dan Perhitungan

- **Total pembayaran**: jumlah `payment_value`, setelah seluruh baris pembayaran dijumlahkan per `order_id`.
- **Jumlah pesanan**: jumlah `order_id` unik pada periode terpilih.
- **Pelanggan unik**: jumlah `customer_unique_id` unik pada pesanan terpilih.
- **Produk berbeda**: jumlah `product_id` unik pada item dari pesanan terpilih.
- **Kategori teratas**: kategori diurutkan berdasarkan jumlah `price` pada setiap item. Nilai ini adalah total harga item, bukan total pembayaran pesanan.
- **Recency**: jumlah hari antara tanggal pesanan terakhir seorang pelanggan dan tanggal pesanan terakhir dalam periode terpilih. Skor lebih tinggi diberikan untuk Recency yang lebih rendah.
- **Frequency**: jumlah `order_id` unik milik pelanggan dalam periode terpilih.
- **Monetary**: total `payment_value` pelanggan dalam periode terpilih.
- Skor setiap komponen RFM dibagi ke lima kelompok berdasarkan peringkat persentil pada data terpilih. Skor Recency dibalik agar nilai lebih rendah mendapat skor lebih tinggi; skor Frequency dan Monetary tidak dibalik. Skor R, F, dan M dijumlahkan, lalu peringkat skor gabungan dibagi menjadi **Low Value** (25% terbawah), **Medium Value** (bagian tengah), dan **High Value** (25% teratas).
- Nilai transaksi ditampilkan dalam real Brasil (`R$`), mengikuti satuan pada dataset.

Karena penghitungan RFM dan grafik mengikuti periode yang dipilih, hasil segmentasi dapat berubah saat filter tanggal atau tahun diubah.

## Membaca Hasil

Gunakan grafik tren untuk membandingkan pembayaran antarbulan dan grafik kategori untuk menemukan kategori dengan total harga item tertinggi. Pada ringkasan RFM, bandingkan jumlah pelanggan serta total pembayaran tiap segmen. Hasil ini dapat menjadi masukan untuk analisis lanjutan, tetapi tidak dengan sendirinya membuktikan penyebab perubahan pembayaran atau perilaku pelanggan.
