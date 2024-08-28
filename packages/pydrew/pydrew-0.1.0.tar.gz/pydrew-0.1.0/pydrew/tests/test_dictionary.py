import pytest
from typing import Dict

from pydrew.modules.dictionary import Dictionary


class TestDictionary:

    def test_initialization(self) -> None:
        # Test initialization with no data
        d: Dictionary[str, int] = Dictionary()
        assert d.to_dict() == {}

        # Test initialization with some data
        data: Dict[str, int] = {'a': 1, 'b': 2}
        d = Dictionary(data)
        assert d.to_dict() == data

    def test_add(self) -> None:
        d: Dictionary[str, int] = Dictionary()
        d.add('a', 1)
        assert d.to_dict() == {'a': 1}

    def test_remove(self) -> None:
        d: Dictionary[str, int] = Dictionary({'a': 1})
        value = d.remove('a')
        assert value == 1
        assert d.to_dict() == {}

        # Test that removing a non-existent key raises a KeyError
        with pytest.raises(KeyError):
            d.remove('b')

    def test_at_key(self) -> None:
        d: Dictionary[str, int] = Dictionary({'a': 1, 'b': 2})
        assert d.at_key('a') == 1
        assert d.at_key('b') == 2

        # Test accessing a non-existent key raises a KeyError
        with pytest.raises(KeyError):
            d.at_key('c')

    def test_keys(self) -> None:
        d: Dictionary[str, int] = Dictionary({'a': 1, 'b': 2})
        assert set(d.keys()) == {'a', 'b'}

    def test_values(self) -> None:
        d: Dictionary[str, int] = Dictionary({'a': 1, 'b': 2})
        assert set(d.values()) == {1, 2}

    def test_magic_methods(self) -> None:
        d: Dictionary[str, int] = Dictionary()

        # Test __setitem__ and __getitem__
        d['a'] = 1
        assert d['a'] == 1

        # Test __bool__
        assert bool(d) is True
        d.remove('a')
        assert bool(d) is False
