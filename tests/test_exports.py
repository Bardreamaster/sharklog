import collections

import sharklog


def test_star_import_works():
    namespace = {}
    exec("from sharklog import *", namespace)
    for name in sharklog.__all__:
        assert name in namespace


def test_all_names_exist_and_are_unique():
    missing = [name for name in sharklog.__all__ if not hasattr(sharklog, name)]
    assert missing == []
    duplicates = [n for n, c in collections.Counter(sharklog.__all__).items() if c > 1]
    assert duplicates == []
