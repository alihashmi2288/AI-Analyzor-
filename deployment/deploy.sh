#!/bin/bash

# Deployment script for ResumeAI Pro

echo "🚀 Deploying ResumeAI Pro..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements_phase3.txt

# Download spaCy model if needed
echo "🧠 Setting up NLP model..."
python -m spacy download en_core_web_sm

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p .streamlit
mkdir -p logs
mkdir -p uploads

# Copy configuration
echo "⚙️ Setting up configuration..."
cp deployment/streamlit_config.toml .streamlit/config.toml

# Set permissions
echo "🔐 Setting permissions..."
chmod +x phase3_app.py

# Start application
echo "🎯 Starting ResumeAI Pro..."
streamlit run phase3_app.py --server.port=8501 --server.address=0.0.0.0

echo "✅ Deployment complete!"
echo "🌐 Access your app at: http://localhost:8501"