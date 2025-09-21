"""
Semantic embeddings module using sentence-transformers
Provides advanced semantic similarity analysis
"""

import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import pickle
import os

class EmbeddingProcessor:
    """Handles semantic embeddings and similarity calculations"""
    
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        self.model_name = model_name
        self.model = None
        self.cache_dir = "embeddings_cache"
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
            st.warning(f"Could not load embedding model: {str(e)}")
            return False
    
    def compute_similarity(self, resume_text: str, jd_text: str) -> Dict:
        """Compute semantic similarity between resume and job description"""
        if not self.model and not self.load_model():
            return {'semantic_score': 0, 'semantic_breakdown': {}}
        
        try:
            # Split texts into sentences for detailed analysis
            resume_sentences = self._split_into_sentences(resume_text)
            jd_sentences = self._split_into_sentences(jd_text)
            
            # Compute embeddings
            resume_embeddings = self._get_embeddings(resume_sentences)
            jd_embeddings = self._get_embeddings(jd_sentences)
            
            # Overall similarity
            resume_doc_embedding = np.mean(resume_embeddings, axis=0).reshape(1, -1)
            jd_doc_embedding = np.mean(jd_embeddings, axis=0).reshape(1, -1)
            
            overall_similarity = cosine_similarity(resume_doc_embedding, jd_doc_embedding)[0][0]
            
            # Detailed breakdown
            breakdown = self._analyze_semantic_breakdown(
                resume_sentences, jd_sentences,
                resume_embeddings, jd_embeddings
            )
            
            return {
                'semantic_score': round(overall_similarity * 100, 2),
                'semantic_breakdown': breakdown,
                'embedding_model': self.model_name
            }
            
        except Exception as e:
            st.error(f"Error computing semantic similarity: {str(e)}")
            return {'semantic_score': 0, 'semantic_breakdown': {}}
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return sentences
    
    @st.cache_data
    def _get_embeddings(_self, texts: List[str]) -> np.ndarray:
        """Get embeddings for list of texts with caching"""
        if not _self.model:
            return np.array([])
        
        # Create cache key
        cache_key = hash(str(texts))
        cache_file = os.path.join(_self.cache_dir, f"embeddings_{cache_key}.pkl")
        
        # Try to load from cache
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                pass  # If cache fails, compute fresh
        
        # Compute embeddings
        embeddings = _self.model.encode(texts)
        
        # Save to cache
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embeddings, f)
        except:
            pass  # If caching fails, continue without caching
        
        return embeddings
    
    def _analyze_semantic_breakdown(self, resume_sentences: List[str], jd_sentences: List[str],
                                  resume_embeddings: np.ndarray, jd_embeddings: np.ndarray) -> Dict:
        """Analyze semantic similarity breakdown"""
        breakdown = {
            'best_matches': [],
            'section_similarities': {},
            'coverage_score': 0
        }
        
        try:
            # Find best matching sentences
            similarity_matrix = cosine_similarity(resume_embeddings, jd_embeddings)
            
            # Get top matches
            best_matches = []
            for i, jd_sentence in enumerate(jd_sentences):
                best_resume_idx = np.argmax(similarity_matrix[:, i])
                best_score = similarity_matrix[best_resume_idx, i]
                
                if best_score > 0.3:  # Threshold for meaningful similarity
                    best_matches.append({
                        'jd_sentence': jd_sentence[:100] + "..." if len(jd_sentence) > 100 else jd_sentence,
                        'resume_sentence': resume_sentences[best_resume_idx][:100] + "..." if len(resume_sentences[best_resume_idx]) > 100 else resume_sentences[best_resume_idx],
                        'similarity': round(best_score, 3)
                    })
            
            # Sort by similarity and take top 5
            best_matches.sort(key=lambda x: x['similarity'], reverse=True)
            breakdown['best_matches'] = best_matches[:5]
            
            # Calculate coverage score
            high_similarity_count = np.sum(np.max(similarity_matrix, axis=0) > 0.4)
            coverage_score = (high_similarity_count / len(jd_sentences)) * 100
            breakdown['coverage_score'] = round(coverage_score, 1)
            
            # Section-based analysis (if we can identify sections)
            breakdown['section_similarities'] = self._analyze_sections(
                resume_sentences, jd_sentences, similarity_matrix
            )
            
        except Exception as e:
            st.error(f"Error in semantic breakdown: {str(e)}")
        
        return breakdown
    
    def _analyze_sections(self, resume_sentences: List[str], jd_sentences: List[str],
                         similarity_matrix: np.ndarray) -> Dict:
        """Analyze similarity by resume sections"""
        sections = {
            'experience': [],
            'skills': [],
            'education': [],
            'other': []
        }
        
        # Simple keyword-based section classification
        experience_keywords = ['worked', 'managed', 'led', 'developed', 'implemented', 'achieved']
        skills_keywords = ['proficient', 'experienced', 'skilled', 'knowledge', 'familiar']
        education_keywords = ['degree', 'university', 'college', 'graduated', 'studied']
        
        for i, sentence in enumerate(resume_sentences):
            sentence_lower = sentence.lower()
            
            if any(keyword in sentence_lower for keyword in experience_keywords):
                sections['experience'].append(i)
            elif any(keyword in sentence_lower for keyword in skills_keywords):
                sections['skills'].append(i)
            elif any(keyword in sentence_lower for keyword in education_keywords):
                sections['education'].append(i)
            else:
                sections['other'].append(i)
        
        # Calculate average similarity for each section
        section_similarities = {}
        for section, indices in sections.items():
            if indices:
                section_similarities[section] = round(
                    np.mean(similarity_matrix[indices, :]), 3
                )
        
        return section_similarities
    
    def find_similar_phrases(self, resume_text: str, jd_text: str, threshold: float = 0.7) -> List[Dict]:
        """Find similar phrases between resume and job description"""
        if not self.model and not self.load_model():
            return []
        
        try:
            # Extract phrases (simple approach - can be improved)
            resume_phrases = self._extract_phrases(resume_text)
            jd_phrases = self._extract_phrases(jd_text)
            
            # Get embeddings
            resume_embeddings = self._get_embeddings(resume_phrases)
            jd_embeddings = self._get_embeddings(jd_phrases)
            
            # Find similar phrases
            similarity_matrix = cosine_similarity(resume_embeddings, jd_embeddings)
            
            similar_phrases = []
            for i, resume_phrase in enumerate(resume_phrases):
                for j, jd_phrase in enumerate(jd_phrases):
                    similarity = similarity_matrix[i, j]
                    if similarity >= threshold:
                        similar_phrases.append({
                            'resume_phrase': resume_phrase,
                            'jd_phrase': jd_phrase,
                            'similarity': round(similarity, 3)
                        })
            
            # Sort by similarity
            similar_phrases.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_phrases[:10]  # Return top 10
            
        except Exception as e:
            st.error(f"Error finding similar phrases: {str(e)}")
            return []
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract meaningful phrases from text"""
        import re
        
        # Split by common delimiters
        phrases = re.split(r'[.!?;,\n]+', text)
        
        # Filter and clean phrases
        cleaned_phrases = []
        for phrase in phrases:
            phrase = phrase.strip()
            # Keep phrases that are meaningful (3-50 words)
            if 3 <= len(phrase.split()) <= 50:
                cleaned_phrases.append(phrase)
        
        return cleaned_phrases
    
    def get_embedding_stats(self) -> Dict:
        """Get statistics about the embedding model"""
        if not self.model:
            return {}
        
        return {
            'model_name': self.model_name,
            'max_seq_length': getattr(self.model, 'max_seq_length', 'Unknown'),
            'embedding_dimension': self.model.get_sentence_embedding_dimension(),
            'cache_dir': self.cache_dir,
            'cached_files': len([f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]) if os.path.exists(self.cache_dir) else 0
        }