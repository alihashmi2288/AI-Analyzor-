"""
Performance monitoring and optimization module
Tracks API usage, caching, and system performance
"""

import time
import functools
import streamlit as st
from typing import Dict, Any, Callable
import json
import os
from datetime import datetime, timedelta

class PerformanceMonitor:
    """Monitor and optimize application performance"""
    
    def __init__(self):
        self.metrics = {
            'api_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'processing_times': [],
            'errors': []
        }
        self.cost_tracking = {
            'openai_tokens': 0,
            'estimated_cost': 0.0
        }
    
    def track_api_call(self, tokens_used: int = 0, cost: float = 0.0):
        """Track API usage and costs"""
        self.metrics['api_calls'] += 1
        self.cost_tracking['openai_tokens'] += tokens_used
        self.cost_tracking['estimated_cost'] += cost
    
    def track_cache_hit(self):
        """Track cache hit"""
        self.metrics['cache_hits'] += 1
    
    def track_cache_miss(self):
        """Track cache miss"""
        self.metrics['cache_misses'] += 1
    
    def track_processing_time(self, operation: str, duration: float):
        """Track processing time for operations"""
        self.metrics['processing_times'].append({
            'operation': operation,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
    
    def track_error(self, error_type: str, error_message: str):
        """Track errors for monitoring"""
        self.metrics['errors'].append({
            'type': error_type,
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        cache_total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = (self.metrics['cache_hits'] / cache_total * 100) if cache_total > 0 else 0
        
        avg_processing_time = 0
        if self.metrics['processing_times']:
            avg_processing_time = sum(p['duration'] for p in self.metrics['processing_times']) / len(self.metrics['processing_times'])
        
        return {
            'api_calls': self.metrics['api_calls'],
            'cache_hit_rate': round(cache_hit_rate, 1),
            'avg_processing_time': round(avg_processing_time, 2),
            'total_errors': len(self.metrics['errors']),
            'estimated_cost': round(self.cost_tracking['estimated_cost'], 4),
            'tokens_used': self.cost_tracking['openai_tokens']
        }
    
    def display_performance_dashboard(self):
        """Display performance metrics in Streamlit"""
        stats = self.get_performance_stats()
        
        st.subheader("📊 Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("API Calls", stats['api_calls'])
        with col2:
            st.metric("Cache Hit Rate", f"{stats['cache_hit_rate']}%")
        with col3:
            st.metric("Avg Processing Time", f"{stats['avg_processing_time']}s")
        with col4:
            st.metric("Estimated Cost", f"${stats['estimated_cost']}")

def performance_timer(operation_name: str):
    """Decorator to time function execution"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Track performance if monitor is available
                if hasattr(st.session_state, 'performance_monitor'):
                    st.session_state.performance_monitor.track_processing_time(operation_name, duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Track error if monitor is available
                if hasattr(st.session_state, 'performance_monitor'):
                    st.session_state.performance_monitor.track_error(type(e).__name__, str(e))
                
                raise
        return wrapper
    return decorator

class CacheManager:
    """Manage application caching for performance optimization"""
    
    def __init__(self, cache_dir: str = "app_cache"):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        import hashlib
        key_string = str(args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str, max_age_hours: int = 24):
        """Get cached result if it exists and is not expired"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                # Check if cache is expired
                file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(cache_file))
                if file_age > timedelta(hours=max_age_hours):
                    os.remove(cache_file)
                    return None
                
                # Load cached result
                with open(cache_file, 'r') as f:
                    result = json.load(f)
                
                # Track cache hit
                if hasattr(st.session_state, 'performance_monitor'):
                    st.session_state.performance_monitor.track_cache_hit()
                
                return result
                
            except Exception:
                # Cache corrupted, remove it
                try:
                    os.remove(cache_file)
                except:
                    pass
                return None
        
        # Track cache miss
        if hasattr(st.session_state, 'performance_monitor'):
            st.session_state.performance_monitor.track_cache_miss()
        
        return None
    
    def cache_result(self, cache_key: str, result: Any):
        """Cache a result"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f)
        except Exception:
            pass  # Caching failed, continue without caching
    
    def clear_cache(self):
        """Clear all cached results"""
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
        except Exception:
            pass

def cached_analysis(cache_manager: CacheManager, max_age_hours: int = 24):
    """Decorator for caching analysis results"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_key = cache_manager.get_cache_key(func.__name__, *args, *kwargs.values())
            
            # Try to get cached result
            cached_result = cache_manager.get_cached_result(cache_key, max_age_hours)
            if cached_result is not None:
                return cached_result
            
            # Compute result and cache it
            result = func(*args, **kwargs)
            cache_manager.cache_result(cache_key, result)
            
            return result
        return wrapper
    return decorator

class ResourceOptimizer:
    """Optimize resource usage and memory management"""
    
    @staticmethod
    def optimize_text_processing(text: str, max_length: int = 10000) -> str:
        """Optimize text for processing by truncating if too long"""
        if len(text) > max_length:
            return text[:max_length] + "\\n[Text truncated for processing efficiency]"
        return text
    
    @staticmethod
    def batch_process_resumes(resumes: list, batch_size: int = 5):
        """Process resumes in batches to avoid memory issues"""
        for i in range(0, len(resumes), batch_size):
            yield resumes[i:i + batch_size]
    
    @staticmethod
    def cleanup_session_state():
        """Clean up large objects from session state"""
        cleanup_keys = ['large_embeddings', 'processed_texts', 'temp_data']
        for key in cleanup_keys:
            if key in st.session_state:
                del st.session_state[key]