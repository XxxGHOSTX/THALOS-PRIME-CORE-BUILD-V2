"""
Photon Vault - Event-sourced storage with Merkle verification chains.
Uses crystalline frequency-based caching instead of standard LRU.
"""

import sqlite3
import threading
import struct
import zlib
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
from pathlib import Path
import time
import hashlib


class CrystallineCache:
    """
    Frequency-based cache using resonance scoring.
    Items accessed more recently AND frequently get higher scores.
    """
    
    def __init__(self, max_photons: int = 512):
        self.max_photons = max_photons
        self.photon_chamber: Dict[str, bytes] = {}
        self.resonance_freq: Dict[str, int] = defaultdict(int)
        self.last_pulse: Dict[str, float] = {}
        self.mutex = threading.Lock()
        self.total_queries = 0
        self.photon_hits = 0
    
    def beam_in(self, nebula_key: str, photon_data: bytes) -> None:
        """Store data in crystalline matrix with resonance tracking."""
        with self.mutex:
            current_pulse = time.time()
            
            if nebula_key in self.photon_chamber:
                self.resonance_freq[nebula_key] += 1
                self.last_pulse[nebula_key] = current_pulse
                self.photon_chamber[nebula_key] = photon_data
                return
            
            if len(self.photon_chamber) >= self.max_photons:
                victim_key = self._find_lowest_resonance()
                if victim_key:
                    del self.photon_chamber[victim_key]
                    del self.resonance_freq[victim_key]
                    del self.last_pulse[victim_key]
            
            self.photon_chamber[nebula_key] = photon_data
            self.resonance_freq[nebula_key] = 1
            self.last_pulse[nebula_key] = current_pulse
    
    def beam_out(self, nebula_key: str) -> Optional[bytes]:
        """Retrieve data and update resonance frequency."""
        with self.mutex:
            self.total_queries += 1
            
            if nebula_key in self.photon_chamber:
                self.photon_hits += 1
                self.resonance_freq[nebula_key] += 1
                self.last_pulse[nebula_key] = time.time()
                return self.photon_chamber[nebula_key]
            
            return None
    
    def _find_lowest_resonance(self) -> Optional[str]:
        """Find key with lowest resonance score (freq * recency)."""
        if not self.photon_chamber:
            return None
        
        current_time = time.time()
        min_score = float('inf')
        victim = None
        
        for key in self.photon_chamber:
            age = current_time - self.last_pulse[key]
            recency_factor = 1.0 / (1.0 + age)
            score = self.resonance_freq[key] * recency_factor
            
            if score < min_score:
                min_score = score
                victim = key
        
        return victim
    
    def collapse_all(self) -> None:
        """Collapse all photonic states."""
        with self.mutex:
            self.photon_chamber.clear()
            self.resonance_freq.clear()
            self.last_pulse.clear()
    
    def efficiency_quotient(self) -> float:
        """Calculate photon hit efficiency."""
        return self.photon_hits / self.total_queries if self.total_queries > 0 else 0.0


class MerkleChainBuilder:
    """Build Merkle-style verification chains for data integrity."""
    
    @staticmethod
    def compute_merkle_root(data_chunks: List[bytes]) -> str:
        """Compute Merkle root from data chunks."""
        if not data_chunks:
            return hashlib.sha256(b"empty").hexdigest()
        
        current_level = [hashlib.sha256(chunk).digest() for chunk in data_chunks]
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                else:
                    combined = current_level[i] + current_level[i]
                next_level.append(hashlib.sha256(combined).digest())
            current_level = next_level
        
        return current_level[0].hex()
    
    @staticmethod
    def encode_photon_packet(data: bytes, compression: bool = True) -> bytes:
        """Encode data into photon packet with custom header."""
        if compression:
            compressed = zlib.compress(data, level=6)
            header = struct.pack('!BIH', 1, len(data), len(compressed))
            return header + compressed
        else:
            header = struct.pack('!BIH', 0, len(data), len(data))
            return header + data
    
    @staticmethod
    def decode_photon_packet(packet: bytes) -> bytes:
        """Decode photon packet."""
        header_size = struct.calcsize('!BIH')
        if len(packet) < header_size:
            raise ValueError("Invalid photon packet")
        
        compressed_flag, original_size, packet_size = struct.unpack('!BIH', packet[:header_size])
        payload = packet[header_size:]
        
        if compressed_flag == 1:
            return zlib.decompress(payload)
        return payload


class PhotonVault:
    """
    Event-sourced SQLite vault with Merkle verification.
    Uses custom photon encoding and crystalline caching.
    """
    
    def __init__(self, vault_path: str = "data.db", cache_size: int = 512):
        self.vault_path = Path(vault_path)
        self.crystal_cache = CrystallineCache(max_photons=cache_size)
        self.merkle_builder = MerkleChainBuilder()
        self.thread_pool = threading.local()
        self.event_counter = 0
        self.counter_lock = threading.Lock()
        self._forge_vault()
    
    def _forge_vault(self) -> None:
        """Forge the photon vault schema."""
        conn = self._acquire_conduit()
        
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS photon_ledger (
                event_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                nebula_coord TEXT NOT NULL,
                galaxy_zone TEXT NOT NULL,
                photon_packet BLOB NOT NULL,
                merkle_proof TEXT NOT NULL,
                pulse_timestamp REAL NOT NULL,
                event_type TEXT DEFAULT 'MATERIALIZE',
                is_active INTEGER DEFAULT 1,
                UNIQUE(nebula_coord, event_sequence)
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_galaxy_traverse 
            ON photon_ledger(galaxy_zone, pulse_timestamp DESC, is_active)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_stream
            ON photon_ledger(event_sequence, is_active)
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS integrity_beacon (
                beacon_id INTEGER PRIMARY KEY AUTOINCREMENT,
                merkle_root TEXT NOT NULL,
                event_batch_start INTEGER NOT NULL,
                event_batch_end INTEGER NOT NULL,
                beacon_timestamp REAL NOT NULL
            )
        """)
        
        conn.commit()
    
    def _acquire_conduit(self) -> sqlite3.Connection:
        """Acquire thread-local database conduit."""
        if not hasattr(self.thread_pool, 'conduit'):
            self.thread_pool.conduit = sqlite3.connect(
                self.vault_path,
                check_same_thread=False,
                isolation_level=None,
                timeout=45.0
            )
        return self.thread_pool.conduit
    
    def materialize(self, nebula_coord: str, galaxy_zone: str, payload: bytes) -> bool:
        """
        Materialize photonic data into vault with event sourcing.
        
        Args:
            nebula_coord: Unique coordinate identifier
            galaxy_zone: Zone classification
            payload: Raw binary payload
            
        Returns:
            True if materialization succeeded
        """
        try:
            encoded_packet = self.merkle_builder.encode_photon_packet(payload, compression=True)
            
            chunks = [payload[i:i+256] for i in range(0, len(payload), 256)]
            merkle_proof = self.merkle_builder.compute_merkle_root(chunks)
            
            pulse_time = time.time()
            
            conduit = self._acquire_conduit()
            
            conduit.execute("BEGIN IMMEDIATE")
            
            conduit.execute("""
                UPDATE photon_ledger 
                SET is_active = 0 
                WHERE nebula_coord = ? AND is_active = 1
            """, (nebula_coord,))
            
            conduit.execute("""
                INSERT INTO photon_ledger 
                (nebula_coord, galaxy_zone, photon_packet, merkle_proof, 
                 pulse_timestamp, event_type, is_active)
                VALUES (?, ?, ?, ?, ?, 'MATERIALIZE', 1)
            """, (nebula_coord, galaxy_zone, encoded_packet, merkle_proof, pulse_time))
            
            conduit.execute("COMMIT")
            
            self.crystal_cache.beam_in(nebula_coord, payload)
            
            with self.counter_lock:
                self.event_counter += 1
            
            return True
            
        except Exception as e:
            conduit.execute("ROLLBACK")
            return False
    
    def dematerialize(self, nebula_coord: str) -> Optional[Tuple[str, bytes, float]]:
        """
        Dematerialize photonic data from vault.
        
        Returns:
            Tuple of (galaxy_zone, payload, pulse_timestamp) or None
        """
        cached = self.crystal_cache.beam_out(nebula_coord)
        if cached is not None:
            conduit = self._acquire_conduit()
            cursor = conduit.execute("""
                SELECT galaxy_zone, pulse_timestamp
                FROM photon_ledger
                WHERE nebula_coord = ? AND is_active = 1
                ORDER BY event_sequence DESC LIMIT 1
            """, (nebula_coord,))
            row = cursor.fetchone()
            if row:
                return (row[0], cached, row[1])
        
        conduit = self._acquire_conduit()
        cursor = conduit.execute("""
            SELECT galaxy_zone, photon_packet, pulse_timestamp
            FROM photon_ledger
            WHERE nebula_coord = ? AND is_active = 1
            ORDER BY event_sequence DESC LIMIT 1
        """, (nebula_coord,))
        
        row = cursor.fetchone()
        if row:
            galaxy_zone, encoded_packet, pulse_time = row
            payload = self.merkle_builder.decode_photon_packet(encoded_packet)
            
            self.crystal_cache.beam_in(nebula_coord, payload)
            
            return (galaxy_zone, payload, pulse_time)
        
        return None
    
    def scan_sector(self, galaxy_zone: str, horizon: int = 100) -> List[Dict[str, Any]]:
        """
        Scan all coordinates in a galaxy zone.
        
        Args:
            galaxy_zone: Zone identifier
            horizon: Maximum results
            
        Returns:
            List of coordinate manifests
        """
        conduit = self._acquire_conduit()
        cursor = conduit.execute("""
            SELECT nebula_coord, pulse_timestamp, merkle_proof, event_sequence
            FROM photon_ledger
            WHERE galaxy_zone = ? AND is_active = 1
            ORDER BY pulse_timestamp DESC
            LIMIT ?
        """, (galaxy_zone, horizon))
        
        manifests = []
        for row in cursor.fetchall():
            manifests.append({
                'nebula_coord': row[0],
                'pulse_timestamp': row[1],
                'merkle_proof': row[2],
                'event_sequence': row[3]
            })
        
        return manifests
    
    def purge_coordinate(self, nebula_coord: str) -> bool:
        """
        Purge coordinate from active state (event-sourced soft delete).
        
        Args:
            nebula_coord: Coordinate to purge
            
        Returns:
            True if purged
        """
        conduit = self._acquire_conduit()
        pulse_time = time.time()
        
        try:
            conduit.execute("BEGIN IMMEDIATE")
            
            conduit.execute("""
                UPDATE photon_ledger 
                SET is_active = 0
                WHERE nebula_coord = ? AND is_active = 1
            """, (nebula_coord,))
            
            conduit.execute("""
                INSERT INTO photon_ledger 
                (nebula_coord, galaxy_zone, photon_packet, merkle_proof,
                 pulse_timestamp, event_type, is_active)
                SELECT nebula_coord, galaxy_zone, X'00', '', ?, 'PURGE', 0
                FROM photon_ledger
                WHERE nebula_coord = ?
                LIMIT 1
            """, (pulse_time, nebula_coord))
            
            conduit.execute("COMMIT")
            
            return True
        except Exception:
            conduit.execute("ROLLBACK")
            return False
    
    def traverse(self, start_pulse: float = 0.0, end_pulse: Optional[float] = None,
                 active_filter: bool = True) -> List[Dict[str, Any]]:
        """
        Traverse photon ledger across temporal dimension.
        
        Args:
            start_pulse: Starting timestamp
            end_pulse: Ending timestamp (None = now)
            active_filter: Only return active entries
            
        Returns:
            List of traversed photon records
        """
        if end_pulse is None:
            end_pulse = time.time()
        
        conduit = self._acquire_conduit()
        
        query = """
            SELECT nebula_coord, galaxy_zone, pulse_timestamp, 
                   merkle_proof, event_type, is_active
            FROM photon_ledger
            WHERE pulse_timestamp BETWEEN ? AND ?
        """
        
        params = [start_pulse, end_pulse]
        
        if active_filter:
            query += " AND is_active = 1"
        
        query += " ORDER BY pulse_timestamp ASC"
        
        cursor = conduit.execute(query, params)
        
        journey = []
        for row in cursor.fetchall():
            journey.append({
                'nebula_coord': row[0],
                'galaxy_zone': row[1],
                'pulse_timestamp': row[2],
                'merkle_proof': row[3],
                'event_type': row[4],
                'is_active': row[5]
            })
        
        return journey
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retrieve vault telemetry."""
        conduit = self._acquire_conduit()
        
        cursor = conduit.execute("""
            SELECT 
                COUNT(DISTINCT nebula_coord) as total_coords,
                COUNT(DISTINCT CASE WHEN is_active = 1 THEN nebula_coord END) as active_coords,
                COUNT(DISTINCT galaxy_zone) as zone_count,
                COUNT(*) as total_events
            FROM photon_ledger
        """)
        
        row = cursor.fetchone()
        
        return {
            'total_coordinates': row[0],
            'active_coordinates': row[1],
            'galaxy_zones': row[2],
            'total_events': row[3],
            'photon_efficiency': self.crystal_cache.efficiency_quotient(),
            'cache_hits': self.crystal_cache.photon_hits,
            'cache_queries': self.crystal_cache.total_queries
        }
    
    def shutdown_gateway(self) -> None:
        """Shutdown vault conduit."""
        if hasattr(self.thread_pool, 'conduit'):
            self.thread_pool.conduit.close()
        self.crystal_cache.collapse_all()
