# 🤖 Judol Remover - AI-Powered Spam Comment Detection

Sistem otomatis untuk mendeteksi dan menghapus komentar spam/judol di Facebook menggunakan model IndoBERT dan Graph API.

## 📁 Struktur Project

```
📦 Programm/
├── 📁 src/                     # Source code utama
│   ├── 📁 monitors/            # Auto monitoring systems
│   │   ├── auto_monitor.js     # Polling-based monitor
│   │   └── webhook_server.js   # Real-time webhook server
│   ├── 📁 bridges/             # Bridge komunikasi
│   │   └── spamDetectorBridge.js # Node.js ↔ Python bridge
│   ├── 📁 utils/               # Utility functions (future)
│   └── index.js                # Main application (manual mode)
├── 📁 python/                  # Python services
│   ├── 📁 models/              # Model IndoBERT
│   │   ├── config.json
│   │   ├── model.safetensors
│   │   ├── tokenizer_config.json
│   │   └── vocab.txt
│   └── 📁 services/            # Python AI services
│       ├── spam_detector.py    # Basic detector
│       ├── spam_detector_optimized.py # Optimized detector
│       └── spam_api.py         # Flask API server
├── 📁 tests/                   # Testing scripts
│   ├── test_spam_detector.js   # Comprehensive tests
│   ├── test_simple.js          # Simple tests
│   ├── debug_monitor.js        # Debug auto monitor
│   └── debug_facebook.js       # Debug Facebook API
├── 📁 scripts/                 # Helper scripts
│   └── start_api_server.js     # Start Python API server
├── 📁 docs/                    # Documentation
│   ├── README.md               # Detailed documentation
│   └── AUTO_MONITORING.md      # Auto monitoring guide
├── 📁 config/                  # Configuration files
│   ├── .env.example            # Environment template
│   └── requirements.txt        # Python dependencies
├── .env                        # Your environment variables
├── package.json                # Node.js dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Node.js dependencies
npm install

# Python dependencies
npm run install-python-deps
```

### 2. Setup Environment

```bash
# Copy environment template
cp config/.env.example .env

# Edit .env with your Facebook credentials
```

### 3. Test System

```bash
# Test model
npm run test-simple

# Test Facebook API
npm run debug-facebook
```

### 4. Run Auto Monitor

```bash
# Start auto monitoring (recommended)
npm run monitor

# Or run manual mode
npm start
```

## 📋 Available Commands

### 🧪 Testing
- `npm test` - Run comprehensive tests
- `npm run test-simple` - Quick model test
- `npm run debug-facebook` - Debug Facebook API
- `npm run debug-monitor` - Debug auto monitor

### 🚀 Production
- `npm start` - Manual spam removal
- `npm run monitor` - Auto monitoring (polling)
- `npm run webhook` - Real-time webhook server
- `npm run ui` - Web dashboard interface

### 🔧 Development
- `npm run dev` - UI + Auto monitor bersamaan
- `npm run start-api` - Start Python API server
- `npm run install-python-deps` - Install Python dependencies

## 🎯 Features

- ✅ **AI-Powered Detection** - IndoBERT model untuk akurasi tinggi
- ✅ **Web Dashboard** - Interface modern dan user-friendly
- ✅ **Auto Monitoring** - Deteksi real-time komentar baru
- ✅ **Dual Mode** - Polling dan Webhook support
- ✅ **Smart Caching** - Hindari pemrosesan ulang
- ✅ **Fallback System** - Regex backup jika AI gagal
- ✅ **Production Ready** - Error handling & logging

## 📖 Documentation

- 📚 [Detailed Guide](docs/README.md) - Setup lengkap dan troubleshooting
- 🔄 [Auto Monitoring](docs/AUTO_MONITORING.md) - Panduan monitoring otomatis
- 🎨 [UI Dashboard](docs/UI_GUIDE.md) - Panduan web interface
- 📱 [Collapsible Comments](docs/COLLAPSIBLE_COMMENTS.md) - Fitur UI collapsible
- ⚡ [Performance Optimization](docs/PERFORMANCE_OPTIMIZATION.md) - Optimasi performa

## 🛠️ Configuration

Edit file `.env`:

```env
# Facebook API
PAGE_ID=your_page_id
PAGE_ACCESS_TOKEN=your_access_token

# Auto Monitor
MONITOR_POLL_INTERVAL=30000
CONFIDENCE_THRESHOLD=0.8
```

## 🤝 Support

Jika mengalami masalah:

1. Cek log output untuk error messages
2. Jalankan `npm run debug-facebook` untuk test API
3. Pastikan permissions Facebook sudah benar
4. Lihat dokumentasi di folder `docs/`

## 📄 License

MIT License - Lihat file LICENSE untuk detail.

---

**🎉 Sistem siap digunakan!**

- **Web Dashboard**: `npm run ui` → http://localhost:3001
- **Auto Monitor**: `npm run monitor`
- **Development**: `npm run dev` (UI + Monitor bersamaan)
