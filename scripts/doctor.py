#!/usr/bin/env python3
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_CONFIG = ROOT / "local" / "workflow.local.json"
EXAMPLE_CONFIG = ROOT / "config" / "workflow.example.json"


def load_config() -> dict:
    path = LOCAL_CONFIG if LOCAL_CONFIG.exists() else EXAMPLE_CONFIG
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def command_ok(cmd: str) -> tuple[bool, str]:
    exe = shutil.which(cmd)
    if not exe:
        return False, "not found"
    try:
        result = subprocess.run(
            [exe, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=8,
        )
        first = (result.stdout or "").splitlines()[0] if result.stdout else exe
        return result.returncode == 0, first
    except Exception as exc:
        return False, str(exc)


def ffmpeg_ok(ffmpeg_cmd: str) -> tuple[bool, str]:
    exe = shutil.which(ffmpeg_cmd) if ffmpeg_cmd == "ffmpeg" else ffmpeg_cmd
    if not exe or not Path(exe).exists() and "\\" in exe:
        return False, "not found"
    try:
        result = subprocess.run(
            [exe, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=8,
        )
        first = (result.stdout or "").splitlines()[0] if result.stdout else exe
        return result.returncode == 0, first
    except Exception as exc:
        return False, str(exc)


def print_check(name: str, ok: bool, detail: str) -> None:
    mark = "OK" if ok else "FAIL"
    print(f"[{mark}] {name}: {detail}")


def main() -> int:
    config = load_config()
    print(f"workspace: {ROOT}")
    print(f"system: {platform.system()} {platform.release()}")
    print(f"python: {sys.version.split()[0]}")
    print("")

    checks: list[bool] = []
    ok, detail = command_ok("git")
    print_check("git", ok, detail)
    checks.append(ok)

    ffmpeg_cmd = config.get("ffmpeg", "ffmpeg")
    ok, detail = ffmpeg_ok(ffmpeg_cmd)
    print_check("ffmpeg", ok, detail)
    checks.append(ok)

    for key in ["input_dir", "output_dir", "assets_dir", "today_posts_dir", "local_dir"]:
        value = config.get(key)
        if not value:
            print_check(key, False, "missing in config")
            checks.append(False)
            continue
        path = Path(value)
        exists = path.exists()
        print_check(key, exists, str(path))
        checks.append(exists)

    print("")
    if all(checks):
        print("Environment is ready for the local workflow.")
        return 0
    print("Environment is not ready. Fix FAIL items before rendering videos.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

