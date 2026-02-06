"""
Telemetry Collector
Collects real-time metrics from all system components
"""

import time
from datetime import datetime as dt
from collections import deque
import threading as thr


class TelemetryCollector:
    """Collects and aggregates system telemetry"""
    
    def __init__(self, retention_seconds=3600):
        self.retention_seconds = retention_seconds
        self.metrics = {}
        self.events = deque(maxlen=10000)
        self.lock = thr.Lock()
        self.start_time = time.time()
        
    def record_metric(self, metric_name, value, tags=None):
        """Record a metric value"""
        with self.lock:
            if metric_name not in self.metrics:
                self.metrics[metric_name] = {
                    'values': deque(maxlen=1000),
                    'timestamps': deque(maxlen=1000),
                    'tags': []
                }
                
            self.metrics[metric_name]['values'].append(float(value))
            self.metrics[metric_name]['timestamps'].append(time.time())
            
            if tags:
                self.metrics[metric_name]['tags'].append(tags)
                
    def record_event(self, event_type, event_data):
        """Record an event"""
        with self.lock:
            self.events.append({
                'type': event_type,
                'data': event_data,
                'timestamp': dt.now().isoformat()
            })
            
    def get_metric_stats(self, metric_name):
        """Get statistics for a metric"""
        with self.lock:
            if metric_name not in self.metrics:
                return None
                
            values = list(self.metrics[metric_name]['values'])
            
            if not values:
                return None
                
            import numpy as np
            
            return {
                'name': metric_name,
                'count': len(values),
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'p50': float(np.percentile(values, 50)),
                'p95': float(np.percentile(values, 95)),
                'p99': float(np.percentile(values, 99))
            }
            
    def get_all_metrics(self):
        """Get all metric names"""
        with self.lock:
            return list(self.metrics.keys())
            
    def get_recent_events(self, count=100):
        """Get recent events"""
        with self.lock:
            return list(self.events)[-count:]
            
    def get_uptime(self):
        """Get system uptime"""
        return time.time() - self.start_time
        
    def generate_report(self):
        """Generate telemetry report"""
        with self.lock:
            report = {
                'uptime_seconds': self.get_uptime(),
                'total_metrics': len(self.metrics),
                'total_events': len(self.events),
                'timestamp': dt.now().isoformat(),
                'metrics': {}
            }
            
            for metric_name in self.metrics.keys():
                stats = self.get_metric_stats(metric_name)
                if stats:
                    report['metrics'][metric_name] = stats
                    
            return report
            
    def clear_old_data(self):
        """Clear data older than retention period"""
        cutoff_time = time.time() - self.retention_seconds
        
        with self.lock:
            for metric_name in self.metrics:
                metric_data = self.metrics[metric_name]
                
                # Remove old timestamps and corresponding values
                while (metric_data['timestamps'] and 
                       metric_data['timestamps'][0] < cutoff_time):
                    metric_data['timestamps'].popleft()
                    if metric_data['values']:
                        metric_data['values'].popleft()
