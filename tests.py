"""Simple test suite"""
import unittest as ut
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from synapse_matrix.bio_synthesizer import BioSynthesizer
from cognition_store.persistence import CognitionVault
from lob_db.loader import LoBLoader
from src.matrix_codex import MatrixCodex


class BasicTests(ut.TestCase):
    
    def test_bio_init(self):
        bio = BioSynthesizer(1000000)
        self.assertGreater(bio.param_total, 0)
        
    def test_bio_query(self):
        bio = BioSynthesizer(1000000)
        resp = bio.infer_query("test")
        self.assertIn('answer', resp)
        self.assertGreater(resp['certainty'], 0)
        
    def test_memory(self):
        mem = CognitionVault("test.db")
        ex_id = mem.archive_exchange("q", {'answer': 'a', 'certainty': 0.8})
        self.assertIsNotNone(ex_id)
        
        recent = mem.recall_recent(5)
        self.assertGreater(len(recent), 0)
        
        os.remove("test.db")


class MindInterfaceTests(ut.TestCase):
    
    def test_lob_loader_shard(self):
        loader = LoBLoader()
        shard = loader.get_shard("hello")
        self.assertIn("__shard_id", shard)
        self.assertGreater(len(shard.get("entries", [])), 0)
    
    def test_matrix_codex_forward(self):
        codex = MatrixCodex()
        result = codex.forward({"text": "hello", "context": {}})
        self.assertIn("certainty", result)
        self.assertIn("coherence", result)


if __name__ == '__main__':
    ut.main()
