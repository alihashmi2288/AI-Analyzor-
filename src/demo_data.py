"""
Demo data module for quick testing and portfolio demonstrations
Provides sample resume and job description data
"""

SAMPLE_RESUME = """
SARAH JOHNSON
Senior Software Engineer
Email: sarah.johnson@email.com | Phone: (555) 123-4567
LinkedIn: linkedin.com/in/sarahjohnson | GitHub: github.com/sarahjohnson

PROFESSIONAL SUMMARY
Results-driven Senior Software Engineer with 7+ years of experience in full-stack development, cloud architecture, and team leadership. Proven track record of delivering scalable applications serving 1M+ users and reducing system costs by 40%. Expert in Python, React, and AWS with strong background in machine learning and data engineering.

TECHNICAL SKILLS
• Programming: Python, JavaScript, TypeScript, Java, SQL, Go
• Frontend: React, Vue.js, HTML5, CSS3, Redux, Next.js
• Backend: Django, Flask, Node.js, Express.js, FastAPI
• Databases: PostgreSQL, MongoDB, Redis, Elasticsearch
• Cloud: AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes
• ML/Data: TensorFlow, PyTorch, Pandas, NumPy, Apache Spark
• Tools: Git, Jenkins, Jira, Terraform, Grafana

PROFESSIONAL EXPERIENCE

Lead Software Engineer | TechCorp Solutions | 2021 - Present
• Led cross-functional team of 8 engineers to deliver microservices platform serving 2M+ daily requests
• Architected and implemented CI/CD pipeline reducing deployment time from 2 hours to 15 minutes
• Optimized database queries and caching strategies, improving application response time by 60%
• Mentored 5 junior developers and established code review processes increasing team productivity by 35%
• Collaborated with product managers to define technical roadmap and delivered 12 major features on schedule

Senior Software Engineer | DataFlow Inc | 2019 - 2021
• Developed real-time data processing pipeline handling 500GB+ daily using Apache Kafka and Spark
• Built machine learning recommendation system increasing user engagement by 25%
• Implemented automated testing framework achieving 90% code coverage across 15 microservices
• Reduced infrastructure costs by $200K annually through cloud optimization and resource management
• Participated in on-call rotation maintaining 99.9% system uptime

Software Engineer | StartupXYZ | 2017 - 2019
• Created responsive web applications using React and Python/Django serving 100K+ users
• Integrated payment processing systems (Stripe, PayPal) handling $2M+ in transactions
• Developed RESTful APIs and GraphQL endpoints consumed by mobile and web clients
• Implemented OAuth2 authentication and role-based access control for enterprise customers
• Collaborated in agile environment delivering bi-weekly releases with zero critical bugs

EDUCATION
Master of Science in Computer Science | Stanford University | 2017
Bachelor of Science in Software Engineering | UC Berkeley | 2015

CERTIFICATIONS
• AWS Certified Solutions Architect - Professional (2023)
• Certified Kubernetes Administrator (2022)
• Google Cloud Professional Data Engineer (2021)

PROJECTS
E-Commerce Analytics Platform
• Built end-to-end analytics platform using React, Python, and AWS processing 10M+ events daily
• Implemented real-time dashboards with 99.5% accuracy in sales forecasting
• Reduced customer acquisition cost by 30% through predictive modeling

Open Source Contributions
• Contributor to TensorFlow and Apache Spark projects with 50+ merged pull requests
• Maintained Python library with 1000+ GitHub stars and 50K+ monthly downloads
• Speaker at 3 tech conferences on machine learning and cloud architecture

ACHIEVEMENTS
• Promoted to Lead Engineer within 18 months based on exceptional performance
• Won "Innovation Award" for developing automated code deployment system
• Increased team velocity by 40% through process improvements and tooling
• Published 5 technical articles with 10K+ total views on engineering best practices
"""

SAMPLE_JOB_DESCRIPTION = """
Senior Full Stack Engineer
Company: InnovateTech Solutions
Location: San Francisco, CA | Remote Friendly
Salary: $140,000 - $200,000 + Equity

ABOUT THE ROLE
We're seeking an exceptional Senior Full Stack Engineer to join our rapidly growing engineering team. You'll be responsible for architecting and building scalable web applications that power our SaaS platform used by 500K+ businesses worldwide. This is a high-impact role where you'll work directly with our CTO and product team to shape the technical direction of our platform.

KEY RESPONSIBILITIES
• Design and develop full-stack applications using modern JavaScript frameworks and Python
• Build and maintain microservices architecture handling millions of API requests daily
• Collaborate with product managers, designers, and other engineers in an agile environment
• Implement automated testing, CI/CD pipelines, and monitoring solutions
• Optimize application performance, scalability, and security
• Mentor junior engineers and participate in technical decision-making
• Lead code reviews and ensure high-quality software delivery
• Stay current with emerging technologies and industry best practices

REQUIRED QUALIFICATIONS
• 5+ years of professional software development experience
• Strong proficiency in Python and modern JavaScript (React, Vue.js, or Angular)
• Experience with backend frameworks (Django, Flask, FastAPI, or Node.js)
• Solid understanding of databases (PostgreSQL, MongoDB) and caching (Redis)
• Experience with cloud platforms (AWS, GCP, or Azure) and containerization (Docker)
• Knowledge of microservices architecture and RESTful API design
• Familiarity with CI/CD tools (Jenkins, GitLab CI, or GitHub Actions)
• Experience with version control (Git) and agile development methodologies
• Strong problem-solving skills and attention to detail
• Excellent communication and collaboration abilities

PREFERRED QUALIFICATIONS
• Master's degree in Computer Science or related field
• Experience with machine learning and data engineering
• Knowledge of DevOps practices and infrastructure as code (Terraform, CloudFormation)
• Experience with message queues (Kafka, RabbitMQ) and event-driven architecture
• Familiarity with monitoring tools (Grafana, DataDog, New Relic)
• Previous experience in a leadership or mentoring role
• Contributions to open-source projects
• Experience in fast-paced startup environments

TECHNICAL STACK
• Frontend: React, TypeScript, Redux, Next.js, Tailwind CSS
• Backend: Python, Django, FastAPI, Node.js, GraphQL
• Databases: PostgreSQL, MongoDB, Redis, Elasticsearch
• Infrastructure: AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes
• Tools: Git, Jenkins, Jira, Terraform, Grafana, DataDog
• Testing: Jest, Pytest, Cypress, Selenium

WHAT WE OFFER
• Competitive salary ($140K-$200K) based on experience
• Significant equity package with high growth potential
• Comprehensive health, dental, and vision insurance
• $5,000 annual learning and development budget
• Flexible work arrangements and unlimited PTO
• Top-tier equipment and home office setup allowance
• Stock options and 401(k) with company matching
• Team retreats and professional conference attendance
• Opportunity to work with cutting-edge technologies

COMPANY CULTURE
InnovateTech Solutions is committed to building a diverse and inclusive team. We value innovation, continuous learning, and work-life balance. Our engineering team follows best practices including code reviews, automated testing, and regular retrospectives. We believe in giving engineers autonomy while providing the support needed to succeed.

INTERVIEW PROCESS
1. Initial phone screening (30 minutes)
2. Technical assessment and coding challenge
3. Virtual technical interviews with team members (2-3 rounds)
4. Final interview with engineering leadership
5. Reference checks and offer

We are an equal opportunity employer committed to diversity and inclusion. All qualified applicants will receive consideration regardless of race, color, religion, sex, sexual orientation, gender identity, national origin, disability, or veteran status.

TO APPLY
Please submit your resume, cover letter, and links to your GitHub profile or portfolio. We review applications on a rolling basis and aim to respond within one week.
"""

def get_sample_data():
    """Get sample resume and job description for demo purposes"""
    return {
        'resume': SAMPLE_RESUME,
        'job_description': SAMPLE_JOB_DESCRIPTION,
        'job_title': 'Senior Full Stack Engineer',
        'company': 'InnovateTech Solutions'
    }

def get_demo_analysis_results():
    """Get pre-computed demo analysis results for quick display"""
    return {
        'similarity_score': 87.5,
        'ats_score': 92,
        'skill_match_rate': 85.2,
        'semantic_score': 89.3,
        'improvement_score': 78,
        'matched_skills': [
            'Python', 'JavaScript', 'React', 'Django', 'PostgreSQL', 'MongoDB', 
            'Redis', 'AWS', 'Docker', 'Git', 'Machine Learning', 'FastAPI',
            'Node.js', 'TypeScript', 'Kubernetes', 'Jenkins', 'Agile'
        ],
        'missing_skills': [
            'Vue.js', 'Angular', 'GraphQL', 'Terraform', 'Grafana', 'DataDog'
        ],
        'resume_keywords': [
            ('python', 0.156), ('react', 0.142), ('aws', 0.138), ('django', 0.125),
            ('javascript', 0.118), ('machine learning', 0.112), ('postgresql', 0.098),
            ('docker', 0.089), ('kubernetes', 0.085), ('microservices', 0.082)
        ],
        'jd_keywords': [
            ('python', 0.168), ('javascript', 0.155), ('react', 0.148), ('aws', 0.142),
            ('postgresql', 0.135), ('docker', 0.128), ('microservices', 0.122),
            ('api', 0.115), ('agile', 0.108), ('ci/cd', 0.102)
        ],
        'ai_suggestions': [
            "Add GraphQL experience to match the job requirements",
            "Highlight Vue.js or Angular experience if you have any",
            "Mention specific experience with Terraform for infrastructure as code",
            "Include monitoring tools experience (Grafana, DataDog) in your skills",
            "Quantify your leadership experience with specific team sizes and outcomes"
        ],
        'ats_feedback': [
            "Excellent use of action verbs and quantifiable achievements",
            "Strong keyword alignment with job description",
            "Well-structured resume with clear sections"
        ]
    }