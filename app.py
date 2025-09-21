"""
AI Resume Analyzer - Main Streamlit Application
Professional resume analysis with ATS scoring, skill matching, and AI-powered improvements
"""

import streamlit as st
import os
from dotenv import load_dotenv
from src.ui_components import UIComponents
from src.auth import AuthManager
from src.storage import StorageManager
from src.parsers import DocumentParser
from src.nlp import NLPProcessor
from src.embeddings import EmbeddingProcessor
from src.llm_client import LLMClient
from src.export import ReportExporter

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ResumeAnalyzerApp:
    def __init__(self):
        self.ui = UIComponents()
        self.auth = AuthManager()
        self.storage = StorageManager()
        self.parser = DocumentParser()
        self.nlp = NLPProcessor()
        self.embeddings = EmbeddingProcessor()
        self.llm = LLMClient()
        self.exporter = ReportExporter()
        
        # Initialize session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
    
    def run(self):
        """Main application entry point"""
        self.ui.apply_custom_css()
        
        # Authentication check
        if not st.session_state.authenticated:
            self.show_auth_page()
            return
        
        # Main application
        self.show_main_app()
    
    def show_auth_page(self):
        """Display authentication page"""
        st.markdown(self.ui.get_header_html("🎯 AI Resume Analyzer Pro"), unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Welcome! Please sign in to continue")
            
            tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
            
            with tab1:
                if self.auth.show_login_form():
                    st.session_state.authenticated = True
                    st.rerun()
            
            with tab2:
                if self.auth.show_signup_form():
                    st.success("Account created! Please sign in.")
    
    def show_main_app(self):
        """Display main application interface"""
        # Header
        st.markdown(self.ui.get_header_html("🎯 AI Resume Analyzer Pro"), unsafe_allow_html=True)
        
        # Sidebar
        self.show_sidebar()
        
        # Main content
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📄 Resume Analysis", 
            "🔄 Multi-Compare", 
            "📝 AI Improvements", 
            "❓ Interview Prep",
            "📊 History"
        ])
        
        with tab1:
            self.show_resume_analysis()
        
        with tab2:
            self.show_multi_compare()
        
        with tab3:
            self.show_ai_improvements()
        
        with tab4:
            self.show_interview_prep()
        
        with tab5:
            self.show_history()
    
    def show_sidebar(self):
        """Display sidebar configuration"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # User info
            user_info = self.auth.get_current_user()
            st.info(f"👤 Welcome, {user_info.get('name', 'User')}!")
            
            if st.button("🚪 Logout"):
                st.session_state.authenticated = False
                st.rerun()
            
            st.divider()
            
            # API Configuration
            st.subheader("🔑 API Settings")
            openai_key = st.text_input("OpenAI API Key", type="password")
            if openai_key:
                os.environ['OPENAI_API_KEY'] = openai_key
                self.llm.set_api_key(openai_key)
            
            st.divider()
            
            # Analysis Options
            st.subheader("📊 Analysis Options")
            self.analysis_depth = st.selectbox(
                "Analysis Depth",
                ["Quick", "Standard", "Deep"],
                index=1
            )
            
            self.include_ats = st.checkbox("ATS Scoring", value=True)
            self.include_semantic = st.checkbox("Semantic Analysis", value=True)
            self.include_suggestions = st.checkbox("AI Suggestions", value=True)
    
    def show_resume_analysis(self):
        """Main resume analysis interface"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📄 Upload Resume")
            resume_file = st.file_uploader(
                "Choose resume file", 
                type=['pdf', 'docx'],
                help="Upload your resume in PDF or DOCX format"
            )
            
            if resume_file:
                st.success("✅ Resume uploaded successfully!")
                resume_text = self.parser.extract_text(resume_file)
                st.session_state.resume_text = resume_text
        
        with col2:
            st.markdown("### 📋 Job Description")
            input_method = st.radio("Input method:", ["Paste Text", "Upload File"])
            
            if input_method == "Paste Text":
                jd_text = st.text_area("Paste job description:", height=200)
            else:
                jd_file = st.file_uploader("Upload job description", type=['pdf', 'docx', 'txt'])
                jd_text = self.parser.extract_text(jd_file) if jd_file else ""
            
            if jd_text:
                st.session_state.jd_text = jd_text
        
        # Analysis button
        if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
            if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'jd_text'):
                self.perform_analysis()
            else:
                st.error("Please upload both resume and job description")
        
        # Display results
        if st.session_state.analysis_results:
            self.display_analysis_results()
    
    def perform_analysis(self):
        """Perform comprehensive resume analysis"""
        with st.spinner("🔄 Analyzing resume... This may take a moment."):
            resume_text = st.session_state.resume_text
            jd_text = st.session_state.jd_text
            
            # Basic NLP analysis
            nlp_results = self.nlp.analyze_documents(resume_text, jd_text)
            
            # Semantic analysis
            if self.include_semantic:
                semantic_results = self.embeddings.compute_similarity(resume_text, jd_text)
                nlp_results.update(semantic_results)
            
            # ATS scoring
            if self.include_ats:
                ats_results = self.nlp.calculate_ats_score(resume_text, jd_text)
                nlp_results.update(ats_results)
            
            # AI suggestions
            if self.include_suggestions and os.getenv('OPENAI_API_KEY'):
                ai_suggestions = self.llm.generate_suggestions(resume_text, jd_text)
                nlp_results.update(ai_suggestions)
            
            st.session_state.analysis_results = nlp_results
            
            # Save to history
            self.storage.save_analysis(
                user_id=self.auth.get_current_user()['id'],
                results=nlp_results
            )
    
    def display_analysis_results(self):
        """Display comprehensive analysis results"""
        results = st.session_state.analysis_results
        
        st.markdown("---")
        st.header("📊 Analysis Results")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.ui.display_metric_card("Match Score", f"{results.get('similarity_score', 0)}%")
        with col2:
            self.ui.display_metric_card("ATS Score", f"{results.get('ats_score', 0)}/100")
        with col3:
            self.ui.display_metric_card("Skills Match", f"{results.get('skill_match_rate', 0)}%")
        with col4:
            self.ui.display_metric_card("Improvement Potential", f"{results.get('improvement_score', 0)}%")
        
        # Detailed analysis tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Scores", "🎯 Skills", "💡 Suggestions", "📥 Export"])
        
        with tab1:
            self.ui.display_score_analysis(results)
        
        with tab2:
            self.ui.display_skills_analysis(results)
        
        with tab3:
            self.ui.display_ai_suggestions(results)
        
        with tab4:
            self.show_export_options(results)
    
    def show_multi_compare(self):
        """Multi-resume comparison interface"""
        st.markdown("### 🔄 Multi-Resume Comparison")
        st.info("Compare multiple resumes against the same job description")
        
        # Job description input
        jd_text = st.text_area("Job Description:", height=150)
        
        # Multiple resume upload
        resume_files = st.file_uploader(
            "Upload multiple resumes",
            type=['pdf', 'docx'],
            accept_multiple_files=True
        )
        
        if st.button("Compare Resumes") and resume_files and jd_text:
            self.perform_multi_comparison(resume_files, jd_text)
    
    def show_ai_improvements(self):
        """AI-powered resume improvements"""
        st.markdown("### 📝 AI-Powered Resume Improvements")
        
        if not st.session_state.analysis_results:
            st.warning("Please analyze a resume first")
            return
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🔄 Rewrite Resume Bullets")
            if st.button("Generate Improved Bullets"):
                self.generate_improved_bullets()
        
        with col2:
            st.subheader("📝 Cover Letter Templates")
            template = st.selectbox("Choose template:", ["Professional", "Creative", "Technical"])
            if st.button("Generate Cover Letter"):
                self.generate_cover_letter(template)
    
    def show_interview_prep(self):
        """Interview preparation tools"""
        st.markdown("### ❓ Interview Preparation")
        
        if not st.session_state.analysis_results:
            st.warning("Please analyze a resume first")
            return
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("❓ Generate Interview Questions")
            difficulty = st.selectbox("Difficulty:", ["Beginner", "Intermediate", "Advanced"])
            if st.button("Generate Questions"):
                self.generate_interview_questions(difficulty)
        
        with col2:
            st.subheader("💡 STAR Method Examples")
            if st.button("Generate STAR Examples"):
                self.generate_star_examples()
    
    def show_history(self):
        """User analysis history"""
        st.markdown("### 📊 Analysis History")
        
        user_id = self.auth.get_current_user()['id']
        history = self.storage.get_user_history(user_id)
        
        if history:
            for item in history:
                with st.expander(f"Analysis from {item['date']}"):
                    st.json(item['results'])
        else:
            st.info("No analysis history found")
    
    def show_export_options(self, results):
        """Export options for analysis results"""
        st.subheader("📥 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export PDF Report"):
                pdf_data = self.exporter.generate_pdf_report(results)
                st.download_button(
                    "Download PDF",
                    pdf_data,
                    "resume_analysis_report.pdf",
                    "application/pdf"
                )
        
        with col2:
            if st.button("📝 Export DOCX Report"):
                docx_data = self.exporter.generate_docx_report(results)
                st.download_button(
                    "Download DOCX",
                    docx_data,
                    "resume_analysis_report.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        
        with col3:
            if st.button("📊 Export JSON Data"):
                import json
                json_data = json.dumps(results, indent=2)
                st.download_button(
                    "Download JSON",
                    json_data,
                    "analysis_results.json",
                    "application/json"
                )
    
    def perform_multi_comparison(self, resume_files, jd_text):
        """Perform multi-resume comparison"""
        results = []
        
        for resume_file in resume_files:
            resume_text = self.parser.extract_text(resume_file)
            analysis = self.nlp.analyze_documents(resume_text, jd_text)
            analysis['filename'] = resume_file.name
            results.append(analysis)
        
        # Display comparison results
        self.ui.display_comparison_results(results)
    
    def generate_improved_bullets(self):
        """Generate improved resume bullet points"""
        if os.getenv('OPENAI_API_KEY'):
            improved_bullets = self.llm.improve_resume_bullets(
                st.session_state.resume_text,
                st.session_state.jd_text
            )
            st.text_area("Improved Bullets:", improved_bullets, height=300)
        else:
            st.error("OpenAI API key required")
    
    def generate_cover_letter(self, template):
        """Generate cover letter with selected template"""
        if os.getenv('OPENAI_API_KEY'):
            cover_letter = self.llm.generate_cover_letter(
                st.session_state.resume_text,
                st.session_state.jd_text,
                template
            )
            st.text_area("Generated Cover Letter:", cover_letter, height=400)
        else:
            st.error("OpenAI API key required")
    
    def generate_interview_questions(self, difficulty):
        """Generate interview questions"""
        if os.getenv('OPENAI_API_KEY'):
            questions = self.llm.generate_interview_questions(
                st.session_state.jd_text,
                difficulty
            )
            st.write(questions)
        else:
            st.error("OpenAI API key required")
    
    def generate_star_examples(self):
        """Generate STAR method examples"""
        if os.getenv('OPENAI_API_KEY'):
            examples = self.llm.generate_star_examples(
                st.session_state.resume_text
            )
            st.write(examples)
        else:
            st.error("OpenAI API key required")

def main():
    """Application entry point"""
    app = ResumeAnalyzerApp()
    app.run()

if __name__ == "__main__":
    main()