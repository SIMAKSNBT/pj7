from browser import document, html, window
from datetime import datetime

# 1. State / Data Awal Aplikasi
data = {
    "saldo_jajan": 0,
    "saldo_tabungan": 0,
    "saldo_darurat": 0,
    "target_nama": "Sepeda Baru",
    "target_harga": 150000,
    "target_terkumpul": 0,
    "target_ikon": "🚲"
}

# Fungsi Helper format rupiah
def format_rp(angka):
    return f"Rp {int(angka):,}".replace(",", ".")

# Fungsi Sinkronisasi Data ke Tampilan (UI)
def update_ui():
    document["saldo-jajan"].text = format_rp(data["saldo_jajan"])
    document["saldo-tabungan"].text = format_rp(data["saldo_tabungan"])
    document["saldo-darurat"].text = format_rp(data["saldo_darurat"])
    
    # Update data target impian
    document["target-nama"].text = data["target_nama"]
    document["target-ikon"].text = data["target_ikon"]
    document["target-rasio"].text = f"{format_rp(data['target_terkumpul'])} / {format_rp(data['target_harga'])}"
    
    # Hitung progress bar persen
    if data["target_harga"] > 0:
        persen = (data["target_terkumpul"] / data["target_harga"]) * 100
        persen = min(persen, 100) # Maksimal 100%
    else:
        persen = 0
    
    document["target-progress"].style.width = f"{persen}%"

# Fungsi Menambah Baris Riwayat Transaksi baru
def tambah_riwayat(kegiatan, kategori, jumlah, tipe="masuk"):
    if "empty-row" in document:
        del document["empty-row"]

    waktu_sekarang = datetime.now().strftime("%H:%M:%S")
    warna_jumlah = "text-emerald-600" if tipe == "masuk" else "text-rose-600"
    tanda = "+" if tipe == "masuk" else "-"

    baris = html.TR(border_b=True)
    baris <= html.TD(waktu_sekarang, Class="p-3 text-slate-400 text-xs")
    baris <= html.TD(kegiatan, Class="p-3 font-semibold")
    baris <= html.TD(kategori, Class="p-3 text-xs text-slate-500")
    baris <= html.TD(f"{tanda} {format_rp(abs(jumlah))}", Class=f"p-3 text-right font-bold {warna_jumlah}")

    # Masukkan ke baris paling atas tabel
    document["tabel-riwayat"].insert(0, baris)

# 2. FITUR LOGIKA BISNIS (EVENT HANDLERS)

# Fitur Amplop Otomatis
def proses_amplop(ev):
    input_val = document["input-uang-jajan"].value
    if not input_val or int(input_val) <= 0:
        window.alert("Masukkan jumlah uang jajan yang benar ya!")
        return
    
    total_uang = int(input_val)
    
    # Alokasi Rumus Persentase (70% : 20% : 10%)
    porsi_jajan = int(total_uang * 0.70)
    porsi_tabungan = int(total_uang * 0.20)
    porsi_darurat = total_uang - (porsi_jajan + porsi_tabungan)

    # Update State
    data["saldo_jajan"] += porsi_jajan
    data["saldo_tabungan"] += porsi_tabungan
    data["saldo_darurat"] += porsi_darurat

    # Catat ke log riwayat
    tambah_riwayat("Terima Uang Jajan Baru", "Jajan Harian (70%)", porsi_jajan, "masuk")
    tambah_riwayat("Simpan Tabungan Otomatis", "Tabungan Utama (20%)", porsi_tabungan, "masuk")
    tambah_riwayat("Alokasi Dana Sekolah", "Kebutuhan Mandiri (10%)", porsi_darurat, "masuk")

    document["input-uang-jajan"].value = ""
    update_ui()
    window.alert("Hore! Uang jajanmu berhasil dibagi ke dalam 3 dompet pintar!")

# Fitur Manual Potong Uang Jajan
def kurangi_jajan(ev):
    jumlah = window.prompt("Kamu habis jajan berapa hari ini? (Masukkan Angka):")
    if not jumlah: return
    try:
        jumlah = int(jumlah)
        if jumlah <= 0: raise ValueError
        if jumlah > data["saldo_jajan"]:
            window.alert("Waduh, saldo di dompet jajan harianmu tidak cukup!")
            return
        
        data["saldo_jajan"] -= jumlah
        tambah_riwayat("Beli Jajanan / Makanan", "Dompet Jajan", jumlah, "keluar")
        update_ui()
    except ValueError:
        window.alert("Masukkan angka yang benar ya, Kak!")

# Fitur Pindah Dana ke Tabungan Manual
def tambah_tabungan(ev):
    jumlah = window.prompt("Mau masukin berapa uang dari Dompet Jajan ke Celengan Utama?:")
    if not jumlah: return
    try:
        jumlah = int(jumlah)
        if jumlah <= 0: raise ValueError
        if jumlah > data["saldo_jajan"]:
            window.alert("Uang di dompet jajanmu tidak cukup untuk ditabung segitu.")
            return
        
        data["saldo_jajan"] -= jumlah
        data["saldo_tabungan"] += jumlah
        tambah_riwayat("Nabung Manual", "Tabungan Utama", jumlah, "masuk")
        update_ui()
    except ValueError:
        window.alert("Masukkan angka keuangan yang valid.")

# Fitur Setor Dana Tabungan ke Target Impian khusus
def setor_ke_target(ev):
    input_val = document["input-setor-target"].value
    if not input_val or int(input_val) <= 0:
        window.alert("Masukkan nominal setoran target yang benar!")
        return
    
    jumlah = int(input_val)
    if jumlah > data["saldo_tabungan"]:
        window.alert("Uang di Tabungan Utamamu tidak cukup. Kumpulkan uang dulu ya!")
        return

    data["saldo_tabungan"] -= jumlah
    data["target_terkumpul"] += jumlah
    
    tambah_riwayat(f"Setor Target: {data['target_nama']}", "Celengan Impian", jumlah, "keluar")
    document["input-setor-target"].value = ""
    update_ui()

    if data["target_terkumpul"] >= data["target_harga"]:
        window.alert(f"🎉 SELAMAT! Celengan untuk {data['target_nama']} sudah penuh! Kamu hebat bisa mandiri! 🥳")

# Fitur Membuat Ganti Target Baru
def update_target_baru(ev):
    nama = document["new-target-name"].value
    harga = document["new-target-price"].value
    ikon = document["new-target-icon"].value

    if not nama or not harga or int(harga) <= 0:
        window.alert("Tolong isi nama barang dan harga target dengan benar!")
        return

    data["target_nama"] = nama
    data["target_harga"] = int(harga)
    data["target_ikon"] = ikon
    data["target_terkumpul"] = 0
    
    update_ui()
    window.alert(f"Target impianmu berhasil diubah ke {ikon} {nama}! Semangat menabung!")
    
    document["new-target-name"].value = ""
    document["new-target-price"].value = ""

# 3. Binding Aksi ke Elemen HTML
document["btn-proses-amplop"].bind("click", proses_amplop)
document["btn-modal-jajan"].bind("click", kurangi_jajan)
document["btn-modal-tabung"].bind("click", tambah_tabungan)
document["btn-setor-target"].bind("click", setor_ke_target)
document["btn-update-target"].bind("click", update_target_baru)

# Jalankan fungsi saat web pertama kali dimuat
update_ui()
