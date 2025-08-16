"""
Configuration management for the Movie & TV Telegram Bot
Handles environment variables and API keys
"""

import os
from typing import Optional

class Config:
    """Configuration class for managing environment variables and settings"""
    
    def __init__(self):
        # Telegram Bot Configuration
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_telegram_bot_token_here')
        
        # TMDB API Configuration
        self.TMDB_API_KEY = os.getenv('TMDB_API_KEY', 'your_tmdb_api_key_here')
        
        # OMDB API Configuration
        self.OMDB_API_KEY = os.getenv('OMDB_API_KEY', 'your_omdb_api_key_here')
        
        # YouTube API Configuration
        self.YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'your_youtube_api_key_here')
        
        # Flask Configuration
        self.FLASK_ENV = os.getenv('FLASK_ENV', 'production')
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        self.PORT = int(os.getenv('PORT', 5000))
        
        # Webhook Configuration
        self.WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
        
        # Data Storage Configuration
        self.DATA_DIR = os.getenv('DATA_DIR', 'data')
        
        # Rate Limiting Configuration
        self.RATE_LIMIT_PER_USER = int(os.getenv('RATE_LIMIT_PER_USER', 30))  # requests per minute
        
        # Cache Configuration
        self.CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 3600))  # 1 hour in seconds
        
        # Recommendation Configuration
        self.MAX_RECOMMENDATIONS = int(os.getenv('MAX_RECOMMENDATIONS', 10))
        self.MIN_VOTE_COUNT_MOVIES = int(os.getenv('MIN_VOTE_COUNT_MOVIES', 100))
        self.MIN_VOTE_COUNT_TV = int(os.getenv('MIN_VOTE_COUNT_TV', 50))
        
        # User Data Retention
        self.USER_DATA_RETENTION_DAYS = int(os.getenv('USER_DATA_RETENTION_DAYS', 90))
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required configuration is present"""
        required_vars = [
            ('TELEGRAM_BOT_TOKEN', self.TELEGRAM_BOT_TOKEN),
            ('TMDB_API_KEY', self.TMDB_API_KEY),
            ('OMDB_API_KEY', self.OMDB_API_KEY),
            ('YOUTUBE_API_KEY', self.YOUTUBE_API_KEY)
        ]
        
        missing_vars = []
        
        for var_name, var_value in required_vars:
            if not var_value or var_value.startswith('your_'):
                missing_vars.append(var_name)
        
        if missing_vars:
            print(f"Warning: Missing required environment variables: {', '.join(missing_vars)}")
            print("Please set these environment variables for the bot to work properly.")
    
    def get_telegram_bot_token(self) -> str:
        """Get Telegram bot token"""
        return self.TELEGRAM_BOT_TOKEN
    
    def get_tmdb_api_key(self) -> str:
        """Get TMDB API key"""
        return self.TMDB_API_KEY
    
    def get_omdb_api_key(self) -> str:
        """Get OMDB API key"""
        return self.OMDB_API_KEY
    
    def get_youtube_api_key(self) -> str:
        """Get YouTube API key"""
        return self.YOUTUBE_API_KEY
    
    def get_webhook_url(self) -> Optional[str]:
        """Get webhook URL"""
        return self.WEBHOOK_URL if self.WEBHOOK_URL else None
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return self.DEBUG
    
    def get_port(self) -> int:
        """Get application port"""
        return self.PORT
    
    def get_data_directory(self) -> str:
        """Get data directory path"""
        return self.DATA_DIR
    
    def get_rate_limit(self) -> int:
        """Get rate limit per user"""
        return self.RATE_LIMIT_PER_USER
    
    def get_cache_timeout(self) -> int:
        """Get cache timeout in seconds"""
        return self.CACHE_TIMEOUT
    
    def get_max_recommendations(self) -> int:
        """Get maximum number of recommendations to return"""
        return self.MAX_RECOMMENDATIONS
    
    def get_retention_days(self) -> int:
        """Get user data retention period in days"""
        return self.USER_DATA_RETENTION_DAYS
