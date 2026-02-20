#!/usr/bin/env python3
"""
Generate a self-contained HTML migration report from report-data.json.

Reads structured migration data and produces an HTML report with three sections:
Action Required, What Was Done, and Visual Comparison.
"""

import json
import base64
import argparse
import sys
from pathlib import Path
from datetime import datetime


def load_report_data(work_dir):
    json_path = Path(work_dir) / "report-data.json"
    if not json_path.exists():
        print(f"Error: report-data.json not found in {work_dir}", file=sys.stderr)
        print("Suggestion: Generate report-data.json before running this script.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in report-data.json: {e}", file=sys.stderr)
        sys.exit(1)


def encode_image(path):
    try:
        data = Path(path).read_bytes()
        ext = Path(path).suffix.lower()
        mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".gif": "image/gif", ".webp": "image/webp"}.get(ext, "image/png")
        return f"data:{mime};base64,{base64.b64encode(data).decode()}"
    except Exception:
        return None


def status_badge(status):
    colors = {
        "PASS": ("#16a34a", "#dcfce7"),
        "FAIL": ("#dc2626", "#fee2e2"),
        "NONE": ("#6b7280", "#f3f4f6"),
        "complete": ("#16a34a", "#dcfce7"),
        "incomplete": ("#dc2626", "#fee2e2"),
        "pass": ("#16a34a", "#dcfce7"),
        "fail": ("#dc2626", "#fee2e2"),
        "info": ("#2563eb", "#dbeafe"),
    }
    fg, bg = colors.get(status, ("#6b7280", "#f3f4f6"))
    return f'<span class="badge" style="color:{fg};background:{bg}">{status}</span>'


def render_action_required(items):
    if not items:
        return '<div class="banner banner-success">No action required. Migration completed successfully.</div>'

    type_labels = {
        "unresolved_issue": "Unresolved Issue",
        "false_positive": "False Positive to Verify",
        "visual_review": "Visual Change to Review",
        "manual_intervention": "Manual Intervention Needed",
    }
    type_colors = {
        "unresolved_issue": "#dc2626",
        "false_positive": "#d97706",
        "visual_review": "#2563eb",
        "manual_intervention": "#7c3aed",
    }

    cards = []
    for item in items:
        item_type = item.get("type", "unresolved_issue")
        color = type_colors.get(item_type, "#6b7280")
        label = type_labels.get(item_type, item_type)
        desc = item.get("description", "")
        rec = item.get("recommendation", "")
        details = item.get("details", "")
        page = item.get("page", "")

        card = f'<div class="card" style="border-left:4px solid {color}">'
        card += f'<div class="card-header"><span class="card-type" style="color:{color}">{label}</span>'
        if page:
            card += f'<span class="card-page">Page: {page}</span>'
        card += '</div>'
        card += f'<p>{desc}</p>'
        if rec:
            card += f'<p class="recommendation"><strong>Recommendation:</strong> {rec}</p>'
        if details:
            card += f'<p class="details">{details}</p>'
        card += '</div>'
        cards.append(card)

    return "\n".join(cards)


def render_what_was_done(data):
    summary = data.get("summary", {})
    groups = data.get("groups", [])
    rounds = data.get("rounds", [])
    kantra = data.get("kantra_residual", {})

    # Status grid
    grid_items = [
        ("Build", summary.get("build", "NONE")),
        ("Unit Tests", summary.get("unit_tests", "NONE")),
        ("E2E Tests", summary.get("e2e_tests", "NONE")),
        ("Lint", summary.get("lint", "NONE")),
        ("Target Validation", summary.get("target_validation", "NONE")),
    ]
    grid = '<div class="status-grid">'
    for label, val in grid_items:
        grid += f'<div class="status-item"><span class="status-label">{label}</span>{status_badge(val)}</div>'
    grid += '</div>'

    # Groups table
    groups_html = ""
    if groups:
        groups_html = '<h3>Groups</h3><table><thead><tr><th>Group</th><th>Status</th><th>Issues Fixed</th><th>Description</th></tr></thead><tbody>'
        for g in groups:
            groups_html += f'<tr><td>{g.get("name", "")}</td><td>{status_badge(g.get("status", "incomplete"))}</td>'
            groups_html += f'<td>{g.get("issues_fixed", 0)}</td><td>{g.get("description", "")}</td></tr>'
        groups_html += '</tbody></table>'

    # Round log
    rounds_html = ""
    if rounds:
        rounds_html = '<h3>Round Log</h3><details><summary>Show all rounds</summary><table>'
        rounds_html += '<thead><tr><th>Round</th><th>Group</th><th>Fixed</th><th>New Issues</th><th>Build</th><th>Tests</th></tr></thead><tbody>'
        for r in rounds:
            rounds_html += f'<tr><td>{r.get("number", "")}</td><td>{r.get("group", "")}</td>'
            rounds_html += f'<td>{r.get("issues_fixed", 0)}</td><td>{r.get("new_issues", 0)}</td>'
            rounds_html += f'<td>{status_badge(r.get("build", "NONE"))}</td><td>{r.get("tests", "N/A")}</td></tr>'
        rounds_html += '</tbody></table></details>'

    # Kantra residual
    kantra_html = ""
    if kantra and kantra.get("categories"):
        kantra_html = f'<h3>Kantra Residual ({kantra.get("total_incidents", 0)} incidents)</h3>'
        kantra_html += '<table><thead><tr><th>Rule</th><th>Count</th><th>Reason</th></tr></thead><tbody>'
        for cat in kantra.get("categories", []):
            kantra_html += f'<tr><td>{cat.get("rule", "")}</td><td>{cat.get("count", 0)}</td><td>{cat.get("reason", "")}</td></tr>'
        kantra_html += '</tbody></table>'

    return f"{grid}{groups_html}{rounds_html}{kantra_html}"


def render_visual_comparison(visual, work_dir):
    if not visual or not visual.get("has_screenshots"):
        return '<p class="muted">No visual testing was performed for this migration.</p>'

    pages = visual.get("pages", [])
    if not pages:
        return '<p class="muted">No screenshots captured.</p>'

    baseline_dir = visual.get("baseline_dir", "baseline")
    post_dir = visual.get("post_migration_dir", "post-migration")

    html = ""
    for page in pages:
        name = page.get("name", "Unknown")
        status = page.get("status", "info")
        notes = page.get("notes", "")
        baseline_rel = page.get("baseline", "")
        post_rel = page.get("post_migration", "")

        # Per-page paths may be relative to work_dir (e.g. "baseline/login.png")
        # or just filenames (e.g. "login.png"). Resolve accordingly.
        if baseline_rel and "/" not in baseline_rel:
            baseline_path = Path(work_dir) / baseline_dir / baseline_rel
        else:
            baseline_path = Path(work_dir) / baseline_rel

        if post_rel and "/" not in post_rel:
            post_path = Path(work_dir) / post_dir / post_rel
        else:
            post_path = Path(work_dir) / post_rel

        baseline_src = encode_image(baseline_path)
        post_src = encode_image(post_path)

        placeholder = "data:image/svg+xml;base64," + base64.b64encode(
            b'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">'
            b'<rect fill="#f3f4f6" width="400" height="300"/>'
            b'<text x="200" y="150" text-anchor="middle" fill="#9ca3af" font-size="16">Screenshot not available</text>'
            b'</svg>'
        ).decode()

        html += f'<div class="visual-page"><h3>{name} {status_badge(status)}</h3>'
        if notes:
            html += f'<p class="notes">{notes}</p>'
        html += '<div class="screenshots">'
        html += f'<div class="screenshot"><h4>Baseline</h4><img src="{baseline_src or placeholder}" alt="Baseline - {name}"></div>'
        html += f'<div class="screenshot"><h4>Post-Migration</h4><img src="{post_src or placeholder}" alt="Post-migration - {name}"></div>'
        html += '</div></div>'

    return html


def generate_html(data, work_dir):
    migration = data.get("migration", {})
    summary = data.get("summary", {})

    project = migration.get("project", "Unknown Project")
    source = migration.get("source", "Unknown")
    target = migration.get("target", "Unknown")
    status = summary.get("status", "incomplete")
    timestamp = migration.get("timestamp", datetime.now().isoformat())
    total_rounds = summary.get("total_rounds", 0)

    try:
        ts_display = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except Exception:
        ts_display = timestamp

    action_html = render_action_required(data.get("action_required", []))
    done_html = render_what_was_done(data)
    visual_html = render_visual_comparison(data.get("visual"), work_dir)

    has_visual = data.get("visual", {}).get("has_screenshots", False)
    visual_tab = f'<button class="tab" onclick="switchTab(\'visual\')">Visual Comparison</button>' if has_visual else ""
    visual_section = f'<div id="visual" class="tab-content">{visual_html}</div>' if has_visual else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Migration Report - {project}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #1f2937; background: #f9fafb; line-height: 1.5; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
  header {{ background: #1e293b; color: white; padding: 32px; margin: -24px -24px 24px; }}
  header h1 {{ font-size: 24px; margin-bottom: 8px; }}
  .header-meta {{ display: flex; gap: 24px; flex-wrap: wrap; font-size: 14px; color: #94a3b8; }}
  .header-meta span {{ display: flex; align-items: center; gap: 4px; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
  .tabs {{ display: flex; gap: 0; border-bottom: 2px solid #e5e7eb; margin-bottom: 24px; }}
  .tab {{ background: none; border: none; padding: 12px 24px; cursor: pointer; font-size: 14px; font-weight: 500; color: #6b7280; border-bottom: 2px solid transparent; margin-bottom: -2px; }}
  .tab:hover {{ color: #1f2937; }}
  .tab.active {{ color: #2563eb; border-bottom-color: #2563eb; }}
  .tab-content {{ display: none; }}
  .tab-content.active {{ display: block; }}
  .banner {{ padding: 16px 20px; border-radius: 8px; margin-bottom: 16px; font-weight: 500; }}
  .banner-success {{ background: #dcfce7; color: #16a34a; }}
  .card {{ background: white; border-radius: 8px; padding: 16px 20px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
  .card-type {{ font-weight: 600; font-size: 13px; text-transform: uppercase; }}
  .card-page {{ font-size: 13px; color: #6b7280; }}
  .recommendation {{ color: #4b5563; font-size: 14px; }}
  .details {{ color: #6b7280; font-size: 13px; }}
  .status-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; margin-bottom: 24px; }}
  .status-item {{ background: white; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 8px; }}
  .status-label {{ font-size: 13px; color: #6b7280; font-weight: 500; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  th {{ background: #f8fafc; text-align: left; padding: 10px 16px; font-size: 13px; font-weight: 600; color: #475569; border-bottom: 1px solid #e5e7eb; }}
  td {{ padding: 10px 16px; font-size: 14px; border-bottom: 1px solid #f1f5f9; }}
  details {{ margin-bottom: 24px; }}
  summary {{ cursor: pointer; font-weight: 500; padding: 8px 0; color: #2563eb; }}
  h3 {{ font-size: 18px; margin-bottom: 12px; color: #1e293b; }}
  .visual-page {{ margin-bottom: 32px; }}
  .screenshots {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .screenshot {{ flex: 1; min-width: 300px; }}
  .screenshot h4 {{ font-size: 14px; color: #6b7280; margin-bottom: 8px; }}
  .screenshot img {{ width: 100%; border: 1px solid #e5e7eb; border-radius: 8px; }}
  .notes {{ color: #6b7280; font-size: 14px; margin-bottom: 12px; }}
  .muted {{ color: #9ca3af; font-style: italic; }}
  @media print {{
    body {{ background: white; }}
    .container {{ max-width: none; padding: 0; }}
    header {{ background: #1e293b !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .tab-content {{ display: block !important; page-break-inside: avoid; }}
    .tabs {{ display: none; }}
    .tab-content::before {{ content: attr(data-title); display: block; font-size: 20px; font-weight: 700; margin: 24px 0 12px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
    .screenshot img {{ max-height: 400px; object-fit: contain; }}
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>{project}</h1>
    <div class="header-meta">
      <span>{source} &rarr; {target}</span>
      <span>{status_badge(status)}</span>
      <span>{total_rounds} rounds</span>
      <span>{ts_display}</span>
    </div>
  </header>

  <div class="tabs">
    <button class="tab active" onclick="switchTab('action')">Action Required</button>
    <button class="tab" onclick="switchTab('done')">What Was Done</button>
    {visual_tab}
  </div>

  <div id="action" class="tab-content active" data-title="Action Required">
    {action_html}
  </div>

  <div id="done" class="tab-content" data-title="What Was Done">
    {done_html}
  </div>

  {visual_section}

</div>
<script>
function switchTab(id) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  event.target.classList.add('active');
}}
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(
        description="Generate a self-contained HTML migration report from report-data.json"
    )
    parser.add_argument(
        "work_dir",
        help="Path to the migration workspace directory containing report-data.json"
    )
    parser.add_argument(
        "--output",
        help="Output path for the HTML report (default: <work_dir>/report.html)"
    )

    args = parser.parse_args()
    work_dir = Path(args.work_dir)

    if not work_dir.is_dir():
        print(f"Error: Directory not found: {work_dir}", file=sys.stderr)
        sys.exit(1)

    data = load_report_data(work_dir)
    html = generate_html(data, work_dir)

    output_path = Path(args.output) if args.output else work_dir / "report.html"
    output_path.write_text(html, encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
