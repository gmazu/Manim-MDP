#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def esc(val: object) -> str:
    return html.escape("" if val is None else str(val))


def read_jsonl(path: Path) -> list[dict]:
    items: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if obj.get("type") == "meta":
            continue
        items.append(obj)
    return items


def read_project_name(context_path: Path) -> tuple[str | None, str | None]:
    """Return (project_name, warning_message)."""
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


def http_view(action: str, result: str) -> tuple[str, str, str]:
    """Return (method, status, css_class)."""
    a = (action or "").strip().lower()
    r = (result or "").strip().lower()

    if r == "error":
        return ("ERROR", "500 ERROR", "error")

    # Treat rename as update (PATCH)
    if a in {"edit", "update", "rename"}:
        return ("UPDATE", "200 OK", "ok")

    if a in {"create", "add", "copy"}:
        return ("CREATE", "201 CREATED", "ok")

    if a in {"delete", "remove"}:
        return ("DELETE", "204 NO CONTENT", "ok")

    if a in {"render", "generate"}:
        return ("GENERATE", "201 CREATED", "ok")

    if a in {"cleanup"}:
        return ("DELETE", "200 OK", "ok")

    if a in {"info", "policy", "schema", "meta"}:
        return ("INFO", "200 INFO", "info")

    return ("INFO", "200 OK", "info")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a human-friendly HTML changelog from CHANGELOG.log (JSONL)."
    )
    parser.add_argument("--log", default="logs/CHANGELOG.log", help="Input JSONL log path")
    parser.add_argument("--context", default="CONTEXT.md", help="Context file containing 'Project: ...'")
    parser.add_argument("--out", default="logs/CHANGELOG.html", help="Output HTML path")
    parser.add_argument("--stdout", action="store_true", help="Write HTML to stdout")
    args = parser.parse_args()

    log_path = Path(args.log)
    out_path = Path(args.out)

    project_name, warning = read_project_name(Path(args.context))

    entries = read_jsonl(log_path)

    def parse_ts(e: dict) -> float:
        ts = e.get("ts") or ""
        try:
            return datetime.fromisoformat(ts).timestamp()
        except Exception:
            return 0.0

    entries.sort(key=parse_ts, reverse=True)

    by_fecha: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        fecha = str(e.get("fecha") or "")
        if not fecha:
            ts = e.get("ts") or ""
            try:
                fecha = datetime.fromisoformat(ts).strftime("%Y-%m-%d")
            except Exception:
                fecha = "(sin fecha)"
        by_fecha[fecha].append(e)

    sections: list[str] = []
    for fecha in sorted(by_fecha.keys(), reverse=True):
        sections.append(f"<h2 class='date-header'>{esc(fecha)}</h2>")
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
            hora = esc(hora_val)
            user = esc(e.get("user") or "")
            host = esc(e.get("host") or "")
            actor = esc(e.get("actor") or "")
            action = esc(e.get("action") or "")
            result = esc(e.get("result") or "")
            vfile = esc(e.get("version_file") or "")
            vlabel = esc(e.get("version_label") or "")
            notes = esc(e.get("notes") or "")
            cmd = esc(e.get("command") or "")

            method, status, cls = http_view(action, result)

            files = e.get("files_changed")
            if isinstance(files, list):
                files_str = ", ".join(esc(x) for x in files)
            else:
                files_str = esc(files or "")

            meta = " · ".join(filter(None, [hora, f"{user}@{host}" if user or host else "", actor]))

            badges = [
                f"<span class='badge {cls}'>{esc(method)} {esc(status)}</span>",
            ]
            if vlabel:
                badges.append(f"<span class='badge gray'>{vlabel}</span>")
            if action:
                badges.append(f"<span class='badge gray'>action:{action}</span>")

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
            + esc(warning)
            + "</div>"
        )

    html_doc = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>CHANGELOG{esc(title_suffix)}</title>
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

    /* REST-style badges: colored background + white letters */
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
  <h1>CHANGELOG{esc(title_suffix)}</h1>
  <div class=\"subtitle\">Fuente: <span class=\"mono\">{esc(log_path.as_posix())}</span> · Contexto: <span class=\"mono\">{esc(Path(args.context).as_posix())}</span></div>
  {warning_html}

  {''.join(sections)}

  <div class=\"footer\">Regenera: <span class=\"mono\">python3 logs/generate_changelog_html.py --stdout &gt; logs/CHANGELOG.html</span></div>
</body>
</html>
"""

    if args.stdout:
        print(html_doc)
        return

    out_path.write_text(html_doc, encoding="utf-8")
    print(f"OK: generado {out_path}")


if __name__ == "__main__":
    main()
