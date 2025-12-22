#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


def esc(v: object) -> str:
    return html.escape("" if v is None else str(v))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if obj.get("type") == "meta":
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


def crud_label(action: str, result: str) -> tuple[str, str]:
    a = (action or "").strip().lower()
    r = (result or "").strip().lower()
    if r == "error":
        return ("ERROR", "error")
    if a in {"delete", "remove", "cleanup"}:
        return ("DELETE OK", "ok")
    if a in {"edit", "update", "rename"}:
        return ("UPDATE OK", "ok")
    if a in {"create", "add", "copy", "render", "generate"}:
        return ("CREATE OK", "ok")
    return ("INFO", "info")


def parse_backlog(md: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    current_title = None
    buf: list[str] = []

    def flush():
        if current_title is None and not buf:
            return
        body = "\n".join(buf).strip()
        ts = ""
        m_ts = re.search(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]", body)
        if m_ts:
            ts = m_ts.group(1)
        prio = None
        m_prio = re.search(r"\[P(\d+)\]", current_title or "") or re.search(r"\[P(\d+)\]", body)
        if m_prio:
            prio = int(m_prio.group(1))
        is_trash = bool(re.search(r"\[(?:X|TRASH)\]", (current_title or "") + body, re.IGNORECASE))
        items.append({"title": (current_title or "").strip(), "text": body, "ts": ts, "priority": prio, "trash": is_trash})

    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("## "):
            flush()
            current_title = line[3:].strip()
            buf = []
            continue
        if line.startswith("# "):
            continue
        if not line.strip():
            continue
        buf.append(line[2:].strip() if line.lstrip().startswith('- ') else line.strip())

    flush()
    return [it for it in items if it.get("title") or it.get("text")]


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a 2-column ChangeBacklog (BACKLOG + CHANGELOG combinado)")
    ap.add_argument("--backlog", default="BACKLOG.md")
    ap.add_argument("--log", default="logs/CHANGELOG.log")
    ap.add_argument("--out", default="logs/STATUS.html")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--limit", type=int, default=80, help="How many changelog entries to show")
    args = ap.parse_args()

    backlog_path = Path(args.backlog)
    backlog_md = backlog_path.read_text(encoding="utf-8") if backlog_path.exists() else "# BACKLOG\n- (no existe)"
    backlog_items = parse_backlog(backlog_md)

    mtime = ""
    if backlog_path.exists():
        mtime = datetime.fromtimestamp(backlog_path.stat().st_mtime).astimezone().isoformat(timespec="seconds")

    # CHANGELOG
    entries = read_jsonl(Path(args.log))

    def ts_key(e: dict[str, Any]) -> float:
        ts = str(e.get("ts") or "")
        try:
            return datetime.fromisoformat(ts).timestamp()
        except Exception:
            return 0.0

    entries.sort(key=ts_key, reverse=True)
    entries = entries[: max(args.limit, 0)]

    # Ordenar backlog en 3 grupos: Prioridad, Sin prioridad, Trash
    def ts_value(ts: str) -> float:
        try:
            return datetime.fromisoformat(ts).timestamp()
        except Exception:
            return 0.0

    prioritized = [it for it in backlog_items if it.get("priority") is not None and not it.get("trash")]
    normal = [it for it in backlog_items if it.get("priority") is None and not it.get("trash")]
    trash = [it for it in backlog_items if it.get("trash")]

    prioritized.sort(key=lambda it: (it.get("priority", 9999), -ts_value(it.get("ts", ""))))
    normal.sort(key=lambda it: -ts_value(it.get("ts", "")))
    trash.sort(key=lambda it: -ts_value(it.get("ts", "")))

    for idx, it in enumerate(prioritized, 1):
        it["display_order"] = idx

    def render_cards(items: list[dict[str, str]], badge_kind: str = "warn") -> str:
        cards: list[str] = []
        for it in items:
            meta_parts = [it.get("ts", ""), "BACKLOG"]
            meta = " · ".join(filter(None, meta_parts))
            prio_badge = f"<span class='badge warn'>P{it['priority']}</span>" if it.get("priority") is not None else ""
            order_badge = f"<span class='badge gray'>#{it.get('display_order')}</span>" if it.get("display_order") else ""
            trash_badge = "<span class='badge error'>TRASH</span>" if it.get("trash") else ""
            body = esc(it.get("text", "")).replace("\n", "<br>")
            title = esc(it.get("title", ""))
            cards.append(
                "<div class='changelog-entry'>"
                "  <div class='entry-head'>"
                f"    <div class='meta'>{meta}</div>"
                f"    <div class='badges'>{prio_badge}{order_badge}{trash_badge}<span class='badge {badge_kind}'>TODO</span></div>"
                "  </div>"
                f"  <div class='card-title'>{title}</div>"
                f"  <div class='notes'>{body}</div>"
                "</div>"
            )
        if not cards:
            cards.append("<div class='notes'>Sin pendientes</div>")
        return "".join(cards)

    backlog_html = (
        "<div class='backlog-group'><h3>Prioridad</h3><div class='backlog-list'>"
        + render_cards(prioritized, badge_kind="warn")
        + "</div></div>"
        + "<div class='backlog-group'><h3>Sin prioridad</h3><div class='backlog-list'>"
        + render_cards(normal, badge_kind="warn")
        + "</div></div>"
        + "<div class='backlog-group'><h3>Trash</h3><div class='backlog-list'>"
        + render_cards(trash, badge_kind="error")
        + "</div></div>"
    )

    # Render changelog as cards
    changelog_cards: list[str] = []
    last_fecha = None
    for e in entries:
        fecha = str(e.get("fecha") or "")
        if fecha and fecha != last_fecha:
            changelog_cards.append(f"<h2 class='date-header'>{esc(fecha)}</h2>")
            last_fecha = fecha

        label, cls = crud_label(str(e.get("action") or ""), str(e.get("result") or ""))
        ts_raw = str(e.get("ts") or "")
        hora_val = ""
        if ts_raw:
            try:
                hora_val = datetime.fromisoformat(ts_raw).strftime("%H:%M:%S")
            except Exception:
                hora_val = ""
        if not hora_val:
            hora_val = str(e.get("hora") or "")
        meta = " · ".join(filter(None, [hora_val, f"{e.get('user','')}@{e.get('host','')}".strip("@"), str(e.get("actor") or "")]))
        notes = str(e.get("notes") or "")
        vfile = str(e.get("version_file") or "")
        changelog_cards.append(
            "<div class='changelog-entry'>"
            "  <div class='entry-head'>"
            f"    <div class='meta'>{esc(meta)}</div>"
            f"    <div class='badges'><span class='badge {esc(cls)}'>{esc(label)}</span></div>"
            "  </div>"
            f"  <div class='notes'>{esc(notes)}</div>"
            + (f"<div class='kv'><span class='k'>file</span><span class='v mono'>{esc(vfile)}</span></div>" if vfile else "")
            + "</div>"
        )

    html_doc = f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>CHANGEBACKLOG</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, 'Helvetica Neue', sans-serif;
      font-size: 14px;
      line-height: 1.6;
      color: #172B4D;
      background: #FFFFFF;
      padding: 40px 20px;
      max-width: 1400px;
      margin: 0 auto;
    }}

    h1 {{ font-size: 26px; font-weight: 800; margin-bottom: 10px; }}
    .subtitle {{ color: #5E6C84; margin-bottom: 18px; }}

    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}

    .panel {{
      border: 1px solid #DFE1E6;
      border-radius: 12px;
      background: #FFFFFF;
      padding: 14px 14px;
      overflow: hidden;
    }}

    .panel-title {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 12px;
      margin-bottom: 10px;
    }}

    .panel-title h2 {{ font-size: 18px; margin: 0; }}
    .panel-title .hint {{ color: #5E6C84; font-size: 12px; }}

    .date-header {{
      font-size: 16px;
      font-weight: 700;
      color: #172B4D;
      margin-bottom: 10px;
      margin-top: 18px;
      padding-top: 10px;
      border-top: 1px solid #DFE1E6;
    }}
    .date-header:first-of-type {{ margin-top: 0; border-top: 0; padding-top: 0; }}

    .changelog-entry {{
      margin-bottom: 12px;
      padding: 12px 12px;
      border: 1px solid #DFE1E6;
      border-radius: 10px;
      background: #FAFBFC;
      transition: box-shadow 120ms ease, transform 120ms ease, opacity 120ms ease;
    }}

    .entry-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
      margin-bottom: 8px;
    }}

    .meta {{ color: #5E6C84; font-size: 12px; }}
    .badges {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }}

    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 800;
      color: #FFFFFF;
      white-space: nowrap;
    }}

    .badge.ok {{ background: #2DA44E; }}
    .badge.error {{ background: #D1242F; }}
    .badge.info {{ background: #0969DA; }}
    .badge.warn {{ background: #BF8700; }}

    .card-title {{ font-weight: 800; margin-bottom: 4px; color: #172B4D; }}
    .notes {{ margin: 6px 0; }}

    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; }}

    .kv {{ display: grid; grid-template-columns: 46px 1fr; gap: 8px; margin-top: 6px; }}
    .k {{ color: #5E6C84; font-weight: 700; }}
    .v {{ color: #172B4D; }}

    .backlog-group {{ margin-bottom: 14px; }}
    .backlog-group h3 {{ margin: 0 0 6px 2px; font-size: 14px; color: #172B4D; }}

    /* Drag-and-drop backlog */
    .backlog-list .changelog-entry {{ cursor: grab; }}
    .backlog-list .changelog-entry.dragging {{ opacity: 0.7; box-shadow: 0 6px 18px rgba(0,0,0,0.08); transform: scale(1.01); }}

    @media (max-width: 1100px) {{
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <h1>CHANGEBACKLOG</h1>
  <div class='subtitle'>Backlog + cambios realizados en una sola vista. Regenera con: <span class='mono'>python3 logs/generate_status_html.py --stdout &gt; logs/STATUS.html</span></div>

  <div class='grid'>
    <div class='panel'>
      <div class='panel-title'>
        <h2>BACKLOG (Pendientes)</h2>
        <div class='hint'>Archivo: <span class='mono'>{esc(backlog_path.as_posix())}</span>{(' · mtime: <span class="mono">' + esc(mtime) + '</span>') if mtime else ''}</div>
      </div>
      {backlog_html}
    </div>

    <div class='panel'>
      <div class='panel-title'>
        <h2>CHANGELOG (Hechos recientes)</h2>
        <div class='hint'>Fuente: <span class='mono'>{esc(Path(args.log).as_posix())}</span></div>
      </div>
      {''.join(changelog_cards) if changelog_cards else "<div class='notes'>Sin cambios</div>"}
    </div>
  </div>
  <script>
  // Permite reordenar visualmente las tarjetas del backlog (3 listas: prioridad, sin prioridad, trash).
  document.addEventListener('DOMContentLoaded', () => {{
    const lists = document.querySelectorAll('.backlog-list');
    if (!lists.length) return;

    let dragging = null;

    const makeDraggable = (el) => {{
      el.setAttribute('draggable', 'true');
      el.addEventListener('dragstart', () => {{ dragging = el; el.classList.add('dragging'); }});
      el.addEventListener('dragend', () => {{ el.classList.remove('dragging'); dragging = null; }});
    }};

    lists.forEach((list) => {{
      list.querySelectorAll('.changelog-entry').forEach(makeDraggable);
      list.addEventListener('dragover', (e) => {{
        e.preventDefault();
        if (!dragging) return;
        const cards = Array.from(list.querySelectorAll('.changelog-entry:not(.dragging)'));
        const next = cards.find(card => {{
          const box = card.getBoundingClientRect();
          return e.clientY < box.top + box.height / 2;
        }});
        if (next) {{ list.insertBefore(dragging, next); }} else {{ list.appendChild(dragging); }}
      }});
    }});
  }});
  </script>
</body>
</html>
"""

    if args.stdout:
        print(html_doc)
        return

    Path(args.out).write_text(html_doc, encoding="utf-8")


if __name__ == "__main__":
    main()
