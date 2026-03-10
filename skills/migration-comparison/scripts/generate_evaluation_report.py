#!/usr/bin/env python3
"""
Generate a self-contained HTML evaluation report from evaluation-results.json.

Tabs:
  1. Executive Summary — grade badges, visual score breakdown, deltas
  2. Problem Areas — cards grouped by severity with code context & filtering
  3. Attempt Comparison — cross-attempt quadrant breakdown
  4. LLM Assessment — per-file expandable issue details
  5. Detailed Scores — full pattern results with file:line details
  6. File Changes — expandable diffs per file

Follows the same CSS design system as generate_comparison_report.py.
"""

from __future__ import annotations

import argparse
import html as html_mod
import json
import re
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


def category_badge(cat: str) -> str:
    colors: dict[str, tuple[str, str]] = {
        "structural": ("#b45309", "#fef3c7"),
        "semantic": ("#7c3aed", "#ede9fe"),
        "api_changes": ("#dc2626", "#fee2e2"),
        "cosmetic": ("#6b7280", "#f3f4f6"),
        "additive": ("#16a34a", "#dcfce7"),
        "subtractive": ("#ea580c", "#fff7ed"),
    }
    fg, bg = colors.get(cat, ("#6b7280", "#f3f4f6"))
    label = cat.replace("_", " ").title()
    return f'<span class="badge" style="color:{fg};background:{bg}">{label}</span>'


def parse_unified_diff(diff_text: str) -> list[tuple[str, str, str]]:
    """Parse unified diff into list of (line_number, css_class, text) tuples for inline display."""
    result: list[tuple[str, str, str]] = []
    left_num = 0
    right_num = 0

    for line in diff_text.split("\n"):
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("@@"):
            match = re.match(r"@@ -(\d+)", line)
            if match:
                left_num = int(match.group(1)) - 1
            match2 = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", line)
            if match2:
                right_num = int(match2.group(1)) - 1
            result.append(("", "diff-hunk", line))
            continue
        if line.startswith("-"):
            left_num += 1
            result.append((str(left_num), "diff-del", line))
        elif line.startswith("+"):
            right_num += 1
            result.append((str(right_num), "diff-add", line))
        elif line.startswith(" ") or line == "":
            left_num += 1
            right_num += 1
            result.append((str(right_num), "", line[1:] if line.startswith(" ") else ""))

    return result


def _build_pattern_detail_index(data: dict[str, Any]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Build index: attempt -> pattern_id -> list of detail dicts."""
    index: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for attempt_name, scoring in data.get("pairwise_data", {}).items():
        pat_index: dict[str, list[dict[str, Any]]] = {}
        for pr in scoring.get("pattern_results", []):
            pat_index[pr.get("pattern_id", "")] = pr.get("details", [])
        index[attempt_name] = pat_index
    return index


def _build_diff_index(comparison_data: dict[str, dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Build index: attempt -> file_path -> text_diff from comparison data."""
    index: dict[str, dict[str, str]] = {}
    for attempt_name, comp_data in comparison_data.items():
        file_diffs: dict[str, str] = {}
        for f in comp_data.get("files", {}).get("modified", []):
            path = f.get("path", "")
            diff = f.get("text_diff", "")
            if path and diff:
                file_diffs[path] = diff
        index[attempt_name] = file_diffs
    return index


def _extract_diff_snippet(diff_text: str, max_lines: int = 20) -> str:
    """Extract a snippet from a diff, centered around the first change."""
    lines = diff_text.split("\n")
    # Find first actual change line
    first_change = 0
    for i, line in enumerate(lines):
        if line.startswith("+") or line.startswith("-"):
            if not line.startswith("---") and not line.startswith("+++"):
                first_change = i
                break

    start = max(0, first_change - 5)
    end = min(len(lines), start + max_lines)
    snippet_lines = lines[start:end]

    parts: list[str] = []
    for line in snippet_lines:
        escaped = escape(line)
        if line.startswith("+") and not line.startswith("+++"):
            parts.append(f'<span class="diff-add">{escaped}</span>')
        elif line.startswith("-") and not line.startswith("---"):
            parts.append(f'<span class="diff-del">{escaped}</span>')
        elif line.startswith("@@"):
            parts.append(f'<span class="diff-hunk">{escaped}</span>')
        else:
            parts.append(f'{escaped}\n')

    return "".join(parts)


def render_executive_summary(data: dict[str, Any]) -> str:
    attempt_scores = data.get("attempt_scores", {})
    comparisons = data.get("comparisons", {})
    problem_areas = data.get("problem_areas", [])

    parts: list[str] = []

    # Grade cards with visual score breakdown
    parts.append('<div class="status-grid">')
    for name, score in attempt_scores.items():
        composite_percent = score.get("composite_percent", score.get("overall_percent", 0))
        composite_grade = score.get("composite_grade", score.get("grade", "?"))
        det_percent = score.get("overall_percent", 0)
        llm_score = score.get("llm_score")
        components = score.get("components", {})

        parts.append(f'''<div class="status-item" style="text-align:center">
            <span class="status-label">{escape(name)}</span>
            {grade_badge(composite_grade, composite_percent)}
        </div>''')
    parts.append('</div>')

    # Visual score breakdown bars per attempt
    pairwise_data = data.get("pairwise_data", {})
    for name, score in attempt_scores.items():
        components = score.get("components", {})
        llm_score = score.get("llm_score")

        # Components may be flat floats (from attempt_scores) or nested dicts (from pairwise_data)
        # Try pairwise_data first for detailed component info
        pw_scoring = pairwise_data.get(name, {})
        pw_components = pw_scoring.get("score", {}).get("components", {})

        fc_detail = pw_components.get("file_coverage", {})
        ps_detail = pw_components.get("pattern_score", {})
        np_detail = pw_components.get("noise_penalty", {})

        if isinstance(fc_detail, dict) and "score" in fc_detail:
            fc_score = fc_detail.get("score", 0)
            fc_weight = fc_detail.get("weight", 0.2)
            fc_matched = fc_detail.get("matched", 0)
            fc_total = fc_detail.get("total", 0)
        else:
            fc_val = components.get("file_coverage", 0)
            fc_score = fc_val if isinstance(fc_val, (int, float)) else 0
            fc_weight = 0.2
            fc_matched = 0
            fc_total = 0

        if isinstance(ps_detail, dict) and "score" in ps_detail:
            ps_score = ps_detail.get("score", 0)
            ps_weight = ps_detail.get("weight", 0.65)
        else:
            ps_val = components.get("pattern_score", 0)
            ps_score = ps_val if isinstance(ps_val, (int, float)) else 0
            ps_weight = 0.65

        if isinstance(np_detail, dict) and "raw_penalty" in np_detail:
            noise_raw = np_detail.get("raw_penalty", 0)
            noise_weight = np_detail.get("weight", 0.15)
            noise_instances = np_detail.get("instance_count", 0)
        else:
            np_val = components.get("noise_penalty", 0)
            noise_raw = np_val if isinstance(np_val, (int, float)) else 0
            noise_weight = 0.15
            noise_instances = 0

        fc_weighted = fc_score * fc_weight * 100
        ps_weighted = ps_score * ps_weight * 100

        llm_weighted = 0
        if llm_score is not None:
            llm_weight = 0.15
            llm_weighted = llm_score * llm_weight * 100

        noise_deduction = noise_raw * noise_weight * 100

        parts.append(f'<div class="category-section">')
        parts.append(f'<h4>{escape(name)} — Score Breakdown</h4>')
        parts.append('<div class="score-bar-container">')
        parts.append(f'<div class="score-bar">')
        if fc_weighted > 0:
            parts.append(f'<div class="score-segment" style="width:{fc_weighted:.1f}%;background:#3b82f6" '
                         f'title="File Coverage: {fc_score:.0%} × {fc_weight:.0%} weight">'
                         f'<span class="score-segment-label">Files {fc_score:.0%}</span></div>')
        if ps_weighted > 0:
            parts.append(f'<div class="score-segment" style="width:{ps_weighted:.1f}%;background:#8b5cf6" '
                         f'title="Pattern Score: {ps_score:.0%} × {ps_weight:.0%} weight">'
                         f'<span class="score-segment-label">Patterns {ps_score:.0%}</span></div>')
        if llm_weighted > 0:
            parts.append(f'<div class="score-segment" style="width:{llm_weighted:.1f}%;background:#06b6d4" '
                         f'title="LLM Score: {llm_score:.0%}">'
                         f'<span class="score-segment-label">LLM {llm_score:.0%}</span></div>')
        parts.append('</div>')

        if noise_deduction > 0:
            parts.append(f'<div class="noise-deduction">'
                         f'<span style="color:#dc2626;font-weight:600">−{noise_deduction:.1f}%</span> '
                         f'<span style="color:#6b7280;font-size:12px">noise penalty '
                         f'({noise_raw:.0%} raw × {noise_weight:.0%} weight, '
                         f'{noise_instances} instances)</span></div>')

        parts.append('</div>')
        parts.append(f'<div class="info-row" style="font-size:12px">')
        if fc_total:
            parts.append(f'<span>File Coverage: <strong>{fc_score:.0%}</strong> '
                         f'({fc_matched}/{fc_total}, weight {fc_weight:.0%})</span>')
        else:
            parts.append(f'<span>File Coverage: <strong>{fc_score:.0%}</strong> (weight {fc_weight:.0%})</span>')
        parts.append(f'<span>Pattern Score: <strong>{ps_score:.0%}</strong> (weight {ps_weight:.0%})</span>')
        if llm_score is not None:
            parts.append(f'<span>LLM Score: <strong>{llm_score:.0%}</strong></span>')
        parts.append('</div>')
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


def render_problem_areas(
    data: dict[str, Any],
    comparison_data: dict[str, dict[str, Any]],
) -> str:
    problem_areas: list[dict[str, Any]] = data.get("problem_areas", [])
    if not problem_areas:
        return '<p class="muted">No problem areas identified.</p>'

    # Build lookup indexes
    detail_index = _build_pattern_detail_index(data)
    diff_index = _build_diff_index(comparison_data)

    parts: list[str] = []

    # Filter toolbar
    parts.append('<div class="filter-bar">')
    parts.append('<input type="text" class="filter-input" id="problem-search" '
                 'placeholder="Search problems..." onkeyup="filterProblems()">')
    parts.append('<label class="filter-checkbox"><input type="checkbox" value="critical" '
                 'onchange="filterProblems()" checked> Critical</label>')
    parts.append('<label class="filter-checkbox"><input type="checkbox" value="high" '
                 'onchange="filterProblems()" checked> High</label>')
    parts.append('<label class="filter-checkbox"><input type="checkbox" value="medium" '
                 'onchange="filterProblems()" checked> Medium</label>')
    parts.append('<label class="filter-checkbox"><input type="checkbox" value="low" '
                 'onchange="filterProblems()" checked> Low</label>')
    parts.append('<select class="filter-input" id="problem-source-filter" onchange="filterProblems()">')
    parts.append('<option value="">All sources</option>')
    parts.append('<option value="deterministic">Deterministic</option>')
    parts.append('<option value="adversarial">Adversarial</option>')
    parts.append('</select>')
    parts.append('</div>')

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
            attempt_raw = pa.get("attempt", "")
            desc = escape(pa.get("description", ""))
            source = pa.get("source", "deterministic")
            recommendation = escape(pa.get("recommendation", ""))
            affected = pa.get("affected_files", [])
            pattern_ids = pa.get("pattern_ids", [])
            confidence = pa.get("referee_confidence")

            parts.append(f'<div class="category-section problem-card" '
                         f'data-severity="{sev}" data-source="{source}">')
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

            # Enhanced: show code context for deterministic problems
            attempt_diffs = diff_index.get(attempt_raw, {})
            if source == "deterministic" and pattern_ids and attempt_raw in detail_index:
                attempt_details = detail_index[attempt_raw]
                for pid in pattern_ids:
                    details = attempt_details.get(pid, [])
                    if details:
                        parts.append(f'<details style="margin-top:8px"><summary style="cursor:pointer;font-size:13px;color:#2563eb">'
                                     f'Pattern details: <code>{escape(pid)}</code> ({len(details)} files)</summary>')
                        parts.append('<div style="margin-top:6px">')
                        for d in details[:20]:
                            d_file_raw = d.get("file", "")
                            d_file = escape(d_file_raw)
                            d_line = d.get("line")
                            d_status = d.get("status", "")
                            d_msg = escape(d.get("message", ""))
                            loc = f'{d_file}:{d_line}' if d_line else d_file
                            parts.append(
                                f'<div style="padding:4px 8px;margin:2px 0;background:#f9fafb;border-radius:4px;font-size:13px">'
                                f'<code>{loc}</code> {status_badge(d_status)} '
                                f'<span style="color:#6b7280">{d_msg}</span>'
                            )
                            # Show diff snippet for this file if available
                            file_diff = attempt_diffs.get(d_file_raw, "")
                            if file_diff and len(file_diff.encode("utf-8", errors="replace")) < 50 * 1024:
                                snippet = _extract_diff_snippet(file_diff, max_lines=15)
                                parts.append(f'<details style="margin-top:4px"><summary style="cursor:pointer;font-size:12px;color:#6b7280">'
                                             f'View diff</summary>'
                                             f'<pre class="diff-pre" style="margin-top:4px;font-size:11px">{snippet}</pre>'
                                             f'</details>')
                            parts.append('</div>')
                        if len(details) > 20:
                            parts.append(f'<p class="muted" style="font-size:12px">... and {len(details) - 20} more</p>')
                        parts.append('</div></details>')

            # Enhanced: show diff snippet for adversarial problems
            if source == "adversarial" and affected and attempt_diffs:
                for af in affected[:3]:
                    diff_text = attempt_diffs.get(af, "")
                    if diff_text:
                        snippet = _extract_diff_snippet(diff_text, max_lines=20)
                        parts.append(f'<details style="margin-top:8px"><summary style="cursor:pointer;font-size:13px;color:#7c3aed">'
                                     f'Diff: <code>{escape(af)}</code></summary>')
                        parts.append(f'<pre class="diff-pre" style="margin-top:6px">{snippet}</pre>')
                        parts.append('</details>')

            # Fallback: still show affected files if no richer context was shown
            if affected and source != "adversarial":
                has_detail_context = source == "deterministic" and pattern_ids and attempt_raw in detail_index
                if not has_detail_context:
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


def render_llm_assessment(
    data: dict[str, Any],
    llm_assessment: dict[str, Any] | None,
) -> str:
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

    # Per-file expandable sections from llm-assessment.json
    file_assessments: list[dict[str, Any]] = []
    if llm_assessment:
        file_assessments = llm_assessment.get("file_assessments", [])

    if file_assessments:
        # Filter toolbar
        parts.append('<div class="filter-bar">')
        parts.append('<input type="text" class="filter-input" id="llm-file-search" '
                     'placeholder="Search files..." onkeyup="filterLLMFiles()">')
        parts.append('</div>')

        parts.append('<h3>Per-File Assessment</h3>')

        # Sort by score ascending (worst first)
        sorted_files = sorted(file_assessments, key=lambda x: x.get("summary_score", 1.0))

        parts.append('<div id="llm-file-list">')
        for fa in sorted_files:
            file_path = fa.get("file", "")
            attempt = fa.get("attempt", "")
            issues = fa.get("issues", [])
            file_score = fa.get("summary_score", 1.0)
            issue_count = len(issues)

            score_color = "#16a34a" if file_score >= 0.8 else ("#ea580c" if file_score >= 0.6 else "#dc2626")

            parts.append(f'<details class="llm-file-item" data-filepath="{escape(file_path).lower()}">')
            parts.append(f'<summary style="cursor:pointer;padding:10px;display:flex;gap:12px;align-items:center;flex-wrap:wrap">')
            parts.append(f'<code style="flex:1;min-width:200px">{escape(file_path)}</code>')
            parts.append(f'<span class="badge" style="color:#475569;background:#f1f5f9">{escape(attempt)}</span>')
            parts.append(f'<span style="color:{score_color};font-weight:600">{file_score:.0%}</span>')
            parts.append(f'<span style="font-size:12px;color:#6b7280">{issue_count} issue{"s" if issue_count != 1 else ""}</span>')
            parts.append('</summary>')

            if issues:
                parts.append('<table style="margin:8px 0 0 0"><thead><tr>')
                parts.append('<th>Severity</th><th>Description</th><th>Impact</th><th>Verdict</th><th>Confidence</th>')
                parts.append('</tr></thead><tbody>')
                for issue in issues:
                    i_sev = issue.get("severity", "medium")
                    i_desc = escape(issue.get("description", ""))
                    i_impact = issue.get("impact_score", 0)
                    i_verdict = issue.get("referee_verdict", "")
                    i_conf = issue.get("referee_confidence")
                    conf_str = f"{i_conf:.0%}" if i_conf is not None else "—"

                    parts.append(f'<tr><td>{severity_badge(i_sev)}</td>')
                    parts.append(f'<td style="font-size:13px">{i_desc}</td>')
                    parts.append(f'<td style="text-align:center">{i_impact}</td>')
                    parts.append(f'<td>{status_badge(i_verdict)}</td>')
                    parts.append(f'<td>{conf_str}</td></tr>')
                parts.append('</tbody></table>')

            parts.append('</details>')
        parts.append('</div>')
    else:
        # Fallback: flat table from problem_areas
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
                # Filter toolbar
                parts.append('<div class="filter-bar">')
                parts.append(f'<input type="text" class="filter-input" id="score-search-{escape(attempt_name)}" '
                             f'placeholder="Search patterns..." '
                             f'onkeyup="filterScoreTable(\'{escape(attempt_name)}\')">')
                parts.append(f'<select class="filter-input" id="score-status-{escape(attempt_name)}" '
                             f'onchange="filterScoreTable(\'{escape(attempt_name)}\')">')
                parts.append('<option value="">All statuses</option>')
                parts.append('<option value="correct">Correct</option>')
                parts.append('<option value="incorrect">Incorrect</option>')
                parts.append('<option value="missing">Missing</option>')
                parts.append('<option value="file_missing">File Missing</option>')
                parts.append('</select>')
                parts.append('</div>')

                parts.append(f'<table id="score-table-{escape(attempt_name)}"><thead><tr>')
                parts.append('<th>Pattern</th><th>Complexity</th><th>Status</th><th>Files</th>')
                parts.append('</tr></thead><tbody>')

                complexity_colors: dict[str, tuple[str, str]] = {
                    "trivial": ("#6b7280", "#f3f4f6"),
                    "moderate": ("#b45309", "#fef3c7"),
                    "complex": ("#dc2626", "#fee2e2"),
                }

                for pr in applicable:
                    name = escape(pr.get("name", pr.get("pattern_id", "")))
                    pid = escape(pr.get("pattern_id", ""))
                    complexity = pr.get("complexity", "moderate")
                    p_status = pr.get("status", "not_applicable")
                    details: list[dict[str, Any]] = pr.get("details", [])
                    c_fg, c_bg = complexity_colors.get(complexity, ("#6b7280", "#f3f4f6"))

                    # Build files column with expandable details
                    if details:
                        files_html = (f'<details><summary style="cursor:pointer;font-size:13px;color:#2563eb">'
                                      f'{len(details)} file{"s" if len(details) != 1 else ""}</summary>'
                                      f'<div style="margin-top:6px">')
                        for d in details[:20]:
                            d_file = escape(d.get("file", ""))
                            d_line = d.get("line")
                            d_status = d.get("status", "")
                            d_msg = escape(d.get("message", ""))
                            loc = f'{d_file}:{d_line}' if d_line else d_file
                            files_html += (
                                f'<div style="padding:3px 6px;margin:2px 0;background:#f9fafb;border-radius:4px;font-size:12px">'
                                f'<code>{loc}</code> {status_badge(d_status)} '
                                f'<span style="color:#6b7280">{d_msg}</span></div>'
                            )
                        if len(details) > 20:
                            files_html += f'<p class="muted" style="font-size:11px">... and {len(details) - 20} more</p>'
                        files_html += '</div></details>'
                    else:
                        message = escape(pr.get("message", ""))
                        files_html = f'<span style="font-size:13px;color:#6b7280">{message}</span>'

                    parts.append(f'<tr data-name="{name.lower()} {pid.lower()}" data-status="{p_status}">')
                    parts.append(f'<td><strong>{name}</strong>'
                                 f'<div style="font-size:11px;color:#9ca3af;margin-top:1px">{pid}</div></td>')
                    parts.append(f'<td><span class="badge" style="color:{c_fg};background:{c_bg}">{complexity}</span></td>')
                    parts.append(f'<td>{status_badge(p_status)}</td>')
                    parts.append(f'<td>{files_html}</td></tr>')

                parts.append('</tbody></table>')

    return "\n".join(parts)


def render_file_changes(
    data: dict[str, Any],
    comparison_data: dict[str, dict[str, Any]],
) -> str:
    pairwise_data: dict[str, Any] = data.get("pairwise_data", {})
    if not pairwise_data:
        return '<p class="muted">No file change data available.</p>'

    diff_index = _build_diff_index(comparison_data)

    parts: list[str] = []

    for attempt_name, scoring in pairwise_data.items():
        file_results: list[dict[str, Any]] = scoring.get("file_results", [])
        if not file_results:
            continue

        attempt_diffs = diff_index.get(attempt_name, {})
        # Also get category info from comparison data
        comp_data = comparison_data.get(attempt_name, {})
        modified_files = comp_data.get("files", {}).get("modified", [])
        # Build path -> modified file info index
        mod_index: dict[str, dict[str, Any]] = {}
        for mf in modified_files:
            mod_index[mf.get("path", "")] = mf

        parts.append(f'<h3>{escape(attempt_name)} — File Results</h3>')

        # Filter toolbar
        parts.append('<div class="filter-bar">')
        parts.append(f'<input type="text" class="filter-input" id="file-search-{escape(attempt_name)}" '
                     f'placeholder="Search files..." '
                     f'onkeyup="filterFileChanges(\'{escape(attempt_name)}\')">')
        parts.append('</div>')

        parts.append(f'<div id="file-list-{escape(attempt_name)}">')

        for fr in file_results:
            path = fr.get("path", "")
            pattern_statuses: dict[str, str] = fr.get("pattern_statuses", {})
            noise_count = fr.get("noise_count", 0)
            diff_text = attempt_diffs.get(path, "")
            mod_info = mod_index.get(path, {})

            statuses_html = " ".join(
                f'{status_badge(s)}'
                for s in sorted(set(pattern_statuses.values()))
                if s != "not_applicable"
            ) or '<span class="muted">—</span>'

            # Category badges from comparison data
            cats = mod_info.get("categories", [])
            cats_html = " ".join(category_badge(c) for c in cats) if cats else ""

            # Line stats
            stats = mod_info.get("stats", {})
            la = stats.get("lines_added", 0)
            lr = stats.get("lines_removed", 0)
            stats_html = ""
            if la or lr:
                stats_html = (f' <span style="color:#16a34a;font-size:12px">+{la}</span>'
                              f' <span style="color:#dc2626;font-size:12px">-{lr}</span>')

            noise_html = f' <span style="color:#dc2626;font-size:12px">({noise_count} noise)</span>' if noise_count else ""

            # Check if diff is too large to embed
            diff_size = len(diff_text.encode("utf-8", errors="replace")) if diff_text else 0
            diff_lines = diff_text.count("\n") if diff_text else 0

            parts.append(f'<details class="file-change-item" data-filepath="{escape(path).lower()}">')
            parts.append(f'<summary style="cursor:pointer;padding:8px 12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">')
            parts.append(f'<code style="flex:1;min-width:200px">{escape(path)}</code>')
            parts.append(f'{cats_html}{stats_html}{noise_html}')
            parts.append(f'<span>{statuses_html}</span>')
            parts.append('</summary>')

            # Show diff content
            if diff_text:
                if diff_size > 50 * 1024:
                    parts.append(f'<div style="padding:12px;color:#6b7280;font-size:13px">'
                                 f'File too large to display inline ({diff_size // 1024}KB, {diff_lines} lines). '
                                 f'<span style="color:#16a34a">+{la}</span> / <span style="color:#dc2626">-{lr}</span></div>')
                else:
                    parsed = parse_unified_diff(diff_text)
                    truncated = False
                    if len(parsed) > 200:
                        parsed = parsed[:200]
                        truncated = True

                    parts.append('<div class="diff-container" style="margin:8px 12px 12px">')
                    diff_lines: list[str] = []
                    for line_num, css_class, text in parsed:
                        escaped_text = escape(text)
                        if css_class:
                            diff_lines.append(f'<span class="{css_class}">{escaped_text}</span>')
                        else:
                            diff_lines.append(escaped_text)
                    parts.append(f'<pre class="diff-pre" style="margin:0">{"".join(diff_lines)}</pre>')
                    if truncated:
                        parts.append(f'<p class="muted" style="padding:4px 8px;font-size:12px">(truncated — showing first 200 lines)</p>')
                    parts.append('</div>')
            else:
                parts.append('<div style="padding:12px;color:#9ca3af;font-size:13px;font-style:italic">No diff available</div>')

            parts.append('</details>')

        parts.append('</div>')

    return "\n".join(parts)


def generate_html(
    data: dict[str, Any],
    comparison_data: dict[str, dict[str, Any]] | None = None,
    llm_assessment: dict[str, Any] | None = None,
) -> str:
    if comparison_data is None:
        comparison_data = {}

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
    problems_html = render_problem_areas(data, comparison_data)
    comparison_html = render_attempt_comparison(data)
    llm_html = render_llm_assessment(data, llm_assessment)
    scores_html = render_detailed_scores(data)
    files_html = render_file_changes(data, comparison_data)

    has_comparisons = bool(data.get("comparisons"))
    has_llm = data.get("llm_summary") is not None

    comparison_tab = '<button class="tab" onclick="switchTab(\'comparison\')">Attempt Comparison</button>' if has_comparisons else ""
    comparison_section = f'<div id="comparison" class="tab-content" data-title="Attempt Comparison">{comparison_html}</div>' if has_comparisons else ""

    llm_tab = '<button class="tab" onclick="switchTab(\'llm\')">LLM Assessment</button>'
    llm_section = f'<div id="llm" class="tab-content" data-title="LLM Assessment">{llm_html}</div>'

    # Collect attempt names for JS
    attempt_names_js = json.dumps(attempt_names)

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

  /* Score breakdown bar */
  .score-bar-container {{ margin: 8px 0 4px; }}
  .score-bar {{ display: flex; height: 32px; border-radius: 8px; overflow: hidden; background: #f3f4f6; }}
  .score-segment {{ display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: 600; min-width: 40px; transition: width 0.3s; }}
  .score-segment-label {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 6px; }}
  .noise-deduction {{ margin-top: 6px; font-size: 13px; }}

  /* Diff styling */
  .diff-add {{ background: #dcfce7; display: block; }}
  .diff-del {{ background: #fee2e2; display: block; }}
  .diff-hunk {{ background: #dbeafe; color: #2563eb; display: block; font-weight: 500; }}
  .diff-pre {{ font-family: "SF Mono", "Fira Code", "Cascadia Code", monospace; font-size: 12px; line-height: 1.5; overflow-x: auto; padding: 8px; background: white; border: 1px solid #e5e7eb; border-radius: 6px; white-space: pre-wrap; word-break: break-all; }}
  .diff-container {{ border-radius: 6px; overflow: hidden; }}

  /* Filter bar */
  .filter-bar {{ display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }}
  .filter-input {{ padding: 6px 12px; border: 1px solid #e5e7eb; border-radius: 6px; font-size: 13px; }}
  .filter-input:focus {{ outline: none; border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37,99,235,0.1); }}
  .filter-checkbox {{ font-size: 13px; color: #4b5563; display: flex; align-items: center; gap: 4px; cursor: pointer; }}
  .filter-checkbox input {{ cursor: pointer; }}

  /* File change items */
  .file-change-item {{ background: white; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; }}
  .file-change-item summary {{ list-style: none; }}
  .file-change-item summary::-webkit-details-marker {{ display: none; }}
  .file-change-item summary::before {{ content: "\\25B6"; font-size: 10px; color: #9ca3af; margin-right: 8px; transition: transform 0.2s; }}
  .file-change-item[open] summary::before {{ transform: rotate(90deg); }}

  /* LLM file items */
  .llm-file-item {{ background: white; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; }}
  .llm-file-item summary {{ list-style: none; }}
  .llm-file-item summary::-webkit-details-marker {{ display: none; }}
  .llm-file-item summary::before {{ content: "\\25B6"; font-size: 10px; color: #9ca3af; margin-right: 8px; transition: transform 0.2s; }}
  .llm-file-item[open] summary::before {{ transform: rotate(90deg); }}

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
var attemptNames = {attempt_names_js};

function switchTab(id) {{
  document.querySelectorAll('.tab-content').forEach(function(el) {{ el.classList.remove('active'); }});
  document.querySelectorAll('.tab').forEach(function(el) {{ el.classList.remove('active'); }});
  document.getElementById(id).classList.add('active');
  event.target.classList.add('active');
}}

/* Problem Areas filtering */
function filterProblems() {{
  var search = (document.getElementById('problem-search') || {{}}).value || '';
  search = search.toLowerCase();
  var sourceFilter = (document.getElementById('problem-source-filter') || {{}}).value || '';

  var checkedSeverities = [];
  document.querySelectorAll('.filter-checkbox input[type=checkbox]').forEach(function(cb) {{
    if (cb.checked) checkedSeverities.push(cb.value);
  }});

  document.querySelectorAll('.problem-card').forEach(function(card) {{
    var sev = card.getAttribute('data-severity') || '';
    var source = card.getAttribute('data-source') || '';
    var text = card.textContent.toLowerCase();

    var show = true;
    if (checkedSeverities.length > 0 && checkedSeverities.indexOf(sev) === -1) show = false;
    if (sourceFilter && source !== sourceFilter) show = false;
    if (search && text.indexOf(search) === -1) show = false;
    card.style.display = show ? '' : 'none';
  }});
}}

/* LLM file filtering */
function filterLLMFiles() {{
  var search = (document.getElementById('llm-file-search') || {{}}).value || '';
  search = search.toLowerCase();
  document.querySelectorAll('.llm-file-item').forEach(function(item) {{
    var path = item.getAttribute('data-filepath') || '';
    item.style.display = (!search || path.indexOf(search) !== -1) ? '' : 'none';
  }});
}}

/* Detailed Scores filtering */
function filterScoreTable(attempt) {{
  var searchEl = document.getElementById('score-search-' + attempt);
  var statusEl = document.getElementById('score-status-' + attempt);
  var search = searchEl ? searchEl.value.toLowerCase() : '';
  var status = statusEl ? statusEl.value : '';
  var table = document.getElementById('score-table-' + attempt);
  if (!table) return;
  table.querySelectorAll('tbody tr').forEach(function(row) {{
    var name = (row.getAttribute('data-name') || '').toLowerCase();
    var rowStatus = row.getAttribute('data-status') || '';
    var show = true;
    if (search && name.indexOf(search) === -1) show = false;
    if (status && rowStatus !== status) show = false;
    row.style.display = show ? '' : 'none';
  }});
}}

/* File Changes filtering */
function filterFileChanges(attempt) {{
  var searchEl = document.getElementById('file-search-' + attempt);
  var search = searchEl ? searchEl.value.toLowerCase() : '';
  var list = document.getElementById('file-list-' + attempt);
  if (!list) return;
  list.querySelectorAll('.file-change-item').forEach(function(item) {{
    var path = item.getAttribute('data-filepath') || '';
    item.style.display = (!search || path.indexOf(search) !== -1) ? '' : 'none';
  }});
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

    # Load comparison data from golden-vs-* subdirectories
    comparison_data: dict[str, dict[str, Any]] = {}
    for subdir in sorted(work_dir.iterdir()):
        if subdir.is_dir() and subdir.name.startswith("golden-vs-"):
            attempt_name = subdir.name.removeprefix("golden-vs-")
            comp_path = subdir / "comparison-data.json"
            if comp_path.exists():
                try:
                    with open(comp_path, "r", encoding="utf-8") as f:
                        comparison_data[attempt_name] = json.load(f)
                except (json.JSONDecodeError, OSError):
                    pass

    # Load LLM assessment
    llm_assessment: dict[str, Any] | None = None
    llm_path = work_dir / "llm-assessment.json"
    if llm_path.exists():
        try:
            with open(llm_path, "r", encoding="utf-8") as f:
                llm_assessment = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    html_output = generate_html(data, comparison_data=comparison_data, llm_assessment=llm_assessment)

    output_path = Path(args.output) if args.output else work_dir / "evaluation-report.html"
    output_path.write_text(html_output, encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
