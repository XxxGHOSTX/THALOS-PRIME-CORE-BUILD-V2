"""
Emergent Pattern Detector
Detects emergent patterns in system behavior and data
"""

import numpy as np
from datetime import datetime as dt
from collections import deque


class EmergentPatternDetector:
    """Detects emergent patterns and anomalies"""
    
    def __init__(self, sensitivity=0.7):
        self.sensitivity = sensitivity
        self.pattern_history = deque(maxlen=1000)
        self.detected_patterns = []
        self.pattern_types = {
            'repetition': 0,
            'divergence': 0,
            'convergence': 0,
            'anomaly': 0,
            'trend': 0
        }
        
    def analyze_sequence(self, sequence, context=None):
        """Analyze a sequence for emergent patterns"""
        if len(sequence) < 3:
            return {'patterns': [], 'confidence': 0.0}
            
        patterns = []
        
        # Convert to numpy array if needed
        if not isinstance(sequence, np.ndarray):
            sequence = np.array([float(x) if isinstance(x, (int, float)) else hash(x) % 1000 for x in sequence])
            
        # Detect repetition
        if self._check_repetition(sequence):
            patterns.append({
                'type': 'repetition',
                'confidence': 0.8,
                'description': 'Repeating pattern detected'
            })
            self.pattern_types['repetition'] += 1
            
        # Detect trends
        trend = self._detect_trend(sequence)
        if trend != 'stable':
            patterns.append({
                'type': 'trend',
                'direction': trend,
                'confidence': 0.75,
                'description': f'{trend.capitalize()} trend detected'
            })
            self.pattern_types['trend'] += 1
            
        # Detect anomalies
        anomalies = self._detect_anomalies(sequence)
        if anomalies:
            patterns.append({
                'type': 'anomaly',
                'indices': anomalies,
                'confidence': 0.85,
                'description': f'{len(anomalies)} anomalies detected'
            })
            self.pattern_types['anomaly'] += 1
            
        # Detect convergence/divergence
        if len(sequence) >= 5:
            convergence = self._detect_convergence(sequence)
            if convergence != 'stable':
                patterns.append({
                    'type': convergence,
                    'confidence': 0.7,
                    'description': f'{convergence.capitalize()} behavior detected'
                })
                self.pattern_types[convergence] += 1
                
        # Log patterns
        if patterns:
            self._log_patterns(patterns, context)
            
        return {
            'patterns': patterns,
            'count': len(patterns),
            'confidence': np.mean([p['confidence'] for p in patterns]) if patterns else 0.0,
            'timestamp': dt.now().isoformat()
        }
        
    def _check_repetition(self, sequence):
        """Check for repeating patterns"""
        if len(sequence) < 4:
            return False
            
        # Check for simple repetition
        for period in range(1, len(sequence) // 2 + 1):
            is_repetitive = True
            for i in range(period, len(sequence)):
                if abs(sequence[i] - sequence[i % period]) > self.sensitivity * np.std(sequence):
                    is_repetitive = False
                    break
            if is_repetitive and period < len(sequence) / 2:
                return True
                
        return False
        
    def _detect_trend(self, sequence):
        """Detect upward or downward trend"""
        if len(sequence) < 3:
            return 'stable'
            
        # Simple linear regression
        x = np.arange(len(sequence))
        slope = np.polyfit(x, sequence, 1)[0]
        
        threshold = self.sensitivity * np.std(sequence) / len(sequence)
        
        if slope > threshold:
            return 'upward'
        elif slope < -threshold:
            return 'downward'
        else:
            return 'stable'
            
    def _detect_anomalies(self, sequence):
        """Detect anomalous values"""
        if len(sequence) < 5:
            return []
            
        mean = np.mean(sequence)
        std = np.std(sequence)
        
        if std == 0:
            return []
            
        # Z-score method
        z_scores = np.abs((sequence - mean) / std)
        threshold = 2.0 / self.sensitivity  # Inverse relationship with sensitivity
        
        anomalies = np.where(z_scores > threshold)[0].tolist()
        return anomalies
        
    def _detect_convergence(self, sequence):
        """Detect convergence or divergence"""
        if len(sequence) < 5:
            return 'stable'
            
        # Check if values are getting closer (convergence) or farther apart (divergence)
        first_half = sequence[:len(sequence)//2]
        second_half = sequence[len(sequence)//2:]
        
        std_first = np.std(first_half)
        std_second = np.std(second_half)
        
        if std_first == 0:
            return 'stable'
            
        ratio = std_second / std_first
        
        if ratio < 0.7:
            return 'convergence'
        elif ratio > 1.3:
            return 'divergence'
        else:
            return 'stable'
            
    def _log_patterns(self, patterns, context):
        """Log detected patterns"""
        self.detected_patterns.append({
            'patterns': patterns,
            'context': context,
            'timestamp': dt.now().isoformat()
        })
        
        if len(self.detected_patterns) > 100:
            self.detected_patterns = self.detected_patterns[-100:]
            
    def get_pattern_statistics(self):
        """Get statistics on detected patterns"""
        return {
            'total_detections': len(self.detected_patterns),
            'pattern_types': self.pattern_types.copy(),
            'sensitivity': self.sensitivity
        }
        
    def reset_statistics(self):
        """Reset pattern statistics"""
        self.pattern_types = {k: 0 for k in self.pattern_types}
        self.detected_patterns = []
