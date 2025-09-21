import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from utils import ResumeAnalyzer, CoverLetterGenerator, ReportGenerator, UIHelpers
from config import *

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .skill-match {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        margin: 0.3rem;
        display: inline-block;
        font-weight: 500;
        border: 1px solid #c3e6cb;
    }
    
    .skill-missing {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        margin: 0.3rem;
        display: inline-block;
        font-weight: 500;
        border: 1px solid #f5c6cb;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'cover_letter' not in st.session_state:
        st.session_state.cover_letter = None
    
    # Header
    st.markdown(f'<h1 class="main-header">{APP_ICON} {APP_TITLE}</h1>', unsafe_allow_html=True)
    
    # Subtitle with animation
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3 style="color: #666; font-weight: 300;">
            🚀 Optimize your resume • 🎯 Match job requirements • 🤖 Generate AI cover letters
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "🔑 OpenAI API Key", 
            type="password",
            help="Required for AI cover letter generation"
        )
        
        if api_key:
            st.success("✅ API Key configured")
        else:
            st.info("💡 Add API key to enable cover letter generation")
        
        st.divider()
        
        # Analysis options
        st.header("📊 Analysis Options")
        show_wordcloud = st.checkbox("Show Word Clouds", value=True)
        show_keywords = st.checkbox("Show Top Keywords", value=True)
        show_detailed_analysis = st.checkbox("Show Detailed Analysis", value=True)
        
        st.divider()
        
        # Additional inputs for cover letter
        st.header("📝 Cover Letter Details")
        company_name = st.text_input("Company Name (Optional)")
        position_title = st.text_input("Position Title (Optional)")
        
        st.divider()
        
        # Tips
        st.header("💡 Tips")
        st.info("""
        **For best results:**
        - Use recent resume versions
        - Include complete job descriptions
        - Ensure files are text-readable
        - Add specific company details
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1], gap="large")
    
    # Resume upload section
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>📄 Step 1: Upload Your Resume</h3>
            <p>Upload your resume in PDF or DOCX format for analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        resume_file = st.file_uploader(
            "Choose your resume file",
            type=SUPPORTED_RESUME_FORMATS,
            help=f"Supported formats: {', '.join(SUPPORTED_RESUME_FORMATS).upper()}"
        )
        
        if resume_file:
            st.markdown("""
            <div class="success-box">
                ✅ <strong>Resume uploaded successfully!</strong><br>
                Ready for analysis
            </div>
            """, unsafe_allow_html=True)
            
            # Show file details
            st.caption(f"📁 {resume_file.name} ({resume_file.size} bytes)")
    
    # Job description section
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>📋 Step 2: Add Job Description</h3>
            <p>Paste the job description or upload a file</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["📝 Paste Text", "📁 Upload File"],
            horizontal=True
        )
        
        jd_text = ""
        
        if input_method == "📝 Paste Text":
            jd_text = st.text_area(
                "Paste job description here:",
                height=200,
                placeholder="Paste the complete job description including requirements, responsibilities, and qualifications..."
            )
        else:
            jd_file = st.file_uploader(
                "Choose job description file",
                type=SUPPORTED_JD_FORMATS,
                key="jd_file"
            )
            
            if jd_file:
                analyzer = ResumeAnalyzer()
                if jd_file.type == "application/pdf":
                    jd_text = analyzer.extract_text_from_pdf(jd_file)
                else:
                    jd_text = analyzer.extract_text_from_docx(jd_file)
                
                st.markdown("""
                <div class="success-box">
                    ✅ <strong>Job description uploaded!</strong><br>
                    Text extracted successfully
                </div>
                """, unsafe_allow_html=True)
        
        if jd_text:
            st.caption(f"📊 {len(jd_text.split())} words extracted")
    
    # Analysis section
    st.markdown("---")
    
    # Center the analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🚀 Analyze Resume",
            type="primary",
            use_container_width=True
        )
    
    # Perform analysis
    if analyze_button:
        if resume_file and jd_text.strip():
            with st.spinner("🔄 Analyzing your resume... This may take a moment."):
                # Initialize analyzer
                analyzer = ResumeAnalyzer()
                
                # Extract resume text
                if resume_file.type == "application/pdf":
                    resume_text = analyzer.extract_text_from_pdf(resume_file)
                else:
                    resume_text = analyzer.extract_text_from_docx(resume_file)
                
                # Perform analysis
                analysis_results = analyzer.analyze_resume(resume_text, jd_text)
                st.session_state.analysis_results = analysis_results
                
                # Store texts for cover letter generation
                st.session_state.resume_text = resume_text
                st.session_state.jd_text = jd_text
            
            st.success("✅ Analysis completed successfully!")
        else:
            st.error("⚠️ Please upload both resume and job description to proceed")
    
    # Display results if analysis is complete
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown("---")
        st.header("📊 Analysis Results")
        
        # Score interpretation
        UIHelpers.display_score_interpretation(results['similarity_score'])
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{results['similarity_score']}%</h2>
                <p>Overall Match</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{len(results['matched_skills'])}</h2>
                <p>Skills Matched</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{len(results['missing_skills'])}</h2>
                <p>Skills Missing</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{results['skill_match_rate']}%</h2>
                <p>Skill Match Rate</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Visualizations
        st.subheader("📈 Visual Analysis")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Gauge chart for overall score
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=results['similarity_score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Resume Match Score"},
                delta={'reference': 70},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': CHART_COLOR_SCHEME['primary']},
                    'steps': [
                        {'range': [0, 40], 'color': "lightgray"},
                        {'range': [40, 70], 'color': CHART_COLOR_SCHEME['warning']},
                        {'range': [70, 100], 'color': CHART_COLOR_SCHEME['success']}
                    ],
                    'threshold': {
                        'line': {'color': CHART_COLOR_SCHEME['danger'], 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Skills comparison pie chart
            skills_data = pd.DataFrame({
                'Category': ['Matched Skills', 'Missing Skills', 'Extra Skills'],
                'Count': [
                    len(results['matched_skills']),
                    len(results['missing_skills']),
                    max(0, results['total_resume_skills'] - len(results['matched_skills']))
                ]
            })
            
            fig = px.pie(
                skills_data, 
                values='Count', 
                names='Category',
                title="Skills Breakdown",
                color_discrete_sequence=[
                    CHART_COLOR_SCHEME['success'],
                    CHART_COLOR_SCHEME['danger'],
                    CHART_COLOR_SCHEME['info']
                ]
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Skills analysis
        st.subheader("🎯 Skills Analysis")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### ✅ Matched Skills")
            if results['matched_skills']:
                UIHelpers.display_skills_with_styling(results['matched_skills'], "matched")
            else:
                st.info("No matching skills found. Consider adding relevant skills to your resume.")
        
        with col2:
            st.markdown("### ❌ Missing Skills")
            if results['missing_skills']:
                UIHelpers.display_skills_with_styling(results['missing_skills'], "missing")
                st.markdown("""
                <div class="warning-box">
                    💡 <strong>Recommendation:</strong> Consider adding these skills to your resume or highlighting related experience.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("🎉 All required skills are present in your resume!")
        
        # Detailed analysis (optional)
        if show_detailed_analysis:
            st.subheader("🔍 Detailed Analysis")
            
            # Keywords analysis
            if show_keywords and results['resume_keywords']:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("#### 📄 Resume Keywords")
                    keywords_df = pd.DataFrame(
                        results['resume_keywords'][:10], 
                        columns=['Keyword', 'Score']
                    )
                    st.dataframe(keywords_df, use_container_width=True)
                
                with col2:
                    st.markdown("#### 📋 Job Description Keywords")
                    jd_keywords_df = pd.DataFrame(
                        results['jd_keywords'][:10], 
                        columns=['Keyword', 'Score']
                    )
                    st.dataframe(jd_keywords_df, use_container_width=True)
            
            # Word clouds
            if show_wordcloud:
                st.markdown("#### ☁️ Word Clouds")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.session_state.resume_text:
                        try:
                            wordcloud = WordCloud(
                                width=400, 
                                height=300, 
                                background_color='white',
                                colormap='viridis'
                            ).generate(st.session_state.resume_text)
                            
                            fig, ax = plt.subplots(figsize=(8, 6))
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis('off')
                            ax.set_title('Resume Word Cloud', fontsize=14, fontweight='bold')
                            st.pyplot(fig)
                        except:
                            st.info("Unable to generate word cloud for resume")
                
                with col2:
                    if st.session_state.jd_text:
                        try:
                            wordcloud = WordCloud(
                                width=400, 
                                height=300, 
                                background_color='white',
                                colormap='plasma'
                            ).generate(st.session_state.jd_text)
                            
                            fig, ax = plt.subplots(figsize=(8, 6))
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis('off')
                            ax.set_title('Job Description Word Cloud', fontsize=14, fontweight='bold')
                            st.pyplot(fig)
                        except:
                            st.info("Unable to generate word cloud for job description")
        
        # Cover letter generation
        st.markdown("---")
        st.header("📝 AI Cover Letter Generator")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="info-box">
                <h4>🤖 Generate Personalized Cover Letter</h4>
                <p>Our AI will create a tailored cover letter based on your resume and the job description.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            generate_cover_letter = st.button(
                "✨ Generate Cover Letter",
                type="secondary",
                use_container_width=True,
                disabled=not api_key
            )
        
        if generate_cover_letter and api_key:
            with st.spinner("🤖 Generating your personalized cover letter..."):
                generator = CoverLetterGenerator(api_key)
                cover_letter = generator.generate_cover_letter(
                    st.session_state.resume_text,
                    st.session_state.jd_text,
                    company_name,
                    position_title
                )
                st.session_state.cover_letter = cover_letter
        
        # Display cover letter
        if st.session_state.cover_letter:
            st.subheader("📄 Generated Cover Letter")
            
            # Editable cover letter
            edited_cover_letter = st.text_area(
                "Edit your cover letter:",
                value=st.session_state.cover_letter,
                height=400,
                help="You can edit the generated cover letter before downloading"
            )
            
            # Download button
            st.download_button(
                label="📥 Download Cover Letter",
                data=edited_cover_letter,
                file_name=f"cover_letter_{company_name or 'job_application'}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        elif not api_key:
            st.warning("🔑 Please add your OpenAI API key in the sidebar to generate cover letters")
        
        # Download report
        st.markdown("---")
        st.header("📥 Download Analysis Report")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="info-box">
                <h4>📊 Comprehensive Analysis Report</h4>
                <p>Download a detailed PDF report with all analysis results, recommendations, and insights.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("📄 Generate PDF Report", use_container_width=True):
                with st.spinner("📄 Generating PDF report..."):
                    report_generator = ReportGenerator()
                    pdf_data = report_generator.create_pdf_report(
                        results,
                        st.session_state.cover_letter or ""
                    )
                    
                    if pdf_data:
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_data,
                            file_name=f"resume_analysis_report_{company_name or 'analysis'}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("✅ PDF report generated successfully!")
                    else:
                        st.error("❌ Error generating PDF report")

if __name__ == "__main__":
    main()