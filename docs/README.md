# Judol Remover - Spam Comment Detector

Program untuk menghapus komentar spam/judol di Facebook menggunakan Graph API dan model IndoBERT untuk deteksi yang lebih akurat.

## Fitur

- ✅ Integrasi dengan Facebook Graph API
- ✅ Deteksi spam menggunakan model IndoBERT yang sudah dilatih
- ✅ Dua mode operasi: Child Process dan HTTP API
- ✅ Fallback ke regex pattern jika model gagal
- ✅ Batch prediction untuk performa lebih baik
- ✅ Logging dan monitoring prediksi

## Struktur Project

```
├── Model/                          # Model IndoBERT
│   ├── config.json
│   ├── model.safetensors
│   ├── tokenizer_config.json
│   └── vocab.txt
├── index.js                        # Main application
├── spamDetectorBridge.js           # Bridge Node.js ↔ Python
├── spam_detector.py                # Python script untuk prediksi
├── spam_api.py                     # Flask API server
├── test_spam_detector.js           # Testing script
├── start_api_server.js             # Script untuk start API server
├── requirements.txt                # Python dependencies
└── .env.example                    # Environment variables template
```

## Setup dan Instalasi

### 1. Install Node.js Dependencies

```bash
npm install
```

### 2. Install Python Dependencies

Pastikan Python sudah terinstall, kemudian:

```bash
pip install -r requirements.txt
```

Atau menggunakan npm script:

```bash
npm run install-python-deps
```

### 3. Setup Environment Variables

Copy `.env.example` ke `.env` dan isi dengan konfigurasi Anda:

```bash
cp .env.example .env
```

Edit file `.env`:

```env
PAGE_ID=your_facebook_page_id_here
PAGE_ACCESS_TOKEN=your_facebook_page_access_token_here
```

### 4. Test Model

Test apakah model berfungsi dengan baik:

```bash
npm test
# atau
npm run test-detector
```

## Cara Penggunaan

### Mode 1: Child Process (Default)

Jalankan langsung aplikasi utama:

```bash
npm start
```

### Mode 2: HTTP API Server

1. Start Python API server:

```bash
npm run start-api
```

2. Di terminal lain, ubah mode di `index.js`:

```javascript
const spamDetector = new SpamDetectorBridge({
  mode: 'http', // Ubah dari 'child_process' ke 'http'
  apiUrl: 'http://localhost:5000',
  timeout: 30000
});
```

3. Jalankan aplikasi:

```bash
npm start
```

## Konfigurasi

### SpamDetectorBridge Options

```javascript
const spamDetector = new SpamDetectorBridge({
  mode: 'child_process',           // 'child_process' atau 'http'
  apiUrl: 'http://localhost:5000', // URL untuk HTTP mode
  pythonPath: 'python',            // Path ke Python executable
  scriptPath: './spam_detector.py', // Path ke script Python
  timeout: 30000                   // Timeout dalam milliseconds
});
```

### Confidence Threshold

Ubah threshold confidence di fungsi `isSpamComment`:

```javascript
// Return true jika diprediksi sebagai spam dengan confidence > 0.8 (lebih ketat)
return prediction.is_spam && prediction.confidence > 0.8;
```

### Optimized Mode

Untuk performa terbaik, gunakan optimized mode yang memuat model sekali dan menggunakannya berulang kali:

```javascript
const spamDetector = new SpamDetectorBridge({
  mode: 'child_process',
  useOptimized: true,  // Aktifkan optimized mode
  timeout: 30000
});
```

## API Endpoints (HTTP Mode)

### Health Check
```
GET /health
```

### Single Prediction
```
POST /predict
Content-Type: application/json

{
  "text": "Teks yang akan diprediksi"
}
```

### Batch Prediction
```
POST /predict_batch
Content-Type: application/json

{
  "texts": ["Teks 1", "Teks 2", "Teks 3"]
}
```

## Testing

### Test Model Prediksi

```bash
npm test
```

### Test Simple (Recommended)

```bash
node test_simple.js
```

### Test Manual dengan Python

```bash
python spam_detector.py "Teks yang akan ditest"
```

### Test Optimized Python Script

```bash
echo "Teks yang akan ditest" | python spam_detector_optimized.py
```

### Test API Server

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "PROMO GILA! Diskon 90%!"}'
```

## Troubleshooting

### Python tidak ditemukan

- Install Python dari [python.org](https://python.org)
- Atau ubah `pythonPath` di konfigurasi ke `python3`

### Model tidak bisa dimuat

- Pastikan file model ada di folder `Model/`
- Check apakah semua dependencies Python sudah terinstall
- Coba jalankan `python spam_detector.py "test"` untuk debug

### Facebook API Error

- Pastikan `PAGE_ACCESS_TOKEN` valid dan memiliki permission yang tepat
- Check apakah `PAGE_ID` benar
- Pastikan token belum expired

### Memory/Performance Issues

- Gunakan HTTP mode untuk aplikasi production
- Adjust timeout sesuai kebutuhan
- Consider menggunakan GPU jika tersedia

## Model Information

Model IndoBERT yang digunakan sudah dilatih khusus untuk mendeteksi komentar spam/judol dalam bahasa Indonesia. Model ini dapat mengenali:

- Promosi produk/jasa
- Link spam
- Kontak WhatsApp/Telegram
- Penipuan online
- Dan pola spam lainnya

## Contributing

1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Create Pull Request

## License

MIT License
