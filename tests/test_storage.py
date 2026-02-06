"""Test suite for Photon Vault storage system"""
import pytest
import tempfile
import os
from pathlib import Path

from thalos_prime.stargate_storage import PhotonVault


@pytest.fixture
def temp_vault_path():
    """Create temporary vault storage"""
    fd, path = tempfile.mkstemp(suffix='.photon.db')
    os.close(fd)
    yield path
    for ext in ['', '-wal', '-shm']:
        p = path + ext
        if Path(p).exists():
            os.unlink(p)


def test_vault_materialize(temp_vault_path):
    """Test vault materialization"""
    vault = PhotonVault(temp_vault_path)
    vault.materialize()
    assert Path(temp_vault_path).exists()
    vault.collapse()


def test_photon_inscription_and_retrieval(temp_vault_path):
    """Test writing and reading photons"""
    vault = PhotonVault(temp_vault_path)
    vault.materialize()
    
    vault.inscribe_photon("coordinate:alpha", "quantum_data")
    data = vault.retrieve_photon("coordinate:alpha")
    
    assert data == "quantum_data"
    vault.collapse()


def test_retrieve_void_coordinate(temp_vault_path):
    """Test reading non-existent coordinate"""
    vault = PhotonVault(temp_vault_path)
    vault.materialize()
    
    data = vault.retrieve_photon("void:coordinate")
    assert data is None
    
    vault.collapse()


def test_photon_mutation(temp_vault_path):
    """Test updating photon data"""
    vault = PhotonVault(temp_vault_path)
    vault.materialize()
    
    vault.inscribe_photon("mutable:photon", "initial_state")
    assert vault.retrieve_photon("mutable:photon") == "initial_state"
    
    vault.inscribe_photon("mutable:photon", "evolved_state")
    assert vault.retrieve_photon("mutable:photon") == "evolved_state"
    
    vault.collapse()


def test_photon_annihilation(temp_vault_path):
    """Test photon deletion"""
    vault = PhotonVault(temp_vault_path)
    vault.materialize()
    
    vault.inscribe_photon("ephemeral:photon", "temporary")
    assert vault.retrieve_photon("ephemeral:photon") == "temporary"
    
    result = vault.annihilate_photon("ephemeral:photon")
    assert result is True
    assert vault.retrieve_photon("ephemeral:photon") is None
    
    vault.collapse()


def test_sector_traversal(temp_vault_path):
    """Test scanning photon sectors"""
    vault = PhotonVault(temp_vault_path)
    vault.materialize()
    
    vault.inscribe_photon("sector:alpha:1", "data1")
    vault.inscribe_photon("sector:alpha:2", "data2")
    vault.inscribe_photon("sector:beta:1", "data3")
    
    alpha_photons = vault.traverse_sector("sector:alpha:")
    assert len(alpha_photons) == 2
    
    vault.collapse()


def test_persistence_across_sessions(temp_vault_path):
    """Test data persists after collapse"""
    vault1 = PhotonVault(temp_vault_path)
    vault1.materialize()
    vault1.inscribe_photon("persistent:data", "eternal")
    vault1.collapse()
    
    vault2 = PhotonVault(temp_vault_path)
    vault2.materialize()
    data = vault2.retrieve_photon("persistent:data")
    assert data == "eternal"
    vault2.collapse()


def test_wal_journaling_enabled(temp_vault_path):
    """Test WAL mode activation"""
    vault = PhotonVault(temp_vault_path)
    vault.materialize()
    
    cursor = vault.nexus_gate.execute("PRAGMA journal_mode")
    mode = cursor.fetchone()[0]
    assert mode.upper() == "WAL"
    
    vault.collapse()


def test_unmaterialized_access(temp_vault_path):
    """Test operations fail before materialization"""
    vault = PhotonVault(temp_vault_path)
    
    with pytest.raises(RuntimeError):
        vault.retrieve_photon("test")
    
    with pytest.raises(RuntimeError):
        vault.inscribe_photon("test", "data")
