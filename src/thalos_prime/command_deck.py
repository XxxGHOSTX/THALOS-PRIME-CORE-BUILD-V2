"""
Navigation Bridge - Command execution hub with dynamic registration protocol.
Orchestrates system operations through a flexible command lattice.
"""

import sys
import argparse
import time
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass

from .stargate_storage import PhotonVault
from .quantum_mind import CosmicBrain


@dataclass
class CommandManifest:
    """Manifest for a registered command."""
    name: str
    executor: Callable
    description: str
    needs_vault: bool = False
    needs_brain: bool = False


class NavigationBridge:
    """
    Command execution hub with dynamic registration.
    Coordinates operations across vault and brain systems.
    """
    
    def __init__(self):
        self.command_lattice: Dict[str, CommandManifest] = {}
        self.vault: Optional[PhotonVault] = None
        self.brain: Optional[CosmicBrain] = None
        self.last_execution_time = 0.0
        self.execution_log: List[str] = []
        
        self._initialize_command_lattice()
    
    def register_command(self, manifest: CommandManifest) -> None:
        """Register a command in the lattice."""
        self.command_lattice[manifest.name] = manifest
    
    def _initialize_command_lattice(self) -> None:
        """Initialize core command lattice."""
        self.register_command(CommandManifest(
            name="bootstrap",
            executor=self._execute_bootstrap,
            description="Bootstrap photon vault with test photon streams",
            needs_vault=True
        ))
        
        self.register_command(CommandManifest(
            name="terminate",
            executor=self._execute_terminate,
            description="Graceful system termination sequence",
            needs_vault=True
        ))
        
        self.register_command(CommandManifest(
            name="inspect",
            executor=self._execute_inspect,
            description="Inspect system telemetry and diagnostics",
            needs_vault=True,
            needs_brain=True
        ))
        
        self.register_command(CommandManifest(
            name="inject-data",
            executor=self._execute_injection,
            description="Inject photon stream into vault coordinates",
            needs_vault=True
        ))
        
        self.register_command(CommandManifest(
            name="validate",
            executor=self._execute_validation,
            description="Validate system integrity and coherence",
            needs_vault=True
        ))
    
    def initialize_systems(self, vault_path: str = "data.db") -> None:
        """Initialize vault and brain subsystems."""
        self.vault = PhotonVault(vault_path=vault_path)
        self.brain = CosmicBrain()
    
    def _execute_bootstrap(self, args: argparse.Namespace) -> int:
        """Execute bootstrap sequence."""
        print("🌌 Initiating photon vault bootstrap sequence...")
        
        galaxy_zones = ["nebula-alpha", "nebula-beta", "nebula-gamma", 
                       "nebula-delta", "nebula-epsilon"]
        
        photon_streams = [
            b"Initialization vector for neural pathway reconstruction",
            b"Quantum coherence calibration matrix for temporal anchoring",
            b"Synaptic weight distribution array for pattern recognition",
            b"Temporal synchronization signal for cascade prevention",
            b"Harmonic spectrum data for wave interference analysis"
        ]
        
        for idx, (zone, stream) in enumerate(zip(galaxy_zones, photon_streams)):
            nebula_coord = f"photon_{zone}_{idx:05d}"
            result = self.vault.materialize(nebula_coord, zone, stream)
            status = "✅ SUCCESS" if result else "❌ FAILED"
            print(f"  {status} | Materialized {nebula_coord} in zone {zone}")
        
        print(f"\n🎉 Bootstrap complete. {len(galaxy_zones)} photon streams materialized.")
        return 0
    
    def _execute_terminate(self, args: argparse.Namespace) -> int:
        """Execute termination sequence."""
        print("🛑 Initiating graceful termination protocol...")
        
        if self.vault:
            telemetry = self.vault.get_metrics()
            print(f"  📊 Final telemetry: {telemetry['active_coordinates']} active coordinates")
            self.vault.shutdown_gateway()
            print("  ✅ Photon vault conduit closed")
        
        if self.brain:
            self.brain.collapse_field()
            print("  ✅ Thought field collapsed")
        
        print("\n✅ Termination sequence complete. Systems offline.")
        return 0
    
    def _execute_inspect(self, args: argparse.Namespace) -> int:
        """Execute inspection protocol."""
        print("🔬 System Telemetry & Diagnostics")
        print("=" * 70)
        
        if self.vault:
            print("\n📦 PHOTON VAULT TELEMETRY:")
            telemetry = self.vault.get_metrics()
            for metric_key, metric_value in telemetry.items():
                print(f"  {metric_key:.<45} {metric_value}")
        
        if self.brain:
            print("\n🧠 COSMIC BRAIN DIAGNOSTICS:")
            diagnostics = self.brain.get_cognitive_metrics()
            for diag_key, diag_value in diagnostics.items():
                print(f"  {diag_key:.<45} {diag_value}")
        
        print("\n" + "=" * 70)
        return 0
    
    def _execute_injection(self, args: argparse.Namespace) -> int:
        """Execute data injection."""
        nebula_coord = getattr(args, 'coordinate', None)
        galaxy_zone = getattr(args, 'sector', 'custom-zone')
        photon_stream = getattr(args, 'data', '')
        
        if not nebula_coord or not photon_stream:
            print("❌ Error: --coordinate and --data parameters required")
            return 1
        
        print(f"💉 Injecting photon stream at {nebula_coord} in zone {galaxy_zone}...")
        
        result = self.vault.materialize(
            nebula_coord,
            galaxy_zone,
            photon_stream.encode('utf-8')
        )
        
        if result:
            print(f"✅ Photon stream injection successful")
            return 0
        else:
            print(f"❌ Photon stream injection failed")
            return 1
    
    def _execute_validation(self, args: argparse.Namespace) -> int:
        """Execute validation protocol."""
        print("✅ Executing system validation protocol...")
        
        anomalies = []
        
        if self.vault:
            telemetry = self.vault.get_metrics()
            if telemetry['active_coordinates'] == 0:
                anomalies.append("⚠️  No active coordinates detected in vault")
            
            if telemetry['photon_efficiency'] < 0.15 and telemetry['cache_queries'] > 10:
                anomalies.append("⚠️  Low photon cache efficiency detected")
        
        if self.brain:
            diagnostics = self.brain.get_cognitive_metrics()
            if diagnostics['cognitive_phase'] not in ['QUIESCENT', 'COLLAPSED']:
                anomalies.append(f"⚠️  Unusual cognitive phase: {diagnostics['cognitive_phase']}")
            
            if diagnostics['quantum_coherence'] < 0.5 and diagnostics['thought_waves'] > 50:
                anomalies.append("⚠️  Low quantum coherence in thought field")
        
        if not anomalies:
            print("✅ All validation protocols passed. Systems nominal.")
            return 0
        else:
            print("⚠️  Validation anomalies detected:")
            for anomaly in anomalies:
                print(f"  {anomaly}")
            return 1
    
    def execute_command(self, command_name: str, args: argparse.Namespace) -> int:
        """
        Execute a registered command.
        
        Args:
            command_name: Command identifier
            args: Parsed arguments
            
        Returns:
            Exit code (0 = success, non-zero = failure)
        """
        if command_name not in self.command_lattice:
            print(f"❌ Unknown command: {command_name}")
            return 1
        
        manifest = self.command_lattice[command_name]
        
        if manifest.needs_vault and not self.vault:
            print("❌ Command requires photon vault. Initialize systems first.")
            return 1
        
        if manifest.needs_brain and not self.brain:
            print("❌ Command requires cosmic brain. Initialize systems first.")
            return 1
        
        self.execution_log.append(command_name)
        self.last_execution_time = time.time()
        
        try:
            return manifest.executor(args)
        except Exception as exc:
            print(f"❌ Command execution failed: {exc}")
            return 1
    
    def list_commands(self) -> List[Dict[str, str]]:
        """List all registered commands."""
        return [
            {
                'name': name,
                'description': manifest.description
            }
            for name, manifest in self.command_lattice.items()
        ]


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Thalos Prime Navigation Bridge - Hyperdimensional Command Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--storage-path',
        default='data.db',
        help='Path to photon vault database'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    subparsers.add_parser('bootstrap', help='Bootstrap system with photon streams')
    subparsers.add_parser('terminate', help='Terminate all systems gracefully')
    subparsers.add_parser('inspect', help='Inspect system telemetry')
    subparsers.add_parser('validate', help='Validate system integrity')
    
    inject_parser = subparsers.add_parser('inject-data', help='Inject photon stream')
    inject_parser.add_argument('--coordinate', required=True, help='Coordinate identifier')
    inject_parser.add_argument('--sector', default='custom-zone', help='Galaxy zone')
    inject_parser.add_argument('--data', required=True, help='Photon stream payload')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    bridge = NavigationBridge()
    bridge.initialize_systems(vault_path=args.storage_path)
    
    exit_code = bridge.execute_command(args.command, args)
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
