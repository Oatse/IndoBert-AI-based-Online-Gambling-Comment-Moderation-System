#!/usr/bin/env node
/**
 * Script untuk menjalankan Python API server
 */

const SpamDetectorBridge = require('../src/bridges/spamDetectorBridge');

console.log('Starting Python Spam Detector API Server...');

const detector = new SpamDetectorBridge({
  mode: 'http',
  apiUrl: 'http://localhost:5000'
});

const server = detector.startAPIServer();

if (server) {
  console.log('Python API server started. Press Ctrl+C to stop.');
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\nShutting down Python API server...');
    server.kill('SIGTERM');
    process.exit(0);
  });
  
  process.on('SIGTERM', () => {
    console.log('\nShutting down Python API server...');
    server.kill('SIGTERM');
    process.exit(0);
  });
} else {
  console.error('Failed to start Python API server');
  process.exit(1);
}
