"""
Phase 3 - Pro-Level Features with FREE Gemini AI
Complete SaaS application using Google's free Gemini API instead of paid OpenAI
"""

import streamlit as st
import streamlit_authenticator as stauth
import sqlite3
import hashlib
import json
from datetime import datetime
import pdfplumber
import docx2txt
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
from docx import Document
from docx.shared import Inches
import io
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config with branding
st.set_page_config(
    page_title="ResumeAI Pro (Free)",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional branding
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
    .free-badge {
        background: linear-gradient(90deg, #00c851 0%, #007e33 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Database and auth functions (same as before)
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
            cover_letter TEXT,
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

def save_session(user_id, resume_text, jd_text, match_score, ats_score, cover_letter=""):
    conn = sqlite3.connect('resumeai.db')
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO sessions 
                     (user_id, resume_text, jd_text, match_score, ats_score, cover_letter)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (user_id, resume_text, jd_text, match_score, ats_score, cover_letter))
    conn.commit()
    conn.close()

def get_user_sessions(user_id):
    conn = sqlite3.connect('resumeai.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC',
                  (user_id,))
    sessions = cursor.fetchall()
    conn.close()
    
    return sessions

# Core analysis functions
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

# Gemini AI functions
def generate_with_gemini(prompt, api_key, max_tokens=1000):
    """Generate content using Gemini AI"""
    if not api_key:
        return "Please provide Gemini API key"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"Error: {str(e)}"

def generate_cover_letter_gemini(resume_text, jd_text, job_title, template_type, api_key):
    """Generate cover letter using Gemini"""
    template_styles = {
        "Formal": "formal and professional tone",
        "Modern": "contemporary and engaging style", 
        "Creative": "creative and innovative approach",
        "Short": "concise and direct format"
    }
    
    style = template_styles.get(template_type, "professional")
    
    prompt = f"""
    Write a {style} cover letter for the job: {job_title}
    
    Resume Summary: {resume_text[:1500]}
    Job Description: {jd_text[:1000]}
    
    Requirements:
    - Use {style}
    - 3-4 paragraphs maximum
    - Highlight relevant skills from resume
    - Address job requirements
    - Professional closing
    - Under 400 words
    """
    
    return generate_with_gemini(prompt, api_key)

def generate_resume_rewrite_gemini(resume_text, jd_text, api_key):
    """Rewrite resume using Gemini"""
    prompt = f"""
    Rewrite this resume to match the job description perfectly:
    
    Original Resume: {resume_text[:2000]}
    Target Job: {jd_text[:1000]}
    
    Instructions:
    1. Keep same structure but improve content
    2. Add keywords from job description
    3. Quantify achievements where possible
    4. Use strong action verbs
    5. Make it ATS-friendly
    
    Return the complete improved resume.
    """
    
    return generate_with_gemini(prompt, api_key, max_tokens=1500)

def generate_interview_questions_gemini(resume_text, jd_text, api_key):
    """Generate interview questions using Gemini"""
    prompt = f"""
    Generate 8 interview questions based on:
    
    Resume: {resume_text[:1500]}
    Job Description: {jd_text[:1000]}
    
    Create:
    - 4 technical/role-specific questions
    - 4 behavioral questions
    
    For each question provide:
    1. The question
    2. Key points to address
    3. Example answer framework
    
    Format as numbered list.
    """
    
    return generate_with_gemini(prompt, api_key, max_tokens=1200)

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    # Header with FREE badge
    st.markdown("""
    <div class="main-header">
        <h1>🎯 ResumeAI Pro</h1>
        <div class="free-badge">✨ 100% FREE with Gemini AI ✨</div>
        <p>Professional AI-Powered Resume Analysis & Optimization</p>
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
        st.markdown("### Welcome to ResumeAI Pro (FREE)")
        st.info("🆓 Powered by Google Gemini - Completely FREE to use!")
        
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
        
        st.header("⚙️ Settings")
        st.markdown("🆓 **FREE Gemini API Setup:**")
        st.info("Get your FREE API key at: https://makersuite.google.com/app/apikey")
        api_key = st.text_input("Gemini API Key", type="password", help="Free from Google AI Studio")
        
        if api_key:
            st.success("✅ Gemini AI Ready!")
        
        st.markdown("---")
        st.markdown("### 🎯 Why Gemini?")
        st.success("✅ Completely FREE")
        st.success("✅ No usage limits")
        st.success("✅ High quality AI")
        st.success("✅ Fast responses")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "📄 Resume Rewrite", 
        "📝 Cover Letters",
        "❓ Interview Prep",
        "📚 History"
    ])
    
    with tab1:
        show_dashboard_tab()
    
    with tab2:
        show_resume_rewrite_tab(api_key)
    
    with tab3:
        show_cover_letter_tab(api_key)
    
    with tab4:
        show_interview_prep_tab(api_key)
    
    with tab5:
        show_history_tab()

def show_dashboard_tab():
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
        else:
            st.error("Please upload resume and add job description")

def show_resume_rewrite_tab(api_key):
    st.header("📄 AI Resume Rewrite (FREE)")
    
    if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
        st.info("🤖 Gemini AI will rewrite your resume for FREE!")
        
        if st.button("✨ Rewrite My Resume", type="primary"):
            if api_key:
                with st.spinner("🤖 Gemini AI is rewriting your resume..."):
                    rewritten_resume = generate_resume_rewrite_gemini(
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        api_key
                    )
                
                st.subheader("📝 Your Optimized Resume")
                edited_resume = st.text_area("AI-Optimized Resume:", rewritten_resume, height=400)
                
                st.download_button(
                    "📥 Download Optimized Resume",
                    edited_resume,
                    "optimized_resume.txt",
                    "text/plain",
                    use_container_width=True
                )
            else:
                st.warning("🔑 Please add your FREE Gemini API key in the sidebar")
    else:
        st.info("📄 Please analyze a resume first in the Dashboard tab")

def show_cover_letter_tab(api_key):
    st.header("📝 AI Cover Letter Generator (FREE)")
    
    if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            job_title = st.text_input("Job Title", placeholder="e.g., Senior Software Engineer")
            template_type = st.selectbox("Cover Letter Style", ["Formal", "Modern", "Creative", "Short"])
        
        with col2:
            st.markdown("**✨ FREE Gemini AI Generation**")
            st.success("🆓 Unlimited cover letters")
            st.success("🚀 High quality output")
        
        if st.button("✨ Generate Cover Letter", type="primary"):
            if api_key:
                with st.spinner(f"🤖 Creating {template_type.lower()} cover letter..."):
                    cover_letter = generate_cover_letter_gemini(
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        job_title,
                        template_type,
                        api_key
                    )
                
                st.subheader(f"📄 Your {template_type} Cover Letter")
                edited_letter = st.text_area("Edit your cover letter:", cover_letter, height=400)
                
                st.download_button(
                    "📝 Download Cover Letter",
                    edited_letter,
                    f"cover_letter_{template_type.lower()}.txt",
                    "text/plain",
                    use_container_width=True
                )
            else:
                st.warning("🔑 Please add your FREE Gemini API key")
    else:
        st.info("📄 Please analyze a resume first")

def show_interview_prep_tab(api_key):
    st.header("❓ AI Interview Preparation (FREE)")
    
    if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
        st.info("🎯 Get personalized interview questions with FREE Gemini AI")
        
        if st.button("🎤 Generate Interview Questions", type="primary"):
            if api_key:
                with st.spinner("🤖 Preparing your interview questions..."):
                    questions = generate_interview_questions_gemini(
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        api_key
                    )
                
                st.subheader("📋 Your Personalized Interview Questions")
                st.markdown(questions)
                
                st.download_button(
                    "📥 Download Interview Prep",
                    questions,
                    "interview_questions.txt",
                    "text/plain",
                    use_container_width=True
                )
            else:
                st.warning("🔑 Please add your FREE Gemini API key")
    else:
        st.info("📄 Please analyze a resume first")

def show_history_tab():
    st.header("📚 Analysis History")
    
    if st.session_state.user_data:
        sessions = get_user_sessions(st.session_state.user_data['id'])
        
        if sessions:
            st.subheader(f"📊 Your Past {len(sessions)} Analyses")
            
            for session in sessions:
                with st.expander(f"Analysis from {session[7][:16]} - Score: {session[4]}%"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Match Score", f"{session[4]}%")
                        st.metric("ATS Score", f"{session[5]}%")
                    
                    with col2:
                        if st.button(f"Load Session", key=f"load_{session[0]}"):
                            st.session_state.resume_text = session[2]
                            st.session_state.jd_text = session[3]
                            st.session_state.match_score = session[4]
                            st.session_state.ats_score = session[5]
                            st.success("Session loaded!")
        else:
            st.info("📝 No analysis history yet. Start by analyzing your first resume!")

if __name__ == "__main__":
    main()