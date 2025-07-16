# 🛡️ Judol Remover - Streamlit Edition

Aplikasi deteksi dan penghapusan komentar spam/judol otomatis untuk Facebook menggunakan IndoBERT dan Streamlit.

## 📁 Project Structure

```
📦 Programm/
├── 📄 streamlit_app.py          # Main Streamlit application
├── 📄 streamlit_facebook.py     # Facebook API wrapper
├── 📄 streamlit_monitor.py      # Auto monitoring service
├── 📄 run_streamlit.py          # Startup script
├── 📄 requirements.txt          # Python dependencies
├── 📄 start_streamlit.bat       # Windows batch script
├── 📁 .streamlit/               # Streamlit configuration
│   └── config.toml
├── 📁 python/                   # Python services
│   ├── 📁 models/               # IndoBERT model files
│   │   ├── config.json
│   │   ├── model.safetensors
│   │   ├── tokenizer_config.json
│   │   └── vocab.txt
│   └── 📁 services/             # Python AI services
│       └── spam_detector.py     # Spam detection service
├── 📄 .env                      # Environment variables
├── 📄 README_STREAMLIT.md       # Detailed documentation
└── 📄 CONVERSION_SUMMARY.md     # Migration summary
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
Buat file `.env` dengan konfigurasi berikut:
```
PAGE_ID=your_facebook_page_id
PAGE_ACCESS_TOKEN=your_page_access_token
MODEL_PATH=./python/models
CONFIDENCE_THRESHOLD=0.8
```

### 3. Run Application
```bash
# Menggunakan startup script (recommended)
python run_streamlit.py

# Atau langsung dengan Streamlit
python -m streamlit run streamlit_app.py

# Atau menggunakan batch file (Windows)
start_streamlit.bat
```

### 4. Access Dashboard
Buka browser ke: **http://localhost:8501**

## 🎯 Features

- **🤖 AI-Powered Detection** - IndoBERT untuk deteksi spam bahasa Indonesia
- **📊 Real-time Dashboard** - Monitoring dan statistik live
- **🔄 Auto Monitoring** - Deteksi dan penghapusan otomatis
- **👥 Manual Moderation** - Review dan moderasi manual
- **📝 Activity Logs** - Riwayat lengkap aktivitas
- **⚙️ Configurable Settings** - Pengaturan threshold dan API

## 📊 Dashboard Pages

1. **Dashboard** - Overview dan monitoring real-time
2. **Manual Check** - Periksa post tertentu untuk spam
3. **Test Detector** - Test deteksi dengan teks custom
4. **Settings** - Konfigurasi API dan parameter
5. **Logs** - Riwayat aktivitas dan log sistem

## 🔧 Configuration

### Environment Variables
- `PAGE_ID` - Facebook Page ID
- `PAGE_ACCESS_TOKEN` - Facebook Page Access Token
- `MODEL_PATH` - Path ke model IndoBERT
- `CONFIDENCE_THRESHOLD` - Threshold confidence untuk klasifikasi spam

### Model Requirements
Pastikan file-file berikut ada di `python/models/`:
- `config.json`
- `model.safetensors`
- `tokenizer_config.json`
- `vocab.txt`

## 🛠️ Development

### Testing
```bash
python -m pytest tests/
```

## 📞 Support

Untuk bantuan dan troubleshooting, lihat:
- `README_STREAMLIT.md` - Dokumentasi lengkap
- `CONVERSION_SUMMARY.md` - Ringkasan konversi dari Node.js

## 📄 License

MIT License
