"""
Encryption utilities for sensitive data.

This module provides encryption and decryption functions for securing
sensitive user data in both database and JSON storage systems.
"""
import os
import base64
import logging
from typing import Any, Dict, Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

# Salt for key derivation - this should be stored securely in production
DEFAULT_SALT = b'elysia_secure_salt_value'


class CryptoManager:
    """Manager for encrypting and decrypting sensitive data."""
    
    def __init__(self, encryption_key: Optional[str] = None, salt: Optional[bytes] = None):
        """
        Initialize the crypto manager.
        
        Args:
            encryption_key: The encryption key provided by chatbot.py
            salt: Salt for key derivation (uses default if None)
        """
        self.encryption_key = encryption_key
        self.salt = salt or DEFAULT_SALT
        self.cipher = None
        
        if encryption_key:
            self._setup_cipher()
    
    def _setup_cipher(self) -> None:
        """Set up the encryption cipher from the provided key."""
        try:
            # Use PBKDF2 to derive a secure key from the provided encryption key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
            )
            
            # Convert the string key to bytes
            key_bytes = self.encryption_key.encode('utf-8')
            
            # Derive the key
            key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
            
            # Create Fernet cipher for encryption/decryption
            self.cipher = Fernet(key)
            logger.info("Encryption cipher successfully initialized")
        except Exception as e:
            logger.error(f"Failed to set up encryption cipher: {str(e)}")
            self.cipher = None
    
    def set_encryption_key(self, encryption_key: str) -> bool:
        """
        Set or update the encryption key.
        
        Args:
            encryption_key: The new encryption key
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.encryption_key = encryption_key
            self._setup_cipher()
            return self.cipher is not None
        except Exception as e:
            logger.error(f"Failed to set encryption key: {str(e)}")
            return False
    
    def encrypt(self, data: Union[str, bytes, Dict, Any]) -> Optional[bytes]:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt (string, bytes, or JSON-serializable object)
            
        Returns:
            bytes: Encrypted data as bytes or None if encryption fails
        """
        if not self.cipher:
            logger.warning("Encryption attempted without initialized cipher")
            return None
        
        try:
            # Convert data to string if it's not already bytes
            if isinstance(data, bytes):
                data_bytes = data
            elif isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                # Serialize dict or other objects to JSON string
                import json
                data_bytes = json.dumps(data).encode('utf-8')
            
            # Encrypt the data
            encrypted_data = self.cipher.encrypt(data_bytes)
            return encrypted_data
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            return None
    
    def decrypt(self, encrypted_data: bytes, as_json: bool = False) -> Optional[Any]:
        """
        Decrypt data.
        
        Args:
            encrypted_data: The encrypted data to decrypt
            as_json: Whether to parse the decrypted data as JSON
            
        Returns:
            The decrypted data (string, or parsed JSON object if as_json=True)
        """
        if not self.cipher:
            logger.warning("Decryption attempted without initialized cipher")
            return None
        
        try:
            # Decrypt the data
            decrypted_bytes = self.cipher.decrypt(encrypted_data)
            
            # Convert back to original format
            if as_json:
                import json
                return json.loads(decrypted_bytes.decode('utf-8'))
            else:
                return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            return None
    
    def encrypt_dict_values(self, data_dict: Dict[str, Any], 
                          sensitive_keys: Optional[list] = None) -> Dict[str, Any]:
        """
        Encrypt specific values in a dictionary based on sensitive keys.
        
        Args:
            data_dict: Dictionary containing data to selectively encrypt
            sensitive_keys: List of keys identifying sensitive values to encrypt
            
        Returns:
            Dictionary with sensitive values encrypted
        """
        if not sensitive_keys or not self.cipher:
            return data_dict.copy()
        
        result = {}
        for key, value in data_dict.items():
            if key in sensitive_keys and value is not None:
                # Encrypt sensitive values
                encrypted_value = self.encrypt(value)
                if encrypted_value:
                    # Store as base64 string for easier storage
                    result[key] = {
                        '__encrypted': True,
                        'data': base64.b64encode(encrypted_value).decode('utf-8')
                    }
                else:
                    # Fall back to original value if encryption fails
                    result[key] = value
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                result[key] = self.encrypt_dict_values(value, sensitive_keys)
            else:
                # Keep non-sensitive values as is
                result[key] = value
        
        return result
    
    def decrypt_dict_values(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt values in a dictionary that have been encrypted.
        
        Args:
            data_dict: Dictionary that may contain encrypted values
            
        Returns:
            Dictionary with encrypted values decrypted
        """
        if not self.cipher:
            return data_dict.copy()
        
        result = {}
        for key, value in data_dict.items():
            if isinstance(value, dict):
                if value.get('__encrypted') is True and 'data' in value:
                    # Decrypt this specific value
                    try:
                        encrypted_bytes = base64.b64decode(value['data'])
                        decrypted_value = self.decrypt(encrypted_bytes, as_json=False)
                        result[key] = decrypted_value
                    except Exception as e:
                        logger.error(f"Failed to decrypt field {key}: {str(e)}")
                        result[key] = value
                else:
                    # Recursively process nested dictionaries
                    result[key] = self.decrypt_dict_values(value)
            else:
                # Keep already decrypted values as is
                result[key] = value
        
        return result


# Global instance for use throughout the application
crypto_manager = CryptoManager()


def set_encryption_key(key: str) -> bool:
    """
    Set the global encryption key.
    
    Args:
        key: The encryption key to use
        
    Returns:
        bool: Whether the key was successfully set
    """
    return crypto_manager.set_encryption_key(key)


def encrypt_sensitive_data(data: Any, sensitive_keys: Optional[list] = None) -> Any:
    """
    Encrypt sensitive data in the provided data structure.
    
    Args:
        data: Data to encrypt (can be a dictionary or a simple value)
        sensitive_keys: List of keys that should be encrypted in dictionaries
        
    Returns:
        Data with sensitive parts encrypted
    """
    if isinstance(data, dict):
        return crypto_manager.encrypt_dict_values(data, sensitive_keys)
    else:
        encrypted = crypto_manager.encrypt(data)
        if encrypted:
            return {
                '__encrypted': True,
                'data': base64.b64encode(encrypted).decode('utf-8')
            }
        return data


def decrypt_sensitive_data(data: Any) -> Any:
    """
    Decrypt sensitive data in the provided data structure.
    
    Args:
        data: Data to decrypt (can be a dictionary or an encrypted value)
        
    Returns:
        Decrypted data
    """
    if isinstance(data, dict):
        if data.get('__encrypted') is True and 'data' in data:
            try:
                encrypted_bytes = base64.b64decode(data['data'])
                return crypto_manager.decrypt(encrypted_bytes)
            except Exception as e:
                logger.error(f"Failed to decrypt data: {str(e)}")
                return data
        else:
            return crypto_manager.decrypt_dict_values(data)
    return data


# Default list of keys that should be considered sensitive
DEFAULT_SENSITIVE_KEYS = [
    'password', 
    'api_key', 
    'secret', 
    'token', 
    'credit_card',
    'ssn', 
    'address',
    'phone',
    'email'
] 