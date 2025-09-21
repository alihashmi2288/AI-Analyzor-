import re
import streamlit as st
import pdfplumber
import docx2txt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from fpdf import FPDF
import io
from datetime import datetime
from config import *

class ResumeAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english', 
            max_features=MAX_FEATURES_TFIDF,
            ngram_range=(1, 2)
        )
    
    @staticmethod
    @st.cache_data
    def extract_text_from_pdf(uploaded_file):
        """Extract text from PDF file"""
        try:
            text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + " "
            return text.strip()
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    @staticmethod
    @st.cache_data
    def extract_text_from_docx(uploaded_file):
        """Extract text from DOCX file"""
        try:
            return docx2txt.process(uploaded_file)
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""
    
    @staticmethod
    def clean_text(text):
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_skills(self, text, skill_list=None):
        """Extract skills from text"""
        if skill_list is None:
            skill_list = ALL_SKILLS
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_list:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def calculate_similarity(self, resume_text, jd_text):
        """Calculate similarity between resume and job description"""
        try:
            if not resume_text or not jd_text:
                return 0
            
            vectors = self.vectorizer.fit_transform([resume_text, jd_text])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])
            return round(similarity[0][0] * 100, 2)
        except Exception as e:
            st.error(f"Error calculating similarity: {str(e)}")
            return 0
    
    def extract_keywords(self, text, top_n=TOP_KEYWORDS_COUNT):
        """Extract top keywords from text using TF-IDF"""
        try:
            if not text:
                return []
            
            tfidf_matrix = self.vectorizer.fit_transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            keywords = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
            return sorted(keywords, key=lambda x: x[1], reverse=True)[:top_n]
        except Exception as e:
            st.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def analyze_resume(self, resume_text, jd_text):
        """Comprehensive resume analysis"""
        # Clean texts
        clean_resume = self.clean_text(resume_text)
        clean_jd = self.clean_text(jd_text)
        
        # Calculate similarity
        similarity_score = self.calculate_similarity(clean_resume, clean_jd)
        
        # Extract skills
        resume_skills = self.extract_skills(resume_text)
        jd_skills = self.extract_skills(jd_text)
        
        matched_skills = list(set(resume_skills) & set(jd_skills))
        missing_skills = list(set(jd_skills) - set(resume_skills))
        
        # Extract keywords
        resume_keywords = self.extract_keywords(clean_resume)
        jd_keywords = self.extract_keywords(clean_jd)
        
        # Calculate additional metrics
        skill_match_rate = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0
        
        return {
            'similarity_score': similarity_score,
            'resume_skills': resume_skills,
            'jd_skills': jd_skills,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'skill_match_rate': round(skill_match_rate, 1),
            'resume_keywords': resume_keywords,
            'jd_keywords': jd_keywords,
            'total_resume_skills': len(resume_skills),
            'total_jd_skills': len(jd_skills)
        }

class CoverLetterGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key
    
    def generate_cover_letter(self, resume_text, job_description, company_name="", position_title=""):
        """Generate AI-powered cover letter"""
        if not self.api_key:
            return "Please provide OpenAI API key to generate cover letter."
        
        try:
            # Truncate texts to avoid token limits
            resume_excerpt = resume_text[:2000]
            jd_excerpt = job_description[:1000]
            
            prompt = f"""
            Write a professional cover letter for the following job application:
            
            Position: {position_title if position_title else 'the position'}
            Company: {company_name if company_name else 'your company'}
            
            Resume Summary: {resume_excerpt}
            
            Job Requirements: {jd_excerpt}
            
            Instructions:
            - Write in a professional, engaging tone
            - Highlight relevant skills and experiences from the resume
            - Address key requirements from the job description
            - Keep it concise (3-4 paragraphs)
            - Include a strong opening and closing
            - Make it personalized and specific
            
            Format as a complete cover letter with proper structure.
            """
            
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=MAX_TOKENS_COVER_LETTER,
                temperature=COVER_LETTER_TEMPERATURE
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating cover letter: {str(e)}"

class ReportGenerator:
    @staticmethod
    def create_pdf_report(analysis_results, cover_letter=""):
        """Generate PDF report with analysis results"""
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Title
            pdf.set_font(PDF_FONT, 'B', PDF_TITLE_SIZE)
            pdf.cell(0, 15, 'Resume Analysis Report', ln=True, align='C')
            pdf.ln(5)
            
            # Date
            pdf.set_font(PDF_FONT, '', 10)
            pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True)
            pdf.ln(5)
            
            # Summary Section
            pdf.set_font(PDF_FONT, 'B', 14)
            pdf.cell(0, 10, 'Analysis Summary', ln=True)
            pdf.set_font(PDF_FONT, '', PDF_FONT_SIZE)
            
            pdf.cell(0, 8, f'Overall Match Score: {analysis_results["similarity_score"]}%', ln=True)
            pdf.cell(0, 8, f'Skills Matched: {len(analysis_results["matched_skills"])}', ln=True)
            pdf.cell(0, 8, f'Skills Missing: {len(analysis_results["missing_skills"])}', ln=True)
            pdf.cell(0, 8, f'Skill Match Rate: {analysis_results["skill_match_rate"]}%', ln=True)
            pdf.ln(5)
            
            # Matched Skills
            if analysis_results["matched_skills"]:
                pdf.set_font(PDF_FONT, 'B', 12)
                pdf.cell(0, 10, 'Matched Skills:', ln=True)
                pdf.set_font(PDF_FONT, '', 10)
                
                for i, skill in enumerate(analysis_results["matched_skills"][:15]):  # Limit to 15
                    pdf.cell(0, 6, f'• {skill}', ln=True)
                
                if len(analysis_results["matched_skills"]) > 15:
                    pdf.cell(0, 6, f'... and {len(analysis_results["matched_skills"]) - 15} more', ln=True)
                pdf.ln(3)
            
            # Missing Skills
            if analysis_results["missing_skills"]:
                pdf.set_font(PDF_FONT, 'B', 12)
                pdf.cell(0, 10, 'Missing Skills (Recommendations):', ln=True)
                pdf.set_font(PDF_FONT, '', 10)
                
                for i, skill in enumerate(analysis_results["missing_skills"][:15]):  # Limit to 15
                    pdf.cell(0, 6, f'• {skill}', ln=True)
                
                if len(analysis_results["missing_skills"]) > 15:
                    pdf.cell(0, 6, f'... and {len(analysis_results["missing_skills"]) - 15} more', ln=True)
                pdf.ln(3)
            
            # Top Keywords
            if analysis_results["resume_keywords"]:
                pdf.set_font(PDF_FONT, 'B', 12)
                pdf.cell(0, 10, 'Top Resume Keywords:', ln=True)
                pdf.set_font(PDF_FONT, '', 10)
                
                for keyword, score in analysis_results["resume_keywords"][:10]:
                    pdf.cell(0, 6, f'• {keyword} ({score:.3f})', ln=True)
                pdf.ln(3)
            
            # Recommendations
            pdf.set_font(PDF_FONT, 'B', 12)
            pdf.cell(0, 10, 'Recommendations:', ln=True)
            pdf.set_font(PDF_FONT, '', 10)
            
            score = analysis_results["similarity_score"]
            if score >= SCORE_THRESHOLDS["excellent"]:
                pdf.cell(0, 6, '• Excellent match! Your resume aligns well with the job requirements.', ln=True)
            elif score >= SCORE_THRESHOLDS["good"]:
                pdf.cell(0, 6, '• Good match. Consider highlighting missing skills in your cover letter.', ln=True)
            elif score >= SCORE_THRESHOLDS["fair"]:
                pdf.cell(0, 6, '• Fair match. Focus on developing the missing skills listed above.', ln=True)
            else:
                pdf.cell(0, 6, '• Low match. Consider significant resume improvements or skill development.', ln=True)
            
            pdf.cell(0, 6, '• Tailor your resume to include more job-specific keywords.', ln=True)
            pdf.cell(0, 6, '• Quantify your achievements with specific metrics and results.', ln=True)
            
            return pdf.output(dest='S').encode('latin-1')
            
        except Exception as e:
            st.error(f"Error generating PDF report: {str(e)}")
            return None

class UIHelpers:
    @staticmethod
    def display_score_interpretation(score):
        """Display score interpretation with color coding"""
        if score >= SCORE_THRESHOLDS["excellent"]:
            st.success(f"🎉 Excellent match! ({score}%)")
            st.info("Your resume aligns very well with the job requirements.")
        elif score >= SCORE_THRESHOLDS["good"]:
            st.success(f"✅ Good match! ({score}%)")
            st.info("Your resume shows good alignment. Consider addressing missing skills.")
        elif score >= SCORE_THRESHOLDS["fair"]:
            st.warning(f"⚠️ Fair match ({score}%)")
            st.info("There's room for improvement. Focus on the missing skills.")
        else:
            st.error(f"❌ Low match ({score}%)")
            st.info("Significant improvements needed to match job requirements.")
    
    @staticmethod
    def display_skills_with_styling(skills, skill_type="matched"):
        """Display skills with appropriate styling"""
        if not skills:
            return
        
        css_class = "skill-match" if skill_type == "matched" else "skill-missing"
        icon = "✓" if skill_type == "matched" else "✗"
        
        skills_html = ""
        for skill in skills:
            skills_html += f'<span class="{css_class}">{icon} {skill}</span> '
        
        st.markdown(skills_html, unsafe_allow_html=True)
    
    @staticmethod
    def create_download_link(data, filename, link_text):
        """Create download link for data"""
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{link_text}</a>'
        return href