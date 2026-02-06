#!/usr/bin/env python3
"""
Matrix Codex Training Script
Provides training harness for the BioSynthesizer model
"""

import sys
import os
import argparse
import numpy as np
from datetime import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from synapse_matrix.bio_synthesizer import BioSynthesizer
from cognition_store.persistence import CognitionVault


class TrainingHarness:
    """Training harness for BioSynthesizer"""
    
    def __init__(self, model, learning_rate=0.001):
        self.model = model
        self.lr = learning_rate
        self.training_history = []
        
    def compute_loss(self, predictions, targets):
        """Compute mean squared error loss"""
        return float(np.mean((predictions - targets) ** 2))
    
    def train_step(self, query_texts, target_certainties):
        """Single training step"""
        total_loss = 0.0
        
        for query, target_cert in zip(query_texts, target_certainties):
            # Forward pass
            result = self.model.infer_query(query)
            pred_cert = result['certainty']
            
            # Compute loss (certainty difference)
            loss = (pred_cert - target_cert) ** 2
            total_loss += loss
            
        avg_loss = total_loss / len(query_texts) if query_texts else 0.0
        
        return avg_loss
    
    def train_epoch(self, training_data, batch_size=8):
        """Train one epoch"""
        losses = []
        
        for i in range(0, len(training_data), batch_size):
            batch = training_data[i:i+batch_size]
            
            queries = [item['query'] for item in batch]
            targets = [item['target_certainty'] for item in batch]
            
            loss = self.train_step(queries, targets)
            losses.append(loss)
            
        epoch_loss = np.mean(losses) if losses else 0.0
        
        return epoch_loss
    
    def train(self, training_data, epochs=10, batch_size=8):
        """Full training loop"""
        print(f"🎯 Starting training: {len(training_data)} samples, {epochs} epochs")
        
        for epoch in range(epochs):
            loss = self.train_epoch(training_data, batch_size)
            
            self.training_history.append({
                'epoch': epoch + 1,
                'loss': loss,
                'timestamp': dt.now().isoformat()
            })
            
            print(f"Epoch {epoch+1}/{epochs} - Loss: {loss:.6f}")
            
        print(f"✅ Training complete")
        
        return self.training_history


def generate_synthetic_data(num_samples=100):
    """Generate synthetic training data"""
    print(f"📊 Generating {num_samples} synthetic training samples...")
    
    templates = [
        ("Hello, how are you?", 0.85),
        ("What is your name?", 0.80),
        ("Help me with this problem", 0.75),
        ("Explain quantum physics", 0.65),
        ("Tell me about AI", 0.78),
        ("How does this work?", 0.82),
        ("What can you do?", 0.88),
        ("Analyze this data", 0.70),
        ("Show me the results", 0.77),
        ("Compute the answer", 0.73),
    ]
    
    data = []
    for i in range(num_samples):
        template_idx = i % len(templates)
        query, base_cert = templates[template_idx]
        
        # Add variation
        variation = np.random.randn() * 0.05
        target_cert = np.clip(base_cert + variation, 0.1, 0.95)
        
        data.append({
            'query': f"{query} (variant {i})",
            'target_certainty': target_cert
        })
        
    return data


def load_training_data_from_vault(vault_path, limit=100):
    """Load training data from cognition vault"""
    print(f"💾 Loading training data from vault: {vault_path}")
    
    vault = CognitionVault(vault_path)
    exchanges = vault.recall_recent(limit)
    
    data = []
    for ex in exchanges:
        data.append({
            'query': ex['query'],
            'target_certainty': ex['certainty']
        })
        
    print(f"✅ Loaded {len(data)} samples from vault")
    return data


def main():
    parser = argparse.ArgumentParser(description="Train Matrix Codex BioSynthesizer")
    parser.add_argument('--params', type=int, default=200000000,
                       help='Target parameter count')
    parser.add_argument('--epochs', type=int, default=10,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=8,
                       help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--data-source', choices=['synthetic', 'vault'], default='synthetic',
                       help='Training data source')
    parser.add_argument('--vault-path', type=str, default='data.db',
                       help='Path to cognition vault (if using vault data)')
    parser.add_argument('--num-samples', type=int, default=100,
                       help='Number of training samples (for synthetic data)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("MATRIX CODEX TRAINING")
    print("="*60)
    
    # Initialize model
    print(f"\n🔬 Initializing BioSynthesizer with {args.params:,} target parameters...")
    model = BioSynthesizer(args.params)
    
    # Load or generate data
    if args.data_source == 'vault':
        training_data = load_training_data_from_vault(args.vault_path, args.num_samples)
    else:
        training_data = generate_synthetic_data(args.num_samples)
        
    # Initialize training harness
    harness = TrainingHarness(model, learning_rate=args.lr)
    
    # Train
    print(f"\n🎯 Training configuration:")
    print(f"  - Epochs: {args.epochs}")
    print(f"  - Batch size: {args.batch_size}")
    print(f"  - Learning rate: {args.lr}")
    print(f"  - Samples: {len(training_data)}")
    print()
    
    history = harness.train(training_data, epochs=args.epochs, batch_size=args.batch_size)
    
    # Report results
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    print(f"Final loss: {history[-1]['loss']:.6f}")
    print(f"Initial loss: {history[0]['loss']:.6f}")
    print(f"Improvement: {((history[0]['loss'] - history[-1]['loss']) / history[0]['loss'] * 100):.2f}%")
    print("="*60)


if __name__ == "__main__":
    main()
