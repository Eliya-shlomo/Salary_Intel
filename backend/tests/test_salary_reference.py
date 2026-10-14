import copy
import json

import pytest
from pydantic import ValidationError

from app.ingestion.salary_reference import (
    REFERENCE_PATH,
    SalaryReference,
    confidence_for,
    load_reference,
)


def raw_reference():
    return json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))


def tiny_reference(observations):
    raw = raw_reference()
    raw["sources"] = [
        {"id": "a1", "publisher": "A", "url": "u", "year": 2026, "accessed": "d"},
        {"id": "a2", "publisher": "A", "url": "u", "year": 2025, "accessed": "d"},
        {"id": "b", "publisher": "B", "url": "u", "year": 2026, "accessed": "d"},
        {"id": "c", "publisher": "C", "url": "u", "year": 2026, "accessed": "d"},
    ]
    raw["observations"] = [
        {"role": "backend", "bucket": "mid", "source_role": "x", "source_bucket": "x", **o}
        for o in observations
    ]
    raw["role_weights"]["values"] = {"backend": 1}
    return SalaryReference.model_validate(raw)


def test_real_reference_loads_and_every_cell_is_sourced():
    reference = load_reference()
    assert reference.cells
    for cell in reference.cells:
        assert cell.sources
        assert cell.p25 <= cell.median <= cell.p75


def test_real_cells_stay_inside_the_published_ranges():
    reference = load_reference()
    for cell in reference.cells:
        rows = [
            o for o in reference.observations
            if o.role == cell.role and o.bucket == cell.bucket
        ]
        assert min(o.low for o in rows) <= cell.p25
        assert cell.p75 <= max(o.high for o in rows)


def test_unsourced_weights_are_marked_as_assumptions():
    reference = load_reference()
    for item in reference._all_weights():
        assert item.sources or item.assumption


def test_cell_takes_medians_across_publishers():
    reference = tiny_reference([
        {"source": "a1", "low": 20000, "high": 30000},
        {"source": "b", "low": 24000, "high": 34000},
        {"source": "c", "low": 30000, "high": 40000},
    ])
    cell = reference.cell("backend", "mid")
    assert (cell.p25, cell.median, cell.p75) == (24000, 29000, 34000)
    assert cell.publishers == 3


def test_rows_of_one_publisher_count_once():
    reference = tiny_reference([
        {"source": "a1", "low": 20000, "high": 30000},
        {"source": "a2", "low": 22000, "high": 32000},
        {"source": "b", "low": 30000, "high": 40000},
    ])
    cell = reference.cell("backend", "mid")
    assert cell.publishers == 2
    assert cell.p25 == 25500
    assert cell.year == 2026


def test_uncertain_mapping_makes_the_cell_low_confidence():
    reference = tiny_reference([
        {"source": "a1", "low": 20000, "high": 30000},
        {"source": "b", "low": 20000, "high": 30000},
        {"source": "c", "low": 20000, "high": 30000, "mapping_uncertain": True},
    ])
    assert reference.cell("backend", "mid").confidence == "low"


def test_confidence_rule():
    assert confidence_for(3, [30000, 31000, 32000]) == "high"
    assert confidence_for(2, [30000, 32000]) == "medium"
    assert confidence_for(2, [24000, 36000]) == "low"
    assert confidence_for(1, [30000]) == "low"


def test_rejects_an_unknown_source():
    with pytest.raises(ValidationError, match="unknown source"):
        tiny_reference([{"source": "nobody", "low": 20000, "high": 30000}])


def test_rejects_a_range_printed_backwards():
    with pytest.raises(ValidationError, match="low > high"):
        tiny_reference([{"source": "b", "low": 30000, "high": 20000}])


def test_rejects_weights_without_origin():
    raw = copy.deepcopy(raw_reference())
    raw["style_weights"]["assumption"] = False
    with pytest.raises(ValidationError, match="assumption"):
        SalaryReference.model_validate(raw)
