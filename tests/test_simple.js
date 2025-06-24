#!/usr/bin/env node
/**
 * Simple test untuk spam detector bridge
 */

const SpamDetectorBridge = require('../src/bridges/spamDetectorBridge');

async function testSimple() {
  console.log('Testing Simple Spam Detector Bridge...\n');

  const detector = new SpamDetectorBridge({
    mode: 'child_process',
    useOptimized: true,
    timeout: 30000
  });

  // Test cases
  const testCases = [
    "Halo, bagaimana kabarnya hari ini?",
    "PROMO GILA! Diskon 90% untuk semua produk! WA 08123456789",
    "Terima kasih atas informasinya, sangat bermanfaat"
  ];

  for (let i = 0; i < testCases.length; i++) {
    const text = testCases[i];
    console.log(`\nTest ${i + 1}: "${text}"`);
    
    try {
      const result = await detector.predict(text);
      console.log(`Result: ${result.label} (confidence: ${result.confidence.toFixed(3)})`);
      console.log(`Is Spam: ${result.is_spam}`);
      
      if (result.error) {
        console.log(`Error: ${result.error}`);
      }
    } catch (error) {
      console.error(`Error: ${error.message}`);
    }
  }

  // Cleanup
  detector.cleanup();
  console.log('\nTest completed!');
}

// Run test
testSimple().catch(console.error);
