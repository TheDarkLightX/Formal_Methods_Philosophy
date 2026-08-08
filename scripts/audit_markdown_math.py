#!/usr/bin/env python3
"""Audit Markdown math delimiters for the public tutorial site.

This is a lightweight guard for the bug class that keeps showing up in public
pages: LaTeX commands left outside math delimiters, raw escaped delimiters, or
unbalanced display fences. It is intentionally conservative and path-scoped.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


LATEX_COMMAND = re.compile(r"\\[A-Za-z]+")
RAW_DELIMITER = re.compile(r"\\[()[\]]")
INLINE_MATH = re.compile(r"(?<!\$)\$([^$\n]+)\$(?!\$)")
RAW_INLINE_ASTERISK = re.compile(r"(?<!\\)\*")


@dataclass(frozen=True)
class Issue:
    path: Path
    line_no: int
    message: str
    line: str

    def format(self) -> str:
        return f"{self.path}:{self.line_no}: {self.message}: {self.line.strip()}"


def outside_inline_math_segments(line: str) -> list[str]:
    """Return line segments outside single-dollar inline math."""
    segments: list[str] = []
    current: list[str] = []
    in_math = False
    i = 0
    while i < len(line):
        if line[i] == "$":
            prev_is_dollar = i > 0 and line[i - 1] == "$"
            next_is_dollar = i + 1 < len(line) and line[i + 1] == "$"
            escaped = i > 0 and line[i - 1] == "\\"
            if not escaped and not prev_is_dollar and not next_is_dollar:
                if not in_math:
                    segments.append("".join(current))
                    current = []
                in_math = not in_math
                i += 1
                continue
        if not in_math:
            current.append(line[i])
        i += 1
    if not in_math:
        segments.append("".join(current))
    else:
        segments.append("".join(current))
        segments.append("__UNBALANCED_INLINE_MATH__")
    return segments


def audit_file(path: Path) -> list[Issue]:
    issues: list[Issue] = []
    in_code = False
    in_display = False

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code = not in_code
            continue
        if in_code:
            continue

        display_count = line.count("$$")
        if display_count:
            if display_count % 2 == 1:
                in_display = not in_display
            continue
        if in_display:
            continue

        if RAW_DELIMITER.search(line):
            issues.append(Issue(path, line_no, "raw escaped math delimiter", line))

        segments = outside_inline_math_segments(line)
        if "__UNBALANCED_INLINE_MATH__" in segments:
            issues.append(Issue(path, line_no, "unbalanced inline math delimiter", line))
        for match in INLINE_MATH.finditer(line):
            if RAW_INLINE_ASTERISK.search(match.group(1)):
                issues.append(
                    Issue(
                        path,
                        line_no,
                        "raw asterisk in inline math can become Markdown emphasis; use \\ast",
                        line,
                    )
                )
        for segment in segments:
            if segment == "__UNBALANCED_INLINE_MATH__":
                continue
            match = LATEX_COMMAND.search(segment)
            if match:
                issues.append(
                    Issue(path, line_no, f"LaTeX command outside math: {match.group(0)}", line)
                )

    if in_code:
        issues.append(Issue(path, 0, "unclosed code fence", ""))
    if in_display:
        issues.append(Issue(path, 0, "unclosed display math fence", ""))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    all_issues: list[Issue] = []
    for path in args.paths:
        all_issues.extend(audit_file(path))

    for issue in all_issues:
        print(issue.format())
    if all_issues:
        print(f"Markdown math audit failed: {len(all_issues)} issue(s)", file=sys.stderr)
        return 1
    print("Markdown math audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
