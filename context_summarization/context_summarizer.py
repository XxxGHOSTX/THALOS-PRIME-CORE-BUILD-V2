"""
Context Summarizer
Condenses long conversation history and context into key points
"""

import numpy as np
from datetime import datetime as dt
import hashlib as hl


class ContextSummarizer:
    """Summarizes context and conversation history"""
    
    def __init__(self, max_context_tokens=2048):
        self.max_context_tokens = max_context_tokens
        self.summary_cache = {}
        self.summary_history = []
        
    def _estimate_tokens(self, text):
        """Rough token estimation (4 chars ≈ 1 token)"""
        return len(text) // 4
    
    def _extract_key_phrases(self, text):
        """Extract important phrases from text"""
        # Simple keyword extraction
        words = text.lower().split()
        
        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                    'would', 'should', 'could', 'may', 'might', 'can', 'i', 'you', 'he',
                    'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those'}
        
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Count frequency
        freq = {}
        for word in keywords:
            freq[word] = freq.get(word, 0) + 1
            
        # Get top keywords
        top_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return [word for word, count in top_keywords]
    
    def _score_importance(self, exchange):
        """Score importance of an exchange"""
        score = 0.5  # Base score
        
        # Certainty boost
        if 'certainty' in exchange:
            score += exchange['certainty'] * 0.3
            
        # Length penalty (very long exchanges may be less important)
        if 'query' in exchange:
            query_len = len(exchange['query'])
            if query_len < 50:
                score += 0.1
            elif query_len > 500:
                score -= 0.1
                
        # Question boost
        if 'query' in exchange and '?' in exchange['query']:
            score += 0.15
            
        # Directive boost
        directive_words = ['show', 'display', 'compute', 'analyze', 'explain']
        if 'query' in exchange and any(w in exchange['query'].lower() for w in directive_words):
            score += 0.1
            
        return min(1.0, max(0.0, score))
    
    def summarize_exchanges(self, exchanges, max_summary_length=500):
        """Summarize multiple exchanges"""
        if not exchanges:
            return {"summary": "", "key_points": [], "token_count": 0}
            
        # Check cache
        cache_key = hl.md5(str([e.get('id', i) for i, e in enumerate(exchanges)]).encode()).hexdigest()
        if cache_key in self.summary_cache:
            return self.summary_cache[cache_key]
            
        # Score and sort exchanges by importance
        scored = [(self._score_importance(ex), ex) for ex in exchanges]
        scored.sort(reverse=True)
        
        # Build summary
        summary_parts = []
        key_points = []
        total_chars = 0
        
        for score, exchange in scored:
            if total_chars >= max_summary_length:
                break
                
            query = exchange.get('query', '')
            response = exchange.get('response', {})
            
            if isinstance(response, dict):
                answer = response.get('answer', '')
            else:
                answer = str(response)
                
            # Extract key point
            if query:
                key_phrases = self._extract_key_phrases(query)
                if key_phrases:
                    key_point = f"Query about: {', '.join(key_phrases[:3])}"
                    key_points.append(key_point)
                    
            # Add to summary
            if query and len(summary_parts) < 5:
                summary_line = f"- {query[:100]}"
                if len(query) > 100:
                    summary_line += "..."
                summary_parts.append(summary_line)
                total_chars += len(summary_line)
                
        summary_text = "\n".join(summary_parts)
        
        result = {
            "summary": summary_text,
            "key_points": key_points[:10],
            "token_count": self._estimate_tokens(summary_text),
            "exchanges_summarized": len(exchanges),
            "timestamp": dt.now().isoformat()
        }
        
        # Cache result
        self.summary_cache[cache_key] = result
        
        # Log
        self.summary_history.append({
            'timestamp': dt.now().isoformat(),
            'exchanges': len(exchanges),
            'summary_length': len(summary_text)
        })
        
        if len(self.summary_history) > 100:
            self.summary_history = self.summary_history[-100:]
            
        return result
    
    def summarize_context(self, context_dict):
        """Summarize arbitrary context dictionary"""
        summary_parts = []
        
        for key, value in context_dict.items():
            if isinstance(value, (list, tuple)) and len(value) > 0:
                summary_parts.append(f"{key}: {len(value)} items")
            elif isinstance(value, dict):
                summary_parts.append(f"{key}: {len(value)} keys")
            elif isinstance(value, str) and len(value) > 0:
                preview = value[:50]
                if len(value) > 50:
                    preview += "..."
                summary_parts.append(f"{key}: {preview}")
            elif value is not None:
                summary_parts.append(f"{key}: {value}")
                
        summary = ", ".join(summary_parts)
        
        return {
            "summary": summary,
            "token_count": self._estimate_tokens(summary),
            "keys": list(context_dict.keys())
        }
    
    def adaptive_summarize(self, text, target_tokens=None):
        """Adaptively summarize text to target token count"""
        if target_tokens is None:
            target_tokens = self.max_context_tokens
            
        current_tokens = self._estimate_tokens(text)
        
        if current_tokens <= target_tokens:
            return {
                "summary": text,
                "token_count": current_tokens,
                "compression_ratio": 1.0
            }
            
        # Need to compress
        sentences = text.split('.')
        
        # Keep first and last sentences
        if len(sentences) <= 2:
            summary = text[:target_tokens * 4]
        else:
            important_sentences = [sentences[0]]
            
            # Add middle sentences until we hit target
            chars_used = len(sentences[0])
            for sent in sentences[1:-1]:
                if chars_used + len(sent) > target_tokens * 4:
                    break
                important_sentences.append(sent)
                chars_used += len(sent)
                
            # Always include last sentence if space
            if chars_used + len(sentences[-1]) <= target_tokens * 4:
                important_sentences.append(sentences[-1])
                
            summary = '. '.join(important_sentences)
            if not summary.endswith('.'):
                summary += '.'
                
        summary_tokens = self._estimate_tokens(summary)
        
        return {
            "summary": summary,
            "token_count": summary_tokens,
            "original_tokens": current_tokens,
            "compression_ratio": summary_tokens / current_tokens if current_tokens > 0 else 1.0
        }
    
    def get_metrics(self):
        """Get summarizer metrics"""
        return {
            'max_context_tokens': self.max_context_tokens,
            'cached_summaries': len(self.summary_cache),
            'summary_history': len(self.summary_history),
            'total_summaries': sum(1 for _ in self.summary_history)
        }
