# Copyright 2024 Liant SASU
#
# License: MIT
# See: LICENSE file at root of the repository
#
# Author: Roland Laurès <roland@liant.dev>
"""
Test file for storage module
"""

from pathlib import Path
from typing import Literal, Union
import pytest
from actioncable_client.storage import Storage

# Test initialization
def test_init_without_location():
    obj = Storage()
    assert obj.location.is_absolute()
    assert obj.location == Path.home() / '.actioncable_client'

def test_init_with_valid_location(tmp_path: Path):
    obj = Storage(tmp_path)
    assert obj.location.is_absolute()
    assert obj.location == tmp_path

def test_init_with_valid_location_not_existing(tmp_path: Path):
    path = tmp_path / 'doesntexist'
    obj = Storage(path)
    assert obj.location.is_absolute()
    assert obj.location == path

# Test Save method
@pytest.fixture
def storage(tmp_path: Path):
    return Storage(tmp_path)

@pytest.fixture
def obj() -> dict:
    return {
        'grant_type': "urn:ietf:params:oauth:grant-type:device_code",
        'device_code': '0123456789ABCDF',
        'client_id': 'ABCDEF-0123-GHIJKL-45678',
        'scope': 'user,api'
    }

def test_save_without_filedest(storage: Storage, tmp_path: Path, obj: dict):
    storage.save(obj)
    assert (tmp_path / 'dict.bin').exists()

@pytest.mark.parametrize("filedest", [Path('toto'), 'toto'])
def test_save_with_filedest_not_absolute(storage: Storage, tmp_path: Path, filedest: Union[Path, Literal['toto']], obj: dict):
    file_path = tmp_path / f"{filedest}.bin"
    assert not file_path.exists()
    storage.save(obj, filedest)
    assert file_path.exists()

@pytest.mark.parametrize("filedest", [Path('toto'), 'toto'])
def test_save_with_filedest_absolute(storage: Storage, tmp_path: Path, filedest: Union[Path, Literal['toto']], obj: dict):
    file_path = (tmp_path / f"{filedest}").absolute()
    file_path_with_suffix = file_path.with_suffix('.bin')
    assert not file_path_with_suffix.exists()
    storage.save(obj, file_path)
    assert file_path_with_suffix.exists()

# Test Load method
@pytest.fixture
def saved_object(storage: Storage, tmp_path: Path, obj: dict) -> Union[dict, list[dict]]:
    storage.save(obj)
    return obj

@pytest.mark.parametrize("filedest", ['dict', 'dict.bin', Path('dict'), Path('dict.bin')])
def test_load(storage: Storage, saved_object: dict, filedest: Union[Path, Literal['dict'], Literal['dict.bin']]):
    obj_read = storage.load(filedest)
    assert obj_read == saved_object
