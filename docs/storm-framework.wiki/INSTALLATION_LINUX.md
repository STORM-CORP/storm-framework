# 🛠️ Installation Linux Storm Framework

Untuk instalasi linux ini sebenernya installasi dengan versi lama di environment Linux standar, ini akan menggunakan perintah seperti `--break-system-packages` saat menjalankan `pip` yang dimana ini sebenarnya beresiko konflik terhadap dependesi Python yang di gunakan oleh system Linux.

Tapi kita tetap sediakan ini karena siapa tau ada yang menginginkan instalasi menggunakan metode lama seperti ini, tapi kita tetap menyarankan kamu untuk menggunakan Virtual Environment saat instalasi dengan metode ini supaya lebih aman, atau bisa menggunakan cara lain yang sudah kita sediakan seperti **Venv/Docker.**

## Step Instalasi

### 1. Clone Repositori & Otomatis Instalasi

Ini akan melakukan instalasi secara otomatis hingga selesai.

```bash
curl -fsSL https://raw.githubusercontent.com/StormWorld0/storm-framework/main/setuplinux | bash
```

### 2. Perintah Menjalankan

Ini perintah untuk menjalankan Storm setelah instalasi selesai.

```bash
sudo storm
```

### 3. Perintah Update External

Ini akan menjalankan update tanpa harus masuk ke antarmuka Storm.

```bash
sudo storm --update
```
