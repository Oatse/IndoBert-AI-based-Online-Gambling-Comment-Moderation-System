# 🎨 UI Dashboard Guide - Judol Remover

Web interface yang user-friendly untuk mengelola sistem deteksi spam dengan tampilan modern dan interaktif.

## 🚀 Quick Start

### Menjalankan UI Dashboard

```bash
# Jalankan UI saja
npm run ui

# Jalankan UI + Auto Monitor bersamaan (recommended)
npm run dev
```

Dashboard akan tersedia di: **http://localhost:3001**

## 📊 Fitur Dashboard

### 1. **Status Cards**
- 🟢 **Monitor Status**: Running/Stopped
- 💬 **Comments Processed**: Total komentar yang diproses
- 🗑️ **Spam Removed**: Total spam yang dihapus
- 📘 **Facebook Page**: Page ID yang terkonfigurasi

### 2. **Auto Monitor Control**
- ▶️ **Start Auto Monitor**: Mulai monitoring otomatis
- ⏹️ **Stop Auto Monitor**: Hentikan monitoring
- ⏰ **Runtime Info**: Waktu mulai dan statistik

### 3. **Test Spam Detection**
- 📝 **Text Input**: Masukkan teks untuk ditest
- 🔍 **Test Detection**: Analisis menggunakan AI
- 📊 **Confidence Bar**: Visual confidence score
- 🏷️ **Result Badge**: Spam/Normal classification

### 4. **Recent Posts & Comments**
- 📰 **Posts List**: 5 postingan terbaru (compact view)
- 👆 **Click to Expand**: Klik post untuk lihat komentar
- 💬 **Comments**: Lazy-loaded dengan prediksi AI
- 🚨 **Spam Detection**: Highlight komentar spam
- 🗑️ **Manual Delete**: Hapus komentar dengan dropdown menu
- 🔄 **Refresh Comments**: Update komentar per post

## 🎯 Cara Penggunaan

### Setup Awal

1. **Pastikan .env sudah dikonfigurasi:**
   ```env
   PAGE_ID=your_page_id
   PAGE_ACCESS_TOKEN=your_access_token
   UI_PORT=3001
   ```

2. **Jalankan dashboard:**
   ```bash
   npm run ui
   ```

3. **Buka browser:** http://localhost:3001

### Monitoring Otomatis

1. **Klik "Start Auto Monitor"** di dashboard
2. **Monitor status** akan berubah menjadi "Running"
3. **Statistik real-time** akan terupdate setiap 5 detik
4. **Komentar spam** akan otomatis dihapus

### Testing Manual

1. **Masukkan teks** di "Test Spam Detection"
2. **Klik "Test Detection"** atau tekan Ctrl+Enter
3. **Lihat hasil** dengan confidence score
4. **Confidence bar** menunjukkan tingkat keyakinan AI

### Monitoring Posts

1. **Posts otomatis dimuat** saat dashboard dibuka (compact view)
2. **Klik post header** untuk expand dan lihat komentar
3. **Comments lazy-loaded** saat pertama kali dibuka
4. **Klik "Refresh"** untuk update manual per post
5. **Lihat prediksi AI** untuk setiap komentar
6. **Hapus spam manual** dengan dropdown menu
7. **Real-time badge updates** setelah delete

## 🎨 Interface Elements

### Status Indicators
- 🟢 **Green**: Normal/Running/Safe
- 🔴 **Red**: Spam/Stopped/Danger
- 🟡 **Yellow**: Warning/Medium confidence
- 🔵 **Blue**: Info/Processing

### Confidence Levels
- **High (80-100%)**: Green bar - Sangat yakin
- **Medium (50-79%)**: Yellow bar - Cukup yakin  
- **Low (0-49%)**: Gray bar - Kurang yakin

### Interactive Elements
- **Hover effects** pada cards dan buttons
- **Loading spinners** saat processing
- **Toast notifications** untuk feedback
- **Real-time updates** setiap 5 detik

## 📱 Responsive Design

Dashboard fully responsive untuk:
- 💻 **Desktop**: Full features
- 📱 **Mobile**: Optimized layout
- 📟 **Tablet**: Adaptive design

## 🔧 API Endpoints

Dashboard menggunakan REST API:

### Status & Control
- `GET /api/status` - System status
- `POST /api/monitor/start` - Start monitoring
- `POST /api/monitor/stop` - Stop monitoring

### Detection & Posts
- `POST /api/test-detection` - Test spam detection
- `GET /api/posts` - Get recent posts
- `GET /api/posts/:id/comments` - Get comments
- `DELETE /api/comments/:id` - Delete comment

## 🎯 Best Practices

### Performance
- Dashboard **auto-updates** setiap 5 detik
- **Lazy loading** untuk posts dan comments
- **Optimized API calls** untuk efisiensi

### User Experience
- **Visual feedback** untuk semua actions
- **Error handling** dengan toast notifications
- **Keyboard shortcuts** (Ctrl+Enter untuk test)

### Security
- **No sensitive data** di frontend
- **API validation** untuk semua requests
- **Safe deletion** dengan confirmation

## 🛠️ Customization

### Styling
Edit `src/ui/assets/css/dashboard.css`:
```css
/* Custom colors */
:root {
  --primary-color: #007bff;
  --success-color: #28a745;
  --danger-color: #dc3545;
}
```

### Functionality
Edit `src/ui/assets/js/dashboard.js`:
```javascript
// Custom update interval
this.statusUpdateInterval = setInterval(() => {
    this.updateStatus();
}, 3000); // 3 seconds instead of 5
```

## 🔍 Troubleshooting

### UI tidak muncul
```bash
# Cek apakah server running
npm run ui

# Cek port conflicts
netstat -an | findstr :3001
```

### Data tidak muncul
1. **Cek .env configuration**
2. **Verify Facebook access token**
3. **Check browser console** untuk errors

### Auto monitor tidak jalan
1. **Cek Python dependencies**
2. **Verify model path**
3. **Check server logs**

## 📊 Monitoring & Analytics

Dashboard menyediakan:
- **Real-time statistics**
- **Historical data** (session-based)
- **Performance metrics**
- **Error tracking**

## 🚀 Production Deployment

### Environment Setup
```env
NODE_ENV=production
UI_PORT=80
```

### Process Management
```bash
# Using PM2
pm2 start src/ui/server.js --name "judol-ui"
pm2 start src/monitors/auto_monitor.js --name "judol-monitor"
```

### Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📞 Support

Jika mengalami masalah dengan UI:

1. **Check browser console** untuk JavaScript errors
2. **Verify server logs** di terminal
3. **Test API endpoints** manual dengan curl
4. **Check network connectivity**

---

**🎉 Dashboard siap digunakan! Interface yang intuitif untuk mengelola spam detection dengan mudah.**
