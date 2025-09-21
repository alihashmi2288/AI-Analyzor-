# Configuration file for AI Resume Analyzer

# App Settings
APP_TITLE = "AI Resume Analyzer"
APP_ICON = "📄"
LAYOUT = "wide"

# File Upload Settings
MAX_FILE_SIZE = 10  # MB
SUPPORTED_RESUME_FORMATS = ["pdf", "docx"]
SUPPORTED_JD_FORMATS = ["pdf", "docx", "txt"]

# Analysis Settings
MAX_FEATURES_TFIDF = 1000
TOP_KEYWORDS_COUNT = 20
MIN_SIMILARITY_THRESHOLD = 0.1

# Skills Database - Comprehensive list of technical and soft skills
TECHNICAL_SKILLS = [
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "PHP", "Ruby", 
    "Go", "Rust", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Shell",
    
    # Web Technologies
    "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express.js",
    "Django", "Flask", "FastAPI", "Spring Boot", "Laravel", "Ruby on Rails",
    "ASP.NET", "jQuery", "Bootstrap", "Tailwind CSS", "Sass", "Less",
    
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", "SQL Server",
    "Cassandra", "DynamoDB", "Neo4j", "Elasticsearch", "Firebase",
    
    # Cloud & DevOps
    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "GitLab CI",
    "GitHub Actions", "Terraform", "Ansible", "Chef", "Puppet", "Vagrant",
    
    # Data Science & ML
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn",
    "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly", "Jupyter", "Apache Spark",
    "Hadoop", "Kafka", "Airflow", "MLflow", "Kubeflow",
    
    # Mobile Development
    "React Native", "Flutter", "iOS", "Android", "Xamarin", "Ionic",
    
    # Tools & Technologies
    "Git", "SVN", "Jira", "Confluence", "Slack", "Trello", "Asana", "Notion",
    "Postman", "Swagger", "REST API", "GraphQL", "Microservices", "Serverless",
]

SOFT_SKILLS = [
    # Leadership & Management
    "Leadership", "Team Management", "Project Management", "People Management",
    "Strategic Planning", "Decision Making", "Delegation", "Mentoring",
    
    # Communication
    "Communication", "Public Speaking", "Presentation", "Writing", "Negotiation",
    "Active Listening", "Interpersonal Skills", "Cross-cultural Communication",
    
    # Problem Solving
    "Problem Solving", "Critical Thinking", "Analytical Thinking", "Creative Thinking",
    "Innovation", "Research", "Troubleshooting", "Root Cause Analysis",
    
    # Collaboration
    "Teamwork", "Collaboration", "Cross-functional Collaboration", "Stakeholder Management",
    "Customer Service", "Client Relations", "Vendor Management",
    
    # Adaptability
    "Adaptability", "Flexibility", "Change Management", "Learning Agility",
    "Resilience", "Stress Management", "Multitasking", "Prioritization",
    
    # Work Ethics
    "Time Management", "Organization", "Attention to Detail", "Quality Assurance",
    "Reliability", "Accountability", "Initiative", "Self-motivation",
]

# Combine all skills
ALL_SKILLS = TECHNICAL_SKILLS + SOFT_SKILLS

# Industry-specific keywords
INDUSTRY_KEYWORDS = {
    "Software Development": [
        "Agile", "Scrum", "Kanban", "CI/CD", "Test-Driven Development", "Code Review",
        "Version Control", "API Development", "Database Design", "System Architecture"
    ],
    "Data Science": [
        "Statistical Analysis", "Data Visualization", "Feature Engineering", "Model Deployment",
        "A/B Testing", "Hypothesis Testing", "Data Mining", "Predictive Modeling"
    ],
    "DevOps": [
        "Infrastructure as Code", "Monitoring", "Logging", "Security", "Automation",
        "Container Orchestration", "Load Balancing", "Disaster Recovery"
    ],
    "Product Management": [
        "Product Strategy", "Roadmap Planning", "User Research", "Market Analysis",
        "Competitive Analysis", "Stakeholder Management", "Metrics & KPIs"
    ]
}

# OpenAI Settings
OPENAI_MODEL = "gpt-3.5-turbo"
MAX_TOKENS_COVER_LETTER = 500
COVER_LETTER_TEMPERATURE = 0.7

# Visualization Settings
CHART_COLOR_SCHEME = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e", 
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff7f0e",
    "info": "#17a2b8"
}

# PDF Report Settings
PDF_FONT = "Arial"
PDF_FONT_SIZE = 12
PDF_TITLE_SIZE = 16

# Scoring Thresholds
SCORE_THRESHOLDS = {
    "excellent": 80,
    "good": 60,
    "fair": 40,
    "poor": 20
}

# UI Messages
UI_MESSAGES = {
    "upload_success": "✅ File uploaded successfully!",
    "analysis_complete": "📊 Analysis completed successfully!",
    "no_api_key": "Please provide OpenAI API key to generate cover letter",
    "missing_files": "⚠️ Please upload both resume and job description to proceed",
    "processing": "🔄 Processing your request...",
    "error": "❌ An error occurred. Please try again."
}