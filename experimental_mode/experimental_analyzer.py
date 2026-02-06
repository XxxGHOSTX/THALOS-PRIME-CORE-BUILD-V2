"""
Experimental Analyzer
Performs experimental analysis and exploratory reasoning
"""

import numpy as np
from datetime import datetime as dt


class ExperimentalAnalyzer:
    """Experimental analysis and reasoning engine"""
    
    def __init__(self, enabled=False):
        self.enabled = enabled
        self.experiments = []
        self.hypotheses = []
        self.analysis_log = []
        
    def enable(self):
        """Enable experimental mode"""
        self.enabled = True
        self._log_event('experimental_mode_enabled')
        
    def disable(self):
        """Disable experimental mode"""
        self.enabled = False
        self._log_event('experimental_mode_disabled')
        
    def _log_event(self, event_type, data=None):
        """Log experimental event"""
        self.analysis_log.append({
            'type': event_type,
            'data': data,
            'timestamp': dt.now().isoformat()
        })
        
        if len(self.analysis_log) > 1000:
            self.analysis_log = self.analysis_log[-1000:]
            
    def register_hypothesis(self, hypothesis_name, test_fn, validate_fn):
        """Register a hypothesis to test"""
        hypothesis = {
            'name': hypothesis_name,
            'test_fn': test_fn,
            'validate_fn': validate_fn,
            'tests_run': 0,
            'validations': [],
            'registered_at': dt.now().isoformat()
        }
        self.hypotheses.append(hypothesis)
        self._log_event('hypothesis_registered', {'name': hypothesis_name})
        return len(self.hypotheses) - 1
        
    def run_experiment(self, experiment_name, data):
        """Run an experiment"""
        if not self.enabled:
            return None
            
        experiment = {
            'name': experiment_name,
            'data': data,
            'started_at': dt.now().isoformat(),
            'results': []
        }
        
        # Test all relevant hypotheses
        for hypothesis in self.hypotheses:
            try:
                test_result = hypothesis['test_fn'](data)
                hypothesis['tests_run'] += 1
                
                experiment['results'].append({
                    'hypothesis': hypothesis['name'],
                    'result': test_result,
                    'valid': hypothesis['validate_fn'](test_result)
                })
            except Exception as e:
                experiment['results'].append({
                    'hypothesis': hypothesis['name'],
                    'error': str(e)
                })
                
        experiment['completed_at'] = dt.now().isoformat()
        self.experiments.append(experiment)
        
        self._log_event('experiment_completed', {
            'name': experiment_name,
            'results_count': len(experiment['results'])
        })
        
        return experiment
        
    def analyze_query_experimental(self, query, context):
        """Perform experimental analysis on a query"""
        if not self.enabled:
            return {'experimental': False}
            
        analysis = {
            'experimental': True,
            'query_complexity': self._estimate_complexity(query),
            'context_depth': len(context) if isinstance(context, dict) else 0,
            'novel_patterns': [],
            'confidence_factors': []
        }
        
        # Check for novel patterns
        words = query.lower().split()
        if len(set(words)) / len(words) > 0.8:  # High unique word ratio
            analysis['novel_patterns'].append('high_vocabulary_diversity')
            
        if any(len(w) > 15 for w in words):
            analysis['novel_patterns'].append('complex_terminology')
            
        # Analyze confidence factors
        if '?' in query:
            analysis['confidence_factors'].append('interrogative')
        if any(w in words for w in ['maybe', 'perhaps', 'possibly']):
            analysis['confidence_factors'].append('uncertainty_markers')
            
        self._log_event('experimental_analysis', {
            'query_length': len(query),
            'patterns_found': len(analysis['novel_patterns'])
        })
        
        return analysis
        
    def _estimate_complexity(self, text):
        """Estimate text complexity"""
        words = text.split()
        if not words:
            return 0.0
            
        avg_word_len = np.mean([len(w) for w in words])
        unique_ratio = len(set(words)) / len(words)
        
        complexity = (avg_word_len / 10.0) * 0.5 + unique_ratio * 0.5
        return min(1.0, complexity)
        
    def get_experiment_summary(self):
        """Get summary of all experiments"""
        return {
            'enabled': self.enabled,
            'experiments_run': len(self.experiments),
            'hypotheses_registered': len(self.hypotheses),
            'recent_experiments': self.experiments[-10:] if self.experiments else []
        }
