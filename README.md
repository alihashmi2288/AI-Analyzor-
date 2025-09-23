# 🎯 AI Resume Analyzer Pro - Professional Resume Analysis Platform

**Created by Syed Ali Hashmi** 🚀

A comprehensive, enterprise-grade AI-powered resume analyzer that helps job seekers optimize their resumes, generate tailored cover letters, and prepare for interviews with advanced analytics and machine learning. Now featuring **FREE Google Gemini AI integration** for unlimited content generation.

## 🌟 Project Overview

This professional Streamlit web application provides:
- **Advanced Resume Parsing** (PDF/DOCX) with intelligent text extraction
- **Semantic Job Matching** using TF-IDF and sentence transformers
- **ATS Score Simulation** with actionable improvement suggestions
- **FREE AI-Powered Content Generation** using Google Gemini API
- **User Authentication** with secure login/signup and session history
- **Professional Analytics** with interactive dashboards and visualizations
- **Multi-Format Export** (PDF/DOCX) with branded reports
- **Streamlit Cloud Deployment** ready with optimized performance

## 🏗️ Architecture

```
Users (Browser)
    ↓
Streamlit Frontend
    ↓
Backend Modules:
├── File Parsing (pdfplumber/docx2txt)
├── NLP Processing (spaCy/sentence-transformers)
├── LLM Integration (OpenAI GPT)
├── Database (SQLite/PostgreSQL)
├── Export Engine (reportlab/python-docx)
└── Authentication (JWT/Session)
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit (>=1.24)
- **NLP**: spaCy, sentence-transformers, scikit-learn
- **AI/ML**: Google Gemini API (FREE), TensorFlow (optional)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Export**: ReportLab, python-docx
- **Deployment**: Docker, GitHub Actions, Streamlit Cloud
- **Authentication**: JWT, bcrypt

## 📁 Project Structure

```
ai-resume-analyzer/
├── app.py                      # Streamlit entrypoint
├── requirements.txt
├── Dockerfile
├── README.md
├── src/
│   ├── parsers.py             # PDF/DOCX extractors
│   ├── nlp.py                 # spaCy, skill extraction, TF-IDF
│   ├── embeddings.py          # sentence-transformers wrapper
│   ├── ai_prompts.py          # LLM prompts library
│   ├── llm_client.py          # OpenAI API client
│   ├── export.py              # PDF/DOCX report generator
│   ├── auth.py                # Authentication system
│   ├── storage.py             # Database models & operations
│   └── ui_components.py       # Reusable Streamlit components
├── tests/
│   ├── test_parsers.py
│   ├── test_nlp.py
│   └── ...
├── sample_data/
│   ├── sample_resume.txt
│   └── sample_jd.txt
└── .github/workflows/ci.yml
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/syedali/ai-resume-analyzer.git
cd ai-resume-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Add OpenAI API key, database URL, etc.
```

### 2. Run Application

```bash
# Run the main application (basic features)
streamlit run streamlit_app.py

# Or run with FREE AI features (recommended)
streamlit run phase3_gemini_app.py

# Quick start with batch file
.\run_app.bat
```

## 🎯 Core Features

### 📄 Advanced Resume Analysis
- **Multi-format Support**: PDF, DOCX parsing with intelligent text extraction
- **TF-IDF Similarity Matching**: Precise job-resume alignment scoring
- **ATS Compatibility Scoring**: Simulates applicant tracking systems
- **Interactive Visualizations**: Plotly charts and progress indicators
- **Real-time Analysis**: Instant feedback and recommendations

### 🆓 FREE AI-Powered Features (Built-in Gemini)
- **Resume Rewriting**: Complete optimization for specific jobs
- **Cover Letter Generation**: 4 professional templates (Formal, Modern, Creative, Short)
- **Interview Question Prep**: Personalized questions with answer frameworks
- **No Setup Required**: Built-in API key - works immediately
- **Unlimited Usage**: No costs or rate limits
- **High-Quality Output**: Professional-grade AI content generation

### 🔐 User Management & Security
- **Secure Authentication**: Username/email/password system with SHA-256 hashing
- **Session History**: Persistent storage of all analyses
- **User Dashboard**: Personal analytics and progress tracking
- **Data Privacy**: Secure user data isolation and protection
- **SQLite Database**: Local storage with easy PostgreSQL migration

### 📈 Professional Analytics & Export
- **Interactive Dashboards**: Real-time score visualization with Plotly
- **Gauge Visualizations**: Professional match score displays
- **Branded Reports**: PDF export with custom styling
- **Analysis History**: Track progress over multiple sessions
- **Creator Attribution**: "Created by Syed Ali Hashmi" branding

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Core Settings
GEMINI_API_KEY=your_free_gemini_key_here
DATABASE_URL=sqlite:///resumeai.db
SECRET_KEY=your_secret_key

# Feature Flags
ENABLE_SEMANTIC_ANALYSIS=true
ENABLE_ATS_SCORING=true
ENABLE_AI_SUGGESTIONS=true

# Performance
CACHE_TIMEOUT=300
MAX_FILE_SIZE_MB=10
```

### Database Setup
```bash
# SQLite (Development)
# Automatic setup on first run

# PostgreSQL (Production)
psql -c "CREATE DATABASE resume_analyzer;"
python -c "from src.storage import StorageManager; StorageManager().init_database()"
```

## 🚀 Application Versions

### 🎯 Basic Version (`streamlit_app.py`)
- **Core Features**: Resume analysis, ATS scoring, user authentication
- **No AI Dependencies**: Works without external APIs
- **Streamlit Cloud Ready**: Optimized for deployment
- **Professional UI**: Branded interface with creator attribution

### 🆓 AI-Powered Version (`phase3_gemini_app.py`) - **RECOMMENDED**
- **Built-in Gemini AI**: No setup required - works immediately
- **Complete SaaS Features**: Full user management and analysis history
- **Advanced Content Generation**: Resume rewriting, cover letters, interview prep
- **4 Cover Letter Templates**: Formal, Modern, Creative, Short styles
- **Zero Configuration**: API key built-in, secrets file included

## 🚀 Deployment

### Streamlit Cloud (Live)
**Current deployment:** https://resume-analyzer-ali.streamlit.app/

1. Fork the repository
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy `streamlit_app.py`
4. Add Gemini API key in app settings (optional)

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_nlp.py -v
```

## 📈 Performance Optimization

- **Caching**: Streamlit cache for expensive operations
- **Lazy Loading**: Models loaded on demand
- **Batch Processing**: Multiple resumes efficiently
- **Database Indexing**: Optimized queries
- **CDN Integration**: Static asset delivery

## 🔒 Security Features

- **User Authentication**: Secure login/signup
- **Data Encryption**: Sensitive data protection
- **Rate Limiting**: API abuse prevention
- **Input Validation**: XSS/injection protection
- **HTTPS Enforcement**: Secure communication

## 📊 Analytics & Monitoring

- **User Analytics**: Usage patterns and metrics
- **Performance Monitoring**: Response times and errors
- **A/B Testing**: Feature effectiveness
- **Health Checks**: System status monitoring

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Use type hints
- Add docstrings

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit Team** - Amazing framework
- **Google AI** - FREE Gemini API access
- **spaCy Team** - NLP capabilities
- **Hugging Face** - Transformer models
- **Open Source Community** - Various libraries

## 📞 Support & Contact

- **Creator**: Syed Ali Hashmi 🚀
- **Live Demo**: [AI Resume Analyzer Pro](https://resume-analyzer-ali.streamlit.app/)
- **Repository**: [GitHub](https://github.com/syedali/ai-resume-analyzer)
- **Built-in AI**: No setup required - works immediately
- **Issues**: Report bugs and request features via GitHub Issues

---

**🎯 Built for the modern job market - Empowering careers with FREE AI**

**Created by Syed Ali Hashmi** 🚀

[![Deploy to Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/cloud)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini%20AI-blue?style=for-the-badge&logo=google)](https://makersuite.google.com/app/apikey)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🆓 Live Demo

**Try the app now:** [AI Resume Analyzer Pro](https://resume-analyzer-ali.streamlit.app/)

- ✅ **No setup required** - Built-in AI features
- ✅ **FREE Gemini AI** - Unlimited content generation
- ✅ **Professional analysis** - TF-IDF matching & ATS scoring
- ✅ **Instant results** - Real-time recommendations
- ✅ **Complete SaaS** - User authentication & history