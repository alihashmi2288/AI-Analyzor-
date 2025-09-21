"""
Gemini AI client module for Google's free AI API
Replaces OpenAI with Google Gemini for cost-free usage
"""

import google.generativeai as genai
import streamlit as st
from typing import Dict, List, Optional
import time
from src.ai_prompts import AIPrompts

class GeminiClient:
    """Handles all Gemini AI interactions with retry logic"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.prompts = AIPrompts()
        self.model_name = "gemini-1.5-flash"
        self.max_retries = 3
        self.retry_delay = 1
        
        if api_key:
            self.set_api_key(api_key)
    
    def set_api_key(self, api_key: str):
        """Set Gemini API key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
    
    def _make_api_call(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Make API call with retry logic"""
        if not self.api_key:
            return "Gemini API key not configured"
        
        for attempt in range(self.max_retries):
            try:
                model = genai.GenerativeModel(self.model_name)
                
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
                
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                return response.text.strip()
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    st.info(f"API limit hit. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                return f"Error: {str(e)}"
        
        return "Failed to get response after multiple attempts"
    
    def generate_suggestions(self, resume_text: str, jd_text: str) -> Dict:
        """Generate AI-powered improvement suggestions"""
        prompt = self.prompts.get_improvement_prompt(resume_text, jd_text)
        response = self._make_api_call(prompt, max_tokens=800)
        
        try:
            import json
            suggestions_data = json.loads(response)
            return {
                'ai_suggestions': suggestions_data.get('suggestions', []),
                'improvement_score': suggestions_data.get('improvement_potential', 0),
                'priority_areas': suggestions_data.get('priority_areas', [])
            }
        except:
            return {
                'ai_suggestions': [response],
                'improvement_score': 75,
                'priority_areas': ['General Improvements']
            }
    
    def improve_resume_bullets(self, resume_text: str, jd_text: str) -> str:
        """Generate improved resume bullet points"""
        prompt = self.prompts.get_bullet_improvement_prompt(resume_text, jd_text)
        return self._make_api_call(prompt, max_tokens=1200, temperature=0.6)
    
    def generate_cover_letter(self, resume_text: str, jd_text: str, template: str = "professional") -> str:
        """Generate cover letter with specified template"""
        prompt = self.prompts.get_cover_letter_prompt(resume_text, jd_text, template)
        return self._make_api_call(prompt, max_tokens=1000, temperature=0.7)
    
    def generate_interview_questions(self, jd_text: str, difficulty: str = "intermediate") -> str:
        """Generate interview questions based on job description"""
        prompt = self.prompts.get_interview_questions_prompt(jd_text, difficulty)
        return self._make_api_call(prompt, max_tokens=1200, temperature=0.8)
    
    def generate_star_examples(self, resume_text: str) -> str:
        """Generate STAR method examples from resume"""
        prompt = self.prompts.get_star_examples_prompt(resume_text)
        return self._make_api_call(prompt, max_tokens=1200, temperature=0.7)
    
    def analyze_job_fit(self, resume_text: str, jd_text: str) -> Dict:
        """Analyze overall job fit with detailed feedback"""
        prompt = self.prompts.get_job_fit_prompt(resume_text, jd_text)
        response = self._make_api_call(prompt, max_tokens=1000, temperature=0.6)
        
        try:
            import json
            fit_data = json.loads(response)
            return {
                'overall_fit': fit_data.get('overall_fit_score', 0),
                'strengths': fit_data.get('strengths', []),
                'gaps': fit_data.get('gaps', []),
                'recommendations': fit_data.get('recommendations', []),
                'interview_readiness': fit_data.get('interview_readiness', 0)
            }
        except:
            return {
                'overall_fit': 75,
                'analysis': response,
                'strengths': [],
                'gaps': [],
                'recommendations': []
            }
    
    def get_api_usage_info(self) -> Dict:
        """Get API usage information"""
        return {
            'model': self.model_name,
            'api_key_configured': bool(self.api_key),
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'provider': 'Google Gemini (Free)'
        }