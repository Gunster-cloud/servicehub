from datetime import datetime
from types import SimpleNamespace

import pytest

from servicehub.utils import signals
from servicehub.apps.quotes.models import Proposal, Quote
from servicehub.apps.services.models import ServiceOrder


class _DummyQuerySet:
    def __init__(self, existing, identifier):
        self._existing = existing
        self._identifier = identifier

    def exists(self):
        return self._identifier in self._existing


class _DummyManager:
    def __init__(self, existing=None):
        self._existing = existing or set()

    def filter(self, **kwargs):
        identifier = next(iter(kwargs.values()))
        return _DummyQuerySet(self._existing, identifier)


def _make_dummy_model(existing=None):
    manager = _DummyManager(existing)
    return SimpleNamespace(_default_manager=manager)


@pytest.fixture(autouse=True)
def _freeze_today(monkeypatch):
    monkeypatch.setattr(signals.timezone, "now", lambda: datetime(2024, 1, 30, 12, 0, 0))


def test_generate_unique_identifier_formats_value(monkeypatch):
    dummy_model = _make_dummy_model()
    monkeypatch.setattr(signals.secrets, "randbelow", lambda upper: 42)

    result = signals._generate_unique_identifier(dummy_model, "code", "QT")

    assert result == "QT-20240130-0042"


def test_generate_unique_identifier_skips_collisions(monkeypatch):
    existing = {"QT-20240130-0001"}
    dummy_model = _make_dummy_model(existing)
    attempts = iter([1, 2])
    monkeypatch.setattr(signals.secrets, "randbelow", lambda upper: next(attempts))

    result = signals._generate_unique_identifier(dummy_model, "code", "QT")

    assert result == "QT-20240130-0002"


def test_generate_unique_identifier_raises_when_exhausted(monkeypatch):
    existing = {"QT-20240130-0001"}
    dummy_model = _make_dummy_model(existing)
    monkeypatch.setattr(signals.secrets, "randbelow", lambda upper: 1)
    monkeypatch.setattr(signals, "MAX_IDENTIFIER_ATTEMPTS", 2)

    with pytest.raises(RuntimeError):
        signals._generate_unique_identifier(dummy_model, "code", "QT")


@pytest.mark.parametrize(
    "handler, model, attr",
    [
        (signals.generate_quote_number, Quote, "quote_number"),
        (signals.generate_proposal_number, Proposal, "proposal_number"),
        (signals.generate_order_number, ServiceOrder, "order_number"),
    ],
)
def test_generate_identifier_handlers_assign_when_missing(monkeypatch, handler, model, attr):
    sentinel = "TEST-ID"
    monkeypatch.setattr(signals, "_generate_unique_identifier", lambda *args, **kwargs: sentinel)
    instance = model()
    setattr(instance, attr, "")

    handler(model, instance)

    assert getattr(instance, attr) == sentinel


@pytest.mark.parametrize(
    "handler, model, attr",
    [
        (signals.generate_quote_number, Quote, "quote_number"),
        (signals.generate_proposal_number, Proposal, "proposal_number"),
        (signals.generate_order_number, ServiceOrder, "order_number"),
    ],
)
def test_generate_identifier_handlers_respect_existing(monkeypatch, handler, model, attr):
    monkeypatch.setattr(
        signals,
        "_generate_unique_identifier",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not generate")),
    )
    instance = model()
    existing = "EXISTING-ID"
    setattr(instance, attr, existing)

    handler(model, instance)

    assert getattr(instance, attr) == existing
