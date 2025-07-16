Tentu, ini adalah proyek yang menarik dan sangat relevan! Mengembangkan model AI untuk Anti-Money Laundering (AML) melibatkan beberapa tahapan, dari persiapan data hingga implementasi model dan penyajian hasil.

Kita akan membahasnya dalam tiga bagian utama sesuai permintaan Anda:

    Pembuatan Data Training Simulasi (CSV): Kita akan membuat dataset sederhana dengan 10 variabel penting.

    Pembuatan Model AI (Algoritma Populer): Kita akan menggunakan algoritma Isolation Forest, yang sangat populer untuk deteksi anomali (termasuk fraud dan money laundering) karena kemampuannya dalam mengidentifikasi outlier secara efisien tanpa memerlukan label anomali yang banyak.

    Simulasi Prediksi dengan Input JSON: Membuat script yang menerima input JSON transaksi, menggunakan model AI untuk prediksi probabilitas money laundering, dan mengembalikan respons dalam format JSON dengan penjelasan.

1. Membuat Data Training Simulasi (CSV)

Untuk tujuan demonstrasi, kita akan membuat data sintetis. Dalam skenario AML nyata, data akan jauh lebih kompleks dan bervariasi. Variabel-variabel yang umum digunakan dalam deteksi money laundering meliputi:

    transaction_id: ID unik transaksi

    sender_account_type: Tipe akun pengirim (misal: "Personal", "Business")

    receiver_account_type: Tipe akun penerima (misal: "Personal", "Business")

    transaction_amount_usd: Jumlah transaksi dalam Rupiah

    transaction_frequency_30d: Frekuensi transaksi dalam 30 hari terakhir oleh pengirim

    avg_daily_balance_30d: Rata-rata saldo harian dalam 30 hari terakhir

    is_international: Apakah transaksi internasional (0/1)

    transaction_hour: Jam terjadinya transaksi (0-23)

    ip_country_match: Apakah negara IP cocok dengan negara akun (0/1)

    num_flagged_transactions_sender_90d: Jumlah transaksi yang pernah ditandai oleh pengirim dalam 90 hari terakhirs