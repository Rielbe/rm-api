from src.db import db_available
from src.cache import cache_available

def test_avaiable_status():
    assert isinstance(db_available(), bool)

def test_cache_available():
    assert isinstance(cache_available(), bool)
