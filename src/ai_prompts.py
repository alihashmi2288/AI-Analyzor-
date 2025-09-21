"""
AI prompts module containing all LLM prompts for different functionalities
Centralized prompt management for consistency and easy updates
"""

class AIPrompts:
    """Centralized prompt management for all AI interactions"""
    
    def get_improvement_prompt(self, resume_text: str, jd_text: str) -> str:
        """Prompt for general resume improvement suggestions"""
        return f"""
Analyze the following resume against the job description and provide structured improvement suggestions.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{jd_text[:2000]}

Please provide your analysis in the following JSON format:
{{
    "improvement_potential": <score 0-100>,
    "suggestions": [
        "Specific actionable suggestion 1",
        "Specific actionable suggestion 2",
        "..."
    ],
    "priority_areas": [
        "Area that needs most attention",
        "Second priority area",
        "..."
    ]
}}

Focus on:
1. Skills alignment
2. Keyword optimization
3. Quantifiable achievements
4. ATS compatibility
5. Industry-specific improvements
        """
    
    def get_bullet_improvement_prompt(self, resume_text: str, jd_text: str) -> str:
        """Prompt for improving resume bullet points"""
        return f"""
        Rewrite the resume bullet points to be more impactful, ATS-friendly, and aligned with the job requirements.
        
        CURRENT RESUME:
        {resume_text[:3000]}
        
        TARGET JOB:
        {jd_text[:2000]}
        
        Please rewrite the experience bullet points following these guidelines:
        1. Start with strong action verbs
        2. Include quantifiable results where possible
        3. Use keywords from the job description
        4. Follow the format: Action + Context + Result
        5. Keep each bullet to 1-2 lines
        6. Make them ATS-friendly
        
        Provide the improved bullet points organized by job/role, maintaining the original structure but with enhanced content.
        """
    
    def get_cover_letter_prompt(self, resume_text: str, jd_text: str, template: str) -> str:
        """Prompt for generating cover letters"""
        template_styles = {
            "professional": "formal, traditional business style",
            "creative": "engaging, personality-driven while remaining professional",
            "technical": "focused on technical skills and achievements"
        }
        
        style = template_styles.get(template, "professional")
        
        return f"""
        Write a compelling cover letter based on the resume and job description provided.
        
        RESUME SUMMARY:
        {resume_text[:2500]}
        
        JOB DESCRIPTION:
        {jd_text[:1500]}
        
        Style: {style}
        
        Structure the cover letter with:
        1. Strong opening paragraph that grabs attention
        2. 2-3 body paragraphs highlighting relevant experience and skills
        3. Closing paragraph with call to action
        
        Requirements:
        - Keep it to 3-4 paragraphs
        - Highlight specific achievements from the resume
        - Address key requirements from the job description
        - Show enthusiasm for the role and company
        - Include specific examples and metrics where possible
        - Make it personalized and avoid generic language
        
        Do not include placeholder text like [Company Name] - write it as if for a specific application.
        """
    
    def get_interview_questions_prompt(self, jd_text: str, difficulty: str) -> str:
        """Prompt for generating interview questions"""
        return f"""
        Generate interview questions based on the following job description.
        
        JOB DESCRIPTION:
        {jd_text[:2000]}
        
        Difficulty Level: {difficulty}
        
        Please provide:
        1. 5 behavioral questions (STAR method applicable)
        2. 5 technical/role-specific questions
        3. 3 situational questions
        4. 2 company/culture fit questions
        
        For each question, also provide:
        - What the interviewer is looking for
        - Key points to address in the answer
        
        Adjust the complexity based on the difficulty level:
        - Beginner: Entry-level, basic concepts
        - Intermediate: Mid-level, practical experience
        - Advanced: Senior-level, strategic thinking
        
        Format as a structured list with clear categories.
        """
    
    def get_star_examples_prompt(self, resume_text: str) -> str:
        """Prompt for generating STAR method examples"""
        return f"""
        Based on the following resume, create STAR method examples for common interview questions.
        
        RESUME:
        {resume_text[:3000]}
        
        Generate 5 STAR examples covering different aspects:
        1. Leadership/Management
        2. Problem-solving
        3. Teamwork/Collaboration
        4. Achievement/Success
        5. Challenge/Failure and learning
        
        For each example, provide:
        - Situation: Context and background
        - Task: What needed to be accomplished
        - Action: Specific steps taken
        - Result: Quantifiable outcome and impact
        
        Make the examples specific, credible, and impressive while staying true to the resume content.
        Include metrics and specific details where possible.
        """
    
    def get_job_fit_prompt(self, resume_text: str, jd_text: str) -> str:
        """Prompt for analyzing job fit"""
        return f"""
        Analyze how well this candidate fits the job requirements and provide detailed feedback.
        
        CANDIDATE RESUME:
        {resume_text[:3000]}
        
        JOB REQUIREMENTS:
        {jd_text[:2000]}
        
        Provide analysis in JSON format:
        {{
            "overall_fit_score": <0-100>,
            "strengths": [
                "Key strength 1",
                "Key strength 2",
                "..."
            ],
            "gaps": [
                "Missing requirement 1",
                "Skill gap 2",
                "..."
            ],
            "recommendations": [
                "How to address gap 1",
                "Skill development suggestion 2",
                "..."
            ],
            "interview_readiness": <0-100>
        }}
        
        Consider:
        1. Technical skills match
        2. Experience level alignment
        3. Industry background
        4. Soft skills fit
        5. Career progression logic
        6. Cultural fit indicators
        """
    
    def get_salary_negotiation_prompt(self, resume_text: str, jd_text: str) -> str:
        """Prompt for salary negotiation tips"""
        return f"""
        Provide salary negotiation advice based on the candidate's background and target role.
        
        CANDIDATE BACKGROUND:
        {resume_text[:2500]}
        
        TARGET ROLE:
        {jd_text[:1500]}
        
        Provide advice on:
        1. Market research approach
        2. Value proposition points to highlight
        3. Negotiation timing and strategy
        4. Non-salary benefits to consider
        5. How to present the case professionally
        
        Include:
        - Specific achievements to emphasize
        - Industry benchmarks to research
        - Negotiation scripts/phrases
        - Common mistakes to avoid
        - Alternative compensation options
        
        Make it actionable and specific to this candidate's situation.
        """
    
    def get_ats_optimization_prompt(self, resume_text: str, jd_text: str) -> str:
        """Prompt for ATS optimization suggestions"""
        return f"""
        Analyze this resume for ATS (Applicant Tracking System) optimization against the job description.
        
        RESUME:
        {resume_text[:3000]}
        
        JOB DESCRIPTION:
        {jd_text[:2000]}
        
        Provide specific ATS optimization recommendations:
        
        1. KEYWORD OPTIMIZATION:
        - Missing keywords from job description
        - Keyword density improvements
        - Synonym suggestions
        
        2. FORMATTING ISSUES:
        - Section headers optimization
        - Bullet point structure
        - Date formatting
        - Contact information placement
        
        3. CONTENT STRUCTURE:
        - Skills section optimization
        - Experience descriptions
        - Education formatting
        - Certifications placement
        
        4. ATS-FRIENDLY IMPROVEMENTS:
        - File format recommendations
        - Font and styling suggestions
        - Section ordering
        - Length optimization
        
        Provide specific, actionable recommendations with examples.
        """
    
    def get_linkedin_summary_prompt(self, resume_text: str) -> str:
        """Prompt for LinkedIn summary generation"""
        return f"""
        Create a compelling LinkedIn summary based on this resume.
        
        RESUME:
        {resume_text[:3000]}
        
        Write a LinkedIn summary that:
        1. Starts with a strong hook
        2. Highlights key achievements and skills
        3. Shows personality and professional brand
        4. Includes relevant keywords for searchability
        5. Ends with a call to action
        
        Requirements:
        - 2-3 paragraphs, around 200-300 words
        - First person perspective
        - Professional yet personable tone
        - Industry-specific keywords
        - Quantifiable achievements
        - Future-focused closing
        
        Make it engaging and authentic while maintaining professionalism.
        """
    
    def get_skills_gap_analysis_prompt(self, resume_text: str, jd_text: str) -> str:
        """Prompt for detailed skills gap analysis"""
        return f"""
        Perform a detailed skills gap analysis between the candidate and job requirements.
        
        CANDIDATE SKILLS (from resume):
        {resume_text[:2500]}
        
        JOB REQUIREMENTS:
        {jd_text[:2000]}
        
        Analyze and categorize skills into:
        
        1. STRONG MATCHES (candidate exceeds requirements)
        2. GOOD MATCHES (candidate meets requirements)
        3. PARTIAL MATCHES (candidate has related experience)
        4. SKILL GAPS (missing requirements)
        
        For each category, provide:
        - Specific skills/technologies
        - Evidence from resume (for matches)
        - Importance level (critical/important/nice-to-have)
        - Development recommendations (for gaps)
        
        Include learning resources and timeline estimates for addressing gaps.
        """