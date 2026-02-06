#!/usr/bin/env python3
"""
Matrix Codex Inference Script
Provides inference harness and benchmarking for BioSynthesizer
"""

import sys
import os
import argparse
import time
import numpy as np
from datetime import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from synapse_matrix.bio_synthesizer import BioSynthesizer


class InferenceHarness:
    """Inference harness with benchmarking"""
    
    def __init__(self, model):
        self.model = model
        self.inference_times = []
        
    def single_inference(self, query, verbose=True):
        """Run single inference with timing"""
        start = time.time()
        result = self.model.infer_query(query)
        latency = time.time() - start
        
        self.inference_times.append(latency)
        
        if verbose:
            print(f"\nQuery: {query}")
            print(f"Answer: {result['answer']}")
            print(f"Certainty: {result['certainty']:.2%}")
            print(f"Latency: {latency*1000:.2f}ms")
            
        return result, latency
    
    def batch_inference(self, queries, verbose=False):
        """Run batch inference"""
        results = []
        latencies = []
        
        print(f"🔄 Running batch inference on {len(queries)} queries...")
        
        for i, query in enumerate(queries):
            result, latency = self.single_inference(query, verbose=verbose)
            results.append(result)
            latencies.append(latency)
            
            if not verbose and (i + 1) % 10 == 0:
                print(f"  Processed {i+1}/{len(queries)} queries")
                
        return results, latencies
    
    def benchmark(self, num_queries=100):
        """Run performance benchmark"""
        print(f"\n⚡ Running performance benchmark ({num_queries} queries)...")
        
        # Generate test queries
        test_queries = [
            f"Test query number {i}: What is the meaning of this?"
            for i in range(num_queries)
        ]
        
        # Warm-up
        print("  Warming up...")
        for _ in range(5):
            self.model.infer_query("warm up query")
            
        # Benchmark
        print("  Running benchmark...")
        start = time.time()
        results, latencies = self.batch_inference(test_queries, verbose=False)
        total_time = time.time() - start
        
        # Compute statistics
        latencies_ms = [l * 1000 for l in latencies]
        
        stats = {
            'total_queries': num_queries,
            'total_time': total_time,
            'avg_latency_ms': np.mean(latencies_ms),
            'min_latency_ms': np.min(latencies_ms),
            'max_latency_ms': np.max(latencies_ms),
            'p50_latency_ms': np.percentile(latencies_ms, 50),
            'p95_latency_ms': np.percentile(latencies_ms, 95),
            'p99_latency_ms': np.percentile(latencies_ms, 99),
            'throughput_qps': num_queries / total_time
        }
        
        return stats
    
    def profile_latency(self, query_lengths=[10, 50, 100, 200, 500]):
        """Profile latency by query length"""
        print("\n📊 Profiling latency by query length...")
        
        results = []
        
        for length in query_lengths:
            query = "test " * (length // 5)
            query = query[:length]
            
            # Run multiple times and average
            times = []
            for _ in range(10):
                start = time.time()
                self.model.infer_query(query)
                times.append(time.time() - start)
                
            avg_time = np.mean(times) * 1000
            
            results.append({
                'query_length': length,
                'avg_latency_ms': avg_time
            })
            
            print(f"  Length {length:3d}: {avg_time:.2f}ms")
            
        return results


def generate_sample_queries():
    """Generate diverse sample queries"""
    return [
        "Hello, how are you today?",
        "What is THALOS PRIME?",
        "Explain artificial intelligence",
        "Help me understand quantum computing",
        "What can you do for me?",
        "Analyze this complex problem",
        "Show me system capabilities",
        "How does the SBI engine work?",
        "Tell me about neural networks",
        "What are wavefronts in AI?",
    ]


def interactive_mode(harness):
    """Interactive inference mode"""
    print("\n💬 Interactive Mode - Type 'exit' to quit\n")
    
    while True:
        try:
            query = input("Query: ").strip()
            
            if query.lower() in ['exit', 'quit']:
                break
                
            if not query:
                continue
                
            harness.single_inference(query, verbose=True)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Matrix Codex Inference & Benchmarking")
    parser.add_argument('--params', type=int, default=200000000,
                       help='Target parameter count')
    parser.add_argument('--mode', choices=['interactive', 'benchmark', 'sample', 'profile'],
                       default='sample',
                       help='Inference mode')
    parser.add_argument('--benchmark-size', type=int, default=100,
                       help='Number of queries for benchmark')
    parser.add_argument('--query', type=str,
                       help='Single query to run')
    
    args = parser.parse_args()
    
    print("="*60)
    print("MATRIX CODEX INFERENCE")
    print("="*60)
    
    # Initialize model
    print(f"\n🔬 Initializing BioSynthesizer with {args.params:,} target parameters...")
    model = BioSynthesizer(args.params)
    
    # Create harness
    harness = InferenceHarness(model)
    
    # Run mode
    if args.mode == 'interactive':
        interactive_mode(harness)
        
    elif args.mode == 'benchmark':
        stats = harness.benchmark(args.benchmark_size)
        
        print("\n" + "="*60)
        print("BENCHMARK RESULTS")
        print("="*60)
        print(f"Total queries: {stats['total_queries']}")
        print(f"Total time: {stats['total_time']:.2f}s")
        print(f"Throughput: {stats['throughput_qps']:.2f} queries/sec")
        print(f"\nLatency Statistics:")
        print(f"  Average: {stats['avg_latency_ms']:.2f}ms")
        print(f"  Minimum: {stats['min_latency_ms']:.2f}ms")
        print(f"  Maximum: {stats['max_latency_ms']:.2f}ms")
        print(f"  P50: {stats['p50_latency_ms']:.2f}ms")
        print(f"  P95: {stats['p95_latency_ms']:.2f}ms")
        print(f"  P99: {stats['p99_latency_ms']:.2f}ms")
        print("="*60)
        
    elif args.mode == 'profile':
        harness.profile_latency()
        
    elif args.mode == 'sample':
        if args.query:
            harness.single_inference(args.query, verbose=True)
        else:
            queries = generate_sample_queries()
            print(f"\n🔄 Running sample queries...")
            for query in queries:
                harness.single_inference(query, verbose=True)
                print()
    
    # Summary
    if harness.inference_times:
        print("\n" + "="*60)
        print("SESSION SUMMARY")
        print("="*60)
        print(f"Total inferences: {len(harness.inference_times)}")
        print(f"Average latency: {np.mean(harness.inference_times)*1000:.2f}ms")
        print("="*60)


if __name__ == "__main__":
    main()
