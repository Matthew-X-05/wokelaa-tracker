SET NAMES utf8mb4;

CREATE TABLE anggota (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(100) NOT NULL,
  nim VARCHAR(20) NOT NULL UNIQUE
) CHARACTER SET utf8mb4;

CREATE TABLE matkul (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nama_matkul VARCHAR(100) NOT NULL
) CHARACTER SET utf8mb4;

CREATE TABLE tugas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  judul VARCHAR(150) NOT NULL,
  deadline DATE NOT NULL,
  status ENUM('Belum dikerjakan','Sedang dikerjakan','Selesai') NOT NULL DEFAULT 'Belum dikerjakan',
  id_anggota INT NOT NULL,
  id_matkul INT NOT NULL,
  dibuat_pada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_anggota) REFERENCES anggota(id),
  FOREIGN KEY (id_matkul) REFERENCES matkul(id)
) CHARACTER SET utf8mb4;

INSERT INTO anggota (nama, nim) VALUES
('Oktapianus Zalukhu','231111267'),
('Afni Titus Simanjuntak','231111841'),
('Matthew Rivandy','231111820');

INSERT INTO matkul (nama_matkul) VALUES
('Komputasi Awan'),('Kriptografi'),('Penulisan Ilmiah');

INSERT INTO tugas (judul, deadline, status, id_anggota, id_matkul) VALUES
('Tugas Kelompok-1 MID (Docker)','2026-10-10','Sedang dikerjakan',1,1),
('Makalah enkripsi AES','2026-10-15','Belum dikerjakan',2,2),
('Draf proposal skripsi','2026-10-20','Belum dikerjakan',3,3),
('Laporan praktikum 3','2026-10-02','Selesai',2,1);
