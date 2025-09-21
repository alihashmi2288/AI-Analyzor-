"""
AI Resume Analyzer - Streamlit Cloud Compatible Version
Works without external AI APIs for basic functionality
"""

import streamlit as st
import sqlite3
import hashlib
import json
from datetime import datetime
import pdfplumber
import docx2txt
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
import pandas as pd
from fpdf import FPDF
import io

# Page config
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Database functions
def init_database():
    conn = sqlite3.connect('resumeai.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            resume_text TEXT,
            jd_text TEXT,
            match_score REAL,
            ats_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    conn = sqlite3.connect('resumeai.db')
    cursor = conn.cursor()
    
    try:
        hashed_pw = hash_password(password)
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                      (username, email, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def authenticate_user(username, password):
    conn = sqlite3.connect('resumeai.db')
    cursor = conn.cursor()
    
    hashed_pw = hash_password(password)
    cursor.execute('SELECT id, username, email FROM users WHERE username = ? AND password = ?',
                  (username, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    
    return user

def save_session(user_id, resume_text, jd_text, match_score, ats_score):
    conn = sqlite3.connect('resumeai.db')
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO sessions 
                     (user_id, resume_text, jd_text, match_score, ats_score)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, resume_text, jd_text, match_score, ats_score))
    conn.commit()
    conn.close()

# Core functions
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(uploaded_file):
    return docx2txt.process(uploaded_file)

def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()-]', ' ', text)
    return text.strip()

def calculate_match_score(resume_text, jd_text):
    if not resume_text or not jd_text:
        return 0
    
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(jd_text)
    
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    try:
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return round(similarity[0][0] * 100, 1)
    except:
        return 0

def calculate_ats_score(resume_text, jd_text):
    if not resume_text or not jd_text:
        return 0
    
    jd_words = set(clean_text(jd_text).split())
    resume_words = set(clean_text(resume_text).split())
    
    overlap = len(jd_words & resume_words)
    total_jd_words = len(jd_words)
    
    if total_jd_words == 0:
        return 0
    
    ats_score = (overlap / total_jd_words) * 100
    
    action_verbs = ['managed', 'led', 'developed', 'created', 'improved', 'achieved']
    action_count = sum(1 for verb in action_verbs if verb in resume_text.lower())
    ats_score += min(action_count * 5, 20)
    
    return min(round(ats_score, 1), 100)

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 AI Resume Analyzer</h1>
        <p>Professional Resume Analysis & Optimization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication
    if not st.session_state.authenticated:
        show_auth_page()
        return
    
    # Main application
    show_main_app()

def show_auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Welcome to AI Resume Analyzer")
        
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Sign In", use_container_width=True):
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_data = {
                            'id': user[0],
                            'username': user[1],
                            'email': user[2]
                        }
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        
        with tab2:
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Sign Up", use_container_width=True):
                    if new_password != confirm_password:
                        st.error("Passwords don't match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif create_user(new_username, new_email, new_password):
                        st.success("Account created! Please sign in.")
                    else:
                        st.error("Username or email already exists")

def show_main_app():
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user_data['username']}!")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
        
        st.divider()
        st.info("🎯 Upload your resume and job description to get instant analysis!")
    
    # Main content
    st.header("📊 Resume Analysis Dashboard")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Upload Resume")
        resume_file = st.file_uploader("Choose resume file", type=['pdf', 'docx'])
        
        if resume_file:
            if resume_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(resume_file)
            else:
                resume_text = extract_text_from_docx(resume_file)
            
            st.session_state.resume_text = resume_text
            st.success(f"✅ {resume_file.name} uploaded")
    
    with col2:
        st.subheader("📋 Job Description")
        jd_input = st.text_area("Paste job description:", height=200)
        
        if jd_input:
            st.session_state.jd_text = jd_input
    
    # Analysis
    if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
        if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
            with st.spinner("🔄 Analyzing your resume..."):
                match_score = calculate_match_score(st.session_state.resume_text, st.session_state.jd_text)
                ats_score = calculate_ats_score(st.session_state.resume_text, st.session_state.jd_text)
                
                st.session_state.match_score = match_score
                st.session_state.ats_score = ats_score
                
                # Save session
                if st.session_state.user_data:
                    save_session(
                        st.session_state.user_data['id'],
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        match_score,
                        ats_score
                    )
            
            # Display results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h2>{match_score}%</h2>
                    <p>Match Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h2>{ats_score}%</h2>
                    <p>ATS Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                overall = (match_score + ats_score) / 2
                st.markdown(f"""
                <div class="metric-card">
                    <h2>{overall:.1f}%</h2>
                    <p>Overall</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Gauge visualization
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=match_score,
                title={'text': "Resume Match Score"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "#667eea"},
                       'steps': [{'range': [0, 50], 'color': "lightgray"},
                               {'range': [50, 80], 'color': "yellow"},
                               {'range': [80, 100], 'color': "green"}]}
            ))
            st.plotly_chart(fig, use_container_width=True)
            
            # Basic recommendations
            st.subheader("💡 Recommendations")
            if match_score < 70:
                st.warning("Consider adding more relevant keywords from the job description")
            if ats_score < 70:
                st.warning("Improve ATS compatibility by using more action verbs and quantifiable achievements")
            if match_score >= 80 and ats_score >= 80:
                st.success("Great match! Your resume aligns well with the job requirements")
                
        else:
            st.error("Please upload resume and add job description")

if __name__ == "__main__":
    main()