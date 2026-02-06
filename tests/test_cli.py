"""Test suite for Navigation Bridge CLI"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from argparse import Namespace

from thalos_prime.command_deck import command_inspect, command_inject_data, main


@pytest.fixture
def temp_photon_db():
    """Create temp photon vault"""
    fd, path = tempfile.mkstemp(suffix='.photon.db')
    os.close(fd)
    yield path
    for ext in ['', '-wal', '-shm']:
        p = path + ext
        if Path(p).exists():
            os.unlink(p)


@pytest.fixture
def temp_data_file():
    """Create temp JSON file"""
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    if Path(path).exists():
        os.unlink(path)


def test_main_no_args():
    """Test CLI without arguments"""
    result = main([])
    assert result == 1


def test_main_help():
    """Test help display"""
    with pytest.raises(SystemExit) as exc:
        main(['--help'])
    assert exc.value.code == 0


def test_inspect_missing_vault():
    """Test inspect with non-existent vault"""
    args = Namespace(vault_path="/tmp/nonexistent_photon_vault_xyz.db")
    
    result = command_inspect(args)
    assert result == 1


def test_inspect_existing_vault(temp_photon_db):
    """Test inspect with existing vault"""
    from thalos_prime.stargate_storage import PhotonVault
    
    vault = PhotonVault(temp_photon_db)
    vault.materialize()
    vault.inscribe_photon("system:state", "operational")
    vault.collapse()
    
    args = Namespace(vault_path=temp_photon_db)
    result = command_inspect(args)
    assert result == 0


def test_inject_missing_file():
    """Test inject with missing source file"""
    args = Namespace(
        source_file="/tmp/missing_quantum_data_xyz.json",
        vault_path=":memory:"
    )
    
    result = command_inject_data(args)
    assert result == 1


def test_inject_invalid_json(temp_data_file):
    """Test inject with malformed JSON"""
    with open(temp_data_file, 'w') as f:
        f.write("{ invalid json structure")
    
    args = Namespace(source_file=temp_data_file, vault_path=":memory:")
    result = command_inject_data(args)
    assert result == 1


def test_inject_non_dict_json(temp_data_file):
    """Test inject with non-dictionary JSON"""
    with open(temp_data_file, 'w') as f:
        json.dump(["array", "data"], f)
    
    args = Namespace(source_file=temp_data_file, vault_path=":memory:")
    result = command_inject_data(args)
    assert result == 1


def test_inject_success(temp_data_file, temp_photon_db):
    """Test successful data injection"""
    from thalos_prime.stargate_storage import PhotonVault
    
    photon_data = {
        "coord:1": "value1",
        "coord:2": "value2",
        "coord:3": 999
    }
    with open(temp_data_file, 'w') as f:
        json.dump(photon_data, f)
    
    args = Namespace(source_file=temp_data_file, vault_path=temp_photon_db)
    result = command_inject_data(args)
    assert result == 0
    
    vault = PhotonVault(temp_photon_db)
    vault.materialize()
    assert vault.retrieve_photon("coord:1") == "value1"
    assert vault.retrieve_photon("coord:3") == "999"
    vault.collapse()


def test_bootstrap_help():
    """Test bootstrap command help"""
    with pytest.raises(SystemExit):
        main(['bootstrap', '--help'])


def test_inspect_help():
    """Test inspect command help"""
    with pytest.raises(SystemExit):
        main(['inspect', '--help'])


def test_inject_help():
    """Test inject-data command help"""
    with pytest.raises(SystemExit):
        main(['inject-data', '--help'])
