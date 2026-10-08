# Tracker Tugas & Deadline Kelompok (Tim Wokelaa)

Aplikasi web CRUD (Flask + MySQL) yang berjalan di Docker dengan 3 container:
`app` (Flask), `db` (MySQL 8) dan `phpmyadmin`.

## Menjalankan
1. Install Docker Desktop (atau Docker Engine + Compose).
2. Di folder ini jalankan:
   ```
   docker compose up -d --build
   ```
3. Buka:
   - Aplikasi: http://localhost:5000
   - phpMyAdmin: http://localhost:8080 (user dan password sama dengan isi `.env`)

## Perintah berguna
```
docker compose ps            # lihat status container
docker compose logs -f app   # lihat log aplikasi
docker compose down          # hentikan container (data tetap ada di volume)
docker compose down -v       # hentikan dan hapus data database
```

## Struktur
```
docker-compose.yml   # orkestrasi 3 container, network, volume, healthcheck
.env                 # kredensial (jangan di-commit ke GitHub)
db/init.sql          # skema tabel + data contoh
app/                 # kode Flask, Dockerfile, templates
```

## Tabel
- `anggota` (id, nama, nim)
- `matkul` (id, nama_matkul)
- `tugas` (id, judul, deadline, status, id_anggota, id_matkul, dibuat_pada)
