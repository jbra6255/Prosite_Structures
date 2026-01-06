import sqlite3
import hashlib
from datetime import datetime
from typing import Optional
from models import User
from logging import Logger

class UserRepository: 
    def create_user(self, username: str, email: str, password: str) -> Optional[User]:
        """Create a new user account"""
        try:
            # Hash the password
            password_hash = self._hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (username, email, password_hash, now))
                
                user_id = cursor.lastrowid
                return User(id=user_id, username=username, email=email)
        except sqlite3.IntegrityError:
            # Username or email already exists
            return None
        except sqlite3.Error as e:
            print(f"Error creating user: {e}")
            return None
            
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user by username
                cursor.execute('''
                    SELECT id, username, email, password_hash FROM users
                    WHERE username = ?
                ''', (username,))
                
                user_row = cursor.fetchone()
                if not user_row:
                    return None
                    
                # Verify password
                stored_hash = user_row[3]
                if self._verify_password(password, stored_hash):
                    return User(id=user_row[0], username=user_row[1], email=user_row[2])
                    
                return None
        except sqlite3.Error as e:
            print(f"Error authenticating user: {e}")
            return None
            
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email FROM users
                    WHERE username = ?
                ''', (username,))
                
                user_row = cursor.fetchone()
                if user_row:
                    return User(id=user_row[0], username=user_row[1], email=user_row[2])
                return None
        except sqlite3.Error as e:
            print(f"Error getting user: {e}")
            return None
            
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against a hash"""
        return self._hash_password(password) == password_hash