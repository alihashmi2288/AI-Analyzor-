"""
Storage module for database operations and file management
Handles analysis history and user data persistence
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st

class StorageManager:
    """Handles data storage and retrieval operations"""
    
    def __init__(self, db_path: str = "resume_analyzer.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize application database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analysis history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                analysis_data TEXT NOT NULL,
                job_title TEXT,
                company_name TEXT,
                similarity_score REAL,
                ats_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Resume storage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_content BLOB,
                text_content TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Job descriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT,
                company TEXT,
                description_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                preferences TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_analysis(self, user_id: int, results: Dict, job_title: str = "", company_name: str = "") -> bool:
        """Save analysis results to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            analysis_json = json.dumps(results)
            similarity_score = results.get('similarity_score', 0)
            ats_score = results.get('ats_score', 0)
            
            cursor.execute('''
                INSERT INTO analysis_history 
                (user_id, analysis_data, job_title, company_name, similarity_score, ats_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, analysis_json, job_title, company_name, similarity_score, ats_score))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error saving analysis: {str(e)}")
            return False
    
    def get_user_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's analysis history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, analysis_data, job_title, company_name, 
                       similarity_score, ats_score, created_at
                FROM analysis_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            history = []
            for row in cursor.fetchall():
                try:
                    analysis_data = json.loads(row[1])
                except json.JSONDecodeError:
                    analysis_data = {}
                
                history.append({
                    'id': row[0],
                    'results': analysis_data,
                    'job_title': row[2] or 'Untitled',
                    'company_name': row[3] or 'Unknown',
                    'similarity_score': row[4],
                    'ats_score': row[5],
                    'date': row[6]
                })
            
            conn.close()
            return history
            
        except Exception as e:
            st.error(f"Error retrieving history: {str(e)}")
            return []
    
    def save_resume(self, user_id: int, filename: str, file_content: bytes, text_content: str) -> bool:
        """Save resume file and extracted text"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO resumes (user_id, filename, file_content, text_content)
                VALUES (?, ?, ?, ?)
            ''', (user_id, filename, file_content, text_content))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error saving resume: {str(e)}")
            return False
    
    def get_user_resumes(self, user_id: int) -> List[Dict]:
        """Get user's saved resumes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, filename, upload_date
                FROM resumes
                WHERE user_id = ?
                ORDER BY upload_date DESC
            ''', (user_id,))
            
            resumes = []
            for row in cursor.fetchall():
                resumes.append({
                    'id': row[0],
                    'filename': row[1],
                    'upload_date': row[2]
                })
            
            conn.close()
            return resumes
            
        except Exception as e:
            st.error(f"Error retrieving resumes: {str(e)}")
            return []
    
    def save_job_description(self, user_id: int, title: str, company: str, description: str) -> bool:
        """Save job description"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO job_descriptions (user_id, title, company, description_text)
                VALUES (?, ?, ?, ?)
            ''', (user_id, title, company, description))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error saving job description: {str(e)}")
            return False
    
    def get_user_job_descriptions(self, user_id: int) -> List[Dict]:
        """Get user's saved job descriptions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, company, created_at
                FROM job_descriptions
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            job_descriptions = []
            for row in cursor.fetchall():
                job_descriptions.append({
                    'id': row[0],
                    'title': row[1] or 'Untitled',
                    'company': row[2] or 'Unknown',
                    'created_at': row[3]
                })
            
            conn.close()
            return job_descriptions
            
        except Exception as e:
            st.error(f"Error retrieving job descriptions: {str(e)}")
            return []
    
    def save_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        """Save user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            preferences_json = json.dumps(preferences)
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (user_id, preferences)
                VALUES (?, ?)
            ''', (user_id, preferences_json))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error saving preferences: {str(e)}")
            return False
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """Get user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT preferences FROM user_preferences WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            else:
                # Return default preferences
                return {
                    'analysis_depth': 'standard',
                    'include_ats': True,
                    'include_semantic': True,
                    'include_suggestions': True,
                    'theme': 'light'
                }
                
        except Exception as e:
            st.error(f"Error retrieving preferences: {str(e)}")
            return {}
    
    def delete_analysis(self, user_id: int, analysis_id: int) -> bool:
        """Delete specific analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM analysis_history 
                WHERE id = ? AND user_id = ?
            ''', (analysis_id, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error deleting analysis: {str(e)}")
            return False
    
    def get_analysis_stats(self, user_id: int) -> Dict:
        """Get user's analysis statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total analyses
            cursor.execute('SELECT COUNT(*) FROM analysis_history WHERE user_id = ?', (user_id,))
            total_analyses = cursor.fetchone()[0]
            
            # Average scores
            cursor.execute('''
                SELECT AVG(similarity_score), AVG(ats_score)
                FROM analysis_history 
                WHERE user_id = ? AND similarity_score IS NOT NULL
            ''', (user_id,))
            
            avg_scores = cursor.fetchone()
            avg_similarity = avg_scores[0] if avg_scores[0] else 0
            avg_ats = avg_scores[1] if avg_scores[1] else 0
            
            # Recent activity
            cursor.execute('''
                SELECT COUNT(*) FROM analysis_history 
                WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
            ''', (user_id,))
            recent_activity = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_analyses': total_analyses,
                'avg_similarity_score': round(avg_similarity, 1),
                'avg_ats_score': round(avg_ats, 1),
                'recent_activity': recent_activity
            }
            
        except Exception as e:
            st.error(f"Error retrieving stats: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old data (optional maintenance function)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM analysis_history 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error cleaning up data: {str(e)}")
            return False