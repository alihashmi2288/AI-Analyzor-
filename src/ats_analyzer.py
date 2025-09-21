"""
ATS (Applicant Tracking System) analyzer module
Provides transparent ATS scoring with detailed feedback
"""

import re
from typing import Dict, List, Tuple
import streamlit as st

class ATSAnalyzer:
    """Analyzes resume for ATS compatibility with transparent scoring"""
    
    def __init__(self):
        self.action_verbs = [
            'achieved', 'managed', 'led', 'developed', 'implemented', 'created',
            'improved', 'increased', 'decreased', 'optimized', 'streamlined',
            'collaborated', 'coordinated', 'supervised', 'trained', 'mentored',
            'designed', 'built', 'launched', 'delivered', 'executed', 'analyzed'
        ]
        
        self.required_sections = [
            'experience', 'education', 'skills', 'summary', 'objective'
        ]
        
        self.scoring_weights = {
            'keyword_density': 30,
            'action_verbs': 20,
            'quantifiable_results': 20,
            'section_presence': 15,
            'formatting': 10,
            'length': 5
        }
    
    def calculate_ats_score(self, resume_text: str, jd_text: str) -> Dict:
        """Calculate comprehensive ATS score with detailed breakdown"""
        
        scores = {}
        feedback = []
        details = {}
        
        # 1. Keyword Density Analysis (30 points)
        keyword_score, keyword_details = self._analyze_keywords(resume_text, jd_text)
        scores['keyword_density'] = keyword_score
        details['keywords'] = keyword_details
        
        if keyword_score < 20:
            feedback.append("Include more keywords from the job description")
        
        # 2. Action Verbs Analysis (20 points)
        action_score, action_details = self._analyze_action_verbs(resume_text)
        scores['action_verbs'] = action_score
        details['action_verbs'] = action_details
        
        if action_score < 15:
            feedback.append("Use more strong action verbs (achieved, managed, led, etc.)")
        
        # 3. Quantifiable Results (20 points)
        quant_score, quant_details = self._analyze_quantifiable_results(resume_text)
        scores['quantifiable_results'] = quant_score
        details['quantifiable_results'] = quant_details
        
        if quant_score < 15:
            feedback.append("Add more quantifiable achievements with numbers and percentages")
        
        # 4. Section Presence (15 points)
        section_score, section_details = self._analyze_sections(resume_text)
        scores['section_presence'] = section_score
        details['sections'] = section_details
        
        if section_score < 10:
            feedback.append("Ensure all standard resume sections are present and clearly labeled")
        
        # 5. Formatting Analysis (10 points)
        format_score, format_details = self._analyze_formatting(resume_text)
        scores['formatting'] = format_score
        details['formatting'] = format_details
        
        if format_score < 7:
            feedback.append("Improve resume formatting for better ATS readability")
        
        # 6. Length Analysis (5 points)
        length_score, length_details = self._analyze_length(resume_text)
        scores['length'] = length_score
        details['length'] = length_details
        
        if length_score < 3:
            feedback.append("Optimize resume length (aim for 300-800 words)")
        
        # Calculate total ATS score
        total_score = sum(scores.values())
        
        return {\n            'ats_score': min(total_score, 100),\n            'score_breakdown': scores,\n            'ats_feedback': feedback,\n            'detailed_analysis': details,\n            'scoring_weights': self.scoring_weights\n        }\n    \n    def _analyze_keywords(self, resume_text: str, jd_text: str) -> Tuple[float, Dict]:\n        \"\"\"Analyze keyword density and overlap\"\"\"\n        # Extract keywords from job description\n        jd_words = set(self._extract_keywords(jd_text.lower()))\n        resume_words = set(self._extract_keywords(resume_text.lower()))\n        \n        # Calculate overlap\n        matched_keywords = jd_words & resume_words\n        keyword_overlap = len(matched_keywords) / len(jd_words) if jd_words else 0\n        \n        # Score based on overlap percentage\n        score = min(keyword_overlap * self.scoring_weights['keyword_density'], self.scoring_weights['keyword_density'])\n        \n        details = {\n            'jd_keywords': sorted(list(jd_words))[:20],  # Top 20 for display\n            'matched_keywords': sorted(list(matched_keywords)),\n            'missing_keywords': sorted(list(jd_words - matched_keywords))[:10],  # Top 10 missing\n            'overlap_percentage': round(keyword_overlap * 100, 1)\n        }\n        \n        return score, details\n    \n    def _extract_keywords(self, text: str) -> List[str]:\n        \"\"\"Extract meaningful keywords from text\"\"\"\n        # Remove common stop words and extract meaningful terms\n        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}\n        \n        # Extract words (2+ characters, alphanumeric)\n        words = re.findall(r'\\b[a-zA-Z]{2,}\\b', text)\n        keywords = [word for word in words if word.lower() not in stop_words and len(word) > 2]\n        \n        return keywords\n    \n    def _analyze_action_verbs(self, resume_text: str) -> Tuple[float, Dict]:\n        \"\"\"Analyze usage of strong action verbs\"\"\"\n        text_lower = resume_text.lower()\n        found_verbs = []\n        \n        for verb in self.action_verbs:\n            if re.search(r'\\b' + verb + r'\\b', text_lower):\n                found_verbs.append(verb)\n        \n        # Score based on number of unique action verbs\n        verb_count = len(found_verbs)\n        max_expected = 8  # Reasonable number of action verbs\n        score = min((verb_count / max_expected) * self.scoring_weights['action_verbs'], self.scoring_weights['action_verbs'])\n        \n        details = {\n            'found_verbs': found_verbs,\n            'verb_count': verb_count,\n            'missing_verbs': [verb for verb in self.action_verbs[:10] if verb not in found_verbs]\n        }\n        \n        return score, details\n    \n    def _analyze_quantifiable_results(self, resume_text: str) -> Tuple[float, Dict]:\n        \"\"\"Analyze presence of quantifiable achievements\"\"\"\n        # Find numbers, percentages, and quantifiable terms\n        numbers = re.findall(r'\\d+(?:\\.\\d+)?%?', resume_text)\n        money_amounts = re.findall(r'\\$[\\d,]+(?:\\.\\d{2})?[KMB]?', resume_text)\n        time_periods = re.findall(r'\\d+\\s*(?:years?|months?|weeks?|days?)', resume_text, re.IGNORECASE)\n        \n        total_quantifiers = len(numbers) + len(money_amounts) + len(time_periods)\n        \n        # Score based on number of quantifiable results\n        min_expected = 5\n        score = min((total_quantifiers / min_expected) * self.scoring_weights['quantifiable_results'], self.scoring_weights['quantifiable_results'])\n        \n        details = {\n            'numbers_found': numbers[:10],  # Limit for display\n            'money_amounts': money_amounts,\n            'time_periods': time_periods,\n            'total_quantifiers': total_quantifiers\n        }\n        \n        return score, details\n    \n    def _analyze_sections(self, resume_text: str) -> Tuple[float, Dict]:\n        \"\"\"Analyze presence of standard resume sections\"\"\"\n        text_lower = resume_text.lower()\n        found_sections = []\n        \n        section_patterns = {\n            'experience': ['experience', 'work history', 'employment', 'professional experience', 'career history'],\n            'education': ['education', 'academic', 'degree', 'university', 'college', 'school'],\n            'skills': ['skills', 'technical skills', 'competencies', 'technologies', 'proficiencies'],\n            'summary': ['summary', 'profile', 'objective', 'about', 'overview'],\n        }\n        \n        for section, patterns in section_patterns.items():\n            if any(pattern in text_lower for pattern in patterns):\n                found_sections.append(section)\n        \n        # Score based on section presence\n        section_ratio = len(found_sections) / len(section_patterns)\n        score = section_ratio * self.scoring_weights['section_presence']\n        \n        details = {\n            'found_sections': found_sections,\n            'missing_sections': [section for section in section_patterns.keys() if section not in found_sections],\n            'section_count': len(found_sections)\n        }\n        \n        return score, details\n    \n    def _analyze_formatting(self, resume_text: str) -> Tuple[float, Dict]:\n        \"\"\"Analyze formatting quality for ATS readability\"\"\"\n        issues = []\n        score = self.scoring_weights['formatting']\n        \n        # Check for common formatting issues\n        if len(re.findall(r'[^\\w\\s.,;:!?()-]', resume_text)) > 20:\n            issues.append('Too many special characters')\n            score -= 2\n        \n        # Check for reasonable line breaks\n        lines = resume_text.split('\\n')\n        if len(lines) < 10:\n            issues.append('Poor line structure')\n            score -= 2\n        \n        # Check for consistent spacing\n        if '  ' in resume_text:  # Multiple spaces\n            issues.append('Inconsistent spacing')\n            score -= 1\n        \n        # Check for bullet points or structure\n        if not any(char in resume_text for char in ['•', '-', '*', '\\t']):\n            issues.append('No clear bullet points or structure')\n            score -= 2\n        \n        details = {\n            'formatting_issues': issues,\n            'line_count': len(lines),\n            'has_structure': any(char in resume_text for char in ['•', '-', '*', '\\t'])\n        }\n        \n        return max(score, 0), details\n    \n    def _analyze_length(self, resume_text: str) -> Tuple[float, Dict]:\n        \"\"\"Analyze resume length appropriateness\"\"\"\n        word_count = len(resume_text.split())\n        char_count = len(resume_text)\n        \n        # Optimal range: 300-800 words\n        if 300 <= word_count <= 800:\n            score = self.scoring_weights['length']\n        elif 200 <= word_count < 300 or 800 < word_count <= 1000:\n            score = self.scoring_weights['length'] * 0.7\n        else:\n            score = self.scoring_weights['length'] * 0.3\n        \n        details = {\n            'word_count': word_count,\n            'character_count': char_count,\n            'length_assessment': self._get_length_assessment(word_count)\n        }\n        \n        return score, details\n    \n    def _get_length_assessment(self, word_count: int) -> str:\n        \"\"\"Get length assessment message\"\"\"\n        if word_count < 200:\n            return \"Too short - add more detail\"\n        elif word_count < 300:\n            return \"Slightly short - consider adding more achievements\"\n        elif word_count <= 800:\n            return \"Optimal length\"\n        elif word_count <= 1000:\n            return \"Slightly long - consider condensing\"\n        else:\n            return \"Too long - significantly reduce content\"\n    \n    def get_ats_recommendations(self, analysis_results: Dict) -> List[str]:\n        \"\"\"Generate specific ATS improvement recommendations\"\"\"\n        recommendations = []\n        details = analysis_results['detailed_analysis']\n        \n        # Keyword recommendations\n        if details['keywords']['overlap_percentage'] < 30:\n            missing = details['keywords']['missing_keywords'][:5]\n            recommendations.append(f\"Add these missing keywords: {', '.join(missing)}\")\n        \n        # Action verb recommendations\n        if len(details['action_verbs']['found_verbs']) < 5:\n            missing_verbs = details['action_verbs']['missing_verbs'][:3]\n            recommendations.append(f\"Use more action verbs like: {', '.join(missing_verbs)}\")\n        \n        # Quantification recommendations\n        if details['quantifiable_results']['total_quantifiers'] < 3:\n            recommendations.append(\"Add specific numbers, percentages, and metrics to your achievements\")\n        \n        # Section recommendations\n        if details['sections']['missing_sections']:\n            missing_sections = details['sections']['missing_sections']\n            recommendations.append(f\"Add missing sections: {', '.join(missing_sections)}\")\n        \n        return recommendations