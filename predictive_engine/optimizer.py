"""
Predictive Optimizer
Optimizes system parameters based on telemetry and performance data
"""

import numpy as np
from datetime import datetime as dt


class PredictiveOptimizer:
    """Predictive optimization engine"""
    
    def __init__(self, telemetry_collector=None):
        self.telemetry = telemetry_collector
        self.optimization_history = []
        self.parameter_bounds = {}
        self.learning_rate = 0.01
        
    def register_parameter(self, param_name, min_val, max_val, current_val):
        """Register a parameter for optimization"""
        self.parameter_bounds[param_name] = {
            'min': min_val,
            'max': max_val,
            'current': current_val,
            'history': [current_val]
        }
        
    def predict_optimal_value(self, param_name, objective_metric):
        """Predict optimal parameter value"""
        if param_name not in self.parameter_bounds:
            return None
            
        if not self.telemetry:
            return self.parameter_bounds[param_name]['current']
            
        # Get metric statistics
        metric_stats = self.telemetry.get_metric_stats(objective_metric)
        
        if not metric_stats:
            return self.parameter_bounds[param_name]['current']
            
        # Simple gradient-based optimization
        current_val = self.parameter_bounds[param_name]['current']
        bounds = self.parameter_bounds[param_name]
        
        # If metric is below target, adjust parameter
        target_value = 0.8  # Target 80% for certainty-like metrics
        
        if 'certainty' in objective_metric.lower():
            if metric_stats['mean'] < target_value:
                # Increase parameter to improve certainty
                adjustment = self.learning_rate * (target_value - metric_stats['mean'])
                new_val = current_val + adjustment * (bounds['max'] - bounds['min'])
            else:
                # Decrease slightly to optimize
                new_val = current_val - self.learning_rate * 0.1
        else:
            # For latency-like metrics, minimize
            if metric_stats['mean'] > 100:  # 100ms threshold
                new_val = current_val - self.learning_rate * (bounds['max'] - bounds['min'])
            else:
                new_val = current_val
                
        # Clip to bounds
        new_val = np.clip(new_val, bounds['min'], bounds['max'])
        
        return new_val
        
    def optimize_parameters(self, objective_metrics):
        """Optimize all registered parameters"""
        optimizations = {}
        
        for param_name in self.parameter_bounds:
            for metric in objective_metrics:
                new_val = self.predict_optimal_value(param_name, metric)
                
                if new_val is not None:
                    optimizations[param_name] = {
                        'old_value': self.parameter_bounds[param_name]['current'],
                        'new_value': new_val,
                        'metric': metric,
                        'timestamp': dt.now().isoformat()
                    }
                    
                    # Update current value
                    self.parameter_bounds[param_name]['current'] = new_val
                    self.parameter_bounds[param_name]['history'].append(new_val)
                    
        self.optimization_history.append({
            'optimizations': optimizations,
            'timestamp': dt.now().isoformat()
        })
        
        return optimizations
        
    def rollback_parameter(self, param_name):
        """Rollback parameter to previous value"""
        if param_name not in self.parameter_bounds:
            return False
            
        history = self.parameter_bounds[param_name]['history']
        if len(history) > 1:
            self.parameter_bounds[param_name]['current'] = history[-2]
            history.pop()
            return True
            
        return False
        
    def get_optimization_summary(self):
        """Get summary of optimization history"""
        return {
            'parameters_tracked': len(self.parameter_bounds),
            'optimizations_performed': len(self.optimization_history),
            'recent_optimizations': self.optimization_history[-10:] if self.optimization_history else []
        }
