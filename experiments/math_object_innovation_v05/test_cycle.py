#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_motif_controller_is_exact_on_roots() -> None:
    report = build_report()
    assert report["survivor"] == "motif-carved symbolic controller"
    assert report["validation"]["hits"] == report["validation"]["total"]
    assert report["validation"]["first_failure"] is None
    assert report["failure_motif"]["unique_failure_motifs"] == 1


if __name__ == "__main__":
    test_motif_controller_is_exact_on_roots()
    print("ok")
