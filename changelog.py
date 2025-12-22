#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import html
import json
import re
import socket
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 2
META_HEADER = {
    "type": "meta",
    "format": "jsonl",
    "schema_version": SCHEMA_VERSION,
    "fields": [
        "ts",
        "fecha",
        "hora",
        "actor",
        "user",
        "host",
        "action",
        "version_file",
        "version_label",
        "command",
        "result",
        "notes",
        "files_changed",
    ],
}


def _esc(val: object) -> str:
    return html.escape("" if val is None else str(val))


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


def _rewrite_with_append(path: Path, line: str) -> None:
    existing = ""
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"
    path.write_text(existing + line + "\n", encoding="utf-8")


def ensure_log(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if log_path.exists() and log_path.stat().st_size > 0:
        # If the file exists, keep it, but ensure the first line is meta.
        lines = log_path.read_text(encoding="utf-8").splitlines(True)
        if not lines:
            log_path.write_text(json.dumps(META_HEADER, ensure_ascii=False) + "\n", encoding="utf-8")
            return

        try:
            first = json.loads(lines[0])
        except Exception:
            # If corrupt, overwrite with new meta header and keep content below as comment.
            backup = log_path.with_suffix(log_path.suffix + ".bak")
            backup.write_text("".join(lines), encoding="utf-8")
            log_path.write_text(json.dumps(META_HEADER, ensure_ascii=False) + "\n", encoding="utf-8")
            return

        if first.get("type") != "meta":
            log_path.write_text(json.dumps(META_HEADER, ensure_ascii=False) + "\n" + "".join(lines), encoding="utf-8")
            return

        # If meta exists but schema differs, update meta in place.
        lines[0] = json.dumps(META_HEADER, ensure_ascii=False) + "\n"
        log_path.write_text("".join(lines), encoding="utf-8")
        return

    log_path.write_text(json.dumps(META_HEADER, ensure_ascii=False) + "\n", encoding="utf-8")


def append_entry(
    *,
    log_path: Path,
    actor: str,
    action: str,
    version_file: str,
    version_label: str,
    command: str,
    result: str,
    notes: str,
    files_changed: list[str],
    env_path: Path,
) -> None:
    env = _read_env_yaml(env_path)
    now = datetime.now().astimezone()

    entry = {
        "ts": now.isoformat(timespec="seconds"),
        # `fecha`/`hora` deben ser consistentes con `ts` para evitar desfaces
        # cuando `env.yaml` está stale (p.ej. si no se ejecutó `getENV.py`).
        "fecha": now.strftime("%Y-%m-%d"),
        "hora": now.strftime("%H:%M:%S"),
        "actor": actor,
        "user": getpass.getuser(),
        "host": socket.gethostname(),
        "action": action,
        "version_file": version_file,
        "version_label": version_label,
        "command": command,
        "result": result,
        "notes": notes,
        "files_changed": files_changed,
    }

    ensure_log(log_path)
    _rewrite_with_append(log_path, json.dumps(entry, ensure_ascii=False))


def _read_jsonl_entries(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.exists():
        return []

    items: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if obj.get("type") == "meta":
            continue
        if isinstance(obj, dict):
            items.append(obj)
    return items


def _read_project_name(context_path: Path) -> tuple[str | None, str | None]:
    if not context_path.exists():
        return None, f"No existe {context_path.as_posix()}. Agrega una línea 'Project: <nombre>' en CONTEXT.md."

    text = context_path.read_text(encoding="utf-8")
    m = re.search(r"^\s*Project\s*:\s*(.+?)\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if not m:
        return None, "Falta 'Project: <nombre>' en CONTEXT.md (requerido para el título)."

    name = m.group(1).strip()
    if not name or name.lower() in {"tbd", "todo", "pending", "<required>", "required"}:
        return None, "Project está vacío/placeholder en CONTEXT.md. Define un nombre real."

    return name, None


@dataclass
class CrudBadge:
    label: str
    css: str


def crud_badge(action: str, result: str) -> CrudBadge:
    a = (action or "").strip().lower()
    r = (result or "").strip().lower()

    if r == "error":
        return CrudBadge("ERROR", "error")

    if a in {"delete", "remove", "cleanup"}:
        return CrudBadge("DELETE OK", "ok")

    if a in {"create", "add", "copy", "render", "generate"}:
        return CrudBadge("CREATE OK", "ok")

    if a in {"edit", "update", "rename"}:
        return CrudBadge("UPDATE OK", "ok")

    if a in {"info", "policy", "schema", "meta"}:
        return CrudBadge("INFO", "info")

    return CrudBadge("INFO", "info")


def generate_html(*, log_path: Path, context_path: Path) -> str:
    project_name, warning = _read_project_name(context_path)

    entries = _read_jsonl_entries(log_path)

    def parse_ts(e: dict[str, Any]) -> float:
        ts = str(e.get("ts") or "")
        try:
            return datetime.fromisoformat(ts).timestamp()
        except Exception:
            return 0.0

    entries.sort(key=parse_ts, reverse=True)

    by_fecha: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in entries:
        ts_raw = str(e.get("ts") or "")
        fecha = str(e.get("fecha") or "")
        # Para display, preferir `ts` (fuente de verdad) y caer a `fecha` si falta.
        if ts_raw:
            try:
                fecha = datetime.fromisoformat(ts_raw).strftime("%Y-%m-%d")
            except Exception:
                pass
        if not fecha:
            fecha = "(sin fecha)"
        by_fecha[fecha].append(e)

    sections: list[str] = []
    for fecha in sorted(by_fecha.keys(), reverse=True):
        sections.append(f"<h2 class='date-header'>{_esc(fecha)}</h2>")
        for e in by_fecha[fecha]:
            ts_raw = str(e.get("ts") or "")
            hora_val = ""
            if ts_raw:
                try:
                    hora_val = datetime.fromisoformat(ts_raw).strftime("%H:%M:%S")
                except Exception:
                    hora_val = ""
            if not hora_val:
                hora_val = str(e.get("hora") or "")
            hora = _esc(hora_val)
            user = _esc(e.get("user") or "")
            host = _esc(e.get("host") or "")
            actor = _esc(e.get("actor") or "")
            action = str(e.get("action") or "")
            result = str(e.get("result") or "")
            vfile = _esc(e.get("version_file") or "")
            vlabel = _esc(e.get("version_label") or "")
            notes = _esc(e.get("notes") or "")
            cmd = _esc(e.get("command") or "")

            badge = crud_badge(action, result)

            files = e.get("files_changed")
            if isinstance(files, list):
                files_str = ", ".join(_esc(x) for x in files)
            else:
                files_str = _esc(files or "")

            meta = " · ".join(filter(None, [hora, f"{user}@{host}" if user or host else "", actor]))

            badges = [f"<span class='badge {badge.css}'>{_esc(badge.label)}</span>"]
            if vlabel:
                badges.append(f"<span class='badge gray'>{vlabel}</span>")
            if action:
                badges.append(f"<span class='badge gray'>action:{_esc(action)}</span>")

            blocks: list[str] = []
            if notes:
                blocks.append(f"<div class='notes'>{notes}</div>")
            if cmd:
                blocks.append(f"<pre class='code'>{cmd}</pre>")
            if vfile:
                blocks.append(
                    f"<div class='kv'><span class='k'>version_file</span><span class='v mono'>{vfile}</span></div>"
                )
            if files_str:
                blocks.append(
                    f"<div class='kv'><span class='k'>files_changed</span><span class='v mono'>{files_str}</span></div>"
                )

            sections.append(
                "<div class='changelog-entry'>"
                f"  <div class='entry-head'>"
                f"    <div class='meta'>{meta}</div>"
                f"    <div class='badges'>{''.join(badges)}</div>"
                f"  </div>"
                f"  {''.join(blocks)}"
                "</div>"
            )

    title_suffix = f" — {project_name}" if project_name else " — (Project missing)"

    warning_html = ""
    if warning:
        warning_html = (
            "<div class='warning'>"
            "<strong>WARNING</strong>: "
            + _esc(warning)
            + "</div>"
        )

    return f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>CHANGELOG{_esc(title_suffix)}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, 'Helvetica Neue', sans-serif;
      font-size: 14px;
      line-height: 1.6;
      color: #172B4D;
      background: #FFFFFF;
      padding: 40px 20px;
      max-width: 980px;
      margin: 0 auto;
    }}

    h1 {{ font-size: 26px; font-weight: 800; margin-bottom: 10px; }}
    .subtitle {{ color: #5E6C84; margin-bottom: 18px; }}

    .warning {{
      margin: 14px 0 18px;
      padding: 12px 14px;
      border-radius: 10px;
      border: 1px solid #FFD8A8;
      background: #FFF4E5;
      color: #7A4B00;
      font-weight: 600;
    }}

    .date-header {{
      font-size: 20px;
      font-weight: 600;
      color: #172B4D;
      margin-bottom: 14px;
      margin-top: 34px;
      padding-top: 6px;
      border-top: 1px solid #DFE1E6;
    }}
    .date-header:first-of-type {{ margin-top: 0; border-top: 0; }}

    .changelog-entry {{
      margin-bottom: 16px;
      padding: 14px 14px;
      border: 1px solid #DFE1E6;
      border-radius: 10px;
      background: #FAFBFC;
    }}

    .entry-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
      margin-bottom: 10px;
    }}

    .meta {{ color: #5E6C84; font-size: 13px; }}
    .badges {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }}

    /* CRUD-style badges: colored background + white letters */
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 800;
      color: #FFFFFF;
      white-space: nowrap;
    }}

    .badge.ok {{ background: #2DA44E; }}      /* green */
    .badge.error {{ background: #D1242F; }}   /* red */
    .badge.info {{ background: #0969DA; }}    /* blue */
    .badge.warn {{ background: #BF8700; }}    /* yellow */
    .badge.gray {{ background: #6E7781; }}    /* gray */

    .notes {{ margin: 8px 0; }}

    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; }}

    .code {{
      margin: 10px 0;
      padding: 10px 12px;
      background: #FFFFFF;
      border: 1px solid #DFE1E6;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 12px;
      line-height: 1.5;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
      white-space: pre-wrap;
      word-break: break-word;
      color: #172B4D;
    }}

    .kv {{ display: grid; grid-template-columns: 120px 1fr; gap: 8px; margin-top: 6px; }}
    .k {{ color: #5E6C84; font-weight: 700; }}
    .v {{ color: #172B4D; }}

    .footer {{ margin-top: 22px; color: #5E6C84; font-size: 12px; }}
  </style>
</head>
<body>
  <h1>CHANGELOG{_esc(title_suffix)}</h1>
  <div class=\"subtitle\">Fuente: <span class=\"mono\">{_esc(log_path.as_posix())}</span> · Contexto: <span class=\"mono\">{_esc(context_path.as_posix())}</span></div>
  {warning_html}

  {''.join(sections)}

  <div class=\"footer\">Regenera: <span class=\"mono\">python3 changelog.py html --stdout &gt; logs/CHANGELOG.html</span></div>
</body>
</html>
"""


def cmd_init(args: argparse.Namespace) -> None:
    ensure_log(Path(args.log))


def cmd_log(args: argparse.Namespace) -> None:
    files_changed = [f.strip() for f in args.files_changed.split(",") if f.strip()]
    append_entry(
        log_path=Path(args.log),
        actor=args.actor,
        action=args.action,
        version_file=args.version_file,
        version_label=args.version_label,
        command=args.command,
        result=args.result,
        notes=args.notes,
        files_changed=files_changed,
        env_path=Path(args.env),
    )


def cmd_html(args: argparse.Namespace) -> None:
    html_doc = generate_html(log_path=Path(args.log), context_path=Path(args.context))
    if args.stdout:
        print(html_doc)
        return
    Path(args.out).write_text(html_doc, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="changelog.py")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Ensure JSONL changelog exists with meta header")
    p_init.add_argument("--log", default="logs/CHANGELOG.log")
    p_init.set_defaults(func=cmd_init)

    p_log = sub.add_parser("log", help="Append a changelog entry (JSONL)")
    p_log.add_argument("--log", default="logs/CHANGELOG.log")
    p_log.add_argument("--env", default="env.yaml")
    p_log.add_argument("--actor", default="codex")
    p_log.add_argument("--action", required=True)
    p_log.add_argument("--version-file", default="")
    p_log.add_argument("--version-label", default="")
    p_log.add_argument("--command", default="")
    p_log.add_argument("--result", default="ok", choices=["ok", "error"])
    p_log.add_argument("--notes", default="")
    p_log.add_argument("--files-changed", default="")
    p_log.set_defaults(func=cmd_log)

    p_html = sub.add_parser("html", help="Generate human HTML changelog from JSONL")
    p_html.add_argument("--log", default="logs/CHANGELOG.log")
    p_html.add_argument("--context", default="CONTEXT.md")
    p_html.add_argument("--out", default="logs/CHANGELOG.html")
    p_html.add_argument("--stdout", action="store_true")
    p_html.set_defaults(func=cmd_html)

    return p


def main() -> None:
    p = build_parser()
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
