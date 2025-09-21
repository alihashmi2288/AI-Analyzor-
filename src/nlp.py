"""
NLP processing module for text analysis, skill extraction, and ATS scoring
Uses spaCy, scikit-learn, and custom algorithms
"""

import re
import spacy
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import pandas as pd

class NLPProcessor:
    """Handles all NLP-related processing"""
    
    def __init__(self):
        self.load_nlp_model()
        self.skills_database = self._load_skills_database()
        self.ats_keywords = self._load_ats_keywords()
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 3)
        )
    
    @st.cache_resource
    def load_nlp_model(_self):
        """Load spaCy model with caching"""
        try:
            # Try to load the transformer model first
            _self.nlp = spacy.load("en_core_web_trf")
        except OSError:
            try:
                # Fallback to smaller model
                _self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                st.warning("spaCy model not found. Some features may be limited.")
                _self.nlp = None
    
    def _load_skills_database(self) -> Dict[str, List[str]]:
        """Load comprehensive skills database"""
        return {
            'programming': [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 'Ruby',
                'Go', 'Rust', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'SQL', 'HTML', 'CSS'
            ],
            'frameworks': [
                'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring Boot',
                'Laravel', 'Express.js', 'FastAPI', 'ASP.NET', 'Ruby on Rails'
            ],
            'databases': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server',
                'Cassandra', 'DynamoDB', 'Neo4j', 'Elasticsearch'
            ],
            'cloud': [
                'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins',
                'GitLab CI', 'GitHub Actions', 'Terraform', 'Ansible'
            ],
            'data_science': [
                'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn',
                'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Jupyter', 'Apache Spark'
            ],
            'soft_skills': [
                'Leadership', 'Communication', 'Problem Solving', 'Team Work', 'Project Management',
                'Critical Thinking', 'Adaptability', 'Time Management', 'Creativity'
            ]
        }
    
    def _load_ats_keywords(self) -> List[str]:
        """Load ATS-friendly keywords"""
        return [
            'achieved', 'managed', 'led', 'developed', 'implemented', 'created',
            'improved', 'increased', 'decreased', 'optimized', 'streamlined',
            'collaborated', 'coordinated', 'supervised', 'trained', 'mentored'
        ]
    
    def analyze_documents(self, resume_text: str, jd_text: str) -> Dict:
        """Comprehensive document analysis"""
        # Clean texts for matching
        clean_resume = self._clean_text_for_matching(resume_text)
        clean_jd = self._clean_text_for_matching(jd_text)
        
        # Basic similarity
        similarity_score = self._calculate_similarity(clean_resume, clean_jd)
        
        # Skills analysis
        resume_skills = self._extract_skills(resume_text)
        jd_skills = self._extract_skills(jd_text)
        matched_skills = list(set(resume_skills) & set(jd_skills))
        missing_skills = list(set(jd_skills) - set(resume_skills))
        
        # Keyword analysis
        resume_keywords = self._extract_keywords(clean_resume)
        jd_keywords = self._extract_keywords(clean_jd)
        
        # Calculate metrics
        skill_match_rate = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0
        
        return {
            'similarity_score': similarity_score,
            'skill_match_rate': round(skill_match_rate, 1),
            'resume_skills': resume_skills,
            'jd_skills': jd_skills,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'resume_keywords': resume_keywords,
            'jd_keywords': jd_keywords,
            'total_resume_skills': len(resume_skills),
            'total_jd_skills': len(jd_skills)
        }
    
    def calculate_ats_score(self, resume_text: str, jd_text: str) -> Dict:
        """Calculate ATS-friendly score"""
        ats_score = 0
        feedback = []
        
        # Check for action verbs
        action_verbs_count = sum(1 for verb in self.ats_keywords if verb.lower() in resume_text.lower())
        ats_score += min(action_verbs_count * 2, 20)  # Max 20 points
        
        if action_verbs_count < 5:
            feedback.append("Add more action verbs (achieved, managed, led, etc.)")
        
        # Check for quantifiable results
        numbers = re.findall(r'\d+(?:\.\d+)?%?', resume_text)
        if len(numbers) >= 5:
            ats_score += 15
        elif len(numbers) >= 3:
            ats_score += 10
        else:
            ats_score += 5
            feedback.append("Include more quantifiable achievements with numbers/percentages")
        
        # Check keyword density
        jd_words = set(self._clean_text(jd_text).split())
        resume_words = set(self._clean_text(resume_text).split())
        keyword_overlap = len(jd_words & resume_words) / len(jd_words) if jd_words else 0
        ats_score += int(keyword_overlap * 30)  # Max 30 points
        
        if keyword_overlap < 0.3:
            feedback.append("Include more keywords from the job description")
        
        # Check for common sections
        sections = ['experience', 'education', 'skills', 'summary']
        section_score = sum(1 for section in sections if section in resume_text.lower())
        ats_score += section_score * 5  # Max 20 points
        
        # Check formatting issues
        if len(resume_text.split()) < 200:
            feedback.append("Resume might be too short - aim for 300-600 words")
        elif len(resume_text.split()) > 800:
            feedback.append("Resume might be too long - consider condensing")
        else:
            ats_score += 15
        
        return {
            'ats_score': min(ats_score, 100),
            'ats_feedback': feedback,
            'action_verbs_count': action_verbs_count,
            'quantifiable_results': len(numbers),
            'keyword_overlap': round(keyword_overlap * 100, 1)
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Replace newlines with spaces
        text = text.replace('\n', ' ')
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _clean_text_for_matching(self, text: str) -> str:
        """Clean text specifically for similarity matching"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate TF-IDF cosine similarity"""
        try:
            if not text1 or not text2:
                return 0.0
            
            vectors = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])
            return round(similarity[0][0] * 100, 2)
        except Exception:
            return 0.0
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills using deterministic matching + fuzzy matching"""
        found_skills = set()
        text_lower = text.lower()
        
        # Exact matching with word boundaries
        for category, skills in self.skills_database.items():
            for skill in skills:
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.add(skill)
        
        # Fuzzy matching for missed skills
        try:
            from rapidfuzz import process, fuzz
            all_skills = [skill for skills in self.skills_database.values() for skill in skills]
            
            # Split text into potential skill phrases
            words = text_lower.split()
            for i in range(len(words)):
                for j in range(i+1, min(i+4, len(words)+1)):  # Check 1-3 word phrases
                    phrase = ' '.join(words[i:j])
                    matches = process.extract(phrase, all_skills, scorer=fuzz.ratio, limit=1)
                    if matches and matches[0][1] > 85:  # High similarity threshold
                        found_skills.add(matches[0][0])
        except ImportError:
            pass  # Fuzzy matching not available
        
        return sorted(list(found_skills))
    
    def _extract_keywords(self, text: str, top_n: int = 20) -> List[Tuple[str, float]]:
        """Extract top keywords using TF-IDF"""
        try:
            if not text:
                return []
            
            tfidf_matrix = self.vectorizer.fit_transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            keywords = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
            return sorted(keywords, key=lambda x: x[1], reverse=True)[:top_n]
        except Exception:
            return []
    
    def extract_entities(self, text: str) -> Dict:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        entities = {
            'organizations': [ent.text for ent in doc.ents if ent.label_ == "ORG"],
            'persons': [ent.text for ent in doc.ents if ent.label_ == "PERSON"],
            'locations': [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]],
            'dates': [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        }
        
        return entities
    
    def suggest_improvements(self, resume_text: str, jd_text: str) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Analyze current state
        analysis = self.analyze_documents(resume_text, jd_text)
        ats_results = self.calculate_ats_score(resume_text, jd_text)
        
        # Skill-based suggestions
        if analysis['skill_match_rate'] < 50:
            suggestions.append(f"Consider adding these missing skills: {', '.join(analysis['missing_skills'][:5])}")
        
        # ATS suggestions
        suggestions.extend(ats_results['ats_feedback'])
        
        # Keyword suggestions
        if analysis['similarity_score'] < 60:
            top_jd_keywords = [kw[0] for kw in analysis['jd_keywords'][:5]]
            suggestions.append(f"Include more of these keywords: {', '.join(top_jd_keywords)}")
        
        return suggestions