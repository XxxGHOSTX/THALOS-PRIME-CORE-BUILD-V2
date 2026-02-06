"""
Analytics Dashboard
Provides dashboard generation and visualization
"""

from datetime import datetime as dt
import json


class AnalyticsDashboard:
    """Generates analytics dashboards and reports"""
    
    def __init__(self, telemetry_collector):
        self.collector = telemetry_collector
        self.dashboard_config = {
            'refresh_rate': 5,
            'widgets': []
        }
        
    def add_widget(self, widget_type, metric_name, config=None):
        """Add widget to dashboard"""
        widget = {
            'type': widget_type,
            'metric': metric_name,
            'config': config or {}
        }
        self.dashboard_config['widgets'].append(widget)
        
    def generate_text_dashboard(self):
        """Generate text-based dashboard"""
        lines = []
        lines.append("="*70)
        lines.append("THALOS PRIME ANALYTICS DASHBOARD")
        lines.append("="*70)
        lines.append(f"Generated: {dt.now().isoformat()}")
        lines.append(f"Uptime: {self.collector.get_uptime():.1f}s")
        lines.append("")
        
        # Add metrics
        lines.append("METRICS SUMMARY")
        lines.append("-"*70)
        
        for metric_name in self.collector.get_all_metrics():
            stats = self.collector.get_metric_stats(metric_name)
            if stats:
                lines.append(f"\n{metric_name}:")
                lines.append(f"  Count: {stats['count']}")
                lines.append(f"  Mean:  {stats['mean']:.4f}")
                lines.append(f"  Std:   {stats['std']:.4f}")
                lines.append(f"  Range: [{stats['min']:.4f}, {stats['max']:.4f}]")
                lines.append(f"  P50:   {stats['p50']:.4f}")
                lines.append(f"  P95:   {stats['p95']:.4f}")
                
        # Add recent events
        lines.append("\n" + "-"*70)
        lines.append("RECENT EVENTS (Last 10)")
        lines.append("-"*70)
        
        recent_events = self.collector.get_recent_events(10)
        for event in recent_events:
            lines.append(f"[{event['timestamp']}] {event['type']}")
            
        lines.append("="*70)
        
        return "\n".join(lines)
        
    def generate_json_dashboard(self):
        """Generate JSON dashboard data"""
        report = self.collector.generate_report()
        report['recent_events'] = self.collector.get_recent_events(50)
        return json.dumps(report, indent=2)
        
    def display_dashboard(self):
        """Display text dashboard"""
        print(self.generate_text_dashboard())
        
    def export_metrics(self, format='json'):
        """Export metrics in specified format"""
        if format == 'json':
            return self.generate_json_dashboard()
        else:
            return self.generate_text_dashboard()
            
    def get_alert_status(self):
        """Check for alert conditions"""
        alerts = []
        
        # Check for high latency
        latency_stats = self.collector.get_metric_stats('inference_latency')
        if latency_stats and latency_stats['p95'] > 500:  # 500ms threshold
            alerts.append({
                'severity': 'warning',
                'metric': 'inference_latency',
                'message': f"High P95 latency: {latency_stats['p95']:.2f}ms"
            })
            
        # Check for low certainty
        cert_stats = self.collector.get_metric_stats('certainty')
        if cert_stats and cert_stats['mean'] < 0.5:
            alerts.append({
                'severity': 'warning',
                'metric': 'certainty',
                'message': f"Low average certainty: {cert_stats['mean']:.2%}"
            })
            
        return alerts
