/**
 * Bridge untuk komunikasi antara Node.js dan Python Spam Detector
 * Mendukung dua mode: child_process dan HTTP API
 */

const { spawn, exec } = require('child_process');
const axios = require('axios');
const path = require('path');

class SpamDetectorBridge {
  constructor(options = {}) {
    this.mode = options.mode || 'child_process'; // 'child_process' atau 'http'
    this.apiUrl = options.apiUrl || 'http://localhost:5000';
    this.pythonPath = options.pythonPath || 'python';
    this.scriptPath = options.scriptPath || './python/services/spam_detector.py';
    this.optimizedScriptPath = options.optimizedScriptPath || './python/services/spam_detector_optimized.py';
    this.timeout = options.timeout || 15000; // 15 detik timeout untuk UI (increased)
    this.useOptimized = options.useOptimized !== false; // Default true

    // Untuk persistent process
    this.pythonProcess = null;
    this.isReady = false;
    this.pendingRequests = [];

    // Untuk HTTP mode, cek apakah server sudah running
    if (this.mode === 'http') {
      this.checkServerHealth();
    } else if (this.useOptimized) {
      this.startOptimizedProcess();
    }
  }

  /**
   * Start optimized Python process
   */
  startOptimizedProcess() {
    if (this.pythonProcess) {
      return; // Already started
    }

    console.log('Starting optimized Python process...');
    this.pythonProcess = spawn(this.pythonPath, [this.optimizedScriptPath], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    this.pythonProcess.stderr.on('data', (data) => {
      const message = data.toString();
      if (message.includes('Ready for predictions')) {
        this.isReady = true;
        console.log('Python model is ready for predictions');
        this.processPendingRequests();
      } else {
        console.log('Python stderr:', message.trim());
      }
    });

    this.pythonProcess.stdout.on('data', (data) => {
      const lines = data.toString().split('\n').filter(line => line.trim());
      lines.forEach(line => {
        try {
          const result = JSON.parse(line);
          this.handlePredictionResult(result);
        } catch (error) {
          console.error('Failed to parse Python output:', line);
        }
      });
    });

    this.pythonProcess.on('error', (error) => {
      console.error('Python process error:', error);
      this.isReady = false;
    });

    this.pythonProcess.on('exit', (code) => {
      console.log(`Python process exited with code ${code}`);
      this.isReady = false;
      this.pythonProcess = null;
    });
  }

  /**
   * Process pending requests when model becomes ready
   */
  processPendingRequests() {
    while (this.pendingRequests.length > 0 && this.isReady) {
      const request = this.pendingRequests.shift();
      this.sendToPythonProcess(request.text, request.resolve, request.reject);
    }
  }

  /**
   * Handle prediction result from Python process
   */
  handlePredictionResult(result) {
    if (this.currentResolve) {
      clearTimeout(this.requestTimeout);
      this.currentResolve(result);
      this.currentResolve = null;
      this.currentReject = null;
    }
  }

  /**
   * Send text to Python process for prediction
   */
  sendToPythonProcess(text, resolve, reject) {
    if (!this.pythonProcess || !this.isReady) {
      reject(new Error('Python process not ready'));
      return;
    }

    // Store resolve function with timeout
    this.currentResolve = resolve;
    this.currentReject = reject;

    // Set timeout for this specific request
    this.requestTimeout = setTimeout(() => {
      if (this.currentResolve) {
        this.currentReject(new Error('Request timeout'));
        this.currentResolve = null;
        this.currentReject = null;
      }
    }, this.timeout);

    try {
      this.pythonProcess.stdin.write(text + '\n');
    } catch (error) {
      clearTimeout(this.requestTimeout);
      reject(error);
    }
  }

  /**
   * Cek kesehatan server Python API
   */
  async checkServerHealth() {
    try {
      const response = await axios.get(`${this.apiUrl}/health`, { timeout: 5000 });
      console.log('Python API server is healthy:', response.data);
      return true;
    } catch (error) {
      console.warn('Python API server not available. Consider starting it with: python spam_api.py');
      return false;
    }
  }

  /**
   * Prediksi menggunakan optimized process
   */
  async predictWithOptimizedProcess(text) {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Prediction timeout'));
      }, this.timeout);

      if (!this.isReady) {
        // Add to pending requests
        this.pendingRequests.push({ text, resolve: (result) => {
          clearTimeout(timeout);
          resolve(result);
        }, reject: (error) => {
          clearTimeout(timeout);
          reject(error);
        }});
        return;
      }

      this.sendToPythonProcess(text, (result) => {
        clearTimeout(timeout);
        resolve(result);
      }, (error) => {
        clearTimeout(timeout);
        reject(error);
      });
    });
  }

  /**
   * Prediksi menggunakan child_process (fallback)
   */
  async predictWithChildProcess(text) {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Prediction timeout'));
      }, this.timeout);

      // Escape text untuk command line
      const escapedText = text.replace(/"/g, '\\"');

      exec(`${this.pythonPath} "${this.scriptPath}" "${escapedText}"`, (error, stdout, stderr) => {
        clearTimeout(timeout);

        if (error) {
          console.error('Python execution error:', error);
          reject(error);
          return;
        }

        if (stderr) {
          console.warn('Python stderr:', stderr);
        }

        try {
          const result = JSON.parse(stdout.trim());
          resolve(result);
        } catch (parseError) {
          console.error('Failed to parse Python output:', stdout);
          reject(parseError);
        }
      });
    });
  }

  /**
   * Prediksi menggunakan HTTP API
   */
  async predictWithHTTP(text) {
    try {
      const response = await axios.post(`${this.apiUrl}/predict`, {
        text: text
      }, {
        timeout: this.timeout,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(`API Error: ${error.response.status} - ${error.response.data.error || error.response.statusText}`);
      } else if (error.request) {
        throw new Error('No response from Python API server. Make sure it\'s running.');
      } else {
        throw new Error(`Request error: ${error.message}`);
      }
    }
  }

  /**
   * Prediksi batch menggunakan HTTP API
   */
  async predictBatchWithHTTP(texts) {
    try {
      const response = await axios.post(`${this.apiUrl}/predict_batch`, {
        texts: texts
      }, {
        timeout: this.timeout * 2, // Double timeout untuk batch
        headers: {
          'Content-Type': 'application/json'
        }
      });

      return response.data.results;
    } catch (error) {
      if (error.response) {
        throw new Error(`API Error: ${error.response.status} - ${error.response.data.error || error.response.statusText}`);
      } else if (error.request) {
        throw new Error('No response from Python API server. Make sure it\'s running.');
      } else {
        throw new Error(`Request error: ${error.message}`);
      }
    }
  }

  /**
   * Main predict method - otomatis pilih mode
   */
  async predict(text) {
    if (!text || typeof text !== 'string' || text.trim() === '') {
      return {
        is_spam: false,
        confidence: 0.0,
        label: 'normal',
        error: 'Empty or invalid text'
      };
    }

    try {
      if (this.mode === 'http') {
        return await this.predictWithHTTP(text);
      } else if (this.useOptimized) {
        return await this.predictWithOptimizedProcess(text);
      } else {
        return await this.predictWithChildProcess(text);
      }
    } catch (error) {
      console.error('Prediction error:', error.message);

      // Fallback ke mode lain jika gagal
      if (this.mode === 'http') {
        console.log('Falling back to child_process mode...');
        try {
          return await this.predictWithChildProcess(text);
        } catch (fallbackError) {
          console.error('Fallback also failed:', fallbackError.message);
        }
      } else if (this.useOptimized) {
        console.log('Falling back to regular child_process mode...');
        try {
          return await this.predictWithChildProcess(text);
        } catch (fallbackError) {
          console.error('Fallback also failed:', fallbackError.message);
        }
      }

      // Return default jika semua gagal
      return {
        is_spam: false,
        confidence: 0.0,
        label: 'error',
        error: error.message
      };
    }
  }

  /**
   * Prediksi batch (hanya untuk HTTP mode)
   */
  async predictBatch(texts) {
    if (this.mode !== 'http') {
      // Untuk child_process mode, lakukan satu per satu
      const results = [];
      for (const text of texts) {
        const result = await this.predict(text);
        results.push(result);
      }
      return results;
    }

    return await this.predictBatchWithHTTP(texts);
  }

  /**
   * Start Python API server (helper method)
   */
  startAPIServer() {
    if (this.mode !== 'http') {
      console.log('Not in HTTP mode, cannot start API server');
      return null;
    }

    console.log('Starting Python API server...');
    const server = spawn(this.pythonPath, ['spam_api.py'], {
      stdio: 'inherit',
      cwd: process.cwd()
    });

    server.on('error', (error) => {
      console.error('Failed to start Python API server:', error);
    });

    // Wait a bit for server to start
    setTimeout(() => {
      this.checkServerHealth();
    }, 3000);

    return server;
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    if (this.pythonProcess) {
      console.log('Terminating Python process...');
      this.pythonProcess.kill('SIGTERM');
      this.pythonProcess = null;
      this.isReady = false;
    }
  }
}

module.exports = SpamDetectorBridge;
