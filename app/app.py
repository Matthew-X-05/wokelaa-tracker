import csv
import io
import os
import time
from datetime import date

import mysql.connector
from flask import Flask, Response, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-key")

STATUS = ["Belum dikerjakan", "Sedang dikerjakan", "Selesai"]

# Tabel master (anggota & matkul) dibuat generik supaya kodenya ringkas.
MASTER = {
    "anggota": {"judul": "Anggota", "fields": [("nama", "Nama"), ("nim", "NIM")]},
    "matkul": {"judul": "Mata Kuliah", "fields": [("nama_matkul", "Nama mata kuliah")]},
}


def get_conn():
    for _ in range(30):  # tunggu MySQL siap
        try:
            return mysql.connector.connect(
                host=os.getenv("DB_HOST", "db"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
            )
        except mysql.connector.Error:
            time.sleep(2)
    raise RuntimeError("Tidak bisa terhubung ke database")


def query(sql, params=(), one=False, write=False):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        if write:
            conn.commit()
            return cur.lastrowid
        rows = cur.fetchall()
        if one:
            return rows[0] if rows else None
        return rows
    finally:
        cur.close()
        conn.close()


@app.route("/")
def home():
    return redirect(url_for("tugas_list"))


# ---------- TUGAS ----------
@app.route("/tugas")
def tugas_list():
    status = request.args.get("status", "")
    anggota = request.args.get("anggota", "")
    q = request.args.get("q", "").strip()
    view = request.args.get("view", "board")
    rows = query(
        """SELECT t.*, a.nama AS anggota, a.nim AS nim, m.nama_matkul AS matkul
           FROM tugas t
           JOIN anggota a ON a.id = t.id_anggota
           JOIN matkul m ON m.id = t.id_matkul
           WHERE (%s = '' OR t.status = %s) AND (%s = '' OR t.id_anggota = %s)
             AND t.judul LIKE %s
           ORDER BY t.deadline""",
        (status, status, anggota, anggota, f"%{q}%"),
    )
    ringkasan = {r["status"]: r["c"] for r in query("SELECT status, COUNT(*) AS c FROM tugas GROUP BY status")}
    total = sum(ringkasan.values())
    persen = round(ringkasan.get("Selesai", 0) * 100 / total) if total else 0
    return render_template(
        "tugas_list.html",
        rows=rows, kolom={s: [r for r in rows if r["status"] == s] for s in STATUS},
        status_list=STATUS, ringkasan=ringkasan, total=total, persen=persen,
        anggota_list=query("SELECT * FROM anggota ORDER BY nama"),
        f_status=status, f_anggota=anggota, q=q, view=view, today=date.today(),
    )


@app.route("/tugas/<int:id>/status", methods=["POST"])
def tugas_status(id):
    s = request.form.get("status")
    if s in STATUS:
        query("UPDATE tugas SET status=%s WHERE id=%s", (s, id), write=True)
    return redirect(request.referrer or url_for("tugas_list"))


@app.route("/tugas/export.csv")
def tugas_export():
    rows = query(
        """SELECT t.id, t.judul, m.nama_matkul, a.nama, a.nim, t.deadline, t.status
           FROM tugas t JOIN anggota a ON a.id = t.id_anggota JOIN matkul m ON m.id = t.id_matkul
           ORDER BY t.deadline"""
    )
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ID", "Judul", "Mata kuliah", "Penanggung jawab", "NIM", "Deadline", "Status"])
    for r in rows:
        w.writerow(list(r.values()))
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=tugas.csv"})


@app.route("/tugas/tambah", methods=["GET", "POST"])
@app.route("/tugas/<int:id>/ubah", methods=["GET", "POST"])
def tugas_form(id=None):
    data = query("SELECT * FROM tugas WHERE id = %s", (id,), one=True) if id else None
    if id and not data:
        abort(404)
    if request.method == "POST":
        f = request.form
        vals = (f["judul"].strip(), f["deadline"], f["status"], f["id_anggota"], f["id_matkul"])
        if id:
            query("UPDATE tugas SET judul=%s, deadline=%s, status=%s, id_anggota=%s, id_matkul=%s WHERE id=%s",
                  vals + (id,), write=True)
            flash("Tugas diperbarui.", "ok")
        else:
            query("INSERT INTO tugas (judul, deadline, status, id_anggota, id_matkul) VALUES (%s,%s,%s,%s,%s)",
                  vals, write=True)
            flash("Tugas ditambahkan.", "ok")
        return redirect(url_for("tugas_list"))
    return render_template(
        "tugas_form.html", data=data, status_list=STATUS,
        anggota_list=query("SELECT * FROM anggota ORDER BY nama"),
        matkul_list=query("SELECT * FROM matkul ORDER BY nama_matkul"),
    )


@app.route("/tugas/<int:id>/hapus", methods=["POST"])
def tugas_hapus(id):
    query("DELETE FROM tugas WHERE id = %s", (id,), write=True)
    flash("Tugas dihapus.", "ok")
    return redirect(url_for("tugas_list"))


# ---------- ANGGOTA & MATKUL ----------
def get_master(tabel):
    if tabel not in MASTER:
        abort(404)
    return MASTER[tabel]


@app.route("/master/<tabel>")
def master_list(tabel):
    cfg = get_master(tabel)
    rows = query(f"SELECT * FROM {tabel} ORDER BY id")
    return render_template("master_list.html", tabel=tabel, cfg=cfg, rows=rows)


@app.route("/master/<tabel>/tambah", methods=["GET", "POST"])
@app.route("/master/<tabel>/<int:id>/ubah", methods=["GET", "POST"])
def master_form(tabel, id=None):
    cfg = get_master(tabel)
    cols = [c for c, _ in cfg["fields"]]
    data = query(f"SELECT * FROM {tabel} WHERE id = %s", (id,), one=True) if id else None
    if id and not data:
        abort(404)
    if request.method == "POST":
        vals = tuple(request.form[c].strip() for c in cols)
        try:
            if id:
                sets = ", ".join(f"{c}=%s" for c in cols)
                query(f"UPDATE {tabel} SET {sets} WHERE id=%s", vals + (id,), write=True)
            else:
                ph = ", ".join(["%s"] * len(cols))
                query(f"INSERT INTO {tabel} ({', '.join(cols)}) VALUES ({ph})", vals, write=True)
            flash("Data disimpan.", "ok")
            return redirect(url_for("master_list", tabel=tabel))
        except mysql.connector.Error:
            flash("Data gagal disimpan. NIM mungkin sudah terdaftar.", "err")
    return render_template("master_form.html", tabel=tabel, cfg=cfg, data=data)


@app.route("/master/<tabel>/<int:id>/hapus", methods=["POST"])
def master_hapus(tabel, id):
    get_master(tabel)
    try:
        query(f"DELETE FROM {tabel} WHERE id = %s", (id,), write=True)
        flash("Data dihapus.", "ok")
    except mysql.connector.Error:
        flash("Data tidak bisa dihapus karena masih dipakai oleh tugas.", "err")
    return redirect(url_for("master_list", tabel=tabel))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
