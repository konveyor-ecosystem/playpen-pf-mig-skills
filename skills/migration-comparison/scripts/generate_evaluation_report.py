#!/usr/bin/env python3
"""
Generate a self-contained HTML evaluation report from evaluation-results.json.

Tabs:
  1. Executive Summary — grade badges, deltas, one-line verdicts
  2. Problem Areas — cards grouped by severity
  3. Attempt Comparison — cross-attempt quadrant breakdown
  4. LLM Assessment — per-file adversarial results
  5. Detailed Scores — full pattern results per attempt
  6. File Changes — side-by-side diffs

Follows the same CSS design system as generate_comparison_report.py.
"""

from __future__ import annotations

import argparse
import html as html_mod
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def escape(text: Any) -> str:
    return html_mod.escape(str(text)) if text else ""


def grade_badge(grade: str, percent: int, size: str = "large") -> str:
    grade_colors: dict[str, tuple[str, str]] = {
        "A": ("#16a34a", "#dcfce7"),
        "B": ("#2563eb", "#dbeafe"),
        "C": ("#ca8a04", "#fef9c3"),
        "D": ("#ea580c", "#fff7ed"),
        "F": ("#dc2626", "#fee2e2"),
    }
    fg, bg = grade_colors.get(grade, ("#6b7280", "#f3f4f6"))
    if size == "large":
        return (
            f'<span style="display:inline-block;padding:8px 20px;border-radius:12px;'
            f'font-size:28px;font-weight:800;color:{fg};background:{bg}">'
            f'{grade} ({percent}%)</span>'
        )
    return (
        f'<span style="display:inline-block;padding:4px 12px;border-radius:8px;'
        f'font-size:16px;font-weight:700;color:{fg};background:{bg}">'
        f'{grade} ({percent}%)</span>'
    )


def severity_badge(severity: str) -> str:
    colors: dict[str, tuple[str, str]] = {
        "critical": ("#7f1d1d", "#fecaca"),
        "high": ("#dc2626", "#fee2e2"),
        "medium": ("#ea580c", "#fff7ed"),
        "low": ("#6b7280", "#f3f4f6"),
    }
    fg, bg = colors.get(severity, ("#6b7280", "#f3f4f6"))
    return f'<span class="badge" style="color:{fg};background:{bg}">{severity.upper()}</span>'


def source_badge(source: str) -> str:
    colors: dict[str, tuple[str, str]] = {
        "deterministic": ("#2563eb", "#dbeafe"),
        "adversarial": ("#7c3aed", "#ede9fe"),
    }
    fg, bg = colors.get(source, ("#6b7280", "#f3f4f6"))
    return f'<span class="badge" style="color:{fg};background:{bg}">{source}</span>'


def status_badge(status: str) -> str:
    colors: dict[str, tuple[str, str]] = {
        "correct": ("#16a34a", "#dcfce7"),
        "incorrect": ("#dc2626", "#fee2e2"),
        "missing": ("#ea580c", "#fff7ed"),
        "file_missing": ("#9333ea", "#f3e8ff"),
        "not_applicable": ("#6b7280", "#f3f4f6"),
        "real": ("#dc2626", "#fee2e2"),
        "not_real": ("#16a34a", "#dcfce7"),
    }
    fg, bg = colors.get(status, ("#6b7280", "#f3f4f6"))
    return f'<span class="badge" style="color:{fg};background:{bg}">{status}</span>'


def render_executive_summary(data: dict[str, Any]) -> str:
    attempt_scores = data.get("attempt_scores", {})
    comparisons = data.get("comparisons", {})
    problem_areas = data.get("problem_areas", [])

    parts: list[str] = []

    # Grade cards
    parts.append('<div class="status-grid">')
    for name, score in attempt_scores.items():
        composite_percent = score.get("composite_percent", score.get("overall_percent", 0))
        composite_grade = score.get("composite_grade", score.get("grade", "?"))
        det_percent = score.get("overall_percent", 0)
        llm_score = score.get("llm_score")

        parts.append(f'''<div class="status-item" style="text-align:center">
            <span class="status-label">{escape(name)}</span>
            {grade_badge(composite_grade, composite_percent)}
            <div style="margin-top:8px;font-size:13px;color:#6b7280">
                Det: {det_percent}%{f' | LLM: {llm_score:.0%}' if llm_score is not None else ''}
            </div>
        </div>''')
    parts.append('</div>')

    # Comparison deltas
    if comparisons:
        parts.append('<h3>Attempt Comparisons</h3>')
        for key, comp in comparisons.items():
            names = key.split("_vs_")
            name_a = names[0] if len(names) > 0 else "A"
            name_b = names[1] if len(names) > 1 else "B"
            delta = comp.get("delta", 0)
            a_adv = len(comp.get("a_advantages", []))
            b_adv = len(comp.get("b_advantages", []))
            ties_count = len(comp.get("ties", []))

            delta_color = "#16a34a" if delta > 0 else ("#dc2626" if delta < 0 else "#6b7280")
            delta_sign = "+" if delta > 0 else ""

            parts.append(f'''<div class="banner banner-info" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                <span><strong>{escape(name_a)}</strong> vs <strong>{escape(name_b)}</strong></span>
                <span>Delta: <strong style="color:{delta_color}">{delta_sign}{delta}pts</strong></span>
                <span>{escape(name_a)} leads: <strong>{a_adv}</strong> patterns</span>
                <span>{escape(name_b)} leads: <strong>{b_adv}</strong> patterns</span>
                <span>Tied: <strong>{ties_count}</strong></span>
            </div>''')

    # Problem area summary
    if problem_areas:
        critical = sum(1 for p in problem_areas if p.get("severity") == "critical")
        high = sum(1 for p in problem_areas if p.get("severity") == "high")
        medium = sum(1 for p in problem_areas if p.get("severity") == "medium")
        low = sum(1 for p in problem_areas if p.get("severity") == "low")

        parts.append('<h3>Problem Areas Overview</h3>')
        parts.append('<div class="info-row">')
        if critical:
            parts.append(f'<span>{severity_badge("critical")} {critical}</span>')
        if high:
            parts.append(f'<span>{severity_badge("high")} {high}</span>')
        if medium:
            parts.append(f'<span>{severity_badge("medium")} {medium}</span>')
        if low:
            parts.append(f'<span>{severity_badge("low")} {low}</span>')
        parts.append('</div>')

    return "\n".join(parts)


def render_problem_areas(data: dict[str, Any]) -> str:
    problem_areas: list[dict[str, Any]] = data.get("problem_areas", [])
    if not problem_areas:
        return '<p class="muted">No problem areas identified.</p>'

    parts: list[str] = []

    # Group by severity
    by_severity: dict[str, list[dict[str, Any]]] = {}
    for pa in problem_areas:
        sev = pa.get("severity", "low")
        by_severity.setdefault(sev, []).append(pa)

    for sev in ["critical", "high", "medium", "low"]:
        items = by_severity.get(sev, [])
        if not items:
            continue

        parts.append(f'<h3>{severity_badge(sev)} ({len(items)})</h3>')

        for pa in items:
            attempt = escape(pa.get("attempt", ""))
            desc = escape(pa.get("description", ""))
            source = pa.get("source", "deterministic")
            recommendation = escape(pa.get("recommendation", ""))
            affected = pa.get("affected_files", [])
            pattern_ids = pa.get("pattern_ids", [])
            confidence = pa.get("referee_confidence")

            parts.append('<div class="category-section">')
            parts.append(f'<div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">')
            parts.append(f'{source_badge(source)}')
            parts.append(f'<span class="badge" style="color:#475569;background:#f1f5f9">{attempt}</span>')
            if confidence is not None:
                parts.append(f'<span style="font-size:12px;color:#6b7280">Confidence: {confidence:.0%}</span>')
            parts.append('</div>')
            parts.append(f'<p style="margin-bottom:8px"><strong>{desc}</strong></p>')

            if recommendation:
                parts.append(f'<p style="color:#4b5563;font-size:14px;margin-bottom:8px">'
                             f'<em>Recommendation:</em> {recommendation}</p>')

            if pattern_ids:
                parts.append(f'<p style="font-size:13px;color:#6b7280">Patterns: '
                             f'{", ".join(f"<code>{escape(p)}</code>" for p in pattern_ids)}</p>')

            if affected:
                parts.append('<details style="margin-top:8px"><summary style="cursor:pointer;font-size:13px;color:#6b7280">'
                             f'Affected files ({len(affected)})</summary>')
                parts.append('<ul style="margin-top:4px">')
                for f in affected[:20]:
                    parts.append(f'<li style="font-size:13px"><code>{escape(f)}</code></li>')
                if len(affected) > 20:
                    parts.append(f'<li style="font-size:13px;color:#6b7280">... and {len(affected) - 20} more</li>')
                parts.append('</ul></details>')

            parts.append('</div>')

    return "\n".join(parts)


def render_attempt_comparison(data: dict[str, Any]) -> str:
    comparisons = data.get("comparisons", {})
    if not comparisons:
        return '<p class="muted">Only one attempt — no comparison available.</p>'

    parts: list[str] = []

    for key, comp in comparisons.items():
        names = key.split("_vs_")
        name_a = names[0] if len(names) > 0 else "A"
        name_b = names[1] if len(names) > 1 else "B"

        a_advantages: list[dict[str, Any]] = comp.get("a_advantages", [])
        b_advantages: list[dict[str, Any]] = comp.get("b_advantages", [])
        ties: list[str] = comp.get("ties", [])
        neither: list[str] = comp.get("neither", [])

        parts.append(f'<h3>{escape(name_a)} vs {escape(name_b)}</h3>')

        # Quadrant grid
        parts.append('<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px">')

        # Both correct
        parts.append(f'''<div class="category-section" style="border-left:4px solid #16a34a">
            <h4 style="color:#16a34a">Both Correct ({len(ties)})</h4>
            <p style="font-size:13px;color:#6b7280">{", ".join(f"<code>{escape(t)}</code>" for t in ties[:10])}{" ..." if len(ties) > 10 else ""}</p>
        </div>''')

        # A leads
        parts.append(f'''<div class="category-section" style="border-left:4px solid #2563eb">
            <h4 style="color:#2563eb">{escape(name_a)} Leads ({len(a_advantages)})</h4>''')
        if a_advantages:
            parts.append('<ul style="margin:0;padding-left:20px">')
            for adv in a_advantages:
                parts.append(f'<li style="font-size:13px"><code>{escape(adv.get("pattern_id", ""))}</code>'
                             f' — {escape(adv.get("name", ""))}'
                             f' ({status_badge(adv.get("a_status", ""))} vs {status_badge(adv.get("b_status", ""))})</li>')
            parts.append('</ul>')
        parts.append('</div>')

        # B leads
        parts.append(f'''<div class="category-section" style="border-left:4px solid #7c3aed">
            <h4 style="color:#7c3aed">{escape(name_b)} Leads ({len(b_advantages)})</h4>''')
        if b_advantages:
            parts.append('<ul style="margin:0;padding-left:20px">')
            for adv in b_advantages:
                parts.append(f'<li style="font-size:13px"><code>{escape(adv.get("pattern_id", ""))}</code>'
                             f' — {escape(adv.get("name", ""))}'
                             f' ({status_badge(adv.get("a_status", ""))} vs {status_badge(adv.get("b_status", ""))})</li>')
            parts.append('</ul>')
        parts.append('</div>')

        # Neither
        parts.append(f'''<div class="category-section" style="border-left:4px solid #dc2626">
            <h4 style="color:#dc2626">Neither Correct ({len(neither)})</h4>
            <p style="font-size:13px;color:#6b7280">{", ".join(f"<code>{escape(n)}</code>" for n in neither[:10])}{" ..." if len(neither) > 10 else ""}</p>
        </div>''')

        parts.append('</div>')

    return "\n".join(parts)


def render_llm_assessment(data: dict[str, Any]) -> str:
    llm_summary = data.get("llm_summary")
    if not llm_summary:
        return '<p class="muted">No LLM assessment available. Run adversarial subagents to generate LLM assessment.</p>'

    parts: list[str] = []

    # Summary cards
    parts.append('<div class="status-grid">')
    parts.append(f'''<div class="status-item">
        <span class="status-label">Files Assessed</span>
        <span style="font-size:24px;font-weight:700;color:#2563eb">{llm_summary.get("files_assessed", 0)}</span>
    </div>''')
    parts.append(f'''<div class="status-item">
        <span class="status-label">Issues Found</span>
        <span style="font-size:24px;font-weight:700;color:#ea580c">{llm_summary.get("issues_found", 0)}</span>
    </div>''')
    parts.append(f'''<div class="status-item">
        <span class="status-label">Issues Confirmed</span>
        <span style="font-size:24px;font-weight:700;color:#dc2626">{llm_summary.get("issues_confirmed", 0)}</span>
    </div>''')
    avg_score = llm_summary.get("average_file_score", 0)
    avg_color = "#16a34a" if avg_score >= 0.8 else ("#ea580c" if avg_score >= 0.6 else "#dc2626")
    parts.append(f'''<div class="status-item">
        <span class="status-label">Avg File Score</span>
        <span style="font-size:24px;font-weight:700;color:{avg_color}">{avg_score:.0%}</span>
    </div>''')
    parts.append('</div>')

    # Load adversarial data if llm-assessment.json exists in pairwise data
    # (the full adversarial results are in the evaluation-results.json problem_areas)
    problem_areas = data.get("problem_areas", [])
    llm_problems = [p for p in problem_areas if p.get("source") == "adversarial"]

    if llm_problems:
        parts.append('<h3>LLM-Identified Issues</h3>')
        parts.append('<table><thead><tr>')
        parts.append('<th>Attempt</th><th>File</th><th>Severity</th><th>Description</th><th>Confidence</th>')
        parts.append('</tr></thead><tbody>')

        for pa in llm_problems:
            attempt = escape(pa.get("attempt", ""))
            files = pa.get("affected_files", [])
            file_str = escape(files[0] if files else "")
            sev = pa.get("severity", "medium")
            desc = escape(pa.get("description", ""))
            conf = pa.get("referee_confidence")
            conf_str = f"{conf:.0%}" if conf is not None else "—"

            parts.append(f'<tr><td>{attempt}</td><td><code>{file_str}</code></td>')
            parts.append(f'<td>{severity_badge(sev)}</td><td>{desc}</td>')
            parts.append(f'<td>{conf_str}</td></tr>')

        parts.append('</tbody></table>')

    return "\n".join(parts)


def render_detailed_scores(data: dict[str, Any]) -> str:
    pairwise_data: dict[str, Any] = data.get("pairwise_data", {})
    if not pairwise_data:
        return '<p class="muted">No detailed scoring data available.</p>'

    parts: list[str] = []

    for attempt_name, scoring in pairwise_data.items():
        score = scoring.get("score", {})
        grade = score.get("grade", "?")
        percent = score.get("overall_percent", 0)
        pattern_results: list[dict[str, Any]] = scoring.get("pattern_results", [])

        parts.append(f'<h3>{escape(attempt_name)} — {grade_badge(grade, percent, "small")}</h3>')

        # Component breakdown
        components = score.get("components", {})
        fc = components.get("file_coverage", {})
        ps = components.get("pattern_score", {})
        np_ = components.get("noise_penalty", {})

        parts.append('<div class="info-row">')
        parts.append(f'<span>File Coverage: <strong>{fc.get("score", 0):.0%}</strong>'
                     f' ({fc.get("matched", 0)}/{fc.get("total", 0)})</span>')
        parts.append(f'<span>Pattern Score: <strong>{ps.get("score", 0):.0%}</strong></span>')
        parts.append(f'<span>Noise: <strong>{np_.get("raw_penalty", 0):.0%}</strong>'
                     f' ({np_.get("instance_count", 0)} instances)</span>')
        parts.append('</div>')

        if pattern_results:
            applicable = [p for p in pattern_results if p.get("status") != "not_applicable"]
            if applicable:
                parts.append('<table><thead><tr>')
                parts.append('<th>Pattern</th><th>Complexity</th><th>Status</th><th>Message</th>')
                parts.append('</tr></thead><tbody>')

                complexity_colors: dict[str, tuple[str, str]] = {
                    "trivial": ("#6b7280", "#f3f4f6"),
                    "moderate": ("#b45309", "#fef3c7"),
                    "complex": ("#dc2626", "#fee2e2"),
                }

                for pr in applicable:
                    name = escape(pr.get("name", pr.get("pattern_id", "")))
                    complexity = pr.get("complexity", "moderate")
                    p_status = pr.get("status", "not_applicable")
                    message = escape(pr.get("message", ""))
                    c_fg, c_bg = complexity_colors.get(complexity, ("#6b7280", "#f3f4f6"))

                    parts.append(f'<tr><td><strong>{name}</strong></td>')
                    parts.append(f'<td><span class="badge" style="color:{c_fg};background:{c_bg}">{complexity}</span></td>')
                    parts.append(f'<td>{status_badge(p_status)}</td>')
                    parts.append(f'<td style="font-size:13px">{message}</td></tr>')

                parts.append('</tbody></table>')

    return "\n".join(parts)


def render_file_changes(data: dict[str, Any]) -> str:
    pairwise_data: dict[str, Any] = data.get("pairwise_data", {})
    if not pairwise_data:
        return '<p class="muted">No file change data available.</p>'

    parts: list[str] = []

    # Summary across all attempts
    for attempt_name, scoring in pairwise_data.items():
        file_results: list[dict[str, Any]] = scoring.get("file_results", [])
        if not file_results:
            continue

        parts.append(f'<h3>{escape(attempt_name)} — File Results</h3>')
        parts.append('<table><thead><tr>')
        parts.append('<th>File</th><th>Pattern Statuses</th><th>Noise</th>')
        parts.append('</tr></thead><tbody>')

        for fr in file_results:
            path = escape(fr.get("path", ""))
            pattern_statuses: dict[str, str] = fr.get("pattern_statuses", {})
            noise_count = fr.get("noise_count", 0)

            statuses_html = " ".join(
                f'{status_badge(s)}'
                for s in sorted(set(pattern_statuses.values()))
                if s != "not_applicable"
            ) or '<span class="muted">—</span>'

            noise_html = f'<span style="color:#dc2626">{noise_count}</span>' if noise_count else '—'

            parts.append(f'<tr><td><code>{path}</code></td>')
            parts.append(f'<td>{statuses_html}</td>')
            parts.append(f'<td>{noise_html}</td></tr>')

        parts.append('</tbody></table>')

    return "\n".join(parts)


def generate_html(data: dict[str, Any]) -> str:
    metadata = data.get("metadata", {})
    attempt_scores = data.get("attempt_scores", {})
    target = metadata.get("target", "")
    timestamp = metadata.get("timestamp", datetime.now().isoformat())

    try:
        ts_display = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except Exception:
        ts_display = timestamp

    attempt_names = sorted(attempt_scores.keys())
    header_attempts = " vs ".join(attempt_names)

    summary_html = render_executive_summary(data)
    problems_html = render_problem_areas(data)
    comparison_html = render_attempt_comparison(data)
    llm_html = render_llm_assessment(data)
    scores_html = render_detailed_scores(data)
    files_html = render_file_changes(data)

    has_comparisons = bool(data.get("comparisons"))
    has_llm = data.get("llm_summary") is not None

    comparison_tab = '<button class="tab" onclick="switchTab(\'comparison\')">Attempt Comparison</button>' if has_comparisons else ""
    comparison_section = f'<div id="comparison" class="tab-content" data-title="Attempt Comparison">{comparison_html}</div>' if has_comparisons else ""

    llm_tab = '<button class="tab" onclick="switchTab(\'llm\')">LLM Assessment</button>'
    llm_section = f'<div id="llm" class="tab-content" data-title="LLM Assessment">{llm_html}</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Migration Evaluation - {escape(header_attempts)}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #1f2937; background: #f9fafb; line-height: 1.5; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
  header {{ background: #1e293b; color: white; padding: 32px; margin: -24px -24px 24px; }}
  header h1 {{ font-size: 24px; margin-bottom: 8px; }}
  .header-meta {{ display: flex; gap: 24px; flex-wrap: wrap; font-size: 14px; color: #94a3b8; }}
  .header-meta span {{ display: flex; align-items: center; gap: 4px; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
  .tabs {{ display: flex; gap: 0; border-bottom: 2px solid #e5e7eb; margin-bottom: 24px; overflow-x: auto; }}
  .tab {{ background: none; border: none; padding: 12px 24px; cursor: pointer; font-size: 14px; font-weight: 500; color: #6b7280; border-bottom: 2px solid transparent; margin-bottom: -2px; white-space: nowrap; }}
  .tab:hover {{ color: #1f2937; }}
  .tab.active {{ color: #2563eb; border-bottom-color: #2563eb; }}
  .tab-content {{ display: none; }}
  .tab-content.active {{ display: block; }}
  .banner {{ padding: 16px 20px; border-radius: 8px; margin-bottom: 16px; font-weight: 500; }}
  .banner-info {{ background: #dbeafe; color: #2563eb; }}
  .banner-muted {{ background: #f3f4f6; color: #6b7280; }}
  .status-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; margin-bottom: 24px; }}
  .status-item {{ background: white; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 8px; }}
  .status-label {{ font-size: 13px; color: #6b7280; font-weight: 500; }}
  .info-row {{ display: flex; gap: 24px; flex-wrap: wrap; padding: 12px 0; margin-bottom: 16px; font-size: 14px; color: #4b5563; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  th {{ background: #f8fafc; text-align: left; padding: 10px 16px; font-size: 13px; font-weight: 600; color: #475569; border-bottom: 1px solid #e5e7eb; }}
  td {{ padding: 10px 16px; font-size: 14px; border-bottom: 1px solid #f1f5f9; }}
  code {{ background: #f1f5f9; padding: 1px 5px; border-radius: 3px; font-size: 13px; }}
  h3 {{ font-size: 18px; margin-bottom: 12px; color: #1e293b; }}
  h4 {{ font-size: 15px; margin-bottom: 8px; color: #334155; }}
  .muted {{ color: #9ca3af; font-style: italic; }}
  .category-section {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  details summary {{ font-size: 13px; color: #6b7280; cursor: pointer; }}
  details summary:hover {{ color: #1f2937; }}
  @media print {{
    body {{ background: white; }}
    .container {{ max-width: none; padding: 0; }}
    header {{ background: #1e293b !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .tab-content {{ display: block !important; page-break-inside: avoid; }}
    .tabs {{ display: none; }}
    .tab-content::before {{ content: attr(data-title); display: block; font-size: 20px; font-weight: 700; margin: 24px 0 12px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Migration Evaluation Report</h1>
    <div class="header-meta">
      <span>{escape(header_attempts)}</span>
      {f'<span>Target: {escape(target)}</span>' if target else ''}
      <span>{ts_display}</span>
    </div>
  </header>

  <div class="tabs">
    <button class="tab active" onclick="switchTab('summary')">Executive Summary</button>
    <button class="tab" onclick="switchTab('problems')">Problem Areas</button>
    {comparison_tab}
    {llm_tab}
    <button class="tab" onclick="switchTab('scores')">Detailed Scores</button>
    <button class="tab" onclick="switchTab('files')">File Changes</button>
  </div>

  <div id="summary" class="tab-content active" data-title="Executive Summary">
    {summary_html}
  </div>

  <div id="problems" class="tab-content" data-title="Problem Areas">
    {problems_html}
  </div>

  {comparison_section}

  {llm_section}

  <div id="scores" class="tab-content" data-title="Detailed Scores">
    {scores_html}
  </div>

  <div id="files" class="tab-content" data-title="File Changes">
    {files_html}
  </div>
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate HTML evaluation report from evaluation-results.json"
    )
    parser.add_argument(
        "work_dir",
        help="Path to the workspace directory containing evaluation-results.json",
    )
    parser.add_argument(
        "--output",
        help="Output path for the HTML report (default: <work_dir>/evaluation-report.html)",
    )

    args = parser.parse_args()
    work_dir = Path(args.work_dir)

    if not work_dir.is_dir():
        print(f"Error: Directory not found: {work_dir}", file=sys.stderr)
        sys.exit(1)

    results_path = work_dir / "evaluation-results.json"
    if not results_path.exists():
        print(f"Error: evaluation-results.json not found in {work_dir}", file=sys.stderr)
        sys.exit(1)

    with open(results_path, "r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)

    html_output = generate_html(data)

    output_path = Path(args.output) if args.output else work_dir / "evaluation-report.html"
    output_path.write_text(html_output, encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
