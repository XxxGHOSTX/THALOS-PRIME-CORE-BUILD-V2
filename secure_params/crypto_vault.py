"""
Cryptographic Parameter Protection
Custom encryption for sensitive data
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import json
import hashlib as hl
import os


class SecureVault:
    """Encryption vault for parameters"""
    
    def __init__(self, master_secret=None):
        if master_secret is None:
            master_secret = self._gen_secret()
        
        self.master_secret = master_secret
        self.cipher = self._init_cipher(master_secret)
        self.enc_log = []
        
    def _gen_secret(self):
        """Generate secure secret"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    
    def _init_cipher(self, secret):
        """Initialize cipher"""
        
        secret_bytes = secret.encode('utf-8')
        salt_bytes = b'thalos_sbi_vault_salt'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,
            backend=default_backend()
        )
        
        key_derived = base64.urlsafe_b64encode(kdf.derive(secret_bytes))
        return Fernet(key_derived)
    
    def lock(self, data_obj):
        """Encrypt data"""
        
        json_txt = json.dumps(data_obj)
        data_bytes = json_txt.encode('utf-8')
        
        enc_bytes = self.cipher.encrypt(data_bytes)
        enc_txt = enc_bytes.decode('utf-8')
        
        # Log
        sig = hl.sha256(data_bytes).hexdigest()[:16]
        self.enc_log.append({
            'sig': sig,
            'orig_size': len(data_bytes),
            'enc_size': len(enc_bytes)
        })
        
        return enc_txt
    
    def unlock(self, enc_txt):
        """Decrypt data"""
        
        enc_bytes = enc_txt.encode('utf-8')
        dec_bytes = self.cipher.decrypt(enc_bytes)
        
        json_txt = dec_bytes.decode('utf-8')
        data_obj = json.loads(json_txt)
        
        return data_obj
    
    def lock_dict(self, data_dict):
        """Encrypt dictionary"""
        
        enc_dict = {}
        
        for k, v in data_dict.items():
            enc_dict[k] = self.lock(v)
            
        return enc_dict
    
    def unlock_dict(self, enc_dict):
        """Decrypt dictionary"""
        
        dec_dict = {}
        
        for k, enc_v in enc_dict.items():
            dec_dict[k] = self.unlock(enc_v)
            
        return dec_dict
    
    def gen_token(self, ident):
        """Generate secure token"""
        
        token_data = {
            'ident': ident,
            'nonce': os.urandom(16).hex()
        }
        
        return self.lock(token_data)
    
    def verify_token(self, token, expected_ident):
        """Verify token"""
        
        try:
            token_data = self.unlock(token)
            return token_data.get('ident') == expected_ident
        except:
            return False
    
    def vault_stats(self):
        """Get vault statistics"""
        
        total_enc = len(self.enc_log)
        total_orig = sum(log['orig_size'] for log in self.enc_log)
        total_enc_bytes = sum(log['enc_size'] for log in self.enc_log)
        
        return {
            'encrypted': total_enc,
            'orig_bytes': total_orig,
            'enc_bytes': total_enc_bytes,
            'overhead': (total_enc_bytes - total_orig) if total_orig > 0 else 0
        }
