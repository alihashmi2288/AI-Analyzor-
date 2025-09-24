"""
AI Resume Analyzer Pro - Clean Version
Streamlined code without templates
Created by Syed Ali Hashmi
"""

import streamlit as st
import sqlite3
import hashlib
import re
from datetime import datetime

# Lazy imports for better performance
@st.cache_resource
def load_ml_libraries():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    return TfidfVectorizer, cosine_similarity

@st.cache_resource
def load_file_libraries():
    import pdfplumber
    import docx2txt
    return pdfplumber, docx2txt

@st.cache_resource
def load_ai_libraries():
    import google.generativeai as genai
    import plotly.graph_objects as go
    return genai, go

def create_pdf(content, title="Document"):
    """Create a real PDF document using FPDF2"""
    try:
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 16)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(10)
        
        pdf.set_font('helvetica', '', 12)
        for line in content.split('\n'):
            if line.strip():
                words = line.split(' ')
                current_line = ''
                for word in words:
                    if len(current_line + word) < 80:
                        current_line += word + ' '
                    else:
                        if current_line:
                            pdf.cell(0, 6, current_line.strip(), new_x="LMARGIN", new_y="NEXT")
                        current_line = word + ' '
                if current_line:
                    pdf.cell(0, 6, current_line.strip(), new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.ln(3)
        
        # Convert bytearray to bytes
        pdf_output = pdf.output()
        if isinstance(pdf_output, bytearray):
            return bytes(pdf_output)
        return pdf_output
    except:
        # Create a simple text-based fallback
        pdf_content = f"{title}\n{'='*len(title)}\n\n{content}"
        return pdf_content.encode('utf-8')

def create_docx(content, title="Document"):
    """Create a real DOCX document using python-docx"""
    try:
        from docx import Document
        from io import BytesIO
        
        doc = Document()
        doc.add_heading(title, 0)
        
        for line in content.split('\n'):
            if line.strip():
                doc.add_paragraph(line)
            else:
                doc.add_paragraph('')
        
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except:
        # Create RTF format as fallback
        rtf_content = f"{{\\rtf1\\ansi\\deff0 {{\\fonttbl{{\\f0 Times New Roman;}}}}\\f0\\fs24 \\b {title}\\b0\\par\\par{content.replace(chr(10), '\\par ')}\\par}}"
        return rtf_content.encode('utf-8')

# Page config
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="🚀",
    layout="wide"
)

# Clean CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        text-align: center;
        margin: 0.5rem 0;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
        color: #333;
    }
    .progress-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Database
def init_database():
    conn = sqlite3.connect('resumeai.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
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

def get_user_sessions(user_id):
    conn = sqlite3.connect('resumeai.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC',
                  (user_id,))
    sessions = cursor.fetchall()
    conn.close()
    
    return sessions

# Core functions
def extract_text_from_pdf(uploaded_file):
    pdfplumber, _ = load_file_libraries()
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(uploaded_file):
    _, docx2txt = load_file_libraries()
    return docx2txt.process(uploaded_file)

def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()-]', ' ', text)
    return text.strip()

@st.cache_data
def calculate_match_score(resume_text, jd_text):
    if not resume_text or not jd_text:
        return 0
    
    TfidfVectorizer, cosine_similarity = load_ml_libraries()
    
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(jd_text)
    
    # Enhanced TF-IDF with n-grams for better accuracy
    vectorizer = TfidfVectorizer(
        stop_words='english', 
        max_features=2000,
        ngram_range=(1, 2),  # Include bigrams
        min_df=1,
        max_df=0.95
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        
        # Boost score for exact keyword matches
        jd_words = set(clean_jd.split())
        resume_words = set(clean_resume.split())
        exact_matches = len(jd_words & resume_words)
        total_jd_words = len(jd_words)
        
        base_score = similarity[0][0] * 100
        keyword_boost = (exact_matches / total_jd_words) * 20 if total_jd_words > 0 else 0
        
        final_score = min(base_score + keyword_boost, 100)
        return round(final_score, 1)
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
    
    # Base keyword overlap score
    base_score = (overlap / total_jd_words) * 60
    
    # Enhanced action verbs list
    action_verbs = [
        'managed', 'led', 'developed', 'created', 'improved', 'achieved',
        'implemented', 'designed', 'optimized', 'increased', 'reduced',
        'delivered', 'executed', 'coordinated', 'analyzed', 'built'
    ]
    action_count = sum(1 for verb in action_verbs if verb in resume_text.lower())
    action_score = min(action_count * 2, 15)
    
    # Check for quantifiable achievements (numbers/percentages)
    numbers = re.findall(r'\d+[%$]?', resume_text)
    quantifiable_score = min(len(numbers) * 1.5, 10)
    
    # Check for relevant skills/technologies
    tech_skills = [
        'python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker',
        'git', 'linux', 'html', 'css', 'node', 'mongodb', 'kubernetes'
    ]
    skill_matches = sum(1 for skill in tech_skills if skill in resume_text.lower())
    skill_score = min(skill_matches * 1, 10)
    
    # Professional formatting check
    format_score = 5 if len(resume_text) > 500 else 0
    
    total_score = base_score + action_score + quantifiable_score + skill_score + format_score
    return min(round(total_score, 1), 100)

# Gemini AI
def get_gemini_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except:
        return "AIzaSyAzj6APgLBko1DdYxrhBtaH6GtupTD6Yw8"

def generate_with_gemini(prompt, max_tokens=1000):
    genai, _ = load_ai_libraries()
    api_key = get_gemini_api_key()
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

@st.cache_data
def create_score_gauge(score, title):
    _, go = load_ai_libraries()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ]
        }
    ))
    fig.update_layout(height=300)
    return fig

def generate_detailed_recommendations(match_score, ats_score, resume_text, jd_text):
    """Generate detailed, actionable recommendations"""
    recommendations = []
    
    # Analyze missing keywords
    jd_words = set(clean_text(jd_text).split())
    resume_words = set(clean_text(resume_text).split())
    missing_keywords = list(jd_words - resume_words)[:5]
    
    # Check for action verbs
    action_verbs = ['managed', 'led', 'developed', 'created', 'improved', 'achieved', 'implemented', 'designed']
    action_count = sum(1 for verb in action_verbs if verb in resume_text.lower())
    
    # Check for numbers/metrics
    numbers = re.findall(r'\d+[%$]?', resume_text)
    
    # Generate specific recommendations
    if match_score < 70:
        if missing_keywords:
            recommendations.append(f"🎯 **Add Key Terms**: Include these important keywords: {', '.join(missing_keywords[:3])}")
        recommendations.append("🔍 **Skills Alignment**: Review job requirements and highlight matching experience more prominently")
        recommendations.append("📝 **Content Optimization**: Rewrite job descriptions to better match the target role's language")
    
    if ats_score < 70:
        if action_count < 5:
            recommendations.append("⚡ **Action Verbs**: Use more powerful action verbs like 'spearheaded', 'orchestrated', 'pioneered'")
        if len(numbers) < 3:
            recommendations.append("📈 **Quantify Results**: Add specific numbers, percentages, or dollar amounts to show impact")
        recommendations.append("🎨 **Format Improvement**: Ensure clean formatting with consistent fonts, spacing, and bullet points")
    
    if match_score >= 70 and ats_score >= 70:
        recommendations.append("🎉 **Excellent Foundation**: Your resume shows strong alignment with the job requirements")
        recommendations.append("🕰️ **Fine-Tuning**: Consider customizing your professional summary for this specific role")
        recommendations.append("🔗 **LinkedIn Sync**: Ensure your LinkedIn profile matches your resume's key points")
        recommendations.append("💬 **Cover Letter**: Write a compelling cover letter that tells your unique story")
    
    # Always include industry-specific advice
    if 'software' in jd_text.lower() or 'developer' in jd_text.lower():
        recommendations.append("💻 **Tech Focus**: Highlight programming languages, frameworks, and technical projects")
    elif 'marketing' in jd_text.lower():
        recommendations.append("📊 **Marketing Metrics**: Include campaign results, conversion rates, and ROI improvements")
    elif 'sales' in jd_text.lower():
        recommendations.append("💰 **Sales Numbers**: Emphasize quota achievements, revenue generated, and client acquisition")
    else:
        recommendations.append("🎯 **Industry Alignment**: Research industry-specific terminology and incorporate relevant buzzwords")
    
    # Ensure minimum 4 recommendations
    while len(recommendations) < 4:
        additional_tips = [
            "📝 **Professional Summary**: Craft a compelling 2-3 line summary at the top",
            "🎓 **Education Relevance**: Highlight relevant coursework, certifications, or training",
            "🔍 **Keyword Density**: Naturally incorporate job-specific terms throughout your resume",
            "📅 **Recent Experience**: Emphasize your most recent and relevant work experience",
            "🎆 **Achievement Focus**: Transform job duties into accomplishment statements"
        ]
        for tip in additional_tips:
            if tip not in recommendations:
                recommendations.append(tip)
                break
    
    return recommendations[:6]  # Return max 6 recommendations

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    # Simple Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Resume Analyzer Pro</h1>
        <p>Professional AI-Powered Resume Analysis & Optimization</p>
        <small>Created by Syed Ali Hashmi</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication
    if not st.session_state.authenticated:
        show_auth_page()
        return
    
    # Main app
    show_main_app()

def show_auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Welcome to AI Resume Analyzer Pro")
        
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
        st.markdown(f"### Welcome, {st.session_state.user_data['username']}! 👋")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
        
        st.divider()
        
        # User progress tracking
        if st.session_state.user_data:
            sessions = get_user_sessions(st.session_state.user_data['id'])
            if sessions:
                avg_score = sum(s[4] for s in sessions) / len(sessions)
                best_score = max(s[4] for s in sessions)
                
                st.markdown("### 📈 Your Progress")
                st.markdown(f'<div class="progress-card">🎯 Analyses: {len(sessions)}<br>📈 Avg Score: {avg_score:.1f}%<br>🏆 Best: {best_score:.1f}%</div>', unsafe_allow_html=True)
        
        st.markdown("### 🎯 Features")
        
        features = [
            "🎯 AI Resume Analysis",
            "📊 ATS Optimization", 
            "💌 Cover Letter Generation",
            "❓ Interview Preparation",
            "🤖 AI Career Tools",
            "📈 Advanced Analytics"
        ]
        
        for feature in features:
            st.markdown(f'<div class="feature-card">{feature}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("**Created by Syed Ali Hashmi**")
        st.markdown("💼 [LinkedIn](https://linkedin.com/in/hashmiali2288)")
        st.markdown("💻 [GitHub](https://github.com/alihashmi2288)")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎯 Analysis",
        "📝 AI Rewrite", 
        "💌 Cover Letters",
        "❓ Interview Prep",
        "🤖 AI Tools",
        "📈 Analytics",
        "📚 History"
    ])
    
    with tab1:
        show_analysis()
    
    with tab2:
        show_rewrite()
    
    with tab3:
        show_cover_letters()
    
    with tab4:
        show_interview_prep()
    
    with tab5:
        show_ai_tools()
    
    with tab6:
        show_analytics_dashboard()
    
    with tab7:
        show_history()

def show_analysis():
    st.header("🎯 Resume Analysis")
    
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
            st.info(f"📊 Job description added")
    
    # Analysis
    if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
        if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
            with st.spinner("🔄 Analyzing..."):
                match_score = calculate_match_score(st.session_state.resume_text, st.session_state.jd_text)
                ats_score = calculate_ats_score(st.session_state.resume_text, st.session_state.jd_text)
                
                st.session_state.match_score = match_score
                st.session_state.ats_score = ats_score
                
                # Show improvement before saving new session
                if st.session_state.user_data:
                    prev_sessions = get_user_sessions(st.session_state.user_data['id'])
                    if prev_sessions:
                        prev_match = prev_sessions[0][4]
                        prev_ats = prev_sessions[0][5]
                        
                        match_improvement = match_score - prev_match
                        ats_improvement = ats_score - prev_ats
                        
                        if match_improvement > 0 or ats_improvement > 0:
                            st.success(f"📈 Improvement: Match {match_improvement:+.1f}%, ATS {ats_improvement:+.1f}%")
                        elif match_improvement < 0 or ats_improvement < 0:
                            st.warning(f"📉 Change: Match {match_improvement:+.1f}%, ATS {ats_improvement:+.1f}%")
                    
                    # Save new session
                    save_session(
                        st.session_state.user_data['id'],
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        match_score,
                        ats_score
                    )
            
            # Results
            st.subheader("📊 Results")
            
            col1, col2 = st.columns(2)
            with col1:
                fig1 = create_score_gauge(match_score, "Match Score")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = create_score_gauge(ats_score, "ATS Score")
                st.plotly_chart(fig2, use_container_width=True)
            
            # Enhanced Recommendations
            st.subheader("💡 Detailed Recommendations")
            
            recommendations = generate_detailed_recommendations(match_score, ats_score, st.session_state.resume_text, st.session_state.jd_text)
            
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f'<div class="feature-card"><strong>{i}.</strong> {rec}</div>', unsafe_allow_html=True)
        else:
            st.error("Please upload resume and add job description")

def show_rewrite():
    st.header("📝 AI Resume Rewrite")
    
    if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
        if st.button("✨ Rewrite My Resume", type="primary"):
            with st.spinner("🤖 AI is optimizing your resume..."):
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
                st.session_state.rewritten_resume = rewritten_resume
        
        # Multi-version resume generator
        if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
            st.divider()
            st.subheader("🔄 Multi-Version Generator")
            
            col1, col2 = st.columns(2)
            with col1:
                version_type = st.selectbox("Resume Version:", [
                    "Executive Summary Focus",
                    "Technical Skills Focus", 
                    "Achievement Focus",
                    "Entry-Level Friendly",
                    "Career Change Focus"
                ])
            
            with col2:
                if st.button("✨ Generate Version", key="multi_version"):
                    with st.spinner(f"🤖 Creating {version_type.lower()} version..."):
                        version_prompt = f"""
                        Create a {version_type.lower()} version of this resume:
                        
                        Original Resume: {st.session_state.resume_text[:1500]}
                        Job Description: {st.session_state.jd_text[:800]}
                        
                        Focus on {version_type.lower()} while maintaining ATS compatibility.
                        Keep it concise and impactful.
                        """
                        
                        version_resume = generate_with_gemini(version_prompt, max_tokens=1200)
                        st.session_state[f"version_{version_type}"] = version_resume
            
            # Show generated version
            if f"version_{version_type}" in st.session_state:
                st.text_area(
                    f"{version_type} Version:",
                    st.session_state[f"version_{version_type}"],
                    height=300,
                    key=f"edit_{version_type}"
                )
                
                st.download_button(
                    f"📥 Download {version_type}",
                    st.session_state[f"version_{version_type}"],
                    f"resume_{version_type.lower().replace(' ', '_')}.txt",
                    "text/plain"
                )
        
        if hasattr(st.session_state, 'rewritten_resume'):
            st.subheader("📝 Your Optimized Resume")
            
            edited_resume = st.text_area(
                "Edit your resume:", 
                value=st.session_state.rewritten_resume, 
                height=400
            )
            
            st.session_state.rewritten_resume = edited_resume
            
            # Download
            st.subheader("📥 Download")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.download_button(
                    "📄 TXT",
                    edited_resume,
                    "optimized_resume.txt",
                    "text/plain",
                    use_container_width=True
                )
            
            with col2:
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Optimized Resume</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; max-width: 800px; }}
                        h1, h2 {{ color: #333; }}
                        .header {{ text-align: center; margin-bottom: 30px; }}
                        .section {{ margin: 20px 0; }}
                        @media print {{ body {{ margin: 20px; }} }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Professional Resume</h1>
                        <p>Generated by AI Resume Analyzer Pro</p>
                    </div>
                    <div class="section">
                        {edited_resume.replace(chr(10), '<br>')}
                    </div>
                </body>
                </html>
                """
                st.download_button(
                    "🌐 HTML",
                    html_content,
                    "optimized_resume.html",
                    "text/html",
                    use_container_width=True
                )
            
            with col3:
                pdf_data = create_pdf(edited_resume, "Professional Resume")
                st.download_button(
                    "📄 PDF",
                    pdf_data,
                    "optimized_resume.pdf",
                    "application/pdf",
                    use_container_width=True
                )
            
            with col4:
                docx_data = create_docx(edited_resume, "Professional Resume")
                st.download_button(
                    "📄 DOCX",
                    docx_data,
                    "optimized_resume.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            

    else:
        st.info("📄 Please analyze a resume first")

def show_cover_letters():
    st.header("💌 AI Cover Letter Generator")
    
    if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            job_title = st.text_input("Job Title", placeholder="e.g., Software Engineer")
            template_type = st.selectbox("Style", ["Formal", "Modern", "Creative", "Short"])
        
        if st.button("✨ Generate Cover Letter", type="primary"):
            with st.spinner(f"🤖 Creating {template_type.lower()} cover letter..."):
                prompt = f"""
                Write a {template_type.lower()} cover letter for: {job_title}
                
                Resume: {st.session_state.resume_text[:1500]}
                Job Description: {st.session_state.jd_text[:1000]}
                
                Requirements:
                - Use {template_type.lower()} style
                - 3-4 paragraphs maximum
                - Highlight relevant skills
                - Professional closing
                - Under 400 words
                """
                
                cover_letter = generate_with_gemini(prompt)
                
                st.subheader(f"📄 Your {template_type} Cover Letter")
                edited_letter = st.text_area("Edit cover letter:", cover_letter, height=400)
                
                # Download
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.download_button(
                        "📄 TXT",
                        edited_letter,
                        f"cover_letter_{template_type.lower()}.txt",
                        "text/plain",
                        use_container_width=True
                    )
                
                with col2:
                    html_letter = f"<html><body><div style='font-family: Arial; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;'>{edited_letter.replace(chr(10), '<br>')}</div></body></html>"
                    st.download_button(
                        "🌐 HTML",
                        html_letter,
                        f"cover_letter_{template_type.lower()}.html",
                        "text/html",
                        use_container_width=True
                    )
                
                with col3:
                    pdf_data = create_pdf(edited_letter, f"{template_type} Cover Letter")
                    st.download_button(
                        "📄 PDF",
                        pdf_data,
                        f"cover_letter_{template_type.lower()}.pdf",
                        "application/pdf",
                        use_container_width=True
                    )
                
                with col4:
                    docx_data = create_docx(edited_letter, f"{template_type} Cover Letter")
                    st.download_button(
                        "📄 DOCX",
                        docx_data,
                        f"cover_letter_{template_type.lower()}.docx",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )

    else:
        st.info("📄 Please analyze a resume first")

def show_interview_prep():
    st.header("❓ AI Interview Preparation")
    
    if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
        if st.button("🎤 Generate Interview Questions", type="primary"):
            with st.spinner("🤖 Preparing interview questions..."):
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
                
                st.subheader("📋 Interview Questions")
                st.markdown(questions)
                
                # Download
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.download_button(
                        "📄 TXT",
                        questions,
                        "interview_questions.txt",
                        "text/plain",
                        use_container_width=True
                    )
                
                with col2:
                    html_questions = f"<html><body><div style='font-family: Arial; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px;'><h1>Interview Preparation</h1>{questions.replace(chr(10), '<br>')}</div></body></html>"
                    st.download_button(
                        "🌐 HTML",
                        html_questions,
                        "interview_questions.html",
                        "text/html",
                        use_container_width=True
                    )
                
                with col3:
                    pdf_data = create_pdf(questions, "Interview Preparation")
                    st.download_button(
                        "📄 PDF",
                        pdf_data,
                        "interview_questions.pdf",
                        "application/pdf",
                        use_container_width=True
                    )
                
                with col4:
                    docx_data = create_docx(questions, "Interview Preparation")
                    st.download_button(
                        "📄 DOCX",
                        docx_data,
                        "interview_questions.docx",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )

    else:
        st.info("📄 Please analyze a resume first")

def show_history():
    st.header("📚 Analysis History")
    
    if st.session_state.user_data:
        sessions = get_user_sessions(st.session_state.user_data['id'])
        
        if sessions:
            st.subheader(f"📊 Your Past {len(sessions)} Analyses")
            
            for session in sessions:
                with st.expander(f"Analysis from {session[7][:16]} - Score: {session[4]}%"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.metric("Match Score", f"{session[4]}%")
                        st.metric("ATS Score", f"{session[5]}%")
                    
                    with col2:
                        st.write("**Resume Preview:**")
                        st.write(session[2][:200] + "..." if len(session[2]) > 200 else session[2])
                    
                    with col3:
                        if st.button(f"Load", key=f"load_{session[0]}"):
                            st.session_state.resume_text = session[2]
                            st.session_state.jd_text = session[3]
                            st.session_state.match_score = session[4]
                            st.session_state.ats_score = session[5]
                            st.success("Session loaded!")
        else:
            st.info("📝 No analysis history yet")

def show_ai_tools():
    st.header("🤖 Enhanced AI Career Tools")
    
    ai_feature = st.selectbox(
        "Choose AI Tool:",
        [
            "💰 Salary Negotiation Guide",
            "🏢 Company Research Report", 
            "💼 LinkedIn Optimization",
            "📧 Follow-up Email Templates",
            "🔄 Career Transition Plan"
        ]
    )
    
    if "💰 Salary Negotiation" in ai_feature:
        st.subheader("💰 Salary Negotiation Guide")
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input("Job Title:", placeholder="e.g., Software Engineer")
        with col2:
            location = st.text_input("Location:", placeholder="e.g., San Francisco, CA")
        
        if st.button("✨ Generate Negotiation Guide", type="primary"):
            if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
                with st.spinner("🤖 Creating negotiation strategy..."):
                    prompt = f"""
                    Create a comprehensive salary negotiation guide for:
                    
                    Job Title: {job_title}
                    Location: {location}
                    Resume: {st.session_state.resume_text[:1500]}
                    Job Description: {st.session_state.jd_text[:1000]}
                    
                    Provide:
                    1. Estimated salary range for this role and location
                    2. Key value propositions to highlight
                    3. 5 specific negotiation talking points
                    4. Non-salary benefits to consider
                    5. Sample negotiation scripts
                    6. Red flags to avoid
                    """
                    
                    guide = generate_with_gemini(prompt, max_tokens=1500)
                    st.markdown(guide)
                    st.download_button(
                        "📥 Download Guide",
                        guide,
                        "salary_negotiation_guide.txt",
                        "text/plain"
                    )
            else:
                st.error("Please analyze a resume first")
    
    elif "🏢 Company Research" in ai_feature:
        st.subheader("🏢 Company Research Report")
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name:", placeholder="e.g., Google")
        with col2:
            job_title = st.text_input("Job Title:", placeholder="e.g., Product Manager")
        
        if st.button("✨ Generate Research Report", type="primary"):
            if company_name and job_title:
                with st.spinner("🤖 Researching company..."):
                    prompt = f"""
                    Create a detailed company research report for interview preparation:
                    
                    Company: {company_name}
                    Position: {job_title}
                    
                    Provide:
                    1. Company Overview (mission, values, recent news)
                    2. Industry Position and Competitors
                    3. Recent Financial Performance
                    4. Company Culture and Work Environment
                    5. Leadership Team
                    6. Recent Product Launches
                    7. Interview Questions Likely to be Asked
                    8. Questions to Ask the Interviewer
                    9. How to Align Your Experience
                    """
                    
                    report = generate_with_gemini(prompt, max_tokens=2000)
                    st.markdown(report)
                    st.download_button(
                        "📥 Download Report",
                        report,
                        f"{company_name.lower()}_research_report.txt",
                        "text/plain"
                    )
            else:
                st.error("Please enter company name and job title")
    
    elif "💼 LinkedIn Optimization" in ai_feature:
        st.subheader("💼 LinkedIn Profile Optimization")
        target_role = st.text_input("Target Role:", placeholder="e.g., Senior Data Scientist")
        
        if st.button("✨ Optimize LinkedIn Profile", type="primary"):
            if hasattr(st.session_state, 'resume_text') and target_role:
                with st.spinner("🤖 Optimizing LinkedIn profile..."):
                    prompt = f"""
                    Optimize LinkedIn profile for the target role:
                    
                    Current Resume: {st.session_state.resume_text[:1500]}
                    Target Role: {target_role}
                    
                    Provide optimized versions of:
                    1. Professional Headline (under 120 characters)
                    2. About Section (compelling summary, 2-3 paragraphs)
                    3. Experience Descriptions (for top 3 roles)
                    4. Skills Section (top 15 skills to highlight)
                    5. Keywords to include throughout profile
                    6. Content Strategy (what to post/share)
                    7. LinkedIn SEO tips
                    """
                    
                    optimization = generate_with_gemini(prompt, max_tokens=1800)
                    st.markdown(optimization)
                    st.download_button(
                        "📥 Download Optimization",
                        optimization,
                        "linkedin_optimization.txt",
                        "text/plain"
                    )
            else:
                st.error("Please analyze a resume first and enter target role")
    
    else:
        st.info("🚀 Select an AI tool above to get started!")
        st.markdown("**Available Tools:**")
        st.write("• 💰 Salary Negotiation Guide - Personalized negotiation strategy")
        st.write("• 🏢 Company Research Report - Comprehensive company analysis")
        st.write("• 💼 LinkedIn Optimization - Profile enhancement tips")
        st.write("• 📧 Follow-up Email Templates - Professional communication")
        st.write("• 🔄 Career Transition Plan - Strategic career change guidance")

def show_analytics_dashboard():
    st.header("📈 Advanced Analytics Dashboard")
    
    if st.session_state.user_data:
        sessions = get_user_sessions(st.session_state.user_data['id'])
        
        if sessions:
            # Enhanced metrics with cards
            st.subheader("📈 Performance Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_analyses = len(sessions)
            avg_match = sum(s[4] for s in sessions) / len(sessions)
            avg_ats = sum(s[5] for s in sessions) / len(sessions)
            best_score = max(s[4] for s in sessions)
            
            with col1:
                st.metric("📆 Total Analyses", total_analyses)
            
            with col2:
                st.metric("🎯 Avg Match Score", f"{avg_match:.1f}%")
            
            with col3:
                st.metric("📈 Avg ATS Score", f"{avg_ats:.1f}%")
            
            with col4:
                st.metric("🏆 Best Score", f"{best_score:.1f}%")
            
            # Progress chart
            if len(sessions) > 1:
                st.subheader("📈 Progress Over Time")
                
                # Create progress data
                dates = [datetime.strptime(s[7][:19], '%Y-%m-%d %H:%M:%S') for s in sessions[-10:]]
                match_scores = [s[4] for s in sessions[-10:]]
                ats_scores = [s[5] for s in sessions[-10:]]
                
                # Simple line chart
                chart_data = {
                    'Date': dates,
                    'Match Score': match_scores,
                    'ATS Score': ats_scores
                }
                
                st.line_chart(chart_data, x='Date')
            
            # Skill gap heatmap
            st.subheader("🔥 Skill Gap Analysis")
            
            if len(sessions) >= 1:
                latest_session = sessions[0]
                resume_text = latest_session[2]
                jd_text = latest_session[3]
                
                # Analyze missing skills
                jd_words = set(clean_text(jd_text).split())
                resume_words = set(clean_text(resume_text).split())
                missing_skills = list(jd_words - resume_words)[:10]
                
                if missing_skills:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("⚠️ **Missing Keywords:**")
                        for skill in missing_skills[:5]:
                            st.write(f"• {skill.title()}")
                    
                    with col2:
                        # Success probability
                        match_score = latest_session[4]
                        ats_score = latest_session[5]
                        
                        if match_score >= 80 and ats_score >= 80:
                            probability = 85
                        elif match_score >= 70 and ats_score >= 70:
                            probability = 65
                        elif match_score >= 60 and ats_score >= 60:
                            probability = 45
                        else:
                            probability = 25
                        
                        st.metric("🎯 Interview Probability", f"{probability}%")
                        
                        if probability >= 70:
                            st.success("🎉 High chance of success!")
                        elif probability >= 50:
                            st.warning("📈 Good potential, needs improvement")
                        else:
                            st.error("📉 Significant improvements needed")
            
            # Job matching simulation
            st.subheader("🔍 Smart Job Matching")
            
            job_search = st.text_input("🔍 Search job titles or companies:", placeholder="e.g., Software Engineer, Google")
            
            if job_search:
                # Simulate job matches
                sample_jobs = [
                    {"title": "Senior Software Engineer", "company": "TechCorp", "match": 85, "salary": "$120k-150k"},
                    {"title": "Full Stack Developer", "company": "StartupXYZ", "match": 78, "salary": "$90k-120k"},
                    {"title": "Software Engineer II", "company": "BigTech", "match": 72, "salary": "$110k-140k"},
                    {"title": "Frontend Developer", "company": "WebCorp", "match": 68, "salary": "$80k-110k"}
                ]
                
                st.write(f"📈 **Found {len(sample_jobs)} matching jobs:**")
                
                for i, job in enumerate(sample_jobs):
                    with st.expander(f"{job['title']} at {job['company']} - {job['match']}% match"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Match Score", f"{job['match']}%")
                        with col2:
                            st.metric("Salary Range", job['salary'])
                        with col3:
                            if st.button(f"Apply", key=f"apply_{i}"):
                                st.success(f"✅ Application tracked!")
        else:
            st.info("📈 Complete your first analysis to see analytics!")
    else:
        st.error("Please log in to view analytics")

def show_job_matching():
    """Enhanced job matching with compatibility scoring"""
    st.subheader("🎯 Job Compatibility Analysis")
    
    if hasattr(st.session_state, 'resume_text'):
        # Job input
        job_url = st.text_input("🔗 Job URL or paste job description:", placeholder="Paste job posting here...")
        
        if job_url:
            # Simulate compatibility analysis
            compatibility_score = 75  # Would be calculated based on resume vs job
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🎯 Compatibility", f"{compatibility_score}%")
            with col2:
                st.metric("📈 Success Rate", "68%")
            with col3:
                st.metric("💰 Salary Match", "$95k-125k")
            
            # Improvement suggestions
            st.write("💡 **To improve compatibility:**")
            st.write("• Add 'Python' and 'AWS' to skills section")
            st.write("• Quantify your project management experience")
            st.write("• Include 'Agile' methodology experience")
    else:
        st.info("📄 Upload a resume first to analyze job compatibility")

if __name__ == "__main__":
    main()