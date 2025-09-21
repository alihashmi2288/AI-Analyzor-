"""
LLM client module for OpenAI API interactions
Handles cover letter generation, resume improvements, and interview questions
"""

import openai
import streamlit as st
from typing import Dict, List, Optional
import time
import json
from src.ai_prompts import AIPrompts

class LLMClient:
    """Handles all LLM interactions with retry logic and error handling"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.prompts = AIPrompts()
        self.model = "gpt-3.5-turbo"
        self.max_retries = 3
        self.retry_delay = 1
        
        if api_key:
            self.set_api_key(api_key)
    
    def set_api_key(self, api_key: str):
        """Set OpenAI API key"""
        self.api_key = api_key
        openai.api_key = api_key
    
    def _make_api_call(self, messages: List[Dict], max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Make API call with robust retry logic and token management"""
        if not self.api_key:
            return "OpenAI API key not configured"
        
        # Token limit chunking for long contexts
        messages = self._chunk_messages(messages, max_tokens)
        
        for attempt in range(self.max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
                
            except openai.error.RateLimitError:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    st.info(f"Rate limit hit. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                return "Rate limit exceeded. Please try again later."
                
            except openai.error.InvalidRequestError as e:
                return f"Invalid request: {str(e)}"
                
            except openai.error.AuthenticationError:
                return "Invalid API key. Please check your OpenAI API key."
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return f"Error: {str(e)}"
        
        return "Failed to get response after multiple attempts"
    
    def _chunk_messages(self, messages: List[Dict], max_tokens: int) -> List[Dict]:
        """Chunk long messages to fit token limits"""
        chunked_messages = []
        
        for message in messages:
            content = message['content']
            # Rough token estimation (1 token ≈ 4 characters)
            if len(content) > max_tokens * 3:  # Conservative estimate
                # Truncate content to fit token limit
                truncated_content = content[:max_tokens * 3]
                chunked_messages.append({
                    'role': message['role'],
                    'content': truncated_content + "\n[Content truncated for token limit]"
                })
            else:
                chunked_messages.append(message)
        
        return chunked_messages
    
    def generate_suggestions(self, resume_text: str, jd_text: str) -> Dict:
        """Generate AI-powered improvement suggestions"""
        prompt = self.prompts.get_improvement_prompt(resume_text, jd_text)
        
        messages = [
            {"role": "system", "content": "You are an expert resume consultant and career advisor."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_api_call(messages, max_tokens=800)
        
        try:
            # Try to parse as JSON for structured suggestions
            suggestions_data = json.loads(response)
            return {
                'ai_suggestions': suggestions_data.get('suggestions', []),
                'improvement_score': suggestions_data.get('improvement_potential', 0),
                'priority_areas': suggestions_data.get('priority_areas', [])
            }
        except json.JSONDecodeError:
            # Fallback to plain text
            return {
                'ai_suggestions': [response],
                'improvement_score': 75,  # Default score
                'priority_areas': ['General Improvements']
            }
    
    def improve_resume_bullets(self, resume_text: str, jd_text: str) -> str:
        """Generate improved resume bullet points"""
        prompt = self.prompts.get_bullet_improvement_prompt(resume_text, jd_text)
        
        messages = [
            {"role": "system", "content": "You are an expert resume writer specializing in ATS-optimized, impactful bullet points."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, max_tokens=1200, temperature=0.6)
    
    def generate_cover_letter(self, resume_text: str, jd_text: str, template: str = "professional") -> str:
        """Generate cover letter with specified template"""
        prompt = self.prompts.get_cover_letter_prompt(resume_text, jd_text, template)
        
        messages = [
            {"role": "system", "content": "You are a professional cover letter writer with expertise in various industries."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, max_tokens=1000, temperature=0.7)
    
    def generate_interview_questions(self, jd_text: str, difficulty: str = "intermediate") -> str:
        """Generate interview questions based on job description"""
        prompt = self.prompts.get_interview_questions_prompt(jd_text, difficulty)
        
        messages = [
            {"role": "system", "content": "You are an experienced hiring manager and interview expert."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, max_tokens=1200, temperature=0.8)
    
    def generate_star_examples(self, resume_text: str) -> str:
        """Generate STAR method examples from resume"""
        prompt = self.prompts.get_star_examples_prompt(resume_text)
        
        messages = [
            {"role": "system", "content": "You are a career coach specializing in interview preparation and the STAR method."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, max_tokens=1200, temperature=0.7)
    
    def analyze_job_fit(self, resume_text: str, jd_text: str) -> Dict:
        """Analyze overall job fit with detailed feedback"""
        prompt = self.prompts.get_job_fit_prompt(resume_text, jd_text)
        
        messages = [
            {"role": "system", "content": "You are a senior recruiter and career advisor with deep industry knowledge."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_api_call(messages, max_tokens=1000, temperature=0.6)
        
        try:
            # Try to parse structured response
            fit_data = json.loads(response)
            return {
                'overall_fit': fit_data.get('overall_fit_score', 0),
                'strengths': fit_data.get('strengths', []),
                'gaps': fit_data.get('gaps', []),
                'recommendations': fit_data.get('recommendations', []),
                'interview_readiness': fit_data.get('interview_readiness', 0)
            }
        except json.JSONDecodeError:
            return {
                'overall_fit': 75,
                'analysis': response,
                'strengths': [],
                'gaps': [],
                'recommendations': []
            }
    
    def generate_salary_negotiation_tips(self, resume_text: str, jd_text: str) -> str:
        """Generate salary negotiation tips"""
        prompt = self.prompts.get_salary_negotiation_prompt(resume_text, jd_text)
        
        messages = [
            {"role": "system", "content": "You are a career coach specializing in salary negotiation and compensation strategy."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, max_tokens=800, temperature=0.7)
    
    def optimize_for_ats(self, resume_text: str, jd_text: str) -> str:
        """Generate ATS optimization suggestions"""
        prompt = self.prompts.get_ats_optimization_prompt(resume_text, jd_text)
        
        messages = [
            {"role": "system", "content": "You are an ATS (Applicant Tracking System) expert and resume optimization specialist."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, max_tokens=1000, temperature=0.6)
    
    def generate_linkedin_summary(self, resume_text: str) -> str:
        """Generate LinkedIn summary from resume"""
        prompt = self.prompts.get_linkedin_summary_prompt(resume_text)
        
        messages = [
            {"role": "system", "content": "You are a LinkedIn optimization expert and personal branding specialist."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, max_tokens=600, temperature=0.7)
    
    def get_api_usage_info(self) -> Dict:
        """Get API usage information"""
        return {
            'model': self.model,
            'api_key_configured': bool(self.api_key),
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay
        }