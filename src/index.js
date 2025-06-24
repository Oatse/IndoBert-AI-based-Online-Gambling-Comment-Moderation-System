
const FB = require('fb');
const readline = require('readline');
const SpamDetectorBridge = require('./bridges/spamDetectorBridge');
require('dotenv').config();

// Inisialisasi spam detector
const spamDetector = new SpamDetectorBridge({
  mode: 'child_process', // atau 'http' jika ingin menggunakan API server
  useOptimized: true, // Gunakan optimized process untuk efisiensi
  timeout: 30000 // 30 detik timeout
});

// Cleanup saat aplikasi ditutup
process.on('SIGINT', () => {
  console.log('\nShutting down...');
  spamDetector.cleanup();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\nShutting down...');
  spamDetector.cleanup();
  process.exit(0);
});

async function removeSpamComments() {
  const pageId = process.env.PAGE_ID;
  
  FB.setAccessToken(process.env.PAGE_ACCESS_TOKEN);

  try {
    // Ambil postingan halaman
    const postsResponse = await new Promise((resolve, reject) => {
      FB.api(`${pageId}/posts`, { fields: ['message', 'created_time'] }, (response) => {
        if (response && !response.error) {
          resolve(response);
        } else {
          reject(response.error);
        }
      });
    });

    // Tampilkan daftar postingan
    console.log("Daftar Postingan:");
    postsResponse.data.forEach((post, index) => {
      console.log(`[${index + 1}] Postingan pada ${post.created_time}`);
      console.log(`    Isi: ${post.message ? post.message.substring(0, 100) + '...' : 'Tidak ada teks'}`);
      console.log('---');
    });

    // Pilih postingan untuk diproses
    const selectedPosts = await selectPosts(postsResponse.data);

    // Proses postingan yang dipilih
    for (let post of selectedPosts) {
      console.log(`\nMemproses postingan: ${post.id}`);

      // Ambil komentar postingan
      const commentsResponse = await new Promise((resolve, reject) => {
        FB.api(`${post.id}/comments`, (response) => {
          if (response && !response.error) {
            resolve(response);
          } else {
            reject(response.error);
          }
        });
      });

      // Tampilkan komentar
      console.log("Komentar yang akan diperiksa:");
      commentsResponse.data.forEach((comment, index) => {
        console.log(`[${index + 1}] ${comment.message}`);
      });

      // Hapus komentar spam
      for (let comment of commentsResponse.data) {
        const isSpam = await isSpamComment(comment.message);
        if (isSpam) {
          console.log(`Menghapus komentar spam: "${comment.message.substring(0, 100)}..."`);
          await deleteComment(comment.id);
        } else {
          console.log(`Komentar normal: "${comment.message.substring(0, 50)}..."`);
        }
      }
    }
  } catch (error) {
    console.error('Kesalahan:', error);
  }
}

function selectPosts(posts) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise((resolve) => {
    rl.question('Masukkan nomor postingan yang ingin diproses (pisahkan dengan koma, atau "all" untuk semua): ', (answer) => {
      rl.close();

      let selectedPosts;
      if (answer.toLowerCase() === 'all') {
        selectedPosts = posts;
      } else {
        const selectedIndexes = answer.split(',').map(num => parseInt(num.trim()) - 1);
        selectedPosts = selectedIndexes.map(index => posts[index]);
      }

      resolve(selectedPosts);
    });
  });
}

async function isSpamComment(commentText) {
  // Hindari pemeriksaan jika komentar kosong
  if (!commentText) return false;

  try {
    // Gunakan model IndoBERT untuk prediksi
    const prediction = await spamDetector.predict(commentText);

    console.log(`Prediksi untuk "${commentText.substring(0, 50)}...": ${prediction.label} (confidence: ${prediction.confidence.toFixed(3)})`);

    // Return true jika diprediksi sebagai spam dengan confidence > 0.8 (lebih ketat)
    return prediction.is_spam && prediction.confidence > 0.8;

  } catch (error) {
    console.error('Error dalam prediksi spam:', error.message);

    // Fallback ke regex pattern jika model gagal
    console.log('Menggunakan fallback regex pattern...');
    const spamPatterns = [
      /\b(jual|promo|diskon|gratis)\b/i,
      /http(s)?:\/\/\S+/,
      /\b(wa|whatsapp|telegram)\b/i,
      /\d{10,}/
    ];

    return spamPatterns.some(pattern => pattern.test(commentText));
  }
}

async function deleteComment(commentId) {
  return new Promise((resolve, reject) => {
    FB.api(`/${commentId}`, 'DELETE', (response) => {
      if (response === true) {
        console.log(`Komentar ${commentId} dihapus`);
        resolve(true);
      } else {
        console.error(`Gagal menghapus komentar ${commentId}`);
        reject(false);
      }
    });
  });
}

removeSpamComments();
