"""Configuration management for memory system"""
import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Constants for memory store types
STORE_TYPE_JSON = "json"

class Config:
    """Configuration settings for memory management"""
    
    def __init__(self):
        """Initialize configuration with environment variables and defaults"""
        # Environment and debug settings
        self.ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
        self.DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
        
        # Storage configuration - JSON storage
        self.MEMORY_STORE_TYPE = STORE_TYPE_JSON  # Always JSON
        self.DATA_DIR = os.environ.get("DATA_DIR", "./user_data")
        
        # Ensure data directory exists
        Path(self.DATA_DIR).mkdir(parents=True, exist_ok=True)
        
        # Memory settings
        self.MAX_MESSAGES = int(os.environ.get("MAX_MESSAGES", "100"))  # Increased to 100 as requested
        self.MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", "100000"))
        
        # Security settings
        self.SECURITY_LEVEL = os.environ.get("SECURITY_LEVEL", "medium")
        self.ENCRYPTION_ENABLED = os.environ.get("ENCRYPTION_ENABLED", "false").lower() == "true"
        self.ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
        
        # Performance settings
        self.CACHE_ENABLED = os.environ.get("CACHE_ENABLED", "true").lower() == "true"
        self.CACHE_TTL = int(os.environ.get("CACHE_TTL", "3600"))
        
        # Rate limiting
        self.RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", "100"))
        self.RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "3600"))
        
        # Feature flags
        self.FEATURES = {
            "fact_extraction": os.environ.get("FEATURE_FACT_EXTRACTION", "true").lower() == "true",
            "streak_tracking": os.environ.get("FEATURE_STREAK_TRACKING", "true").lower() == "true",
            "metrics_collection": os.environ.get("FEATURE_METRICS", "true").lower() == "true",
            "context_analysis": os.environ.get("FEATURE_CONTEXT_ANALYSIS", "true").lower() == "true"
        }
        
        # Security settings
        self.SECURITY_SETTINGS = {
            "input_validation": True,
            "xss_protection": True,
            "sanitize_inputs": True,
            "anonymize_data": True,
            "secure_headers": True,
            "encryption": self.ENCRYPTION_ENABLED
        }
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format"""
        return {
            "environment": self.ENVIRONMENT,
            "debug": self.DEBUG,
            "store_type": self.MEMORY_STORE_TYPE,
            "data_dir": self.DATA_DIR,
            "max_messages": self.MAX_MESSAGES,
            "max_content_length": self.MAX_CONTENT_LENGTH,
            "security_level": self.SECURITY_LEVEL,
            "encryption_enabled": self.ENCRYPTION_ENABLED,
            "features": self.FEATURES,
            "security": self.SECURITY_SETTINGS
        }
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        for key, value in config_dict.items():
            if hasattr(self, key.upper()):
                setattr(self, key.upper(), value)
            elif isinstance(value, dict):
                # Handle nested dictionaries (features, security settings)
                current_value = getattr(self, key.upper(), {})
                if isinstance(current_value, dict):
                    current_value.update(value)
                    setattr(self, key.upper(), current_value)

# Global configuration instance
_config: Optional[Config] = None

def get_config() -> Config:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config

def initialize(config_override: Optional[Dict[str, Any]] = None) -> None:
    """Initialize configuration with optional overrides"""
    global _config
    _config = Config()
    
    if config_override:
        _config.update(config_override)
    
    logger.info(
        "Configuration initialized with environment=%s, data_dir=%s",
        _config.ENVIRONMENT,
        _config.DATA_DIR
    )