"""
Enhanced AI Resume Analyzer Pro
Version 2.0 with Advanced Features
Created by Syed Ali Hashmi
"""

import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pdfplumber
import docx2txt
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
import plotly.graph_objects as go
from enhanced_features import *

# Page config
st.set_page_config(
    page_title="AI Resume Analyzer Pro v2.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        color: #333;
        font-weight: 500;
    }
    .success-tip {
        background: linear-gradient(90deg, #00c851 0%, #007e33 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.5rem 0;
        display: inline-block;
    }
    .keyword-highlight {
        background-color: #ffeb3b;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Database functions (same as before)
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
                text += page_text + "\\n"
    return text

def extract_text_from_docx(uploaded_file):
    return docx2txt.process(uploaded_file)

def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\\s+', ' ', text)
    text = re.sub(r'[^\\w\\s.,;:!?()-]', ' ', text)
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
def get_gemini_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except:
        # Fallback to built-in key for demo
        return "AIzaSyCdLLR7DaN2-WXw2-kRFoOO99scfXxjMdY"

def generate_with_gemini(prompt, max_tokens=1000):
    api_key = get_gemini_api_key()
    
    if not api_key:
        return "API key not configured. Please check secrets.toml file."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    # Enhanced header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Resume Analyzer Pro v2.0</h1>
        <div class="success-tip">Enhanced with Advanced Features</div>
        <p>Professional AI-Powered Resume Analysis & Career Optimization</p>
        <small>Created by Syed Ali Hashmi</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication
    if not st.session_state.authenticated:
        show_auth_page()
        return
    
    # Main application
    show_enhanced_app()

def show_auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Welcome to AI Resume Analyzer Pro v2.0")
        st.info("🚀 Enhanced with advanced analytics and career insights!")
        
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

def show_enhanced_app():
    # Enhanced sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user_data['username']}! 👋")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
        
        st.divider()
        
        # User analytics
        if st.session_state.user_data:
            sessions = get_user_sessions(st.session_state.user_data['id'])
            analytics = create_usage_analytics(sessions)
            
            if analytics:
                st.markdown("### 📊 Your Stats")
                create_success_metrics_display(analytics)
        
        st.divider()
        
        st.markdown("### 🎯 Why AI Resume Analyzer?")
        st.success("✅ Advanced Analytics")
        st.success("✅ Keyword Highlighting")
        st.success("✅ Progress Tracking")
        st.success("✅ Multiple Export Formats")
        
        st.markdown("---")
        st.markdown("**Made by Syed Ali Hashmi** 🚀")
        st.markdown("📧 [hashmi.ali2288@gmail.com](mailto:hashmi.ali2288@gmail.com)")
        st.markdown("💼 [LinkedIn](https://www.linkedin.com/in/hashmiali2288/)")
        st.markdown("💻 [GitHub](https://github.com/alihashmi2288)")
    
    # Enhanced main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Smart Analysis",
        "📝 AI Rewrite", 
        "💌 Cover Letters",
        "❓ Interview Prep",
        "📊 Analytics",
        "📚 History"
    ])
    
    with tab1:
        show_enhanced_dashboard()
    
    with tab2:
        show_enhanced_rewrite()
    
    with tab3:
        show_enhanced_cover_letters()
    
    with tab4:
        show_enhanced_interview_prep()
    
    with tab5:
        show_analytics_dashboard()
    
    with tab6:
        show_enhanced_history()

def show_enhanced_dashboard():
    st.header("🎯 Smart Resume Analysis")
    
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
            st.success(f"✅ {resume_file.name} uploaded ({len(resume_text)} characters)")
    
    with col2:
        st.subheader("📋 Job Description")
        jd_input = st.text_area("Paste job description:", height=200)
        
        if jd_input:
            st.session_state.jd_text = jd_input
            st.info(f"📊 Job description: {len(jd_input)} characters")
    
    # Enhanced analysis
    if st.button("🚀 Analyze with AI", type="primary", use_container_width=True):
        if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
            with st.spinner("🔄 Running advanced analysis..."):
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
            
            # Enhanced results display
            st.subheader("📊 Analysis Results")
            
            # Gauge charts
            col1, col2 = st.columns(2)
            with col1:
                fig1 = create_score_gauge(match_score, "Match Score")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = create_score_gauge(ats_score, "ATS Score")
                st.plotly_chart(fig2, use_container_width=True)
            
            # Skills analysis
            skills_data = create_skills_analysis(st.session_state.resume_text, st.session_state.jd_text)
            
            st.subheader("🛠️ Skills Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                if skills_data['matched_skills']:
                    st.success("✅ **Matched Skills:**")
                    for skill in skills_data['matched_skills']:
                        st.write(f"• {skill.title()}")
                else:
                    st.info("No specific skills matched")
            
            with col2:
                if skills_data['missing_skills']:
                    st.warning("⚠️ **Missing Skills:**")
                    for skill in skills_data['missing_skills'][:5]:
                        st.write(f"• {skill.title()}")
                else:
                    st.success("All required skills present!")
            
            # Improvement tips
            st.subheader("💡 Personalized Recommendations")
            tips = generate_improvement_tips(match_score, ats_score, skills_data['missing_skills'])
            
            for tip in tips:
                st.markdown(f'<div class="feature-card">{tip}</div>', unsafe_allow_html=True)
            
        else:
            st.error("Please upload resume and add job description")

def show_enhanced_rewrite():
    st.header("📝 AI Resume Rewrite")
    
    if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
        st.info("🤖 Rewrite your resume for free!")
        
        if st.button("✨ Rewrite My Resume", type="primary"):
            with st.spinner("🤖 AI is optimizing your resume..."):
                # Generate rewritten resume
                prompt = f"""
                Rewrite this resume to match the job description perfectly:
                
                Original Resume: {st.session_state.resume_text[:2000]}
                Target Job: {st.session_state.jd_text[:1000]}
                
                Instructions:
                1. Keep same structure but improve content
                2. Add keywords from job description
                3. Quantify achievements where possible
                4. Use strong action verbs
                5. Make it ATS-friendly
                
                Return the complete improved resume.
                """
                
                rewritten_resume = generate_with_gemini(prompt, max_tokens=1500)
                
                st.subheader("📝 Your Optimized Resume")
                edited_resume = st.text_area("AI-Optimized Resume:", rewritten_resume, height=400)
                
                # Enhanced export options
                st.subheader("📥 Download Options")
                export_data = create_export_options(edited_resume, "optimized_resume", "resume")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        "📄 Download TXT",
                        export_data['txt'],
                        "optimized_resume.txt",
                        "text/plain",
                        use_container_width=True
                    )
                with col2:
                    st.download_button(
                        "🌐 Download HTML",
                        export_data['html'],
                        "optimized_resume.html",
                        "text/html",
                        use_container_width=True
                    )
                with col3:
                    st.download_button(
                        "📋 Download Formatted",
                        export_data['formatted'],
                        "optimized_resume_formatted.txt",
                        "text/plain",
                        use_container_width=True
                    )
    else:
        st.info("📄 Please analyze a resume first in the Smart Analysis tab")

def show_enhanced_cover_letters():
    st.header("💌 AI Cover Letter Generator")
    
    if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            job_title = st.text_input("Job Title", placeholder="e.g., Senior Software Engineer")
            template_type = st.selectbox("Cover Letter Style", ["Formal", "Modern", "Creative", "Short"])
        
        with col2:
            st.markdown("**✨ AI-Powered Generation**")
            st.success("🆓 Professional templates")
            st.success("🚀 Instant results")
        
        if st.button("✨ Generate Cover Letter", type="primary"):
            with st.spinner(f"🤖 Creating {template_type.lower()} cover letter..."):
                # Generate cover letter
                prompt = f"""
                Write a {template_type.lower()} cover letter for the job: {job_title}
                
                Resume Summary: {st.session_state.resume_text[:1500]}
                Job Description: {st.session_state.jd_text[:1000]}
                
                Requirements:
                - Use {template_type.lower()} style
                - 3-4 paragraphs maximum
                - Highlight relevant skills from resume
                - Address job requirements
                - Professional closing
                - Under 400 words
                """
                
                cover_letter = generate_with_gemini(prompt)
                
                st.subheader(f"📄 Your {template_type} Cover Letter")
                edited_letter = st.text_area("Edit your cover letter:", cover_letter, height=400)
                
                # Enhanced export options
                st.subheader("📥 Download Options")
                export_data = create_export_options(edited_letter, f"cover_letter_{template_type.lower()}", "cover letter")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📄 Download TXT",
                        export_data['txt'],
                        f"cover_letter_{template_type.lower()}.txt",
                        "text/plain",
                        use_container_width=True
                    )
                with col2:
                    st.download_button(
                        "🌐 Download HTML",
                        export_data['html'],
                        f"cover_letter_{template_type.lower()}.html",
                        "text/html",
                        use_container_width=True
                    )
    else:
        st.info("📄 Please analyze a resume first")

def show_enhanced_interview_prep():
    st.header("❓ AI Interview Preparation")
    
    if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
        st.info("🎯 Get personalized interview questions for Free")
        
        if st.button("🎤 Generate Interview Questions", type="primary"):
            with st.spinner("🤖 Preparing your interview questions..."):
                # Generate interview questions
                prompt = f"""
                Generate 8 interview questions based on:
                
                Resume: {st.session_state.resume_text[:1500]}
                Job Description: {st.session_state.jd_text[:1000]}
                
                Create:
                - 4 technical/role-specific questions
                - 4 behavioral questions
                
                For each question provide:
                1. The question
                2. Key points to address
                3. Example answer framework
                
                Format as numbered list.
                """
                
                questions = generate_with_gemini(prompt, max_tokens=1200)
                
                st.subheader("📋 Your Personalized Interview Questions")
                st.markdown(questions)
                
                # Enhanced export options
                st.subheader("📥 Download Options")
                export_data = create_export_options(questions, "interview_questions", "interview preparation")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📄 Download TXT",
                        export_data['txt'],
                        "interview_questions.txt",
                        "text/plain",
                        use_container_width=True
                    )
                with col2:
                    st.download_button(
                        "🌐 Download HTML",
                        export_data['html'],
                        "interview_questions.html",
                        "text/html",
                        use_container_width=True
                    )
    else:
        st.info("📄 Please analyze a resume first")

def show_analytics_dashboard():
    st.header("📊 Advanced Analytics")
    
    if st.session_state.user_data:
        sessions = get_user_sessions(st.session_state.user_data['id'])
        
        if sessions:
            # Progress chart
            progress_fig = create_progress_chart(sessions)
            if progress_fig:
                st.plotly_chart(progress_fig, use_container_width=True)
            
            # Analytics summary
            analytics = create_usage_analytics(sessions)
            if analytics:
                st.subheader("📈 Performance Summary")
                create_success_metrics_display(analytics)
            
            # Recent activity
            st.subheader("🕒 Recent Activity")
            for session in sessions[:5]:
                with st.expander(f"Analysis from {session[7][:16]} - Score: {session[4]}%"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Match Score", f"{session[4]}%")
                        st.metric("ATS Score", f"{session[5]}%")
                    with col2:
                        if st.button(f"Load Session", key=f"load_analytics_{session[0]}"):
                            st.session_state.resume_text = session[2]
                            st.session_state.jd_text = session[3]
                            st.success("Session loaded!")
        else:
            st.info("📊 No analytics data yet. Start by analyzing your first resume!")
    else:
        st.error("Please log in to view analytics")

def show_enhanced_history():
    st.header("📚 Analysis History")
    
    if st.session_state.user_data:
        sessions = get_user_sessions(st.session_state.user_data['id'])
        
        if sessions:
            st.subheader(f"📊 Your Past {len(sessions)} Analyses")
            
            # Add search and filter
            search_term = st.text_input("🔍 Search your analyses:", placeholder="Search by content...")
            
            filtered_sessions = sessions
            if search_term:
                filtered_sessions = [s for s in sessions if search_term.lower() in s[2].lower() or search_term.lower() in s[3].lower()]
            
            for session in filtered_sessions:
                with st.expander(f"Analysis from {session[7][:16]} - Score: {session[4]}%"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.metric("Match Score", f"{session[4]}%")
                        st.metric("ATS Score", f"{session[5]}%")
                    
                    with col2:
                        st.write("**Resume Preview:**")
                        st.write(session[2][:200] + "..." if len(session[2]) > 200 else session[2])
                    
                    with col3:
                        if st.button(f"Load Session", key=f"load_history_{session[0]}"):
                            st.session_state.resume_text = session[2]
                            st.session_state.jd_text = session[3]
                            st.session_state.match_score = session[4]
                            st.session_state.ats_score = session[5]
                            st.success("Session loaded!")
        else:
            st.info("📝 No analysis history yet. Start by analyzing your first resume!")

if __name__ == "__main__":
    main()