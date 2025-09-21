import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('resumeai.db')

print("=== ALL USERS ===")
users = pd.read_sql_query("SELECT id, username, email, created_at FROM users", conn)
print(users)

print("\n=== USER SESSIONS COUNT ===")
sessions_count = pd.read_sql_query("""
    SELECT u.username, u.email, COUNT(s.id) as total_sessions
    FROM users u 
    LEFT JOIN sessions s ON u.id = s.user_id 
    GROUP BY u.id, u.username, u.email
""", conn)
print(sessions_count)

print("\n=== ALL SESSIONS ===")
sessions = pd.read_sql_query("""
    SELECT s.id, u.username, s.match_score, s.ats_score, s.created_at
    FROM sessions s 
    JOIN users u ON s.user_id = u.id
    ORDER BY s.created_at DESC
""", conn)
print(sessions)

conn.close()