#!/usr/bin/env node
/**
 * Debug version of auto monitor - checks comments from last 24 hours
 */

const AutoSpamMonitor = require('../src/monitors/auto_monitor');

console.log('🐛 Starting Debug Auto Monitor...');
console.log('This will check comments from the last 24 hours for testing\n');

const monitor = new AutoSpamMonitor({
  pollInterval: 10000, // 10 detik untuk debug
  debugMode: true      // Enable debug mode
});

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down debug monitor...');
  await monitor.stop();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Shutting down debug monitor...');
  await monitor.stop();
  process.exit(0);
});

// Start monitoring
monitor.start().catch(console.error);

// Auto stop after 2 minutes for testing
setTimeout(async () => {
  console.log('\n⏰ Debug session completed (2 minutes)');
  await monitor.stop();
  process.exit(0);
}, 120000);
