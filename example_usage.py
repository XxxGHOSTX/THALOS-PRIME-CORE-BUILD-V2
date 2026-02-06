#!/usr/bin/env python3
"""
Example demonstrating programmatic usage of THALOS PRIME
"""

from run_thalos import ThalosApp

def main():
    print("=" * 60)
    print("THALOS PRIME - Programmatic Usage Example")
    print("=" * 60)
    
    # Initialize system
    app = ThalosApp(gui_mode=False, crypto_mode=True)
    
    # Test queries
    queries = [
        "Hello, how are you?",
        "What can you do?",
        "Explain synthetic biological intelligence",
        "What is the meaning of intelligence?",
        "Help me understand neural networks"
    ]
    
    print("\n🧪 Running test queries...\n")
    
    for query in queries:
        print(f"Query: {query}")
        result = app.query(query)
        
        print(f"Response: {result['answer']}")
        print(f"Certainty: {result['certainty']:.1%}")
        print(f"Inference Type: {result['inference']['type']}")
        print("-" * 60)
        print()
    
    # Generate report
    print("\n📊 Final System Report:")
    app.report()
    
    # Cleanup
    app.cleanup()
    
    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    main()
