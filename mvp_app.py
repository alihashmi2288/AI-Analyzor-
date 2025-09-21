"""
Phase 1 - Core MVP: AI Resume Analyzer
Basic functionality with resume upload, job matching, and cover letter generation
"""

import streamlit as st
import pdfplumber
import docx2txt
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
import plotly.graph_objects as go
from fpdf import FPDF
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'jd_text' not in st.session_state:
    st.session_state.jd_text = ""
if 'match_score' not in st.session_state:
    st.session_state.match_score = 0

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF using pdfplumber"""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX using docx2txt"""
    return docx2txt.process(uploaded_file)

def clean_text(text):
    """Clean and preprocess text"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,;:!?()-]', ' ', text)
    
    return text.strip()

def calculate_match_score(resume_text, jd_text):
    """Calculate TF-IDF cosine similarity between resume and job description"""
    if not resume_text or not jd_text:
        return 0
    
    # Clean texts
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(jd_text)
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    try:
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return round(similarity[0][0] * 100, 1)
    except:
        return 0

def create_match_visualization(score):
    """Create gauge chart for match score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Resume Match Score"},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def generate_cover_letter(resume_text, jd_text, job_title="", api_key=""):
    """Generate AI cover letter using OpenAI"""
    if not api_key:
        return "Please provide OpenAI API key to generate cover letter."
    
    try:
        openai.api_key = api_key
        
        prompt = f"""
        Write a professional cover letter based on the following:
        
        Job Title: {job_title if job_title else 'the position'}
        
        Resume Summary: {resume_text[:1500]}
        
        Job Description: {jd_text[:1000]}
        
        Write a concise, professional cover letter (3-4 paragraphs) that:
        - Opens with enthusiasm for the role
        - Highlights relevant skills and experience
        - Shows understanding of company needs
        - Closes with a call to action
        
        Keep it under 400 words and professional in tone.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating cover letter: {str(e)}"

def create_pdf_cover_letter(cover_letter_text, filename="cover_letter.pdf"):
    """Create PDF from cover letter text"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Cover Letter", ln=True, align='C')
    pdf.ln(10)
    
    # Content
    pdf.set_font("Arial", size=11)
    
    # Split text into lines for PDF
    lines = cover_letter_text.split('\n')
    for line in lines:
        if line.strip():
            # Handle long lines
            while len(line) > 80:
                pdf.cell(0, 6, line[:80], ln=True)
                line = line[80:]
            pdf.cell(0, 6, line, ln=True)
        else:
            pdf.ln(3)
    
    return pdf.output(dest='S').encode('latin-1')

# Main App
def main():
    st.title("📄 AI Resume Analyzer")
    st.markdown("### Upload your resume and job description to get instant analysis and AI-generated cover letter!")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input("OpenAI API Key (for cover letter)", type="password")
        
        st.header("📋 Instructions")
        st.info("""
        1. Upload your resume (PDF/DOCX)
        2. Add job description (paste or upload)
        3. Click 'Analyze' for match score
        4. Generate AI cover letter
        5. Download your cover letter
        """)
    
    # Main layout
    col1, col2 = st.columns([1, 1])
    
    # Left column - Inputs
    with col1:
        st.header("📄 Resume Upload")
        resume_file = st.file_uploader(
            "Upload Resume", 
            type=['pdf', 'docx'],
            help="Upload your resume in PDF or DOCX format"
        )
        
        if resume_file:
            st.success(f"✅ {resume_file.name} uploaded successfully!")
            
            # Extract text based on file type
            if resume_file.type == "application/pdf":
                st.session_state.resume_text = extract_text_from_pdf(resume_file)
            else:
                st.session_state.resume_text = extract_text_from_docx(resume_file)
            
            # Show preview
            with st.expander("📖 Resume Preview"):
                st.text_area("Resume Text", st.session_state.resume_text[:500] + "...", height=150, disabled=True)
        
        st.header("📋 Job Description")
        
        # Job description input options
        jd_option = st.radio("Choose input method:", ["Paste Text", "Upload File"])
        
        if jd_option == "Paste Text":
            jd_input = st.text_area("Paste job description here:", height=200)
            if jd_input:
                st.session_state.jd_text = jd_input
        else:
            jd_file = st.file_uploader("Upload Job Description", type=['pdf', 'docx'], key="jd")
            if jd_file:
                if jd_file.type == "application/pdf":
                    st.session_state.jd_text = extract_text_from_pdf(jd_file)
                else:
                    st.session_state.jd_text = extract_text_from_docx(jd_file)
                st.success(f"✅ {jd_file.name} uploaded successfully!")
        
        # Job title input
        job_title = st.text_input("Job Title (optional)", placeholder="e.g., Senior Software Engineer")
    
    # Right column - Results
    with col2:
        st.header("📊 Analysis Results")
        
        # Analyze button
        if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
            if st.session_state.resume_text and st.session_state.jd_text:
                with st.spinner("Analyzing resume..."):
                    st.session_state.match_score = calculate_match_score(
                        st.session_state.resume_text, 
                        st.session_state.jd_text
                    )
                st.success("Analysis complete!")
            else:
                st.error("Please upload both resume and job description")
        
        # Display results if analysis is done
        if st.session_state.match_score > 0:
            # Match score display
            score = st.session_state.match_score
            
            # Score badge
            if score >= 80:
                st.success(f"🎉 Excellent Match: {score}%")
            elif score >= 60:
                st.warning(f"✅ Good Match: {score}%")
            else:
                st.error(f"⚠️ Needs Improvement: {score}%")
            
            # Progress bar
            st.progress(score / 100)
            
            # Gauge visualization
            fig = create_match_visualization(score)
            st.plotly_chart(fig, use_container_width=True)
            
            # Gap analysis
            gap = 100 - score
            col_match, col_gap = st.columns(2)
            with col_match:
                st.metric("Match", f"{score}%", delta=f"{score-70}%")
            with col_gap:
                st.metric("Gap", f"{gap}%", delta=f"{70-score}%", delta_color="inverse")
    
    # Cover Letter Section
    if st.session_state.match_score > 0:
        st.markdown("---")
        st.header("📝 AI Cover Letter Generator")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("Generate a personalized cover letter based on your resume and the job description")
        
        with col2:
            generate_letter = st.button("✨ Generate Cover Letter", type="secondary")
        
        if generate_letter:
            if api_key:
                with st.spinner("Generating cover letter..."):
                    cover_letter = generate_cover_letter(
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        job_title,
                        api_key
                    )
                
                st.subheader("📄 Generated Cover Letter")
                
                # Editable cover letter
                edited_letter = st.text_area(
                    "Edit your cover letter:",
                    value=cover_letter,
                    height=400,
                    help="You can edit the generated cover letter before downloading"
                )
                
                # Download options
                col1, col2 = st.columns(2)
                
                with col1:
                    # Download as PDF
                    if st.button("📥 Download PDF"):
                        pdf_data = create_pdf_cover_letter(edited_letter)
                        st.download_button(
                            label="📄 Download Cover Letter PDF",
                            data=pdf_data,
                            file_name="cover_letter.pdf",
                            mime="application/pdf"
                        )
                
                with col2:
                    # Download as text
                    st.download_button(
                        label="📝 Download Text",
                        data=edited_letter,
                        file_name="cover_letter.txt",
                        mime="text/plain"
                    )
            else:
                st.warning("🔑 Please enter your OpenAI API key in the sidebar to generate cover letter")

if __name__ == "__main__":
    main()