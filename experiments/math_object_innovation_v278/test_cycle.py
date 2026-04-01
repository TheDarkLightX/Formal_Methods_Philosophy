#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


RUN = load_module(ROOT / "run_cycle.py", "v278_run_cycle")


def main() -> int:
    report = RUN.build_report()
    checks = report["theorem_checks"]
    assert checks["characteristic_factorization_matches"]
    assert checks["all_checked_bft_closed_forms_match"]
    assert checks["all_checked_delta_closed_forms_match"]
    assert checks["all_checked_star_forcing_terms_match"]
    assert checks["all_checked_delta_recurrences_explained"]

    row = next(item for item in report["rows"] if item["r"] == 2)
    t10 = next(item for item in row["bft_rows"] if item["t"] == 10)
    assert t10["td"] == 5551
    d10 = next(item for item in row["delta_rows"] if item["t"] == 10)
    assert d10["delta"] == 125520
    assert d10["expected_forcing_term"] == 40962
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
