#!/usr/bin/env python3
"""
Facebook API wrapper for Streamlit application
Handles Facebook Graph API calls for posts and comments
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import streamlit as st

class FacebookAPI:
    def __init__(self, page_id: str, access_token: str):
        """
        Initialize Facebook API wrapper
        
        Args:
            page_id (str): Facebook page ID
            access_token (str): Page access token
        """
        self.page_id = page_id
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.session = requests.Session()
        
        # Test connection
        self.test_connection()
    
    def test_connection(self):
        """Test Facebook API connection"""
        try:
            response = self.session.get(
                f"{self.base_url}/me",
                params={'access_token': self.access_token}
            )
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                raise Exception(f"Facebook API Error: {data['error']['message']}")
                
            st.success(f"✅ Connected to Facebook as: {data.get('name', 'Unknown')}")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Facebook API: {str(e)}")
        except Exception as e:
            raise Exception(f"Facebook API connection error: {str(e)}")
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """
        Get recent posts from the Facebook page
        
        Args:
            limit (int): Number of posts to retrieve
            
        Returns:
            List[Dict]: List of post data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{self.page_id}/posts",
                params={
                    'access_token': self.access_token,
                    'fields': 'id,message,created_time,updated_time,permalink_url',
                    'limit': limit
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                raise Exception(f"Facebook API Error: {data['error']['message']}")
            
            posts = data.get('data', [])
            
            # Format timestamps
            for post in posts:
                if 'created_time' in post:
                    post['created_time'] = self.format_timestamp(post['created_time'])
                if 'updated_time' in post:
                    post['updated_time'] = self.format_timestamp(post['updated_time'])
            
            return posts
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get posts: {str(e)}")
        except Exception as e:
            raise Exception(f"Error getting posts: {str(e)}")
    
    def get_post_comments(self, post_id: str, limit: int = 20) -> List[Dict]:
        """
        Get comments for a specific post
        
        Args:
            post_id (str): Facebook post ID
            limit (int): Number of comments to retrieve
            
        Returns:
            List[Dict]: List of comment data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{post_id}/comments",
                params={
                    'access_token': self.access_token,
                    'fields': 'id,message,created_time,from{id,name},like_count,comment_count',
                    'limit': limit,
                    'order': 'reverse_chronological'
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                raise Exception(f"Facebook API Error: {data['error']['message']}")
            
            comments = data.get('data', [])
            
            # Format timestamps
            for comment in comments:
                if 'created_time' in comment:
                    comment['created_time'] = self.format_timestamp(comment['created_time'])
            
            return comments
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get comments: {str(e)}")
        except Exception as e:
            raise Exception(f"Error getting comments: {str(e)}")
    
    def delete_comment(self, comment_id: str) -> bool:
        """
        Delete a comment
        
        Args:
            comment_id (str): Facebook comment ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self.session.delete(
                f"{self.base_url}/{comment_id}",
                params={'access_token': self.access_token}
            )
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                st.error(f"Facebook API Error: {data['error']['message']}")
                return False
            
            # Facebook returns {"success": true} for successful deletions
            return data.get('success', False) or response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to delete comment: {str(e)}")
            return False
        except Exception as e:
            st.error(f"Error deleting comment: {str(e)}")
            return False
    
    def get_comment_details(self, comment_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific comment
        
        Args:
            comment_id (str): Facebook comment ID
            
        Returns:
            Optional[Dict]: Comment details or None if not found
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{comment_id}",
                params={
                    'access_token': self.access_token,
                    'fields': 'id,message,created_time,updated_time,from{id,name,picture},like_count,comment_count,parent'
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                return None
            
            # Format timestamps
            if 'created_time' in data:
                data['created_time'] = self.format_timestamp(data['created_time'])
            if 'updated_time' in data:
                data['updated_time'] = self.format_timestamp(data['updated_time'])
            
            return data
            
        except Exception as e:
            st.error(f"Error getting comment details: {str(e)}")
            return None
    
    def search_comments(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Search for comments containing specific text
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            List[Dict]: List of matching comments
        """
        try:
            # Get recent posts first
            posts = self.get_recent_posts(limit=10)
            matching_comments = []
            
            for post in posts:
                comments = self.get_post_comments(post['id'], limit=20)
                
                for comment in comments:
                    message = comment.get('message', '').lower()
                    if query.lower() in message:
                        comment['post_id'] = post['id']
                        comment['post_message'] = post.get('message', '')[:100]
                        matching_comments.append(comment)
                        
                        if len(matching_comments) >= limit:
                            return matching_comments
            
            return matching_comments
            
        except Exception as e:
            st.error(f"Error searching comments: {str(e)}")
            return []
    
    def get_page_info(self) -> Optional[Dict]:
        """
        Get information about the Facebook page
        
        Returns:
            Optional[Dict]: Page information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{self.page_id}",
                params={
                    'access_token': self.access_token,
                    'fields': 'id,name,category,fan_count,talking_about_count,picture'
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                return None
            
            return data
            
        except Exception as e:
            st.error(f"Error getting page info: {str(e)}")
            return None
    
    def format_timestamp(self, timestamp_str: str) -> str:
        """
        Format Facebook timestamp to readable format
        
        Args:
            timestamp_str (str): Facebook timestamp string
            
        Returns:
            str: Formatted timestamp
        """
        try:
            # Facebook timestamps are in ISO format
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return timestamp_str
    
    def get_insights(self, metric: str = 'page_impressions', period: str = 'day') -> Optional[Dict]:
        """
        Get page insights/analytics
        
        Args:
            metric (str): Metric to retrieve
            period (str): Time period (day, week, days_28)
            
        Returns:
            Optional[Dict]: Insights data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{self.page_id}/insights",
                params={
                    'access_token': self.access_token,
                    'metric': metric,
                    'period': period
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                return None
            
            return data
            
        except Exception as e:
            st.error(f"Error getting insights: {str(e)}")
            return None
    
    def batch_delete_comments(self, comment_ids: List[str]) -> Dict[str, bool]:
        """
        Delete multiple comments in batch
        
        Args:
            comment_ids (List[str]): List of comment IDs to delete
            
        Returns:
            Dict[str, bool]: Results for each comment ID
        """
        results = {}
        
        for comment_id in comment_ids:
            try:
                success = self.delete_comment(comment_id)
                results[comment_id] = success
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.5)
                
            except Exception as e:
                st.error(f"Error deleting comment {comment_id}: {str(e)}")
                results[comment_id] = False
        
        return results
    
    def get_comment_replies(self, comment_id: str, limit: int = 10) -> List[Dict]:
        """
        Get replies to a specific comment
        
        Args:
            comment_id (str): Parent comment ID
            limit (int): Number of replies to retrieve
            
        Returns:
            List[Dict]: List of reply data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{comment_id}/comments",
                params={
                    'access_token': self.access_token,
                    'fields': 'id,message,created_time,from{id,name}',
                    'limit': limit
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                return []
            
            replies = data.get('data', [])
            
            # Format timestamps
            for reply in replies:
                if 'created_time' in reply:
                    reply['created_time'] = self.format_timestamp(reply['created_time'])
            
            return replies
            
        except Exception as e:
            st.error(f"Error getting comment replies: {str(e)}")
            return []
