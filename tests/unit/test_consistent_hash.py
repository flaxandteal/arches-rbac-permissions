"""Unit tests for the deterministic set-id hashing used by the set applicator.

``_consistent_hash`` turns an arbitrary string (e.g. a set/rule identifier) into
a stable UUID so the same logical set always lands on the same Elasticsearch
document id across recalculations.
"""

import hashlib
import uuid

from arches_inclusion_rule.utils.es_set_applicator import _consistent_hash


def test_returns_a_uuid():
    assert isinstance(_consistent_hash("anything"), uuid.UUID)


def test_is_deterministic():
    title = "Malazan Book of the Fallen"
    assert _consistent_hash(title) == _consistent_hash(title)


def test_distinct_inputs_give_distinct_uuids():
    assert _consistent_hash("Steven Erikson") != _consistent_hash("Ian C. Esslemont")


def test_handles_unicode():
    # encode("utf-8") must not raise on non-ASCII input
    assert isinstance(_consistent_hash("Cód — Cliant"), uuid.UUID)


def test_matches_sha256_every_other_hex_char_contract():
    # Lock the derivation: UUID built from every other char of the sha256 hexdigest.
    value = "rbac"
    expected = uuid.UUID(hashlib.sha256(value.encode("utf-8")).hexdigest()[::2])
    assert _consistent_hash(value) == expected
