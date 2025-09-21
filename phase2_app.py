"""
Phase 2 - Advanced Features: Enhanced Resume Analyzer
Skill extraction, ATS scoring, multi-resume comparison, and interactive dashboard
"""

import streamlit as st
import pdfplumber
import docx2txt
import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="🎯",
    layout="wide"
)

# Load spaCy model
@st.cache_resource
def load_nlp_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
        return None

nlp = load_nlp_model()

# Skills database
SKILLS_LIST = [
    "Python", "Java", "JavaScript", "React", "Angular", "Vue.js", "Node.js", 
    "Django", "Flask", "HTML", "CSS", "SQL", "PostgreSQL", "MongoDB", 
    "AWS", "Azure", "Docker", "Kubernetes", "Git", "Machine Learning",
    "Data Analysis", "Project Management", "Leadership", "Communication"
]

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

def extract_skills(text, skills_list=SKILLS_LIST):
    """Extract skills from text using keyword matching"""
    found_skills = []
    text_lower = text.lower()
    
    for skill in skills_list:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))

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
    """Calculate ATS compatibility score"""
    if not resume_text or not jd_text:
        return 0
    
    # Extract keywords from job description
    jd_words = set(clean_text(jd_text).split())
    resume_words = set(clean_text(resume_text).split())
    
    # Calculate keyword overlap
    overlap = len(jd_words & resume_words)
    total_jd_words = len(jd_words)
    
    if total_jd_words == 0:
        return 0
    
    # ATS score based on keyword density
    ats_score = (overlap / total_jd_words) * 100
    
    # Bonus for action verbs
    action_verbs = ['managed', 'led', 'developed', 'created', 'improved', 'achieved']
    action_count = sum(1 for verb in action_verbs if verb in resume_text.lower())
    ats_score += min(action_count * 5, 20)  # Max 20 bonus points
    
    return min(round(ats_score, 1), 100)

def generate_improvement_suggestions(resume_text, jd_text, api_key):
    """Generate AI-powered resume improvement suggestions"""
    if not api_key:
        return "Please provide OpenAI API key for AI suggestions."
    
    try:
        openai.api_key = api_key
        
        prompt = f"""
        Analyze this resume against the job description and provide 5 specific improvement suggestions:
        
        Resume: {resume_text[:1500]}
        Job Description: {jd_text[:1000]}
        
        Provide actionable suggestions to improve the resume for this specific job.
        Focus on:
        1. Missing keywords
        2. Skills alignment
        3. Experience presentation
        4. Quantifiable achievements
        5. ATS optimization
        
        Format as numbered list.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating suggestions: {str(e)}"

def create_skills_chart(matched_skills, missing_skills):
    """Create skills comparison chart"""
    skills_data = pd.DataFrame({
        'Category': ['Matched Skills', 'Missing Skills'],
        'Count': [len(matched_skills), len(missing_skills)]
    })
    
    fig = px.pie(skills_data, values='Count', names='Category', 
                title="Skills Analysis",
                color_discrete_sequence=['#00cc96', '#ff6692'])
    
    return fig

def create_wordcloud(text, title):
    """Create word cloud visualization"""
    if not text:
        return None
    
    wordcloud = WordCloud(width=400, height=300, background_color='white').generate(text)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    return fig

def compare_multiple_resumes(resume_files, jd_text):
    """Compare multiple resumes against one job description"""
    results = []
    
    for resume_file in resume_files:
        # Extract text
        if resume_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(resume_file)
        else:
            resume_text = extract_text_from_docx(resume_file)
        
        # Calculate scores
        match_score = calculate_match_score(resume_text, jd_text)
        ats_score = calculate_ats_score(resume_text, jd_text)
        
        # Extract skills
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)
        matched_skills = list(set(resume_skills) & set(jd_skills))
        
        results.append({
            'filename': resume_file.name,
            'match_score': match_score,
            'ats_score': ats_score,
            'skills_matched': len(matched_skills),
            'total_skills': len(resume_skills)
        })
    
    return results

def main():
    st.title("🎯 AI Resume Analyzer Pro")
    st.markdown("### Advanced resume analysis with skill extraction, ATS scoring, and AI-powered insights")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input("OpenAI API Key", type="password")
        
        st.header("🎮 Demo Mode")
        if st.button("Load Sample Data"):
            st.session_state.demo_mode = True
            st.success("Sample data loaded!")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🎯 Skills", 
        "📝 Cover Letter", 
        "💡 Suggestions",
        "🔄 Multi-Compare"
    ])
    
    with tab1:
        st.header("📊 Resume Analysis Overview")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📄 Resume Upload")
            resume_file = st.file_uploader("Upload Resume", type=['pdf', 'docx'])
            
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
        if st.button("🚀 Analyze", type="primary"):
            if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
                with st.spinner("Analyzing..."):
                    # Calculate scores
                    match_score = calculate_match_score(st.session_state.resume_text, st.session_state.jd_text)
                    ats_score = calculate_ats_score(st.session_state.resume_text, st.session_state.jd_text)
                    
                    # Store results
                    st.session_state.match_score = match_score
                    st.session_state.ats_score = ats_score
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Match Score", f"{match_score}%")
                with col2:
                    st.metric("ATS Score", f"{ats_score}%")
                with col3:
                    overall = (match_score + ats_score) / 2
                    st.metric("Overall", f"{overall:.1f}%")
                
                # Gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=match_score,
                    title={'text': "Resume Match Score"},
                    gauge={'axis': {'range': [None, 100]},
                           'bar': {'color': "darkblue"},
                           'steps': [{'range': [0, 50], 'color': "lightgray"},
                                   {'range': [50, 80], 'color': "yellow"},
                                   {'range': [80, 100], 'color': "green"}]}
                ))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Please upload resume and add job description")
    
    with tab2:
        st.header("🎯 Skills Analysis")
        
        if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
            # Extract skills
            resume_skills = extract_skills(st.session_state.resume_text)
            jd_skills = extract_skills(st.session_state.jd_text)
            matched_skills = list(set(resume_skills) & set(jd_skills))
            missing_skills = list(set(jd_skills) - set(resume_skills))
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("✅ Matched Skills")
                if matched_skills:
                    for skill in matched_skills:
                        st.success(f"✓ {skill}")
                else:
                    st.info("No matching skills found")
            
            with col2:
                st.subheader("❌ Missing Skills")
                if missing_skills:
                    for skill in missing_skills:
                        st.error(f"✗ {skill}")
                else:
                    st.success("All required skills present!")
            
            # Skills chart
            if matched_skills or missing_skills:
                fig = create_skills_chart(matched_skills, missing_skills)
                st.plotly_chart(fig, use_container_width=True)
            
            # Word clouds
            st.subheader("☁️ Word Clouds")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                fig = create_wordcloud(st.session_state.resume_text, "Resume Keywords")
                if fig:
                    st.pyplot(fig)
            
            with col2:
                fig = create_wordcloud(st.session_state.jd_text, "Job Description Keywords")
                if fig:
                    st.pyplot(fig)
        else:
            st.info("Please analyze a resume first in the Overview tab")
    
    with tab3:
        st.header("📝 AI Cover Letter Generator")
        
        if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
            job_title = st.text_input("Job Title", placeholder="e.g., Senior Software Engineer")
            
            if st.button("Generate Cover Letter"):
                if api_key:
                    with st.spinner("Generating cover letter..."):
                        from mvp_app import generate_cover_letter
                        cover_letter = generate_cover_letter(
                            st.session_state.resume_text,
                            st.session_state.jd_text,
                            job_title,
                            api_key
                        )
                    
                    st.text_area("Generated Cover Letter", cover_letter, height=400)
                    
                    # Download button
                    st.download_button(
                        "📥 Download Cover Letter",
                        cover_letter,
                        "cover_letter.txt",
                        "text/plain"
                    )
                else:
                    st.warning("Please provide OpenAI API key")
        else:
            st.info("Please analyze a resume first")
    
    with tab4:
        st.header("💡 AI-Powered Suggestions")
        
        if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
            if st.button("Generate Improvement Suggestions"):
                if api_key:
                    with st.spinner("Generating suggestions..."):
                        suggestions = generate_improvement_suggestions(
                            st.session_state.resume_text,
                            st.session_state.jd_text,
                            api_key
                        )
                    
                    st.markdown("### 📋 Recommendations")
                    st.write(suggestions)
                else:
                    st.warning("Please provide OpenAI API key")
        else:
            st.info("Please analyze a resume first")
    
    with tab5:
        st.header("🔄 Multi-Resume Comparison")
        
        jd_text = st.text_area("Job Description for comparison:", height=150)
        resume_files = st.file_uploader(
            "Upload multiple resumes to compare",
            type=['pdf', 'docx'],
            accept_multiple_files=True
        )
        
        if st.button("Compare Resumes") and resume_files and jd_text:
            with st.spinner("Comparing resumes..."):
                results = compare_multiple_resumes(resume_files, jd_text)
            
            # Display results table
            df = pd.DataFrame(results)
            df = df.sort_values('match_score', ascending=False)
            
            st.subheader("📊 Comparison Results")
            st.dataframe(df, use_container_width=True)
            
            # Chart
            fig = px.bar(df, x='filename', y=['match_score', 'ats_score'],
                        title="Resume Comparison Scores",
                        barmode='group')
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()