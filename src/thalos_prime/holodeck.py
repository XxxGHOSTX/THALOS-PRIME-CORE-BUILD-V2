"""
Quantum Viewport - GUI with transition matrix state machine.
Provides hyperdimensional visualization of the Thalos Prime nexus.
"""

import time
from typing import Optional, Dict, Any, List
from enum import Enum

try:
    import PySimpleGUI as sg
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

from .stargate_storage import PhotonVault
from .quantum_mind import CosmicBrain


class ViewportPhase(Enum):
    """Phases in the viewport transition matrix."""
    INITIALIZATION = "initialization"
    STANDBY = "standby"
    COMPUTE = "compute"
    QUERY_DATA = "query_data"
    SYNTHESIZE_THOUGHT = "synthesize_thought"
    ALERT_STATE = "alert_state"
    OFFLINE = "offline"


class QuantumViewport:
    """
    GUI interface with state machine for neural interaction.
    Uses PySimpleGUI for hyperdimensional viewport rendering.
    """
    
    def __init__(self, vault_path: str = "data.db"):
        if not GUI_AVAILABLE:
            raise ImportError("PySimpleGUI not available. Install: pip install PySimpleGUI")
        
        self.phase = ViewportPhase.INITIALIZATION
        self.vault = PhotonVault(vault_path=vault_path)
        self.brain = CosmicBrain()
        self.viewport_window: Optional[sg.Window] = None
        self.phase_log: List[ViewportPhase] = [self.phase]
        self.transition_matrix = self._build_transition_matrix()
    
    def _build_transition_matrix(self) -> Dict[ViewportPhase, List[ViewportPhase]]:
        """Build valid state transitions."""
        return {
            ViewportPhase.INITIALIZATION: [ViewportPhase.STANDBY],
            ViewportPhase.STANDBY: [ViewportPhase.COMPUTE, ViewportPhase.QUERY_DATA, 
                                   ViewportPhase.SYNTHESIZE_THOUGHT, ViewportPhase.OFFLINE],
            ViewportPhase.COMPUTE: [ViewportPhase.STANDBY, ViewportPhase.ALERT_STATE],
            ViewportPhase.QUERY_DATA: [ViewportPhase.STANDBY, ViewportPhase.ALERT_STATE],
            ViewportPhase.SYNTHESIZE_THOUGHT: [ViewportPhase.STANDBY, ViewportPhase.ALERT_STATE],
            ViewportPhase.ALERT_STATE: [ViewportPhase.STANDBY],
            ViewportPhase.OFFLINE: []
        }
    
    def _shift_phase(self, target_phase: ViewportPhase) -> bool:
        """Shift to target phase if transition is valid."""
        valid_transitions = self.transition_matrix.get(self.phase, [])
        
        if target_phase in valid_transitions:
            self.phase = target_phase
            self.phase_log.append(target_phase)
            if self.viewport_window:
                self.viewport_window['phase_indicator'].update(f"Phase: {target_phase.value.upper()}")
            return True
        
        return False
    
    def _forge_layout(self) -> list:
        """Forge the viewport GUI layout."""
        sg.theme('DarkTeal12')
        
        layout = [
            [sg.Text('⚡ THALOS PRIME QUANTUM VIEWPORT ⚡', 
                    font=('Courier', 18, 'bold'), 
                    justification='center',
                    expand_x=True,
                    text_color='cyan')],
            [sg.HorizontalSeparator()],
            
            [sg.Text('Phase:', size=(8, 1), font=('Courier', 10)), 
             sg.Text('INITIALIZATION', key='phase_indicator', size=(40, 1), 
                    text_color='yellow', font=('Courier', 10, 'bold'))],
            
            [sg.HorizontalSeparator()],
            
            [sg.Text('🧠 Cosmic Brain Interface', font=('Courier', 12, 'bold'),
                    text_color='lightblue')],
            [sg.Multiline(size=(75, 5), key='thought_input', 
                         font=('Courier', 9),
                         default_text='Enter thought signal for synthesis...',
                         background_color='#1a1a2e')],
            [sg.Button('Synthesize', key='btn_synthesize', button_color=('white', '#16213e')),
             sg.Button('Collapse Field', key='btn_collapse', button_color=('white', '#533483'))],
            
            [sg.HorizontalSeparator()],
            
            [sg.Text('💬 Thought Wave Output', font=('Courier', 12, 'bold'),
                    text_color='lightgreen')],
            [sg.Multiline(size=(75, 8), key='output_display', 
                         font=('Courier', 9),
                         disabled=True,
                         text_color='lightgreen',
                         background_color='#0f3460')],
            
            [sg.HorizontalSeparator()],
            
            [sg.Text('🌌 Photon Vault Operations', font=('Courier', 12, 'bold'),
                    text_color='orange')],
            [sg.Text('Coordinate:'), sg.Input(key='coord_input', size=(22, 1)),
             sg.Text('Zone:'), sg.Input(key='zone_input', size=(18, 1))],
            [sg.Text('Data Stream:'), sg.Input(key='stream_input', size=(55, 1))],
            [sg.Button('Materialize', key='btn_materialize', button_color=('white', '#005f73')),
             sg.Button('Dematerialize', key='btn_dematerialize', button_color=('white', '#0a9396')),
             sg.Button('Scan Zone', key='btn_scan', button_color=('white', '#94d2bd'))],
            
            [sg.HorizontalSeparator()],
            
            [sg.Text('📡 System Telemetry', font=('Courier', 12, 'bold'),
                    text_color='violet')],
            [sg.Multiline(size=(75, 6), key='telemetry_display',
                         font=('Courier', 8),
                         disabled=True,
                         text_color='violet',
                         background_color='#240046')],
            [sg.Button('Refresh Telemetry', key='btn_refresh', button_color=('white', '#7209b7'))],
            
            [sg.HorizontalSeparator()],
            
            [sg.Button('Exit Viewport', key='btn_exit', button_color=('white', 'darkred'),
                      size=(15, 1))]
        ]
        
        return layout
    
    def _process_synthesis(self, values: Dict[str, Any]) -> None:
        """Process thought synthesis request."""
        self._shift_phase(ViewportPhase.SYNTHESIZE_THOUGHT)
        
        thought_signal = values['thought_input'].strip()
        if not thought_signal or thought_signal == 'Enter thought signal for synthesis...':
            self.viewport_window['output_display'].update("⚠️ Please enter a valid thought signal")
            self._shift_phase(ViewportPhase.STANDBY)
            return
        
        output_signal = self.brain.synthesize(thought_signal)
        
        display_text = f"🧠 Thought Wave Response:\n{'=' * 65}\n{output_signal}\n{'=' * 65}"
        self.viewport_window['output_display'].update(display_text)
        
        self._shift_phase(ViewportPhase.STANDBY)
    
    def _process_collapse(self) -> None:
        """Process field collapse request."""
        self._shift_phase(ViewportPhase.COMPUTE)
        
        self.brain.collapse_field()
        self.viewport_window['output_display'].update("🌀 Thought field collapsed to base state")
        
        self._shift_phase(ViewportPhase.STANDBY)
    
    def _process_materialize(self, values: Dict[str, Any]) -> None:
        """Process materialize operation."""
        self._shift_phase(ViewportPhase.QUERY_DATA)
        
        nebula_coord = values['coord_input'].strip()
        galaxy_zone = values['zone_input'].strip() or 'default-zone'
        photon_stream = values['stream_input'].strip()
        
        if not nebula_coord or not photon_stream:
            self.viewport_window['output_display'].update("⚠️ Coordinate and stream required")
            self._shift_phase(ViewportPhase.STANDBY)
            return
        
        success = self.vault.materialize(nebula_coord, galaxy_zone, photon_stream.encode('utf-8'))
        
        if success:
            self.viewport_window['output_display'].update(
                f"✅ Materialized at: {nebula_coord} (zone: {galaxy_zone})"
            )
        else:
            self.viewport_window['output_display'].update(
                f"❌ Materialization failed: {nebula_coord}"
            )
        
        self._shift_phase(ViewportPhase.STANDBY)
    
    def _process_dematerialize(self, values: Dict[str, Any]) -> None:
        """Process dematerialize operation."""
        self._shift_phase(ViewportPhase.QUERY_DATA)
        
        nebula_coord = values['coord_input'].strip()
        if not nebula_coord:
            self.viewport_window['output_display'].update("⚠️ Coordinate required")
            self._shift_phase(ViewportPhase.STANDBY)
            return
        
        result = self.vault.dematerialize(nebula_coord)
        
        if result:
            zone, payload, pulse_time = result
            display_text = (f"📦 Dematerialized Photon Stream:\n"
                          f"  Zone: {zone}\n"
                          f"  Stream: {payload.decode('utf-8', errors='replace')}\n"
                          f"  Pulse: {pulse_time}")
            self.viewport_window['output_display'].update(display_text)
        else:
            self.viewport_window['output_display'].update(
                f"❌ No data at coordinate: {nebula_coord}"
            )
        
        self._shift_phase(ViewportPhase.STANDBY)
    
    def _process_scan(self, values: Dict[str, Any]) -> None:
        """Process zone scan operation."""
        self._shift_phase(ViewportPhase.QUERY_DATA)
        
        galaxy_zone = values['zone_input'].strip()
        if not galaxy_zone:
            self.viewport_window['output_display'].update("⚠️ Zone identifier required")
            self._shift_phase(ViewportPhase.STANDBY)
            return
        
        manifests = self.vault.scan_sector(galaxy_zone, horizon=10)
        
        if manifests:
            display_text = f"🔍 Zone Scan: {galaxy_zone}\n{'=' * 65}\n"
            for manifest in manifests:
                display_text += (f"  • {manifest['nebula_coord']}\n"
                               f"    Proof: {manifest['merkle_proof'][:16]}...\n"
                               f"    Event: {manifest['event_sequence']}\n\n")
            self.viewport_window['output_display'].update(display_text)
        else:
            self.viewport_window['output_display'].update(
                f"🔍 No coordinates in zone: {galaxy_zone}"
            )
        
        self._shift_phase(ViewportPhase.STANDBY)
    
    def _process_telemetry(self) -> None:
        """Process telemetry refresh."""
        vault_telemetry = self.vault.get_metrics()
        brain_diagnostics = self.brain.get_cognitive_metrics()
        
        display_text = "📡 SYSTEM TELEMETRY\n" + "=" * 68 + "\n\n"
        
        display_text += "PHOTON VAULT:\n"
        for key, value in vault_telemetry.items():
            display_text += f"  {key:.<40} {value}\n"
        
        display_text += "\nCOSMIC BRAIN:\n"
        for key, value in brain_diagnostics.items():
            display_text += f"  {key:.<40} {value}\n"
        
        self.viewport_window['telemetry_display'].update(display_text)
    
    def engage(self) -> None:
        """Engage the quantum viewport."""
        self._shift_phase(ViewportPhase.STANDBY)
        
        layout = self._forge_layout()
        self.viewport_window = sg.Window(
            'Thalos Prime Quantum Viewport',
            layout,
            finalize=True,
            resizable=True,
            size=(800, 900)
        )
        
        self._process_telemetry()
        
        while True:
            event, values = self.viewport_window.read()
            
            if event in (sg.WIN_CLOSED, 'btn_exit'):
                break
            
            elif event == 'btn_synthesize':
                self._process_synthesis(values)
            
            elif event == 'btn_collapse':
                self._process_collapse()
            
            elif event == 'btn_materialize':
                self._process_materialize(values)
            
            elif event == 'btn_dematerialize':
                self._process_dematerialize(values)
            
            elif event == 'btn_scan':
                self._process_scan(values)
            
            elif event == 'btn_refresh':
                self._process_telemetry()
        
        self._shift_phase(ViewportPhase.OFFLINE)
        self.viewport_window.close()
        self.vault.shutdown_gateway()


def launch_viewport(vault_path: str = "data.db") -> None:
    """Launch the quantum viewport interface."""
    if not GUI_AVAILABLE:
        print("❌ PySimpleGUI not installed. Install: pip install PySimpleGUI")
        return
    
    viewport = QuantumViewport(vault_path=vault_path)
    viewport.engage()


if __name__ == '__main__':
    launch_viewport()
