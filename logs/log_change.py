#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import getpass
import socket
from datetime import datetime
from pathlib import Path


def _read_env_yaml(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Append an audit entry to CHANGELOG.log (JSONL).")
    parser.add_argument("--actor", default="codex", help="Who performed the action (user/codex/etc).")
    parser.add_argument("--action", required=True, help="Action type: edit/render/copy/cleanup/etc.")
    parser.add_argument("--version-file", default="", help="Script file, e.g. archMDP-ASIS.v221.py")
    parser.add_argument("--version-label", default="", help="On-screen version label, e.g. v2.2.1")
    parser.add_argument("--command", default="", help="Command executed (if any)")
    parser.add_argument("--result", default="ok", choices=["ok", "error"], help="Result status")
    parser.add_argument("--notes", default="", help="Short notes")
    parser.add_argument("--files-changed", default="", help="Comma-separated file list")
    parser.add_argument("--env", default="env.yaml", help="env.yaml path")
    parser.add_argument("--log", default="CHANGELOG.log", help="log file path")

    args = parser.parse_args()

    env = _read_env_yaml(Path(args.env))
    now = datetime.now().astimezone()
    user = getpass.getuser()
    host = socket.gethostname()


    entry = {
        "ts": now.isoformat(timespec="seconds"),
        "fecha": env.get("fecha", now.strftime("%Y-%m-%d")),
        "hora": env.get("hora", now.strftime("%H:%M:%S")),
        "actor": args.actor,
        "user": user,
        "host": host,
        "action": args.action,
        "version_file": args.version_file,
        "version_label": args.version_label,
        "command": args.command,
        "result": args.result,
        "notes": args.notes,
        "files_changed": [f.strip() for f in args.files_changed.split(",") if f.strip()],
    }

    log_path = Path(args.log)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"OK: appended to {log_path}")


if __name__ == "__main__":
    main()
