#!/usr/bin/env python3
"""THALOS PRIME - Main Application"""

import sys
import argparse as ap
from datetime import datetime as dt

from synapse_matrix.bio_synthesizer import BioSynthesizer
from cognition_store.persistence import CognitionVault
from modality_bridges.fusion_conductor import FusionConductor
from inference_network.cognitive_net import CognitiveInferenceNet
from secure_params.crypto_vault import SecureVault
from async_workers.worker_pool import AsyncPool
from src.matrix_codex import MatrixCodex

try:
    from viewport_canvas.dynamic_viewport import DynamicViewport
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("⚠️  GUI not available (tkinter not installed)")


class ThalosApp:
    """Main application controller"""
    
    def __init__(self, gui_mode=True, crypto_mode=True, mind_mode=False):
        print("⚡ Starting THALOS PRIME...")
        
        self.bio = BioSynthesizer(200000000)
        self.mem = CognitionVault("data.db")
        self.fusion = FusionConductor()
        self.infer = CognitiveInferenceNet()
        self.pool = AsyncPool(4)
        self.codex = MatrixCodex() if mind_mode else None
        
        if crypto_mode:
            self.crypto = SecureVault()
        
        self.session = dt.now().strftime("%Y%m%d%H%M%S")
        self.gui_mode = gui_mode
        self.gui = None
        
        print("✅ System ready\n")
        
    def query(self, txt, meta=None):
        """Process query"""
        
        # Infer intent
        intent = self.infer.infer(txt)
        
        # Fuse modalities
        fused = self.fusion.conduct_fusion({
            'text': txt,
            'metadata': meta or {}
        })
        
        # SBI process
        result = self.bio.infer_query(txt, {
            'intent': intent,
            'fused': fused,
            'history': self.mem.recall_recent(3, self.session)
        })
        
        # Add inference and fusion info
        result['inference'] = intent
        result['fusion'] = fused

        # Optional Mind Interface path with LoB awareness
        if self.codex:
            codex_resp = self.codex.forward({'text': txt, 'context': {'latent': fused}})
            result['mind_output'] = codex_resp
        
        # Store
        self.mem.archive_exchange(txt, result, self.session)
        self.mem.log_pattern(intent['type'])
        
        return result
    
    def run_gui(self):
        """Run GUI mode"""
        if not self.gui_mode or not GUI_AVAILABLE:
            print("❌ GUI not available - use CLI mode")
            return
        print("🚀 GUI launching...")
        self.gui = DynamicViewport(self.query)
        self.gui.start()
    
    def run_cli(self):
        """Run CLI mode"""
        print("💬 CLI Mode - Type 'exit' to quit\n")
        
        while True:
            try:
                inp = input("You: ").strip()
                if inp.lower() in ['exit', 'quit']:
                    break
                if not inp:
                    continue
                    
                resp = self.query(inp)
                print(f"\nTHALOS: {resp['answer']}")
                print(f"[Certainty: {resp['certainty']:.1%}]\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def report(self):
        """Generate report"""
        bio_s = self.bio.system_status()
        mem_s = self.mem.vault_metrics()
        pool_s = self.pool.pool_stats()
        
        print("\n" + "="*50)
        print("THALOS PRIME SYSTEM REPORT")
        print("="*50)
        print(f"\n🔬 SBI: {bio_s['parameters']:,} parameters")
        print(f"💾 Memory: {mem_s['exchanges']} exchanges")
        print(f"🔄 Workers: {pool_s['alive']}/{pool_s['workers']}")
        print(f"📊 Session: {self.session}")
        print("="*50 + "\n")
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n🔄 Shutting down...")
        self.pool.terminate()
        if self.gui:
            self.gui.stop()
        print("✅ Goodbye")


def main():
    parser = ap.ArgumentParser(description="THALOS PRIME SBI System")
    parser.add_argument('--mode', choices=['gui', 'cli'], default='gui')
    parser.add_argument('--no-crypto', action='store_true')
    parser.add_argument('--mind-interface', action='store_true')
    parser.add_argument('--report', action='store_true')
    args = parser.parse_args()
    
    try:
        app = ThalosApp(
            gui_mode=(args.mode=='gui'),
            crypto_mode=(not args.no_crypto),
            mind_mode=args.mind_interface
        )
        
        if args.report:
            app.report()
        elif args.mode == 'gui':
            app.run_gui()
        else:
            app.run_cli()
            
        app.cleanup()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
