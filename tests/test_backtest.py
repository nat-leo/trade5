import pytest
from src.main import printf

def test_printf():
    assert printf(5) == 6