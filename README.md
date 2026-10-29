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

- Memfilter data berdasarkan tahun 2016, 2017, atau 2018, lalu memilih rentang tanggal di dalam tahun tersebut. Jika belum memilih tahun, rentang tanggal mencakup seluruh data.
- Menampilkan jumlah pelanggan, rata-rata Recency, rata-rata Frequency, dan total Monetary untuk periode terpilih.
- Menampilkan grafik jumlah pelanggan dan total Monetary untuk setiap segmen RFM.
- Menampilkan tabel ringkasan per segmen yang berisi jumlah pelanggan serta rata-rata Recency, Frequency, dan Monetary.

Dashboard saat ini berfokus pada segmentasi RFM; dashboard tidak menampilkan grafik tren pembayaran bulanan atau peringkat kategori produk.

## Definisi dan Perhitungan

- **Pelanggan**: dihitung dari jumlah `customer_id` unik pada data yang sudah difilter.
- **Recency**: jumlah hari antara tanggal pembelian terakhir pelanggan dan satu hari setelah tanggal pembelian terakhir pada seluruh data terpilih. Semakin kecil nilainya, semakin baru pembelian pelanggan.
- **Frequency**: jumlah baris data pelanggan dalam periode terpilih. Ini bukan jumlah `order_id` unik; karena itu jangan menafsirkan nilainya sebagai jumlah pesanan.
- **Monetary**: jumlah `price` pada baris data pelanggan dalam periode terpilih. Nilai ini menjumlahkan harga item, bukan `payment_value` atau total pembayaran.
- **Skor RFM**: setiap komponen diberi skor 1–5 menggunakan pembagian kuantil atas peringkat nilai komponen. Skor Recency dibalik (Recency lebih rendah mendapat skor lebih tinggi), sedangkan Frequency dan Monetary tidak dibalik. Ketika ada nilai yang sama, peringkat berurutan digunakan agar pembagian skor tetap terbentuk.
- **Segmen pelanggan**: jumlah skor R, F, dan M menghasilkan skor 3–15. Skor 11–15 masuk **High Value**, skor 7–10 **Medium Value**, dan skor di bawah 7 **Low Value**.
- Dashboard memformat nilai uang sebagai `Rp`, tetapi nilai pada dataset sumber menggunakan real Brasil (BRL). Label mata uang pada dashboard tidak mengonversi nilai tersebut.

Penghitungan mengikuti rentang data yang dipilih, sehingga metrik, skor, dan segmen dapat berubah saat filter tahun atau tanggal diubah.

## Membaca Hasil

Mulailah dengan memilih tahun dan rentang tanggal yang ingin dianalisis. Gunakan grafik jumlah pelanggan untuk melihat sebaran pelanggan antarsegmen, lalu bandingkan grafik dan tabel Monetary untuk melihat kontribusi jumlah harga item pada tiap segmen. Rata-rata Recency dan Frequency membantu memberi konteks pada perilaku pembelian pelanggan dalam periode tersebut.

Segmen dibentuk dari skor gabungan relatif terhadap data yang sedang difilter, bukan batas nilai bisnis yang tetap. Karena Frequency menghitung baris data dan Monetary menjumlahkan `price`, keduanya bukan ukuran langsung jumlah pesanan atau total pembayaran. Dashboard ini juga tidak menyediakan tren pembayaran bulanan maupun peringkat kategori produk; gunakan notebook analisis untuk pertanyaan tersebut. Hasil segmentasi bersifat deskriptif dan tidak dengan sendirinya menjelaskan penyebab perilaku pelanggan.
