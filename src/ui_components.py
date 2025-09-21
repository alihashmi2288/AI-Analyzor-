"""
UI components module for Streamlit interface
Reusable components for consistent and professional UI
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Any
import base64

class UIComponents:
    """Reusable UI components for the application"""
    
    def __init__(self):
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
    
    def apply_custom_css(self):
        """Apply custom CSS styling"""
        st.markdown("""
        <style>
            /* Main header styling */
            .main-header {
                font-size: 3.5rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            /* Metric cards */
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                margin: 0.5rem 0;
                transition: transform 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
            }
            
            .metric-value {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            }
            
            .metric-label {
                font-size: 1rem;
                opacity: 0.9;
            }
            
            /* Skill tags */
            .skill-match {
                background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                color: #155724;
                padding: 0.5rem 1rem;
                border-radius: 25px;
                margin: 0.3rem;
                display: inline-block;
                font-weight: 500;
                border: 2px solid #c3e6cb;
                transition: all 0.3s ease;
            }
            
            .skill-match:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            .skill-missing {
                background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
                color: #721c24;
                padding: 0.5rem 1rem;
                border-radius: 25px;
                margin: 0.3rem;
                display: inline-block;
                font-weight: 500;
                border: 2px solid #f5c6cb;
                transition: all 0.3s ease;
            }
            
            .skill-missing:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            /* Info boxes */
            .info-box {
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border-left: 5px solid #2196f3;
                margin: 1rem 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            .success-box {
                background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border-left: 5px solid #4caf50;
                margin: 1rem 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            .warning-box {
                background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border-left: 5px solid #ff9800;
                margin: 1rem 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            .danger-box {
                background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border-left: 5px solid #dc3545;
                margin: 1rem 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            /* Button styling */
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 0.75rem 2rem;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            }
            
            /* Progress bars */
            .progress-container {
                background-color: #e9ecef;
                border-radius: 10px;
                padding: 3px;
                margin: 0.5rem 0;
            }
            
            .progress-bar {
                height: 20px;
                border-radius: 8px;
                transition: width 0.6s ease;
            }
            
            /* Cards */
            .analysis-card {
                background: white;
                padding: 2rem;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                margin: 1rem 0;
                border: 1px solid #e9ecef;
            }
            
            /* Animations */
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .fade-in-up {
                animation: fadeInUp 0.6s ease-out;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def get_header_html(self, title: str) -> str:
        """Generate header HTML"""
        return f'<h1 class="main-header">{title}</h1>'
    
    def display_metric_card(self, label: str, value: str, delta: str = None):
        """Display a metric card"""
        delta_html = f'<div style="font-size: 0.9rem; opacity: 0.8;">{delta}</div>' if delta else ''
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
    
    def display_score_gauge(self, score: float, title: str = "Score") -> go.Figure:
        """Create a gauge chart for scores"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 20}},
            delta={'reference': 70},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': self.color_scheme['primary']},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': '#ffebee'},
                    {'range': [40, 70], 'color': '#fff3e0'},
                    {'range': [70, 100], 'color': '#e8f5e8'}
                ],
                'threshold': {
                    'line': {'color': self.color_scheme['danger'], 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            font={'color': "darkblue", 'family': "Arial"},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        return fig
    
    def display_skills_analysis(self, results: Dict):
        """Display skills analysis with styling"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### ✅ Matched Skills")
            if results.get('matched_skills'):
                skills_html = ""
                for skill in results['matched_skills']:
                    skills_html += f'<span class="skill-match">✓ {skill}</span> '
                st.markdown(skills_html, unsafe_allow_html=True)
            else:
                st.info("No matching skills found")
        
        with col2:
            st.markdown("### ❌ Missing Skills")
            if results.get('missing_skills'):
                skills_html = ""
                for skill in results['missing_skills']:
                    skills_html += f'<span class="skill-missing">✗ {skill}</span> '
                st.markdown(skills_html, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="warning-box">
                    💡 <strong>Recommendation:</strong> Consider adding these skills to your resume or highlighting related experience.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-box">
                    🎉 <strong>Excellent!</strong> All required skills are present in your resume.
                </div>
                """, unsafe_allow_html=True)
    
    def display_score_analysis(self, results: Dict):
        """Display comprehensive score analysis"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Overall score gauge
            score = results.get('similarity_score', 0)
            fig = self.display_score_gauge(score, "Overall Match Score")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # ATS score gauge
            ats_score = results.get('ats_score', 0)
            fig = self.display_score_gauge(ats_score, "ATS Score")
            st.plotly_chart(fig, use_container_width=True)
        
        # Score interpretation
        self._display_score_interpretation(results)
        
        # Detailed metrics
        self._display_detailed_metrics(results)
    
    def _display_score_interpretation(self, results: Dict):
        """Display score interpretation"""
        score = results.get('similarity_score', 0)
        
        if score >= 80:
            st.markdown("""
            <div class="success-box">
                🎉 <strong>Excellent Match!</strong> Your resume aligns very well with the job requirements.
                You're likely to pass initial screening and should focus on interview preparation.
            </div>
            """, unsafe_allow_html=True)
        elif score >= 60:
            st.markdown("""
            <div class="info-box">
                ✅ <strong>Good Match!</strong> Your resume shows good alignment with the job requirements.
                Consider addressing the missing skills highlighted below to strengthen your application.
            </div>
            """, unsafe_allow_html=True)
        elif score >= 40:
            st.markdown("""
            <div class="warning-box">
                ⚠️ <strong>Fair Match</strong> - There's room for improvement.
                Focus on the missing skills and consider tailoring your resume more closely to the job description.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="danger-box">
                ❌ <strong>Low Match</strong> - Significant improvements needed.
                Consider developing the missing skills or targeting roles that better match your current experience.
            </div>
            """, unsafe_allow_html=True)
    
    def _display_detailed_metrics(self, results: Dict):
        """Display detailed metrics breakdown"""
        st.subheader("📊 Detailed Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Skills breakdown pie chart
            skills_data = pd.DataFrame({
                'Category': ['Matched', 'Missing', 'Extra'],
                'Count': [
                    len(results.get('matched_skills', [])),
                    len(results.get('missing_skills', [])),
                    max(0, results.get('total_resume_skills', 0) - len(results.get('matched_skills', [])))
                ]
            })
            
            fig = px.pie(skills_data, values='Count', names='Category', 
                        title="Skills Breakdown",
                        color_discrete_sequence=[self.color_scheme['success'], 
                                               self.color_scheme['danger'], 
                                               self.color_scheme['info']])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Score comparison bar chart
            scores = {
                'Overall Match': results.get('similarity_score', 0),
                'ATS Score': results.get('ats_score', 0),
                'Skill Match': results.get('skill_match_rate', 0),
                'Semantic Score': results.get('semantic_score', 0)
            }
            
            fig = px.bar(x=list(scores.keys()), y=list(scores.values()),
                        title="Score Comparison",
                        color=list(scores.values()),
                        color_continuous_scale='RdYlGn')
            fig.update_layout(showlegend=False, yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Progress bars for different metrics
            st.markdown("#### Key Metrics")
            for metric, value in scores.items():
                self._display_progress_bar(metric, value)
    
    def _display_progress_bar(self, label: str, value: float):
        """Display a progress bar"""
        color = self._get_score_color(value)
        
        st.markdown(f"""
        <div style="margin: 0.5rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
                <span style="font-weight: 500;">{label}</span>
                <span style="font-weight: 600;">{value}%</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {value}%; background: {color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score"""
        if score >= 80:
            return self.color_scheme['success']
        elif score >= 60:
            return self.color_scheme['info']
        elif score >= 40:
            return self.color_scheme['warning']
        else:
            return self.color_scheme['danger']
    
    def display_ai_suggestions(self, results: Dict):
        """Display AI-generated suggestions"""
        suggestions = results.get('ai_suggestions', [])
        
        if suggestions:
            st.subheader("🤖 AI-Powered Suggestions")
            
            for i, suggestion in enumerate(suggestions, 1):
                st.markdown(f"""
                <div class="analysis-card fade-in-up">
                    <h4>💡 Suggestion {i}</h4>
                    <p>{suggestion}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Enable AI suggestions in the sidebar to get personalized recommendations")
    
    def display_comparison_results(self, results: List[Dict]):
        """Display multi-resume comparison results"""
        st.subheader("🔄 Resume Comparison Results")
        
        # Create comparison dataframe
        comparison_data = []
        for result in results:
            comparison_data.append({
                'Resume': result['filename'],
                'Match Score': result.get('similarity_score', 0),
                'ATS Score': result.get('ats_score', 0),
                'Skills Matched': len(result.get('matched_skills', [])),
                'Skills Missing': len(result.get('missing_skills', []))
            })
        
        df = pd.DataFrame(comparison_data)
        
        # Display as table
        st.dataframe(df, use_container_width=True)
        
        # Display as chart
        fig = px.bar(df, x='Resume', y=['Match Score', 'ATS Score'],
                    title="Resume Comparison",
                    barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    def create_download_link(self, data: bytes, filename: str, link_text: str) -> str:
        """Create download link for binary data"""
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" class="download-link">{link_text}</a>'
        return href
    
    def display_loading_animation(self, text: str = "Processing..."):
        """Display loading animation"""
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            <p style="margin-top: 1rem; font-weight: 500;">{text}</p>
        </div>
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """, unsafe_allow_html=True)