#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8714
MAX_BODY_BYTES = 32_000
DEFAULT_TIMEOUT_S = 15.0
TAU_UPSTREAM_URL = "https://github.com/IDNI/tau-lang/"
ALLOWED_ORIGIN_PREFIXES = (
    "http://127.0.0.1:",
    "http://localhost:",
    "https://thedarklightx.github.io",
)


def _strip_inline_comment(line: str) -> str:
    brace_depth = 0
    for idx, ch in enumerate(line):
        if ch == "{":
            brace_depth += 1
        elif ch == "}":
            brace_depth = max(0, brace_depth - 1)
        elif ch == "#" and brace_depth == 0:
            return line[:idx]
    return line


def normalize_spec_text(spec_text: str) -> str:
    lines: list[str] = []
    raw = spec_text.splitlines()
    i = 0
    while i < len(raw):
        line = _strip_inline_comment(raw[i])
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if stripped.startswith("set charvar"):
            i += 1
            continue
        if re.match(r"^always\b", stripped):
            expr_parts: list[str] = []
            tail = stripped[len("always") :].strip()
            if tail:
                if tail.endswith("."):
                    joined = tail[:-1].strip()
                    if not joined:
                        raise ValueError("empty always expression")
                    lines.append(f"always {joined}.")
                    i += 1
                    continue
                expr_parts.append(tail)
            i += 1
            terminated = False
            while i < len(raw):
                nxt = _strip_inline_comment(raw[i]).strip()
                if not nxt or nxt.startswith("#"):
                    i += 1
                    continue
                expr_parts.append(nxt)
                if nxt.endswith("."):
                    terminated = True
                    break
                i += 1
            if not terminated:
                raise ValueError("unterminated always block")
            joined = " ".join(expr_parts).strip()
            if joined.endswith("."):
                joined = joined[:-1].strip()
            lines.append(f"always {joined}.")
            i += 1
            continue
        lines.append(stripped)
        i += 1
    return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class TauDefinition:
    name: str
    params: tuple[str, ...]
    body: str


_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_STREAM_DECL_RE = re.compile(r"^\s*[io]\d+\s*\[[^\]]+\]\s*:")
_OUTPUT_ASSIGN_RE = re.compile(r"\b(o\d+)\[(\d+)\](?::[^\s:=]+)?\s*:=\s*(-?\d+)")


def parse_definitions(spec_text: str) -> dict[str, TauDefinition]:
    defs: dict[str, TauDefinition] = {}
    lines = spec_text.splitlines()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped or stripped.startswith("#") or re.match(r"^always\b", stripped):
            i += 1
            continue
        if _STREAM_DECL_RE.match(lines[i]) or re.match(r"^\s*[io]\d+\s*:", lines[i]):
            i += 1
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\s*:=\s*(.*)$", stripped)
        if not match:
            i += 1
            continue
        name = match.group(1)
        params_raw = match.group(2)
        body_parts: list[str] = []
        first_body = match.group(3).strip()
        if first_body:
            body_parts.append(first_body)
        while True:
            if body_parts and body_parts[-1].endswith("."):
                break
            i += 1
            if i >= len(lines):
                raise ValueError(f"unterminated definition body for {name}")
            nxt = lines[i].strip()
            if not nxt or nxt.startswith("#"):
                continue
            body_parts.append(nxt)
        body_joined = " ".join(body_parts).strip()
        if not body_joined.endswith("."):
            raise ValueError(f"unterminated definition body for {name}")
        params: list[str] = []
        for raw_param in [part.strip() for part in params_raw.split(",") if part.strip()]:
            param_name = raw_param.split(":", 1)[0].strip()
            if " " in param_name:
                param_name = param_name.split()[-1]
            if not _IDENT_RE.fullmatch(param_name):
                raise ValueError(f"invalid parameter name {raw_param!r} in {name}")
            params.append(param_name)
        defs[name] = TauDefinition(name=name, params=tuple(params), body=body_joined[:-1].strip())
        i += 1
    return defs


def _split_call_args(arglist: str) -> list[str]:
    args: list[str] = []
    buf: list[str] = []
    paren = bracket = brace = 0
    for ch in arglist:
        if ch == "(":
            paren += 1
        elif ch == ")":
            paren -= 1
        elif ch == "[":
            bracket += 1
        elif ch == "]":
            bracket -= 1
        elif ch == "{":
            brace += 1
        elif ch == "}":
            brace -= 1
        elif ch == "," and paren == 0 and bracket == 0 and brace == 0:
            args.append("".join(buf).strip())
            buf.clear()
            continue
        buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        args.append(tail)
    return args


def _replace_identifier(text: str, ident: str, replacement: str) -> str:
    return re.sub(rf"(?<![A-Za-z0-9_]){re.escape(ident)}(?![A-Za-z0-9_])", replacement, text)


def inline_definitions(expr: str, defs: dict[str, TauDefinition], *, max_depth: int = 25) -> str:
    if not defs:
        return expr
    if max_depth <= 0:
        raise ValueError("Tau definition inlining exceeded max depth")
    out: list[str] = []
    i = 0
    while i < len(expr):
        match = _IDENT_RE.match(expr, i)
        if not match:
            out.append(expr[i])
            i += 1
            continue
        name = match.group(0)
        j = match.end()
        if name in defs and j < len(expr) and expr[j] == "(":
            depth = 0
            k = j
            while k < len(expr):
                ch = expr[k]
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            if depth != 0 or k >= len(expr):
                raise ValueError(f"unbalanced call while expanding {name}")
            args = _split_call_args(expr[j + 1 : k])
            definition = defs[name]
            if len(args) != len(definition.params):
                out.append(expr[i : k + 1])
                i = k + 1
                continue
            body = definition.body
            for param, arg in zip(definition.params, args):
                body = _replace_identifier(body, param, f"({inline_definitions(arg, defs, max_depth=max_depth - 1)})")
            out.append(f"({inline_definitions(body, defs, max_depth=max_depth - 1)})")
            i = k + 1
            continue
        out.append(name)
        i = j
    return "".join(out)


def extract_stream_types(spec_text: str) -> dict[str, str]:
    stream_types: dict[str, str] = {}
    for match in re.finditer(r"\b([io]\d+)\s*\[[^\]]+\]\s*:\s*([a-zA-Z]+\[\d+\]|[a-zA-Z]+)", spec_text):
        if match.group(1) not in stream_types:
            stream_types[match.group(1)] = match.group(2)
    return stream_types


def extract_always_exprs(spec_text: str) -> list[str]:
    exprs: list[str] = []
    for line in spec_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not re.match(r"^always\b", stripped):
            continue
        match = re.search(r"always\s*(.*)\.\s*$", stripped)
        if match:
            exprs.append(match.group(1))
    return exprs


def build_repl_script(
    *,
    spec_text: str,
    input_streams: dict[str, str],
    output_streams: dict[str, str],
    input_paths: dict[str, Path],
    output_paths: dict[str, Path],
    always_exprs: list[str],
    skip_definitions: bool = True,
) -> str:
    def _tau_file_literal(path: Path) -> str:
        return str(path).replace("\\", "\\\\").replace('"', '\\"')

    lines = ["# Auto-generated Tau REPL harness", ""]
    skipping_def_block = False
    for name in sorted(input_streams.keys(), key=lambda s: int(s[1:])):
        lines.append(f'{name} : {input_streams[name]} := in file("{_tau_file_literal(input_paths[name])}")')
    lines.append("")
    for name in sorted(output_streams.keys(), key=lambda s: int(s[1:])):
        lines.append(f'{name} : {output_streams[name]} := out file("{_tau_file_literal(output_paths[name])}")')
    lines.append("")
    for line in spec_text.splitlines():
        if line.lstrip().startswith("#") or re.match(r"^run\b", line.strip()) or re.match(r"^always\b", line.strip()):
            continue
        if skip_definitions:
            if skipping_def_block:
                if line.strip().endswith("."):
                    skipping_def_block = False
                continue
            if ":=" in line:
                if not line.strip().endswith("."):
                    skipping_def_block = True
                continue
        if _STREAM_DECL_RE.match(line) or re.match(r"^\s*[io]\d+\s*:", line):
            continue
        if line.strip():
            lines.append(line)
    expr = " && ".join(f"({expr})" for expr in always_exprs)
    lines.extend(["", f"r {expr}", "q", ""])
    return "\n".join(lines)


def _extract_outputs_from_text(output_text: str) -> dict[int, dict[str, int]]:
    outputs_by_step: dict[int, dict[str, int]] = {}
    for match in _OUTPUT_ASSIGN_RE.finditer(output_text):
        name = match.group(1)
        idx = int(match.group(2))
        value = int(match.group(3))
        outputs_by_step.setdefault(idx, {})[name] = value
    return outputs_by_step


def _normalize_outputs_by_step(
    outputs_by_step: dict[int, dict[str, int]],
    *,
    step_count: int,
) -> dict[int, dict[str, int]]:
    if not outputs_by_step:
        return {}
    indices = sorted(outputs_by_step.keys())
    if indices and indices[0] == 1 and indices[-1] == step_count:
        return {idx - 1: outputs_by_step[idx] for idx in indices}
    return outputs_by_step


def _outputs_complete(
    *,
    outputs_by_step: dict[int, dict[str, int]],
    out_names: list[str],
    step_count: int,
) -> bool:
    for idx in range(step_count):
        got = outputs_by_step.get(idx, {})
        for out_name in out_names:
            if out_name not in got:
                return False
    return True


def _run_subprocess_with_output_caps(
    cmd: list[str],
    *,
    input_text: str,
    cwd: Path,
    timeout_s: float,
    max_stdout_bytes: int,
    max_stderr_bytes: int,
) -> tuple[int, str, str]:
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        close_fds=True,
        cwd=str(cwd),
        bufsize=0,
    )
    assert proc.stdin is not None and proc.stdout is not None and proc.stderr is not None
    input_bytes = input_text.encode("utf-8")
    stdout_buf = bytearray()
    stderr_buf = bytearray()

    def _decode_stdout() -> str:
        return bytes(stdout_buf).decode("utf-8", errors="replace")

    def _decode_stderr() -> str:
        return bytes(stderr_buf).decode("utf-8", errors="replace")

    def _kill_proc_group() -> None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                return

    try:
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            os.set_blocking(stream.fileno(), False)
        stdin_view = memoryview(input_bytes)
        stdin_off = 0
        stdin_open = len(stdin_view) > 0
        stdout_open = True
        stderr_open = True
        if not stdin_open:
            proc.stdin.close()
        deadline = time.monotonic() + timeout_s
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                _kill_proc_group()
                return -1, _decode_stdout(), "tau timed out"
            rlist = [stream for stream, open_flag in ((proc.stdout, stdout_open), (proc.stderr, stderr_open)) if open_flag]
            wlist = [proc.stdin] if stdin_open and stdin_off < len(stdin_view) else []
            if not rlist and not wlist:
                break
            ready_r, ready_w, _ = select.select(rlist, wlist, [], min(0.1, remaining))
            for stream in ready_w:
                try:
                    written = stream.write(stdin_view[stdin_off : stdin_off + 4096])
                except BrokenPipeError:
                    stdin_open = False
                    try:
                        stream.close()
                    except Exception:
                        pass
                    continue
                if written is None:
                    written = 0
                stdin_off += int(written)
                if stdin_off >= len(stdin_view):
                    stdin_open = False
                    proc.stdin.close()
            for stream in ready_r:
                chunk = stream.read(4096)
                if not chunk:
                    if stream is proc.stdout:
                        stdout_open = False
                    else:
                        stderr_open = False
                    continue
                chunk_b = chunk if isinstance(chunk, (bytes, bytearray)) else str(chunk).encode("utf-8", errors="replace")
                if stream is proc.stdout:
                    stdout_buf += chunk_b
                    if len(stdout_buf) > max_stdout_bytes:
                        stdout_buf[:] = stdout_buf[:max_stdout_bytes]
                        _kill_proc_group()
                        return -1, _decode_stdout(), "tau stdout too large"
                else:
                    stderr_buf += chunk_b
                    if len(stderr_buf) > max_stderr_bytes:
                        stderr_buf[:] = stderr_buf[:max_stderr_bytes]
                        _kill_proc_group()
                        return -1, _decode_stdout(), "tau stderr too large"
            if not stdout_open and not stderr_open and not stdin_open:
                break
        rc = proc.poll()
        if rc is None:
            try:
                rc = proc.wait(timeout=max(0.1, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                _kill_proc_group()
                return -1, _decode_stdout(), "tau timed out"
        return int(rc), _decode_stdout(), _decode_stderr()
    finally:
        try:
            if proc.returncode is None:
                _kill_proc_group()
        except Exception:
            pass
        try:
            proc.wait(timeout=1.0)
        except Exception:
            pass


def find_tau_bin() -> str | None:
    env_tau = os.environ.get("TAU_BIN", "").strip()
    if env_tau:
        candidate = Path(os.path.expanduser(env_tau))
        if candidate.exists() and candidate.is_file() and os.access(str(candidate), os.X_OK):
            return str(candidate.resolve())
    candidates = [
        ROOT / "external" / "tau-lang" / "build-Release" / "tau",
        ROOT / "external" / "tau-lang" / "build-Debug" / "tau",
        ROOT / "external" / "tau-nightly" / "usr" / "bin" / "tau",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file() and os.access(str(candidate), os.X_OK):
            return str(candidate.resolve())
    found = shutil.which("tau")
    return str(Path(found).resolve()) if found else None


def sanitize_trace_text(text: str) -> str:
    text = re.sub(r"/tmp/[^\"'\s)]+", "/tmp/tau-trace-path", text)
    text = re.sub(r"Tau Language Framework version ([^)]+)\)", r"Tau Language Framework version \1)", text)
    return text


def _tau_binary_name(tau_bin: str | None) -> str | None:
    if not tau_bin:
        return None
    return Path(str(tau_bin)).name


def run_tau_spec_steps_with_trace(
    tau_bin: str,
    spec_path: Path,
    steps: list[dict[str, int]],
    *,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    severity: str = "trace",
) -> tuple[dict[int, dict[str, int]], str, str, str]:
    if not steps:
        return {}, "", "", ""
    spec_text = normalize_spec_text(spec_path.read_text(encoding="utf-8"))
    stream_types = extract_stream_types(spec_text)
    input_streams = {k: v for k, v in stream_types.items() if k.startswith("i")}
    output_streams = {k: v for k, v in stream_types.items() if k.startswith("o")}
    always_exprs = extract_always_exprs(spec_text)
    defs = parse_definitions(spec_text)
    expanded_always_exprs = [inline_definitions(expr, defs) for expr in always_exprs]
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        input_paths: dict[str, Path] = {}
        output_paths: dict[str, Path] = {}
        for name in sorted(input_streams.keys(), key=lambda s: int(s[1:])):
            values = []
            for step in steps:
                if name not in step:
                    raise ValueError(f"missing {name} in Tau input step")
                values.append(str(int(step[name])))
            path = tmpdir_path / f"{name}.in"
            path.write_text("\n".join(values) + "\n", encoding="utf-8")
            input_paths[name] = path
        for name in sorted(output_streams.keys(), key=lambda s: int(s[1:])):
            output_paths[name] = tmpdir_path / f"{name}.out"
        repl_script = build_repl_script(
            spec_text=spec_text,
            input_streams=input_streams,
            output_streams=output_streams,
            input_paths=input_paths,
            output_paths=output_paths,
            always_exprs=expanded_always_exprs,
            skip_definitions=True,
        )
        rc, out, err = _run_subprocess_with_output_caps(
            [tau_bin, "--severity", severity, "--charvar", "false"],
            input_text=repl_script,
            cwd=spec_path.parent,
            timeout_s=timeout_s,
            max_stdout_bytes=512_000,
            max_stderr_bytes=128_000,
        )
        if rc != 0:
            raise RuntimeError((err or out or f"tau failed with rc={rc}").strip())
        outputs_by_step: dict[int, dict[str, int]] = {}
        for name, path in output_paths.items():
            if not path.exists():
                raise RuntimeError(f"tau did not create output file {name}")
            values = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if len(values) != len(steps):
                raise RuntimeError(f"{name} output length mismatch: expected {len(steps)}, got {len(values)}")
            for idx, raw in enumerate(values):
                outputs_by_step.setdefault(idx, {})[name] = int(raw)
        return outputs_by_step, out, err, repl_script


def run_tau_spec_steps_spec_mode_with_trace(
    tau_bin: str,
    spec_path: Path,
    steps: list[dict[str, int]],
    *,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    severity: str = "trace",
) -> tuple[dict[int, dict[str, int]], str, str, str, str]:
    if not steps:
        return {}, "", "", "", ""
    spec_text = normalize_spec_text(spec_path.read_text(encoding="utf-8"))
    defs = parse_definitions(spec_text)
    always_exprs = extract_always_exprs(spec_text)
    if always_exprs:
        expanded_always_exprs = [inline_definitions(expr, defs) for expr in always_exprs]
        kept_lines: list[str] = []
        for raw_line in spec_text.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            if re.match(r"^always\b", stripped):
                continue
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*\(.*\)\s*:=\s*.*\.\s*$", stripped):
                continue
            kept_lines.append(stripped)
        for expr in expanded_always_exprs:
            kept_lines.append(f"always {expr}.")
        spec_text = "\n".join(kept_lines) + "\n"
    stream_types = extract_stream_types(spec_text)
    input_streams = {k: v for k, v in stream_types.items() if k.startswith("i")}
    output_streams = {k: v for k, v in stream_types.items() if k.startswith("o")}
    if not input_streams:
        raise ValueError(f"no input streams detected in {spec_path}")
    input_names = sorted(input_streams.keys())
    lines: list[str] = []
    for step in steps:
        for name in input_names:
            if name not in step:
                raise ValueError(f"missing {name} in Tau input step")
            lines.append(str(int(step[name])))
    input_text = "\n".join(lines) + "\n\n"
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        tmp_spec_path = tmpdir_path / spec_path.name
        tmp_spec_path.write_text(spec_text, encoding="utf-8")
        cmd = [tau_bin, str(tmp_spec_path), "--severity", severity, "--charvar", "false", "-x"]
        out_names = sorted(output_streams.keys())
        stdout_budget = 16_384 + len(steps) * max(1, len(out_names)) * 96
        last_rc = -1
        last_out = ""
        last_err = ""
        for attempt_timeout in (float(timeout_s), max(25.0, float(timeout_s))):
            rc, out, err = _run_subprocess_with_output_caps(
                cmd,
                input_text=input_text,
                cwd=tmpdir_path,
                timeout_s=attempt_timeout,
                max_stdout_bytes=min(256_000, max(32_000, int(stdout_budget))),
                max_stderr_bytes=32_000,
            )
            outputs_by_step = _normalize_outputs_by_step(
                _extract_outputs_from_text(out + ("\n" + err if err else "")),
                step_count=len(steps),
            )
            if _outputs_complete(outputs_by_step=outputs_by_step, out_names=out_names, step_count=len(steps)):
                return outputs_by_step, out, err, spec_text, input_text
            last_rc = rc
            last_out = out
            last_err = err
            if (err or "").strip() != "tau timed out":
                break
    raise RuntimeError((last_err or last_out or f"tau failed with rc={last_rc}").strip())


def _u(value: Any, *, lo: int, hi: int, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    if value < lo or value > hi:
        raise ValueError(f"{name} must be in [{lo}, {hi}]")
    return int(value)


def _b(value: Any, *, name: str) -> int:
    return _u(value, lo=0, hi=1, name=name)


def _encode_signed(value: int) -> int:
    return value + 127


def _unsigned_payload(values: dict[str, Any]) -> tuple[Path, dict[str, int], dict[str, Any]]:
    step = {
        "i1": _u(values.get("x1"), lo=0, hi=127, name="x1"),
        "i2": _u(values.get("x2"), lo=0, hi=127, name="x2"),
        "i3": _u(values.get("w1"), lo=0, hi=127, name="w1"),
        "i4": _u(values.get("w2"), lo=0, hi=127, name="w2"),
        "i5": _u(values.get("bias"), lo=0, hi=127, name="bias"),
        "i6": _u(values.get("threshold"), lo=0, hi=127, name="threshold"),
        "i7": _b(values.get("claim"), name="claim"),
    }
    score = (step["i1"] * step["i3"]) + (step["i2"] * step["i4"]) + step["i5"]
    return (
        ROOT / "examples" / "tau" / "perceptron_2input_single_output_v1.tau",
        step,
        {
            "score": score,
            "threshold": step["i6"],
            "actual_class": 1 if score >= step["i6"] else 0,
            "claimed_class": step["i7"],
        },
    )


def _signed_payload(values: dict[str, Any]) -> tuple[Path, dict[str, int], dict[str, Any]]:
    x1 = _u(values.get("x1"), lo=-127, hi=127, name="x1")
    x2 = _u(values.get("x2"), lo=-127, hi=127, name="x2")
    w1 = _u(values.get("w1"), lo=-127, hi=127, name="w1")
    w2 = _u(values.get("w2"), lo=-127, hi=127, name="w2")
    bias = _u(values.get("bias"), lo=-127, hi=127, name="bias")
    threshold = _u(values.get("threshold"), lo=-127, hi=127, name="threshold")
    claim = _b(values.get("claim"), name="claim")
    step = {
        "i1": _encode_signed(x1),
        "i2": _encode_signed(x2),
        "i3": _encode_signed(w1),
        "i4": _encode_signed(w2),
        "i5": _encode_signed(bias),
        "i6": _encode_signed(threshold),
        "i7": claim,
    }
    score = (x1 * w1) + (x2 * w2) + bias
    return (
        ROOT / "examples" / "tau" / "perceptron_2input_signed_offset_v1.tau",
        step,
        {
            "decoded": {
                "x1": x1,
                "x2": x2,
                "w1": w1,
                "w2": w2,
                "bias": bias,
                "threshold": threshold,
            },
            "score": score,
            "actual_class": 1 if score >= threshold else 0,
            "claimed_class": claim,
        },
    )


def _internal_payload(values: dict[str, Any]) -> tuple[Path, dict[str, int], dict[str, Any]]:
    step = {
        "i1": _u(values.get("x1"), lo=0, hi=127, name="x1"),
        "i2": _u(values.get("x2"), lo=0, hi=127, name="x2"),
        "i3": _u(values.get("threshold"), lo=0, hi=127, name="threshold"),
        "i4": _b(values.get("claim"), name="claim"),
    }
    score = (step["i1"] * 4) + (step["i2"] * 5) + 1
    return (
        ROOT / "examples" / "tau" / "perceptron_2input_internal_weights_v1.tau",
        step,
        {
            "internal_weights": {"w1": 4, "w2": 5, "bias": 1},
            "score": score,
            "threshold": step["i3"],
            "actual_class": 1 if score >= step["i3"] else 0,
            "claimed_class": step["i4"],
        },
    )


MODE_BUILDERS = {
    "unsigned": _unsigned_payload,
    "signed": _signed_payload,
    "internal": _internal_payload,
}


class TauBridgeHandler(BaseHTTPRequestHandler):
    server_version = "TauLocalBridge/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        sys.stdout.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format % args))

    def _allowed_origin(self) -> str | None:
        origin = self.headers.get("Origin", "").strip()
        if not origin:
            return None
        for prefix in ALLOWED_ORIGIN_PREFIXES:
            if origin.startswith(prefix):
                return origin
        return None

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        allowed_origin = self._allowed_origin()
        if allowed_origin:
            self.send_header("Access-Control-Allow-Origin", allowed_origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        allowed_origin = self._allowed_origin()
        if allowed_origin:
            self.send_header("Access-Control-Allow-Origin", allowed_origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/health":
            tau_bin = find_tau_bin()
            self._send_json(
                200,
                {
                    "ok": True,
                    "bridge": "tau_local_bridge",
                    "tau_found": bool(tau_bin),
                    "tau_binary_name": _tau_binary_name(tau_bin),
                    "tau_upstream_url": TAU_UPSTREAM_URL,
                    "supported_modes": sorted(MODE_BUILDERS.keys()),
                    "command": "python3 scripts/tau_local_bridge.py",
                },
            )
            return
        self._send_json(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/run-perceptron":
            self._send_json(404, {"ok": False, "error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"ok": False, "error": "bad_content_length"})
            return
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send_json(400, {"ok": False, "error": "invalid_body_size"})
            return
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return
        mode = str(payload.get("mode", "")).strip()
        values = payload.get("values", {})
        if mode not in MODE_BUILDERS:
            self._send_json(400, {"ok": False, "error": "unsupported_mode"})
            return
        if not isinstance(values, dict):
            self._send_json(400, {"ok": False, "error": "values_must_be_object"})
            return
        tau_bin = find_tau_bin()
        if not tau_bin:
            self._send_json(
                503,
                {
                    "ok": False,
                    "error": "tau_not_found",
                    "tau_upstream_url": TAU_UPSTREAM_URL,
                    "hint": "Install Tau from the official upstream and then restart this local bridge.",
                },
            )
            return
        try:
            spec_path, step, derived = MODE_BUILDERS[mode](values)
            outputs, stdout, stderr, normalized_spec, input_text = run_tau_spec_steps_spec_mode_with_trace(
                tau_bin=tau_bin,
                spec_path=spec_path,
                steps=[step],
                timeout_s=DEFAULT_TIMEOUT_S,
                severity="trace",
            )
        except Exception as exc:
            self._send_json(
                400,
                {
                    "ok": False,
                    "error": "tau_run_failed",
                    "message": str(exc),
                },
            )
            return
        trace_excerpt = "\n".join(sanitize_trace_text(stdout).splitlines()[:26])
        self._send_json(
            200,
            {
                "ok": True,
                "mode": mode,
                "tau_binary_name": _tau_binary_name(tau_bin),
                "tau_upstream_url": TAU_UPSTREAM_URL,
                "spec_relpath": str(spec_path.relative_to(ROOT)),
                "inputs": step,
                "derived": derived,
                "outputs_by_step": outputs,
                "trace_excerpt": trace_excerpt,
                "stderr": sanitize_trace_text(stderr),
                "normalized_spec_excerpt": "\n".join(sanitize_trace_text(normalized_spec).splitlines()[:18]),
                "input_text": sanitize_trace_text(input_text),
            },
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Localhost bridge for running the perceptron Tau examples with a local Tau install.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind, defaults to 127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind, defaults to 8714")
    args = parser.parse_args()
    if args.port <= 0 or args.port > 65535:
        raise SystemExit("port must be in 1..65535")
    server = ThreadingHTTPServer((args.host, args.port), TauBridgeHandler)
    tau_bin = find_tau_bin()
    print(f"Tau local bridge listening on http://{args.host}:{args.port}")
    print(f"Tau found: {'yes' if tau_bin else 'no'}")
    if tau_bin:
        print(f"Tau path: {tau_bin}")
    else:
        print(f"Install Tau from {TAU_UPSTREAM_URL} and restart the bridge.")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
