"""Simple test suite"""
import unittest as ut
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from synapse_matrix.bio_synthesizer import BioSynthesizer
from cognition_store.persistence import CognitionVault


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


if __name__ == '__main__':
    ut.main()
