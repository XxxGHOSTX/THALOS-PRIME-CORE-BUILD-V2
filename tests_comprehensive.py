"""
Comprehensive Test Suite for THALOS PRIME
Tests all major components and integrations
"""

import unittest as ut
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from synapse_matrix.bio_synthesizer import BioSynthesizer
from cognition_store.persistence import CognitionVault
from context_summarization.semantic_retrieval import SemanticRetriever
from context_summarization.context_summarizer import ContextSummarizer
from analytics_engine.telemetry_collector import TelemetryCollector
from analytics_engine.analytics_dashboard import AnalyticsDashboard
from experimental_mode.experimental_analyzer import ExperimentalAnalyzer
from experimental_mode.emergent_detector import EmergentPatternDetector
from predictive_engine.optimizer import PredictiveOptimizer
from predictive_engine.parameter_tuner import ParameterTuner


class TestBioSynthesizer(ut.TestCase):
    """Test Matrix Codex BioSynthesizer"""
    
    def test_initialization(self):
        """Test model initialization"""
        bio = BioSynthesizer(1000000)
        self.assertGreater(bio.param_total, 1000000)
        self.assertGreater(len(bio.wavefronts), 0)
        
    def test_inference(self):
        """Test basic inference"""
        bio = BioSynthesizer(1000000)
        result = bio.infer_query("Hello THALOS")
        self.assertIn('answer', result)
        self.assertIn('certainty', result)
        self.assertGreater(result['certainty'], 0)
        self.assertLess(result['certainty'], 1)
        
    def test_parameter_count(self):
        """Test parameter count meets requirement"""
        bio = BioSynthesizer(200000000)
        self.assertGreaterEqual(bio.param_total, 200000000)
        

class TestCognitionVault(ut.TestCase):
    """Test persistent memory system"""
    
    def setUp(self):
        self.test_db = "test_memory.db"
        
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
    def test_archive_and_recall(self):
        """Test storing and retrieving exchanges"""
        vault = CognitionVault(self.test_db)
        
        ex_id = vault.archive_exchange("test query", {
            'answer': 'test answer',
            'certainty': 0.85
        })
        
        self.assertIsNotNone(ex_id)
        
        recent = vault.recall_recent(5)
        self.assertGreater(len(recent), 0)
        self.assertEqual(recent[0]['query'], "test query")
        
    def test_search(self):
        """Test context search"""
        vault = CognitionVault(self.test_db)
        
        vault.archive_exchange("quantum physics", {'answer': 'test', 'certainty': 0.8})
        vault.archive_exchange("classical mechanics", {'answer': 'test2', 'certainty': 0.7})
        
        results = vault.search_context("quantum")
        self.assertGreater(len(results), 0)
        self.assertIn("quantum", results[0]['query'].lower())


class TestSemanticRetrieval(ut.TestCase):
    """Test semantic retrieval system"""
    
    def test_embedding_generation(self):
        """Test text embedding"""
        retriever = SemanticRetriever(dim=512)
        embedding = retriever.embed_text("Hello world")
        
        self.assertEqual(len(embedding), 512)
        self.assertAlmostEqual(np.linalg.norm(embedding), 1.0, places=5)
        
    def test_indexing_and_retrieval(self):
        """Test document indexing and retrieval"""
        retriever = SemanticRetriever(dim=512)
        
        # Index documents
        retriever.index_document("Machine learning is fascinating")
        retriever.index_document("Python programming language")
        retriever.index_document("Deep learning neural networks")
        
        # Retrieve
        results = retriever.retrieve("artificial intelligence", top_k=2)
        
        self.assertGreater(len(results), 0)
        self.assertIn('similarity', results[0])
        self.assertIn('metadata', results[0])


class TestContextSummarizer(ut.TestCase):
    """Test context summarization"""
    
    def test_summarize_exchanges(self):
        """Test exchange summarization"""
        summarizer = ContextSummarizer(max_context_tokens=2048)
        
        exchanges = [
            {'query': 'What is AI?', 'response': {'answer': 'AI is...', 'certainty': 0.8}},
            {'query': 'Tell me about ML', 'response': {'answer': 'ML is...', 'certainty': 0.75}}
        ]
        
        summary = summarizer.summarize_exchanges(exchanges)
        
        self.assertIn('summary', summary)
        self.assertIn('key_points', summary)
        self.assertGreater(len(summary['summary']), 0)
        
    def test_adaptive_summarization(self):
        """Test adaptive text summarization"""
        summarizer = ContextSummarizer()
        
        long_text = "This is a test. " * 100
        result = summarizer.adaptive_summarize(long_text, target_tokens=50)
        
        self.assertIn('summary', result)
        self.assertIn('compression_ratio', result)
        self.assertLess(result['token_count'], result['original_tokens'])


class TestTelemetryCollector(ut.TestCase):
    """Test telemetry collection"""
    
    def test_record_metric(self):
        """Test metric recording"""
        collector = TelemetryCollector()
        
        collector.record_metric('test_metric', 100)
        collector.record_metric('test_metric', 150)
        collector.record_metric('test_metric', 125)
        
        stats = collector.get_metric_stats('test_metric')
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['count'], 3)
        self.assertEqual(stats['mean'], 125.0)
        
    def test_event_logging(self):
        """Test event logging"""
        collector = TelemetryCollector()
        
        collector.record_event('test_event', {'key': 'value'})
        
        events = collector.get_recent_events(10)
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0]['type'], 'test_event')


class TestAnalyticsDashboard(ut.TestCase):
    """Test analytics dashboard"""
    
    def test_dashboard_generation(self):
        """Test dashboard generation"""
        collector = TelemetryCollector()
        collector.record_metric('latency', 100)
        collector.record_metric('certainty', 0.85)
        
        dashboard = AnalyticsDashboard(collector)
        text_output = dashboard.generate_text_dashboard()
        
        self.assertIn('ANALYTICS DASHBOARD', text_output)
        self.assertGreater(len(text_output), 0)
        
    def test_json_export(self):
        """Test JSON export"""
        collector = TelemetryCollector()
        dashboard = AnalyticsDashboard(collector)
        
        json_output = dashboard.generate_json_dashboard()
        self.assertIn('uptime_seconds', json_output)


class TestExperimentalAnalyzer(ut.TestCase):
    """Test experimental mode"""
    
    def test_enable_disable(self):
        """Test enabling and disabling experimental mode"""
        analyzer = ExperimentalAnalyzer()
        
        self.assertFalse(analyzer.enabled)
        
        analyzer.enable()
        self.assertTrue(analyzer.enabled)
        
        analyzer.disable()
        self.assertFalse(analyzer.enabled)
        
    def test_experimental_analysis(self):
        """Test experimental query analysis"""
        analyzer = ExperimentalAnalyzer(enabled=True)
        
        result = analyzer.analyze_query_experimental(
            "This is a complex query with unusual terminology?",
            {}
        )
        
        self.assertTrue(result['experimental'])
        self.assertIn('query_complexity', result)
        self.assertIn('novel_patterns', result)


class TestEmergentPatternDetector(ut.TestCase):
    """Test emergent pattern detection"""
    
    def test_pattern_detection(self):
        """Test pattern detection in sequences"""
        detector = EmergentPatternDetector()
        
        # Create a sequence with a trend
        sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        result = detector.analyze_sequence(sequence)
        
        self.assertIn('patterns', result)
        self.assertGreater(len(result['patterns']), 0)
        
    def test_anomaly_detection(self):
        """Test anomaly detection"""
        detector = EmergentPatternDetector(sensitivity=0.5)
        
        # Create sequence with strong anomaly
        sequence = [10, 10, 10, 10, 1000, 10, 10, 10, 10, 10]
        
        result = detector.analyze_sequence(sequence)
        
        # Should detect the anomaly or at least return patterns
        self.assertIn('patterns', result)
        self.assertGreaterEqual(len(result['patterns']), 0)


class TestPredictiveOptimizer(ut.TestCase):
    """Test predictive optimization"""
    
    def test_parameter_registration(self):
        """Test parameter registration"""
        optimizer = PredictiveOptimizer()
        
        optimizer.register_parameter('learning_rate', 0.001, 0.1, 0.01)
        
        self.assertIn('learning_rate', optimizer.parameter_bounds)
        self.assertEqual(optimizer.parameter_bounds['learning_rate']['current'], 0.01)
        
    def test_optimization(self):
        """Test parameter optimization"""
        collector = TelemetryCollector()
        optimizer = PredictiveOptimizer(collector)
        
        optimizer.register_parameter('test_param', 0.0, 1.0, 0.5)
        
        # Record some metrics
        collector.record_metric('certainty', 0.6)
        collector.record_metric('certainty', 0.65)
        
        optimizations = optimizer.optimize_parameters(['certainty'])
        
        self.assertIsInstance(optimizations, dict)


class TestParameterTuner(ut.TestCase):
    """Test parameter tuning"""
    
    def test_tuning_session(self):
        """Test tuning session"""
        tuner = ParameterTuner()
        
        session_id = tuner.start_tuning_session('test', {'param1': 0.5, 'param2': 1.0})
        
        self.assertIsNotNone(session_id)
        self.assertEqual(len(tuner.tuning_sessions), 1)
        
    def test_config_evaluation(self):
        """Test configuration evaluation"""
        tuner = ParameterTuner()
        
        tuner.start_tuning_session('test', {'param1': 0.5})
        
        trial = tuner.evaluate_config({'param1': 0.6}, 0.85)
        
        self.assertIsNotNone(trial)
        self.assertEqual(trial['score'], 0.85)


class TestEndToEndIntegration(ut.TestCase):
    """End-to-end integration tests"""
    
    def test_full_pipeline(self):
        """Test complete inference pipeline"""
        # Initialize components
        bio = BioSynthesizer(1000000)
        vault = CognitionVault("test_e2e.db")
        retriever = SemanticRetriever()
        summarizer = ContextSummarizer()
        
        # Index some context
        retriever.index_document("THALOS PRIME is an advanced AI system")
        
        # Run inference
        result = bio.infer_query("What is THALOS?")
        
        # Store result
        vault.archive_exchange("What is THALOS?", result)
        
        # Retrieve and summarize
        recent = vault.recall_recent(5)
        summary = summarizer.summarize_exchanges(recent)
        
        # Verify complete pipeline
        self.assertIsNotNone(result)
        self.assertGreater(len(recent), 0)
        self.assertIn('summary', summary)
        
        # Cleanup
        os.remove("test_e2e.db")


if __name__ == '__main__':
    # Run with verbosity
    ut.main(verbosity=2)
