#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from pathlib import Path


def main() -> None:
    now = datetime.now().astimezone()

    data = {
        "fecha": now.strftime("%Y-%m-%d"),
        "hora": now.strftime("%H:%M:%S"),
        "timestamp_iso": now.isoformat(timespec="seconds"),
        "zona_horaria": now.tzinfo.tzname(None) if now.tzinfo else "",
    }

    out_path = Path("env.yaml")
    out_path.write_text(
        "".join(f"{k}: {v}\n" for k, v in data.items()),
        encoding="utf-8",
    )
    print("OK: generado env.yaml")


if __name__ == "__main__":
    main()
