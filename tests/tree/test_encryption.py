import pytest
import os
import json
from pymerkle import MerkleTree
from pymerkle.hashing import HashEngine, SUPPORTED_ALGORITHMS

from tests.conftest import option, resolve_encodings


trees_engines = []
for security in (True, False):
    for algorithm in SUPPORTED_ALGORITHMS:
        for encoding in resolve_encodings(option):
            config = {'algorithm': algorithm, 'encoding': encoding,
                      'security': security}

            trees_engines.append(
                (
                    MerkleTree(**config),
                    HashEngine(**config),
                )
            )


records = []
for tree, engine in trees_engines:
    records.extend(
        [
            (tree, engine, 'record'),
            (tree, engine, 'record'.encode(tree.encoding))
        ]
    )


files = os.path.dirname(os.path.dirname(__file__))


@pytest.mark.parametrize('tree, engine, record', records)
def test_encrypt(tree, engine, record):
    tree.encrypt(record)
    assert tree.get_tail().digest == engine.hash_record(record)


@pytest.mark.parametrize('tree, engine', trees_engines)
def test_encrypt_file_content(tree, engine):
    logfile = os.path.join(files, 'logdata/large_APACHE_log')
    tree.encrypt_file_content(logfile)
    with open(logfile, 'rb') as f:
        content = f.read()
    assert tree.get_tail().digest == engine.hash_record(content)


@pytest.mark.parametrize('tree', [tree for tree, _ in trees_engines])
def test_encrypt_file_per_line(tree):
    tree = MerkleTree(**tree.get_config())
    logfile = os.path.join(files, 'logdata/short_APACHE_log')
    tree.encrypt_file_per_line(logfile)
    records = []
    with open(logfile, 'rb') as f:
        for line in f:
            records.append(line)
    clone = MerkleTree.init_from_records(*records,
                                         config=tree.get_config())
    assert tree.get_root_hash() == clone.get_root_hash()
