#!/usr/bin/env node
/**
 * Script untuk testing Spam Detector
 */

const SpamDetectorBridge = require('../src/bridges/spamDetectorBridge');

async function testSpamDetector() {
  console.log('Testing Spam Detector...\n');

  // Test cases
  const testCases = [
    {
      text: "Halo, bagaimana kabarnya hari ini?",
      expected: "normal"
    },
    {
      text: "PROMO GILA! Diskon 90% untuk semua produk! WA 08123456789",
      expected: "spam"
    },
    {
      text: "Jual HP murah berkualitas, hubungi telegram @seller123",
      expected: "spam"
    },
    {
      text: "Terima kasih atas informasinya, sangat bermanfaat",
      expected: "normal"
    },
    {
      text: "GRATIS ONGKIR ke seluruh Indonesia! Pesan sekarang juga!",
      expected: "spam"
    },
    {
      text: "Selamat pagi, semoga hari ini menyenangkan",
      expected: "normal"
    }
  ];

  // Test dengan child_process mode
  console.log('=== Testing dengan Child Process Mode ===');
  const detectorCP = new SpamDetectorBridge({
    mode: 'child_process',
    timeout: 30000
  });

  for (let i = 0; i < testCases.length; i++) {
    const testCase = testCases[i];
    console.log(`\nTest ${i + 1}: "${testCase.text}"`);
    console.log(`Expected: ${testCase.expected}`);
    
    try {
      const result = await detectorCP.predict(testCase.text);
      console.log(`Predicted: ${result.label} (confidence: ${result.confidence.toFixed(3)})`);
      console.log(`Is Spam: ${result.is_spam}`);
      
      if (result.error) {
        console.log(`Error: ${result.error}`);
      }
    } catch (error) {
      console.error(`Error: ${error.message}`);
    }
  }

  // Test dengan HTTP mode (jika server tersedia)
  console.log('\n\n=== Testing dengan HTTP API Mode ===');
  const detectorHTTP = new SpamDetectorBridge({
    mode: 'http',
    apiUrl: 'http://localhost:5000',
    timeout: 30000
  });

  const isServerHealthy = await detectorHTTP.checkServerHealth();
  
  if (isServerHealthy) {
    console.log('HTTP API server is available, running tests...\n');
    
    for (let i = 0; i < testCases.length; i++) {
      const testCase = testCases[i];
      console.log(`\nTest ${i + 1}: "${testCase.text}"`);
      console.log(`Expected: ${testCase.expected}`);
      
      try {
        const result = await detectorHTTP.predict(testCase.text);
        console.log(`Predicted: ${result.label} (confidence: ${result.confidence.toFixed(3)})`);
        console.log(`Is Spam: ${result.is_spam}`);
        
        if (result.error) {
          console.log(`Error: ${result.error}`);
        }
      } catch (error) {
        console.error(`Error: ${error.message}`);
      }
    }

    // Test batch prediction
    console.log('\n=== Testing Batch Prediction ===');
    try {
      const texts = testCases.map(tc => tc.text);
      const results = await detectorHTTP.predictBatch(texts);
      
      console.log('Batch prediction results:');
      results.forEach((result, index) => {
        console.log(`${index + 1}. ${result.label} (${result.confidence.toFixed(3)})`);
      });
    } catch (error) {
      console.error(`Batch prediction error: ${error.message}`);
    }
  } else {
    console.log('HTTP API server not available. Start it with: node start_api_server.js');
  }

  console.log('\nTesting completed!');
}

// Run tests
testSpamDetector().catch(console.error);
