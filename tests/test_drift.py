from pathlib import Path

from doc_drift.drift import compare

ROOT = Path(__file__).resolve().parents[1]


def test_compare_a_b():
    report = compare(ROOT / "samples" / "docs_a", ROOT / "samples" / "docs_b")
    assert report["scenario_a"]["hit_rate"] >= 0.5
    assert report["scenario_b"]["hit_rate"] >= 0.5
    assert "delta" in report
