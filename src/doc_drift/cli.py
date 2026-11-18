from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from doc_drift.drift import compare

console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="doc-drift")
    parser.add_argument("--docs-a", default="samples/docs_a")
    parser.add_argument("--docs-b", default="samples/docs_b")
    parser.add_argument("--results", default="results")
    args = parser.parse_args(argv)

    report = compare(Path(args.docs_a), Path(args.docs_b))
    out = Path(args.results)
    out.mkdir(parents=True, exist_ok=True)
    (out / "doc_drift.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    table = Table(title="Doc Drift Lab")
    table.add_column("scenario")
    table.add_column("docs", justify="right")
    table.add_column("hit_rate", justify="right")
    table.add_row("A", str(report["scenario_a"]["docs"]), f"{report['scenario_a']['hit_rate']:.0%}")
    table.add_row("B", str(report["scenario_b"]["docs"]), f"{report['scenario_b']['hit_rate']:.0%}")
    console.print(table)
    color = "green" if report["ok"] else "red"
    console.print(f"[{color}]delta={report['delta']:+.0%} regressions={len(report['regressions'])}[/{color}]")
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
