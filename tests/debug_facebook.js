#!/usr/bin/env node
/**
 * Debug script untuk mengecek koneksi Facebook API
 */

const FB = require('fb');
require('dotenv').config();

async function debugFacebookAPI() {
  console.log('🔍 Debugging Facebook API Connection...\n');

  const pageId = process.env.PAGE_ID;
  const accessToken = process.env.PAGE_ACCESS_TOKEN;

  console.log(`📄 Page ID: ${pageId}`);
  console.log(`🔑 Access Token: ${accessToken ? accessToken.substring(0, 20) + '...' : 'NOT SET'}\n`);

  if (!pageId || !accessToken) {
    console.error('❌ PAGE_ID atau PAGE_ACCESS_TOKEN tidak ditemukan di .env');
    return;
  }

  FB.setAccessToken(accessToken);

  // Test 1: Cek informasi page
  console.log('📋 Test 1: Getting page information...');
  try {
    const pageInfo = await new Promise((resolve, reject) => {
      FB.api(pageId, { fields: ['id', 'name', 'category', 'access_token'] }, (response) => {
        if (response && !response.error) {
          resolve(response);
        } else {
          reject(response.error);
        }
      });
    });

    console.log('✅ Page Info:');
    console.log(`   - ID: ${pageInfo.id}`);
    console.log(`   - Name: ${pageInfo.name}`);
    console.log(`   - Category: ${pageInfo.category}`);
    console.log('');

  } catch (error) {
    console.error('❌ Error getting page info:', error);
    console.log('');
  }

  // Test 2: Cek posts
  console.log('📝 Test 2: Getting recent posts...');
  try {
    const postsResponse = await new Promise((resolve, reject) => {
      FB.api(`${pageId}/posts`, { 
        fields: ['id', 'message', 'created_time'],
        limit: 5
      }, (response) => {
        if (response && !response.error) {
          resolve(response);
        } else {
          reject(response.error);
        }
      });
    });

    if (postsResponse.data && postsResponse.data.length > 0) {
      console.log(`✅ Found ${postsResponse.data.length} posts:`);
      postsResponse.data.forEach((post, index) => {
        console.log(`   ${index + 1}. Post ID: ${post.id}`);
        console.log(`      Created: ${post.created_time}`);
        console.log(`      Message: ${post.message ? post.message.substring(0, 50) + '...' : 'No message'}`);
      });
      console.log('');

      // Test 3: Cek comments pada post pertama
      const firstPost = postsResponse.data[0];
      console.log(`💬 Test 3: Getting comments for post ${firstPost.id}...`);
      
      try {
        const commentsResponse = await new Promise((resolve, reject) => {
          FB.api(`${firstPost.id}/comments`, {
            fields: ['id', 'message', 'created_time', 'from'],
            limit: 10
          }, (response) => {
            if (response && !response.error) {
              resolve(response);
            } else {
              reject(response.error);
            }
          });
        });

        if (commentsResponse.data && commentsResponse.data.length > 0) {
          console.log(`✅ Found ${commentsResponse.data.length} comments:`);
          commentsResponse.data.forEach((comment, index) => {
            console.log(`   ${index + 1}. Comment ID: ${comment.id}`);
            console.log(`      From: ${comment.from?.name || 'Unknown'}`);
            console.log(`      Created: ${comment.created_time}`);
            console.log(`      Message: ${comment.message ? comment.message.substring(0, 50) + '...' : 'No message'}`);
          });
        } else {
          console.log('📭 No comments found on this post');
        }
        console.log('');

      } catch (error) {
        console.error('❌ Error getting comments:', error);
        console.log('');
      }

    } else {
      console.log('📭 No posts found');
      console.log('');
    }

  } catch (error) {
    console.error('❌ Error getting posts:', error);
    console.log('');
  }

  // Test 4: Cek permissions
  console.log('🔐 Test 4: Checking token permissions...');
  try {
    const permissionsResponse = await new Promise((resolve, reject) => {
      FB.api('/me/permissions', (response) => {
        if (response && !response.error) {
          resolve(response);
        } else {
          reject(response.error);
        }
      });
    });

    if (permissionsResponse.data) {
      console.log('✅ Token permissions:');
      permissionsResponse.data.forEach(perm => {
        console.log(`   - ${perm.permission}: ${perm.status}`);
      });
    }
    console.log('');

  } catch (error) {
    console.error('❌ Error getting permissions:', error);
    console.log('');
  }

  // Test 5: Cek dengan timestamp filter
  console.log('⏰ Test 5: Getting recent posts with timestamp filter...');
  try {
    const now = Math.floor(Date.now() / 1000);
    const oneHourAgo = now - 3600; // 1 jam yang lalu

    const recentPostsResponse = await new Promise((resolve, reject) => {
      FB.api(`${pageId}/posts`, { 
        fields: ['id', 'message', 'created_time'],
        since: oneHourAgo,
        limit: 10
      }, (response) => {
        if (response && !response.error) {
          resolve(response);
        } else {
          reject(response.error);
        }
      });
    });

    if (recentPostsResponse.data && recentPostsResponse.data.length > 0) {
      console.log(`✅ Found ${recentPostsResponse.data.length} posts in last hour:`);
      recentPostsResponse.data.forEach((post, index) => {
        console.log(`   ${index + 1}. Post ID: ${post.id} (${post.created_time})`);
      });
    } else {
      console.log('📭 No posts found in the last hour');
    }
    console.log('');

  } catch (error) {
    console.error('❌ Error getting recent posts:', error);
    console.log('');
  }

  console.log('🏁 Debug completed!');
  console.log('\n📋 Recommendations:');
  console.log('1. Make sure you have the correct Page ID (not Profile ID)');
  console.log('2. Ensure your access token has the required permissions');
  console.log('3. Try posting a new comment and run this debug again');
  console.log('4. Check if the page is a Facebook Page (not a personal profile)');
}

// Run debug
debugFacebookAPI().catch(console.error);
