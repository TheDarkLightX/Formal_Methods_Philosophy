#!/usr/bin/env python3
"""Fail when a built tutorial leaves TeX raw or produces MathJax errors.

The target URL must already be available from a local HTTP server. The audit
deliberately blocks the old jsDelivr hostname so a hidden CDN dependency cannot
make the check pass.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile


def find_chrome() -> str | None:
    for name in ("google-chrome", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Built tutorial URL served over local HTTP")
    parser.add_argument("--min-math", type=int, default=1)
    args = parser.parse_args()

    chrome = find_chrome()
    if chrome is None:
        print("Rendered math audit failed: Chrome or Chromium was not found.", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="formal-math-audit-") as profile:
        command = [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            f"--user-data-dir={profile}",
            "--host-resolver-rules=MAP cdn.jsdelivr.net 127.0.0.1",
            "--virtual-time-budget=10000",
            "--dump-dom",
            args.url,
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        print("Rendered math audit failed: headless browser exited unsuccessfully.", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        return 1

    document = result.stdout
    main_match = re.search(r"<main\b[^>]*>(.*?)</main>", document, flags=re.DOTALL | re.IGNORECASE)
    main_html = main_match.group(1) if main_match else document

    issues: list[str] = []
    rendered_count = len(re.findall(r"<mjx-container\b", main_html, flags=re.IGNORECASE))
    if rendered_count < args.min_math:
        issues.append(
            f"expected at least {args.min_math} rendered expressions, found {rendered_count}"
        )
    if re.search(r"<mjx-merror\b", main_html, flags=re.IGNORECASE):
        issues.append("MathJax produced an error element")
    if re.search(r"\\\[|\\\]|\\\(|\\\)", main_html):
        issues.append("raw escaped math delimiters remain in the rendered tutorial")
    if "assets/vendor/mathjax/tex-chtml.js" not in document:
        issues.append("the page did not load the self-hosted MathJax component")
    if "cdn.jsdelivr.net/npm/mathjax" in document:
        issues.append("the page still contains the former MathJax CDN dependency")

    if issues:
        for issue in issues:
            print(f"Rendered math audit failed: {issue}", file=sys.stderr)
        return 1

    print(
        "Rendered math audit passed: "
        f"{rendered_count} expressions rendered with the local MathJax component."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
