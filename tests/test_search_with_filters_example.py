from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

EXAMPLE_PATH = Path(__file__).parents[1] / "examples" / "search_with_filters.py"


def load_example(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    monkeypatch.setenv("SGG_API_KEY", "test-key")
    monkeypatch.delenv("CG_API_KEY", raising=False)
    spec = importlib.util.spec_from_file_location(
        "search_with_filters_example", EXAMPLE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sgg_api_key_is_passed_to_client_config(monkeypatch: pytest.MonkeyPatch):
    example = load_example(monkeypatch)

    assert example.client.config.api_key == "test-key"


def test_run_prints_dict_filters(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
):
    example = load_example(monkeypatch)
    result = SimpleNamespace(
        pagination_info=SimpleNamespace(total_items=1),
        items=[],
        errors=[],
        filter_info=SimpleNamespace(
            filters={"status": {"operator": "in", "value": ["open"]}}
        ),
    )

    assert example.run("test", lambda: result) is True
    assert "filters sent:" in capsys.readouterr().out


def test_main_returns_failure_when_a_scenario_fails(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
):
    example = load_example(monkeypatch)
    monkeypatch.setattr(example, "run", lambda *_args: False)

    assert example.main() == 1
    assert "search-with-filters example failed" in capsys.readouterr().err
