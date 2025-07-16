#!/usr/bin/env python3
"""
Application Configuration
Centralized configuration management for the Judol Remover application
"""

import os
from pathlib import Path

class AppConfig:
    """Application configuration class"""
    
    def __init__(self):
        """Initialize configuration with default values"""
        # Get project root directory
        self.project_root = Path(__file__).parent.parent
        
        # Load environment variables
        self.load_environment()
        
        # Set default paths
        self.setup_paths()
    
    def load_environment(self):
        """Load environment variables with defaults"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # Facebook Configuration
        self.page_id = os.getenv('PAGE_ID')
        self.page_access_token = os.getenv('PAGE_ACCESS_TOKEN')
        
        # Model Configuration
        self.model_path = os.getenv('MODEL_PATH', './src/models')
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', '0.8'))
        
        # Auto Delete Configuration
        self.auto_delete_enabled = os.getenv('AUTO_DELETE_SPAM', 'true').lower() == 'true'
        
        # Debug Configuration
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    def setup_paths(self):
        """Setup application paths"""
        # Convert relative paths to absolute paths
        if self.model_path.startswith('./'):
            self.model_path = str(self.project_root / self.model_path[2:])
        
        # Ensure model path exists
        model_path_obj = Path(self.model_path)
        if not model_path_obj.exists():
            print(f"⚠️ Model path does not exist: {self.model_path}")
    
    def validate_config(self):
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check Facebook credentials
        if not self.page_id:
            issues.append("PAGE_ID is not set")
        if not self.page_access_token:
            issues.append("PAGE_ACCESS_TOKEN is not set")
        
        # Check model files
        model_path = Path(self.model_path)
        required_files = [
            "config.json",
            "model.safetensors", 
            "tokenizer_config.json",
            "vocab.txt"
        ]
        
        for file in required_files:
            if not (model_path / file).exists():
                issues.append(f"Model file missing: {file}")
        
        return issues
    
    def get_config_dict(self):
        """Get configuration as dictionary"""
        return {
            'page_id': self.page_id,
            'page_access_token': self.page_access_token,
            'model_path': self.model_path,
            'confidence_threshold': self.confidence_threshold,
            'auto_delete_enabled': self.auto_delete_enabled,
            'debug': self.debug
        }

# Global configuration instance
config = AppConfig()
