"""
Parameter Tuner
Automated parameter tuning based on performance feedback
"""

import numpy as np
from datetime import datetime as dt


class ParameterTuner:
    """Automated parameter tuning engine"""
    
    def __init__(self):
        self.tuning_sessions = []
        self.best_configs = {}
        self.current_config = {}
        
    def start_tuning_session(self, session_name, parameters):
        """Start a new tuning session"""
        session = {
            'name': session_name,
            'parameters': parameters.copy(),
            'started_at': dt.now().isoformat(),
            'trials': [],
            'best_score': -float('inf'),
            'best_config': None
        }
        
        self.tuning_sessions.append(session)
        self.current_config = parameters.copy()
        
        return len(self.tuning_sessions) - 1
        
    def evaluate_config(self, config, score):
        """Evaluate a configuration"""
        if not self.tuning_sessions:
            return None
            
        session = self.tuning_sessions[-1]
        
        trial = {
            'config': config.copy(),
            'score': score,
            'timestamp': dt.now().isoformat()
        }
        
        session['trials'].append(trial)
        
        # Update best if this is better
        if score > session['best_score']:
            session['best_score'] = score
            session['best_config'] = config.copy()
            
        return trial
        
    def suggest_next_config(self, strategy='grid'):
        """Suggest next configuration to try"""
        if not self.tuning_sessions:
            return self.current_config
            
        session = self.tuning_sessions[-1]
        
        if strategy == 'random':
            # Random search
            new_config = {}
            for param, value in session['parameters'].items():
                if isinstance(value, (int, float)):
                    # Add random perturbation
                    perturbation = np.random.randn() * 0.1 * abs(value)
                    new_config[param] = value + perturbation
                else:
                    new_config[param] = value
                    
        elif strategy == 'gradient':
            # Simple gradient ascent
            if len(session['trials']) < 2:
                return self.current_config
                
            # Compare last two trials
            last_trial = session['trials'][-1]
            prev_trial = session['trials'][-2]
            
            score_diff = last_trial['score'] - prev_trial['score']
            
            new_config = {}
            for param in session['parameters']:
                if param in last_trial['config'] and param in prev_trial['config']:
                    last_val = last_trial['config'][param]
                    prev_val = prev_trial['config'][param]
                    
                    if isinstance(last_val, (int, float)) and isinstance(prev_val, (int, float)):
                        param_diff = last_val - prev_val
                        
                        if abs(param_diff) > 1e-10:
                            # Gradient = score_diff / param_diff
                            gradient = score_diff / param_diff
                            # Take step in positive gradient direction
                            new_config[param] = last_val + 0.1 * gradient
                        else:
                            new_config[param] = last_val
                    else:
                        new_config[param] = last_val
                else:
                    new_config[param] = session['parameters'][param]
                    
        else:  # grid or default
            new_config = self.current_config.copy()
            
        self.current_config = new_config
        return new_config
        
    def finish_tuning_session(self):
        """Finish current tuning session"""
        if not self.tuning_sessions:
            return None
            
        session = self.tuning_sessions[-1]
        session['completed_at'] = dt.now().isoformat()
        session['total_trials'] = len(session['trials'])
        
        # Store best config
        if session['best_config']:
            self.best_configs[session['name']] = session['best_config']
            
        return session
        
    def get_best_config(self, session_name=None):
        """Get best configuration"""
        if session_name:
            return self.best_configs.get(session_name)
        elif self.tuning_sessions:
            return self.tuning_sessions[-1].get('best_config')
        else:
            return None
            
    def get_tuning_summary(self):
        """Get summary of tuning sessions"""
        return {
            'sessions_completed': len(self.tuning_sessions),
            'best_configs_found': len(self.best_configs),
            'current_session': self.tuning_sessions[-1] if self.tuning_sessions else None
        }
        
    def compare_configs(self, config1, config2):
        """Compare two configurations"""
        differences = {}
        
        all_keys = set(config1.keys()) | set(config2.keys())
        
        for key in all_keys:
            val1 = config1.get(key)
            val2 = config2.get(key)
            
            if val1 != val2:
                differences[key] = {
                    'config1': val1,
                    'config2': val2
                }
                
        return differences
