import streamlit as st
from database import DatabaseManager
from typing import Optional, Dict
import hashlib
import time

class UserManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_current_user(self) -> Optional[str]:
        """Get current logged in user"""
        return st.session_state.get('current_user', None)
    
    def login_user(self, username: str) -> bool:
        """Simple login (username only for this demo)"""
        try:
            player = self.db.get_player(username)
            if not player:
                player = self.db.create_player(username)
            
            st.session_state['current_user'] = username
            st.session_state['current_player_id'] = player.id
            return True
        except Exception as e:
            st.error(f"Login failed: {e}")
            return False
    
    def logout_user(self):
        """Logout current user"""
        if 'current_user' in st.session_state:
            del st.session_state['current_user']
        if 'current_player_id' in st.session_state:
            del st.session_state['current_player_id']
    
    def render_login_form(self):
        """Render login form in sidebar"""
        current_user = self.get_current_user()
        
        if current_user:
            st.sidebar.success(f"Logged in as: {current_user}")
            if st.sidebar.button("Logout"):
                self.logout_user()
                st.rerun()
        else:
            st.sidebar.subheader("Player Login")
            username = st.sidebar.text_input("Username:", key="login_username")
            
            if st.sidebar.button("Login/Register"):
                if username:
                    if self.login_user(username):
                        st.sidebar.success(f"Welcome, {username}!")
                        st.rerun()
                else:
                    st.sidebar.error("Please enter a username")
    
    def get_player_stats(self, username: str) -> Dict:
        """Get comprehensive player statistics"""
        try:
            player = self.db.get_player(username)
            if not player:
                return {}
            
            return self.db.get_player_statistics(player.id)
        except Exception as e:
            st.error(f"Error fetching player stats: {e}")
            return {}
    
    def get_session_history(self, username: str, limit: int = 10) -> list:
        """Get player's session history"""
        try:
            player = self.db.get_player(username)
            if not player:
                return []
            
            return self.db.get_session_history(player.id, limit)
        except Exception as e:
            st.error(f"Error fetching session history: {e}")
            return []