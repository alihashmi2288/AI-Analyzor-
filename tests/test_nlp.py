"""
Unit tests for NLP processing
"""

import pytest
from src.nlp import NLPProcessor

class TestNLPProcessor:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.nlp_processor = NLPProcessor()
    
    def test_nlp_processor_initialization(self):
        """Test NLP processor initialization"""
        assert self.nlp_processor.skills_database is not None
        assert self.nlp_processor.ats_keywords is not None
        assert len(self.nlp_processor.skills_database) > 0
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        dirty_text = "Hello, World! This is a TEST with 123 numbers."
        clean_text = self.nlp_processor._clean_text(dirty_text)
        
        assert clean_text == "hello world this is a test with 123 numbers"
        assert clean_text.islower()
        assert not any(char in clean_text for char in "!,.")
    
    def test_clean_text_empty(self):
        """Test text cleaning with empty input"""
        assert self.nlp_processor._clean_text("") == ""
        assert self.nlp_processor._clean_text(None) == ""
    
    def test_extract_skills(self):
        """Test skills extraction"""
        resume_text = "I have experience with Python, Java, and React. I also know Machine Learning."
        skills = self.nlp_processor._extract_skills(resume_text)
        
        expected_skills = ["Python", "Java", "React", "Machine Learning"]
        for skill in expected_skills:
            assert skill in skills
    
    def test_extract_skills_empty(self):
        """Test skills extraction with empty text"""
        skills = self.nlp_processor._extract_skills("")
        assert skills == []
    
    def test_calculate_similarity(self):
        """Test similarity calculation"""
        text1 = "software engineer python java"
        text2 = "python developer java programming"
        
        similarity = self.nlp_processor._calculate_similarity(text1, text2)
        assert 0 <= similarity <= 100
        assert similarity > 0  # Should have some similarity
    
    def test_calculate_similarity_identical(self):
        """Test similarity with identical texts"""
        text = "python java programming"
        similarity = self.nlp_processor._calculate_similarity(text, text)
        assert similarity == 100.0
    
    def test_calculate_similarity_empty(self):
        """Test similarity with empty texts"""
        similarity = self.nlp_processor._calculate_similarity("", "")
        assert similarity == 0.0
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        text = "python developer with machine learning experience"
        keywords = self.nlp_processor._extract_keywords(text, top_n=5)
        
        assert len(keywords) <= 5
        assert all(isinstance(kw, tuple) and len(kw) == 2 for kw in keywords)
        assert all(isinstance(kw[1], float) for kw in keywords)
    
    def test_analyze_documents(self):
        """Test comprehensive document analysis"""
        resume_text = "Software engineer with Python and Java experience"
        jd_text = "Looking for Python developer with Java skills"
        
        results = self.nlp_processor.analyze_documents(resume_text, jd_text)
        
        required_keys = [
            'similarity_score', 'skill_match_rate', 'resume_skills', 
            'jd_skills', 'matched_skills', 'missing_skills'
        ]
        
        for key in required_keys:
            assert key in results
        
        assert isinstance(results['similarity_score'], (int, float))
        assert isinstance(results['skill_match_rate'], (int, float))
        assert isinstance(results['matched_skills'], list)
    
    def test_calculate_ats_score(self):
        """Test ATS score calculation"""
        resume_text = "Achieved 50% increase in sales. Managed team of 10 people. Led project to completion."
        jd_text = "Looking for manager with leadership experience"
        
        ats_results = self.nlp_processor.calculate_ats_score(resume_text, jd_text)
        
        required_keys = ['ats_score', 'ats_feedback', 'action_verbs_count', 'quantifiable_results']
        for key in required_keys:
            assert key in ats_results
        
        assert 0 <= ats_results['ats_score'] <= 100
        assert isinstance(ats_results['ats_feedback'], list)
    
    @pytest.mark.parametrize("text,expected_skills", [
        ("Python developer", ["Python"]),
        ("Java and JavaScript programmer", ["Java", "JavaScript"]),
        ("Machine Learning engineer", ["Machine Learning"]),
        ("No technical skills mentioned", [])
    ])
    def test_skill_extraction_cases(self, text, expected_skills):
        """Test various skill extraction cases"""
        extracted_skills = self.nlp_processor._extract_skills(text)
        for skill in expected_skills:
            assert skill in extracted_skills