"""
Authentication module for user management
Simple authentication system with session management
"""

import streamlit as st
import hashlib
import sqlite3
from typing import Dict, Optional
import os

class AuthManager:
    """Handles user authentication and session management"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize user database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, name: str) -> bool:
        """Create new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, name))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            return False  # User already exists
        except Exception as e:
            st.error(f"Error creating user: {str(e)}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, username, email, name FROM users
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'name': user[3]
                }
            return None
            
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return None
    
    def show_login_form(self) -> bool:
        """Display login form and handle authentication"""
        with st.form("login_form"):
            st.subheader("Sign In")
            
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Sign In", use_container_width=True):
                if username and password:
                    user = self.authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.success("Login successful!")
                        return True
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please fill in all fields")
        
        return False
    
    def show_signup_form(self) -> bool:
        """Display signup form and handle registration"""
        with st.form("signup_form"):
            st.subheader("Create Account")
            
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Create Account", use_container_width=True):
                if all([name, email, username, password, confirm_password]):
                    if password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        if self.create_user(username, email, password, name):
                            st.success("Account created successfully!")
                            return True
                        else:
                            st.error("Username or email already exists")
                else:
                    st.error("Please fill in all fields")
        
        return False
    
    def get_current_user(self) -> Dict:
        """Get current authenticated user"""
        return st.session_state.get('user', {})
    
    def logout(self):
        """Logout current user"""
        if 'user' in st.session_state:
            del st.session_state.user
        st.session_state.authenticated = False