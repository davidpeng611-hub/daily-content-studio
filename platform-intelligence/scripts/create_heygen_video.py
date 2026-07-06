#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


HEYGEN = Path.home() / ".local" / "bin" / "heygen"


def main():
    parser = argparse.ArgumentParser(description="Create a clean HeyGen talking-head video from a generated request JSON.")
    parser.add_argument("request_json", help="Path to heygen_request.json")
    parser.add_argument("--wait", action="store_true", help="Wait until HeyGen finishes rendering")
    parser.add_argument("--dry-run", action="store_true", help="Print the command without creating a video")
    args = parser.parse_args()

    request_path = Path(args.request_json).expanduser().resolve()
    data = json.loads(request_path.read_text(encoding="utf-8"))
    avatar_id = data.get("avatar_id") or data.get("avatar_group_id") or ""

    cmd = [
        str(HEYGEN),
        "video-agent",
        "create",
        "--mode",
        "generate",
        "--orientation",
        data.get("orientation", "portrait"),
        "--voice-id",
        data["voice_id"],
        "--prompt",
        data["prompt"],
    ]
    if avatar_id:
        cmd.extend(["--avatar-id", avatar_id])
    if args.wait:
        cmd.append("--wait")

    if args.dry_run:
        print(" ".join(repr(part) for part in cmd))
        return

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

