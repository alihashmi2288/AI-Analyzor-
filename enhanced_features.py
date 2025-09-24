"""
Enhanced Features Module for AI Resume Analyzer Pro
Free features that can be added immediately
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import re
from collections import Counter

def create_keyword_highlighting(resume_text, jd_text):
    """Highlight matching keywords between resume and job description"""
    if not resume_text or not jd_text:
        return resume_text, []
    
    # Extract keywords from job description
    jd_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', jd_text.lower()))
    resume_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower()))
    
    # Find matching keywords
    matching_keywords = jd_words & resume_words
    missing_keywords = jd_words - resume_words
    
    # Create highlighted resume text
    highlighted_resume = resume_text
    for keyword in matching_keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        highlighted_resume = pattern.sub(f"**{keyword.upper()}**", highlighted_resume)
    
    return highlighted_resume, list(missing_keywords)[:10]  # Top 10 missing

def create_skills_analysis(resume_text, jd_text):
    """Analyze skills match between resume and job description"""
    
    # Common skills database
    technical_skills = [
        'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb',
        'aws', 'docker', 'kubernetes', 'git', 'linux', 'html', 'css',
        'machine learning', 'data science', 'artificial intelligence',
        'project management', 'agile', 'scrum', 'devops', 'ci/cd'
    ]
    
    soft_skills = [
        'leadership', 'communication', 'teamwork', 'problem solving',
        'analytical', 'creative', 'adaptable', 'organized', 'detail-oriented',
        'time management', 'collaboration', 'presentation', 'negotiation'
    ]
    
    all_skills = technical_skills + soft_skills
    
    # Find skills in resume and job description
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    
    resume_skills = [skill for skill in all_skills if skill in resume_lower]
    jd_skills = [skill for skill in all_skills if skill in jd_lower]
    
    matched_skills = list(set(resume_skills) & set(jd_skills))
    missing_skills = list(set(jd_skills) - set(resume_skills))
    
    return {
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'resume_skills': resume_skills,
        'jd_skills': jd_skills
    }

def create_progress_chart(sessions):
    """Create progress tracking chart"""
    if len(sessions) < 2:
        return None
    
    dates = [session[7][:10] for session in sessions[-10:]]  # Last 10 sessions
    scores = [session[4] for session in sessions[-10:]]  # Match scores
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=scores,
        mode='lines+markers',
        name='Match Score',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Your Resume Score Progress",
        xaxis_title="Date",
        yaxis_title="Match Score (%)",
        height=400,
        showlegend=False
    )
    
    return fig

def create_score_gauge(score, title):
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': 70},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#667eea"},
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

def create_skills_chart(skills_data):
    """Create skills comparison chart"""
    matched = len(skills_data['matched_skills'])
    missing = len(skills_data['missing_skills'])
    
    fig = go.Figure(data=[
        go.Bar(name='Matched Skills', x=['Skills'], y=[matched], marker_color='green'),
        go.Bar(name='Missing Skills', x=['Skills'], y=[missing], marker_color='red')
    ])
    
    fig.update_layout(
        title="Skills Analysis",
        yaxis_title="Number of Skills",
        barmode='group',
        height=300
    )
    
    return fig

def generate_improvement_tips(match_score, ats_score, missing_skills):
    """Generate personalized improvement tips"""
    tips = []
    
    if match_score < 70:
        tips.extend([
            "🎯 Add more keywords from the job description",
            "📝 Highlight relevant experience more prominently",
            "🔍 Use industry-specific terminology",
            "📊 Quantify your achievements with numbers"
        ])
    
    if ats_score < 70:
        tips.extend([
            "⚡ Use more action verbs (managed, led, developed, created)",
            "📈 Add measurable results and metrics",
            "🏗️ Improve resume structure and formatting",
            "🎯 Include relevant certifications and skills"
        ])
    
    if missing_skills:
        tips.append(f"🛠️ Consider adding these skills: {', '.join(missing_skills[:5])}")
    
    if match_score >= 80 and ats_score >= 80:
        tips.extend([
            "🎉 Excellent work! Your resume is well-optimized",
            "🎯 Consider tailoring for specific companies",
            "📱 Update your LinkedIn profile to match",
            "🤝 Network with professionals in your target companies"
        ])
    
    return tips

def create_export_options(content, filename_base, content_type="resume"):
    """Create multiple export format options"""
    
    # HTML version with styling
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #667eea; }}
            .highlight {{ background-color: yellow; }}
            .section {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>{content_type.title()}</h1>
        <div class="section">
            {content.replace(chr(10), '<br>')}
        </div>
        <footer>
            <p><em>Generated by AI Resume Analyzer Pro - Created by Syed Ali Hashmi</em></p>
        </footer>
    </body>
    </html>
    """
    
    # Formatted text version
    formatted_content = f"""
{content_type.upper()}
{'='*50}

{content}

{'='*50}
Generated by AI Resume Analyzer Pro
Created by Syed Ali Hashmi
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return {
        'txt': content,
        'html': html_content,
        'formatted': formatted_content
    }

def create_usage_analytics(user_sessions):
    """Create user usage analytics"""
    if not user_sessions:
        return None
    
    # Calculate statistics
    total_analyses = len(user_sessions)
    avg_score = sum(session[4] for session in user_sessions) / total_analyses
    best_score = max(session[4] for session in user_sessions)
    recent_sessions = [s for s in user_sessions if datetime.strptime(s[7][:10], '%Y-%m-%d') > datetime.now() - timedelta(days=30)]
    
    analytics = {
        'total_analyses': total_analyses,
        'average_score': round(avg_score, 1),
        'best_score': best_score,
        'recent_activity': len(recent_sessions),
        'improvement_trend': 'improving' if len(user_sessions) > 1 and user_sessions[-1][4] > user_sessions[0][4] else 'stable'
    }
    
    return analytics

def create_resume_templates():
    """Provide basic resume templates"""
    templates = {
        "Professional": """
[Your Name]
[Your Email] | [Your Phone] | [Your Location]
[LinkedIn Profile] | [Portfolio/Website]

PROFESSIONAL SUMMARY
[2-3 lines describing your experience and key strengths]

EXPERIENCE
[Job Title] | [Company Name] | [Dates]
• [Achievement with quantifiable result]
• [Achievement with quantifiable result]
• [Achievement with quantifiable result]

[Job Title] | [Company Name] | [Dates]
• [Achievement with quantifiable result]
• [Achievement with quantifiable result]

EDUCATION
[Degree] | [University] | [Year]

SKILLS
Technical: [List relevant technical skills]
Soft Skills: [List relevant soft skills]
        """,
        
        "Modern": """
[YOUR NAME]
[Email] • [Phone] • [Location] • [LinkedIn] • [Portfolio]

ABOUT ME
[Brief, engaging summary of your professional identity]

PROFESSIONAL EXPERIENCE
[COMPANY NAME] | [Job Title] | [Dates]
→ [Impact-focused achievement]
→ [Impact-focused achievement]
→ [Impact-focused achievement]

[COMPANY NAME] | [Job Title] | [Dates]
→ [Impact-focused achievement]
→ [Impact-focused achievement]

EDUCATION & CERTIFICATIONS
[Degree/Certification] | [Institution] | [Year]

CORE COMPETENCIES
[Skill 1] • [Skill 2] • [Skill 3] • [Skill 4]
        """,
        
        "Technical": """
[Your Name]
Software Engineer
[Email] | [Phone] | [GitHub] | [LinkedIn] | [Portfolio]

TECHNICAL SUMMARY
[Brief overview of your technical expertise and experience]

TECHNICAL SKILLS
Languages: [Programming languages]
Frameworks: [Frameworks and libraries]
Tools: [Development tools and platforms]
Databases: [Database technologies]

PROFESSIONAL EXPERIENCE
[Job Title] | [Company] | [Dates]
• [Technical achievement with metrics]
• [Technical achievement with metrics]
• [Technical achievement with metrics]

PROJECTS
[Project Name] | [Technologies Used]
• [Project description and impact]
• [Technical challenges solved]

EDUCATION
[Degree] in [Field] | [University] | [Year]
        """
    }
    
    return templates

def create_success_metrics_display(analytics):
    """Display success metrics in an attractive format"""
    if not analytics:
        return
    
    # First row - 2 columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="📊 Total",
            value=str(analytics['total_analyses']),
            delta=f"+{analytics['recent_activity']}"
        )
        
    with col2:
        st.metric(
            label="📈 Avg",
            value=f"{analytics['average_score']}%",
            delta="Score"
        )
    
    # Second row - 2 columns
    col3, col4 = st.columns(2)
    
    with col3:
        st.metric(
            label="🎯 Best",
            value=f"{analytics['best_score']}%",
            delta="Record"
        )
        
    with col4:
        trend_text = "Up" if analytics['improvement_trend'] == 'improving' else "Stable"
        trend_icon = "📈" if analytics['improvement_trend'] == 'improving' else "📊"
        st.metric(
            label="📊 Trend",
            value=trend_text,
            delta=trend_icon
        )