# Analisis Data E-Commerce

Proyek ini menganalisis data transaksi e-commerce dan menyediakan dashboard interaktif untuk melihat ringkasan pembayaran, tren bulanan, kategori produk, serta segmentasi pelanggan menggunakan metode RFM.

## Pertanyaan Bisnis

1. Bagaimana tren total nilai pembayaran per bulan selama periode 2016–2018, serta kategori produk apa yang memberikan kontribusi pendapatan tertinggi dalam periode tersebut?
2. Bagaimana segmentasi pelanggan berdasarkan **Recency, Frequency, dan Monetary ** selama periode 2016–2018, serta bagaimana hubungan masing-masing segmen terhadap total pendapatan?

## Fitur Dashboard

- Filter data berdasarkan tahun (semua tahun, 2016, 2017, atau 2018) dan rentang tanggal.
- Ringkasan jumlah pembayaran, pesanan, pelanggan unik, dan produk berbeda.
- Grafik tren total pembayaran per bulan.
- Grafik 10 kategori produk dengan total harga item tertinggi.
- Segmentasi pelanggan berdasarkan skor RFM:
  - **Recency**: jumlah hari sejak pesanan terakhir pada periode yang dipilih.
  - **Frequency**: jumlah pesanan unik pelanggan.
  - **Monetary**: total nilai pembayaran pelanggan.
- Tabel ringkasan segmen dan skor RFM per pelanggan.

Analisis akan mengikuti filter tahun dan tanggal yang dipilih. Pilih **Semua tahun** dan rentang tanggal penuh untuk melihat keseluruhan periode 2016–2018.

## Struktur Proyek

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
└── README.md
```

Dashboard membaca file CSV dari folder `E-Commerce Public Dataset` secara langsung. `dashboard/main_data.csv` tidak dibutuhkan untuk menjalankan dashboard ini.

## Membuka Dashboard Online

Dashboard sudah tersedia di Streamlit Community Cloud:

**[Buka Dashboard Analisis E-Commerce](https://em7uns4wrdxbyszda3hzxt.streamlit.app/)**

Cara menggunakannya:

1. Buka tautan dashboard di browser.
2. Jika aplikasi sedang tidak aktif, tunggu proses aplikasi dimulai kembali.
3. Gunakan pilihan tahun dan rentang tanggal di sidebar untuk memfilter data.
4. Lihat ringkasan pembayaran, tren bulanan, kategori produk, dan segmentasi pelanggan pada halaman dashboard.

Untuk membuka dashboard online, tidak perlu menginstal Python atau mengunduh dataset.

## Persiapan

Pastikan Python sudah terpasang, lalu jalankan perintah berikut dari folder utama proyek.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Jika PowerShell tidak mengizinkan aktivasi environment, jalankan perintah instalasi dengan interpreter dari `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Menjalankan Dashboard

Dari folder utama proyek, jalankan:

```powershell
streamlit run dashboard/dashboard.py
```

Jika perintah `streamlit` tidak dikenali, gunakan:

```powershell
python -m streamlit run dashboard/dashboard.py
```

Streamlit akan membuka dashboard di browser. Pastikan folder dan nama file dataset tetap sama agar dashboard dapat menemukan data.

## Catatan Perhitungan

- Total pembayaran diambil dari `payment_value` dan dijumlahkan per `order_id` sebelum digunakan untuk analisis.
- Jumlah pesanan dihitung sebagai jumlah `order_id` unik.
- Produk berbeda dihitung berdasarkan jumlah `product_id` unik; grafik kategori menjumlahkan `price` pada setiap item.
- Perhitungan RFM menggunakan `customer_unique_id` untuk mengidentifikasi pelanggan. Skor tiap komponen dibagi ke dalam lima kelompok berdasarkan peringkat persentil pada data hasil filter, kemudian skor Recency dibalik agar nilai lebih tinggi berarti lebih baik.
- Nilai transaksi pada dataset ditampilkan sebagai `R$`.

## Kesimpulan

- Tren pembayaran bulanan dapat berubah-ubah sepanjang 2016–2018. Grafik dashboard membantu menemukan bulan dengan pembayaran tertinggi atau terendah pada periode yang dipilih.
- Kategori dengan total harga item terbesar menjadi kategori dengan kontribusi nilai item tertinggi pada grafik. Nilainya menggunakan jumlah harga item (`price`), bukan `payment_value`, supaya pembayaran satu pesanan tidak dihitung berulang untuk setiap item dalam pesanan tersebut.
- Segmentasi RFM membedakan pelanggan menurut kebaruan transaksi, frekuensi pesanan, dan nilai pembayaran. Tabel ringkasan menampilkan jumlah pelanggan dan total pembayaran untuk setiap segmen; total pembayaran segmen dapat digunakan untuk membandingkan kontribusi pendapatan masing-masing kelompok.
- Segmen **High Value** dapat menjadi prioritas program retensi, sedangkan segmen **Low Value** dapat ditargetkan dengan kampanye re-engagement. Evaluasi jumlah pelanggan serta total pembayaran pada tabel dashboard sebelum menentukan prioritas kampanye.
