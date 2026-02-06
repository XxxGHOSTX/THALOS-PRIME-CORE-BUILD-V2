"""
Cosmic Brain - Probabilistic response generator with thought wave propagation.
Uses wave interference patterns for context-aware responses.
"""

import re
import time
import hashlib
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import deque


class ThoughtPattern(Enum):
    """Thought wave patterns detected in inputs."""
    SALUTATION = r"^(hello|hi|hey|greetings|ahoy)"
    DEPARTURE = r"(goodbye|bye|farewell|later|exit|quit)"
    INTERROGATIVE = r"(what|when|where|why|how|who|which|can|could|would)"
    IMPERATIVE = r"(execute|run|launch|initialize|terminate|destroy)"
    DIAGNOSTIC = r"(status|health|metrics|stats|report|check)"
    AFFIRMATION = r"^(yes|yeah|yep|correct|right|affirmative)"
    NEGATION = r"^(no|nope|nah|wrong|negative|incorrect)"


@dataclass
class ThoughtWave:
    """A thought wave in the cosmic memory field."""
    input_signal: str
    output_signal: str
    pulse_time: float
    wave_signature: str
    interference_factor: float = 1.0
    is_coherent: int = 1


class CosmicBrain:
    """
    Probabilistic cognitive engine using thought wave interference.
    Maintains resonance patterns for context-aware synthesis.
    """
    
    def __init__(self, memory_horizon: int = 800):
        self.memory_horizon = memory_horizon
        self.thought_field: deque = deque(maxlen=memory_horizon)
        self.pattern_resonance: Dict[str, float] = {
            pattern.name: 0.5 for pattern in ThoughtPattern
        }
        self.cognitive_phase = "QUIESCENT"
        self.synthesis_count = 0
        self.last_synthesis_pulse = 0.0
        self.entropy_accumulator = 0.0
    
    def _compute_wave_signature(self, signal: str) -> str:
        """Compute wave signature using spectral hash."""
        normalized = ''.join(signal.lower().split())
        spectrum = hashlib.blake2s(normalized.encode(), digest_size=12).digest()
        return ''.join(f'{b:02x}' for b in spectrum[:6])
    
    def _detect_thought_pattern(self, signal: str) -> Optional[ThoughtPattern]:
        """Detect dominant thought pattern in signal."""
        normalized_signal = signal.lower().strip()
        
        pattern_scores = []
        for pattern in ThoughtPattern:
            matches = re.findall(pattern.value, normalized_signal, re.IGNORECASE)
            if matches:
                score = len(matches) * self.pattern_resonance.get(pattern.name, 0.5)
                pattern_scores.append((score, pattern))
        
        if pattern_scores:
            pattern_scores.sort(reverse=True, key=lambda x: x[0])
            return pattern_scores[0][1]
        
        return None
    
    def _generate_interference_response(self, signal: str, 
                                       pattern: Optional[ThoughtPattern]) -> str:
        """Generate response using wave interference from memory."""
        if pattern == ThoughtPattern.SALUTATION:
            variants = [
                "Cosmic Brain interface active. Thought waves aligned.",
                "Greetings, consciousness. Neural pathways synchronized.",
                "Hello! Quantum coherence established. Ready to process."
            ]
            idx = int(self.synthesis_count * self.entropy_accumulator) % len(variants)
            return variants[idx]
        
        elif pattern == ThoughtPattern.DEPARTURE:
            return "Departing thought streams. May your neural pathways remain coherent."
        
        elif pattern == ThoughtPattern.DIAGNOSTIC:
            return (f"Cognitive Phase: {self.cognitive_phase} | "
                   f"Thought Waves: {len(self.thought_field)} | "
                   f"Synthesis Count: {self.synthesis_count} | "
                   f"Entropy: {self.entropy_accumulator:.4f}")
        
        elif pattern == ThoughtPattern.INTERROGATIVE:
            recent_signatures = self._extract_recent_signatures(5)
            if recent_signatures:
                interference_map = " ".join(recent_signatures[:3])
                return (f"Query detected. Analyzing wave interference patterns... "
                       f"Signatures: [{interference_map}]. "
                       f"Coherence probability: {self._compute_coherence():.2%}")
            return "Query acknowledged. Initiating spectral analysis across thought dimensions."
        
        elif pattern == ThoughtPattern.IMPERATIVE:
            return "Command wave received. Configuring execution manifold."
        
        elif pattern == ThoughtPattern.AFFIRMATION:
            return "Affirmative signal detected. Maintaining current trajectory."
        
        elif pattern == ThoughtPattern.NEGATION:
            return "Negative interference noted. Recalibrating thought vectors."
        
        else:
            return self._generate_probabilistic_response(signal)
    
    def _generate_probabilistic_response(self, signal: str) -> str:
        """Generate probabilistic response based on wave mechanics."""
        token_count = len(signal.split())
        
        wave_amplitude = math.sin(self.synthesis_count * 0.1) * 0.5 + 0.5
        
        if token_count < 3:
            return "Minimal wave amplitude. Please amplify input signal for coherent synthesis."
        
        elif token_count < 12:
            harmonic_idx = int(wave_amplitude * 7) + 1
            return (f"Signal received. Wave interference suggests {harmonic_idx} "
                   f"dimensional correlations. Entropy factor: {self.entropy_accumulator:.3f}")
        
        else:
            wave_depth = len(self.thought_field)
            return (f"Complex wave pattern analyzed. Propagating through {wave_depth} "
                   f"thought layers. Coherence maintained at {self._compute_coherence():.1%}. "
                   f"Phase alignment nominal.")
    
    def _extract_recent_signatures(self, count: int = 8) -> List[str]:
        """Extract recent wave signatures from thought field."""
        recent_waves = list(self.thought_field)[-count:] if self.thought_field else []
        return [wave.wave_signature for wave in recent_waves]
    
    def _compute_coherence(self) -> float:
        """Compute quantum coherence of thought field."""
        if not self.thought_field:
            return 1.0
        
        coherent_count = sum(1 for wave in self.thought_field if wave.is_coherent)
        return coherent_count / len(self.thought_field)
    
    def _update_entropy(self, signal: str) -> None:
        """Update entropy accumulator based on signal complexity."""
        unique_chars = len(set(signal.lower()))
        total_chars = len(signal)
        
        if total_chars > 0:
            signal_entropy = unique_chars / total_chars
            self.entropy_accumulator = (self.entropy_accumulator * 0.9) + (signal_entropy * 0.1)
    
    def synthesize(self, input_signal: str) -> str:
        """
        Synthesize response through thought wave propagation.
        
        Args:
            input_signal: Input to process
            
        Returns:
            Synthesized output signal
        """
        if not input_signal or not input_signal.strip():
            return "Empty signal detected. Cannot propagate thought waves through vacuum."
        
        self.cognitive_phase = "SYNTHESIZING"
        
        pattern = self._detect_thought_pattern(input_signal)
        output_signal = self._generate_interference_response(input_signal, pattern)
        
        wave_sig = self._compute_wave_signature(input_signal)
        pulse_time = time.time()
        
        interference = self._compute_coherence()
        
        wave = ThoughtWave(
            input_signal=input_signal,
            output_signal=output_signal,
            pulse_time=pulse_time,
            wave_signature=wave_sig,
            interference_factor=interference
        )
        
        self.thought_field.append(wave)
        
        self._update_entropy(input_signal)
        
        if pattern:
            old_resonance = self.pattern_resonance.get(pattern.name, 0.5)
            self.pattern_resonance[pattern.name] = min(1.0, old_resonance + 0.05)
        
        self.synthesis_count += 1
        self.last_synthesis_pulse = pulse_time
        self.cognitive_phase = "QUIESCENT"
        
        return output_signal
    
    def recall_waves(self, count: int = 12) -> List[Dict[str, Any]]:
        """
        Recall recent thought waves.
        
        Args:
            count: Number of waves to recall
            
        Returns:
            List of wave manifests
        """
        recent_waves = list(self.thought_field)[-count:] if self.thought_field else []
        return [
            {
                'input_signal': wave.input_signal,
                'output_signal': wave.output_signal,
                'pulse_time': wave.pulse_time,
                'wave_signature': wave.wave_signature,
                'interference_factor': wave.interference_factor
            }
            for wave in recent_waves
        ]
    
    def collapse_field(self) -> None:
        """Collapse entire thought field."""
        self.thought_field.clear()
        self.synthesis_count = 0
        self.entropy_accumulator = 0.0
        self.cognitive_phase = "COLLAPSED"
    
    def get_cognitive_metrics(self) -> Dict[str, Any]:
        """Retrieve cognitive telemetry."""
        return {
            'cognitive_phase': self.cognitive_phase,
            'thought_waves': len(self.thought_field),
            'synthesis_count': self.synthesis_count,
            'last_synthesis_pulse': self.last_synthesis_pulse,
            'memory_horizon': self.memory_horizon,
            'quantum_coherence': self._compute_coherence(),
            'entropy_level': self.entropy_accumulator
        }
    
    def modulate_resonance(self, pattern_name: str, resonance_value: float) -> bool:
        """
        Modulate pattern resonance frequency.
        
        Args:
            pattern_name: Pattern identifier
            resonance_value: New resonance (0.0 to 1.0)
            
        Returns:
            True if modulation succeeded
        """
        if pattern_name in self.pattern_resonance and 0.0 <= resonance_value <= 1.0:
            self.pattern_resonance[pattern_name] = resonance_value
            return True
        return False
