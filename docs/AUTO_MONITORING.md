# Auto Monitoring untuk Deteksi Komentar Spam Real-time

Sistem ini menyediakan dua metode untuk mendeteksi dan menghapus komentar spam secara otomatis:

## 1. 🔄 Polling System (Auto Monitor)

Sistem yang mengecek komentar baru secara berkala.

### Cara Penggunaan:

```bash
npm run monitor
```

### Fitur:
- ✅ Cek komentar baru setiap 30 detik (dapat disesuaikan)
- ✅ Deteksi spam menggunakan model IndoBERT
- ✅ Auto delete komentar spam
- ✅ Cache untuk menghindari pemrosesan ulang
- ✅ Logging detail aktivitas

### Konfigurasi:

```javascript
const monitor = new AutoSpamMonitor({
  pollInterval: 30000 // 30 detik (dapat disesuaikan)
});
```

### Kelebihan:
- Mudah setup
- Tidak perlu konfigurasi webhook
- Bekerja dengan akses token biasa

### Kekurangan:
- Delay maksimal sesuai interval polling
- Menggunakan lebih banyak API calls

---

## 2. 🎣 Webhook System (Real-time)

Sistem notifikasi real-time dari Facebook.

### Cara Penggunaan:

```bash
npm run webhook
```

### Setup Webhook:

1. **Buat Facebook App:**
   - Buka [Facebook Developers](https://developers.facebook.com/)
   - Buat app baru
   - Tambahkan produk "Webhooks"

2. **Konfigurasi Webhook:**
   - Callback URL: `https://yourdomain.com/webhook`
   - Verify Token: Set di `.env` sebagai `WEBHOOK_VERIFY_TOKEN`
   - Subscribe ke events: `feed`, `comments`

3. **Environment Variables:**
   ```env
   WEBHOOK_VERIFY_TOKEN=your_unique_verify_token
   WEBHOOK_PORT=3000
   FB_APP_SECRET=your_facebook_app_secret
   ```

### Fitur:
- ✅ Notifikasi real-time saat ada komentar baru
- ✅ Signature verification untuk keamanan
- ✅ Health check endpoint
- ✅ Status monitoring

### Endpoints:
- `GET /webhook` - Webhook verification
- `POST /webhook` - Receive events
- `GET /health` - Health check
- `GET /status` - System status

### Kelebihan:
- Real-time response (instant)
- Efisien dalam penggunaan API
- Scalable untuk volume tinggi

### Kekurangan:
- Perlu setup webhook di Facebook
- Memerlukan domain publik (untuk production)
- Setup lebih kompleks

---

## 3. 🔧 Konfigurasi

### Environment Variables (.env):

```env
# Facebook API
PAGE_ID=your_page_id
PAGE_ACCESS_TOKEN=your_access_token
FB_APP_SECRET=your_app_secret

# Webhook
WEBHOOK_VERIFY_TOKEN=your_verify_token
WEBHOOK_PORT=3000

# Monitor
MONITOR_POLL_INTERVAL=30000

# Spam Detection
CONFIDENCE_THRESHOLD=0.8
```

### Permissions yang Diperlukan:

Untuk Page Access Token:
- `pages_read_engagement` - Membaca komentar
- `pages_manage_engagement` - Menghapus komentar
- `pages_show_list` - Akses basic page info

---

## 4. 🚀 Deployment

### Development (Local):

```bash
# Polling system
npm run monitor

# Webhook system (perlu ngrok untuk testing)
npm run webhook
```

### Production:

1. **Polling System:**
   ```bash
   # Menggunakan PM2
   pm2 start auto_monitor.js --name "spam-monitor"
   ```

2. **Webhook System:**
   ```bash
   # Menggunakan PM2
   pm2 start webhook_server.js --name "spam-webhook"
   ```

### Dengan Docker:

```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "webhook"]
```

---

## 5. 📊 Monitoring & Logging

### Log Output:
```
🚀 Starting auto spam monitor...
🔍 Checking for new comments... (10:30:15 AM)
📝 Found 2 new comments on post 123456789
🚨 SPAM DETECTED: "PROMO GILA! Diskon 90%..." by John Doe
🤖 Prediction: spam (confidence: 0.995)
🗑️  Spam comment deleted: 987654321
✅ Normal comment: "Terima kasih infonya" by Jane Smith
✨ Processed 2 new comments, removed 1 spam comments
```

### Health Check:
```bash
curl http://localhost:3000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "detector_ready": true
}
```

---

## 6. 🛠️ Troubleshooting

### Common Issues:

1. **"Invalid Page ID"**
   - Pastikan menggunakan Page ID, bukan Profile ID
   - Cek permissions access token

2. **"Webhook verification failed"**
   - Pastikan WEBHOOK_VERIFY_TOKEN sama dengan yang di Facebook
   - Cek URL webhook accessible dari internet

3. **"Model not ready"**
   - Tunggu beberapa detik untuk model loading
   - Cek log Python process

4. **"Permission denied"**
   - Pastikan access token memiliki permissions yang tepat
   - Regenerate token jika perlu

### Debug Mode:

Set environment variable untuk debug:
```bash
DEBUG=true npm run monitor
```

---

## 7. 📈 Performance Tips

1. **Polling Interval:**
   - 30 detik untuk aktivitas normal
   - 10 detik untuk aktivitas tinggi
   - 60 detik untuk aktivitas rendah

2. **Cache Management:**
   - Cache dibersihkan otomatis setiap jam
   - Maksimal 1000 comment IDs dalam cache

3. **Model Optimization:**
   - Gunakan `useOptimized: true` untuk performa terbaik
   - Model dimuat sekali dan digunakan berulang

4. **Rate Limiting:**
   - Facebook API: 200 calls per hour per user
   - Webhook tidak terkena rate limit

---

## 8. 🔒 Security

1. **Webhook Signature Verification:**
   - Selalu verifikasi signature dari Facebook
   - Gunakan App Secret yang aman

2. **Access Token Security:**
   - Jangan commit token ke repository
   - Regenerate token secara berkala
   - Gunakan environment variables

3. **Server Security:**
   - Gunakan HTTPS untuk webhook
   - Implement rate limiting
   - Monitor untuk aktivitas mencurigakan

---

## 9. 📞 Support

Jika mengalami masalah:

1. Cek log output untuk error messages
2. Verifikasi konfigurasi Facebook App
3. Test dengan `npm run test-simple`
4. Cek network connectivity
5. Pastikan permissions sudah benar

Untuk bantuan lebih lanjut, silakan buka issue di repository atau hubungi developer.
