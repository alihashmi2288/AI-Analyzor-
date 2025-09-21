"""
Semantic analysis module combining TF-IDF and sentence transformers
Optimized for performance with caching and batch processing
"""

import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import hashlib
import pickle
import os
from typing import Dict, List, Tuple

class SemanticAnalyzer:
    """Combined TF-IDF and semantic similarity analyzer"""
    
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        self.model_name = model_name
        self.model = None
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)
        )
        self.cache_dir = "semantic_cache"
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    @st.cache_resource
    def load_model(_self):
        """Load sentence transformer model with caching"""
        try:
            _self.model = SentenceTransformer(_self.model_name)
            return True
        except Exception as e:
            st.warning(f"Could not load semantic model: {str(e)}")
            return False
    
    def tfidf_similarity(self, doc1: str, doc2: str) -> float:
        """Calculate TF-IDF cosine similarity"""
        try:
            if not doc1 or not doc2:
                return 0.0
            
            vectors = self.tfidf_vectorizer.fit_transform([doc1, doc2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except Exception:
            return 0.0
    
    def semantic_similarity(self, doc1: str, doc2: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        if not self.model and not self.load_model():
            return 0.0
        
        try:
            # Get cached embeddings or compute new ones
            emb1 = self._get_cached_embedding(doc1)
            emb2 = self._get_cached_embedding(doc2)
            
            # Calculate cosine similarity
            cos_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return float(cos_sim)
        except Exception as e:
            st.error(f"Error computing semantic similarity: {str(e)}")
            return 0.0
    
    def _get_cached_embedding(self, text: str) -> np.ndarray:
        """Get embedding with caching"""
        # Create cache key from text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"emb_{text_hash}.pkl")
        
        # Try to load from cache
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                pass  # Cache corrupted, recompute
        
        # Compute new embedding
        embedding = self.model.encode([text])[0]
        
        # Save to cache
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
        except:
            pass  # Caching failed, continue without caching
        
        return embedding
    
    def combined_similarity(self, doc1: str, doc2: str, weights: Dict[str, float] = None) -> Dict[str, float]:
        """Calculate combined similarity score"""
        if weights is None:
            weights = {'tfidf': 0.4, 'semantic': 0.6}
        
        tfidf_score = self.tfidf_similarity(doc1, doc2)
        semantic_score = self.semantic_similarity(doc1, doc2)
        
        combined_score = (
            weights['tfidf'] * tfidf_score + 
            weights['semantic'] * semantic_score
        )
        
        return {
            'tfidf_score': round(tfidf_score * 100, 2),
            'semantic_score': round(semantic_score * 100, 2),
            'combined_score': round(combined_score * 100, 2)
        }
    
    def analyze_sections(self, resume_text: str, jd_text: str) -> Dict:
        """Analyze similarity by resume sections"""
        sections = self._extract_sections(resume_text)
        section_scores = {}
        
        for section_name, section_text in sections.items():
            if section_text.strip():
                score = self.combined_similarity(section_text, jd_text)
                section_scores[section_name] = score['combined_score']
        
        return section_scores
    
    def _extract_sections(self, resume_text: str) -> Dict[str, str]:
        """Extract resume sections using keyword matching"""
        sections = {
            'summary': '',
            'experience': '',
            'skills': '',
            'education': '',
            'projects': ''
        }
        
        lines = resume_text.split('\n')
        current_section = 'summary'
        
        section_keywords = {
            'experience': ['experience', 'work history', 'employment', 'professional experience'],
            'skills': ['skills', 'technical skills', 'competencies', 'technologies'],
            'education': ['education', 'academic', 'degree', 'university', 'college'],
            'projects': ['projects', 'portfolio', 'achievements', 'accomplishments']
        }
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if line is a section header
            section_found = False
            for section, keywords in section_keywords.items():
                if any(keyword in line_lower for keyword in keywords):
                    current_section = section
                    section_found = True
                    break
            
            if not section_found and line.strip():
                sections[current_section] += line + '\n'
        
        return sections
    
    def get_top_matching_sentences(self, resume_text: str, jd_text: str, top_n: int = 5) -> List[Dict]:
        """Find top matching sentences between resume and JD"""
        if not self.model and not self.load_model():
            return []
        
        try:
            resume_sentences = [s.strip() for s in resume_text.split('.') if len(s.strip()) > 20]
            jd_sentences = [s.strip() for s in jd_text.split('.') if len(s.strip()) > 20]
            
            matches = []
            
            for r_sent in resume_sentences[:20]:  # Limit for performance
                for j_sent in jd_sentences[:20]:
                    similarity = self.semantic_similarity(r_sent, j_sent)
                    if similarity > 0.3:  # Threshold for meaningful similarity
                        matches.append({
                            'resume_sentence': r_sent[:100] + "..." if len(r_sent) > 100 else r_sent,
                            'jd_sentence': j_sent[:100] + "..." if len(j_sent) > 100 else j_sent,
                            'similarity': round(similarity, 3)
                        })
            
            # Sort by similarity and return top matches
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            return matches[:top_n]
            
        except Exception as e:
            st.error(f"Error finding matching sentences: {str(e)}")
            return []
    
    def cleanup_cache(self, max_files: int = 1000):
        """Clean up old cache files"""
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]
            if len(cache_files) > max_files:
                # Remove oldest files
                cache_files.sort(key=lambda x: os.path.getctime(os.path.join(self.cache_dir, x)))
                for file in cache_files[:-max_files]:
                    os.remove(os.path.join(self.cache_dir, file))
        except Exception:
            pass  # Cleanup failed, continue