#!/usr/bin/env python3
"""
Compose evaluation results from pairwise scoring and LLM assessment.

Reads all pairwise scoring-results.json files + optional llm-assessment.json,
produces evaluation-results.json with cross-attempt comparisons, problem areas,
and composite scores.

Usage:
    python3 scripts/compose_evaluation.py \
      --output-dir /tmp/eval-workspace \
      --golden /path/to/golden \
      --attempt ai-agent=/path/to/ai-output \
      --attempt codemods=/path/to/codemods-output \
      --target patternfly
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

from models import (
    AttemptComparison,
    AttemptScore,
    EvaluationMetadata,
    EvaluationResults,
    LLMAssessment,
    LLMSummary,
    PatternAdvantage,
    ProblemArea,
    ProblemAreaSource,
    ProblemAreaType,
    Severity,
)

# Composite scoring weights
WEIGHT_FILE_COVERAGE = 0.15
WEIGHT_DETERMINISTIC = 0.50
WEIGHT_NOISE = 0.10
WEIGHT_LLM = 0.25

# Grade thresholds
GRADE_THRESHOLDS: list[tuple[int, str]] = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]


def grade_from_percent(percent: int) -> str:
    for threshold, letter in GRADE_THRESHOLDS:
        if percent >= threshold:
            return letter
    return "F"


def load_scoring_results(output_dir: Path, attempt_name: str) -> dict[str, Any] | None:
    """Load scoring-results.json for a specific attempt."""
    label = f"golden-vs-{attempt_name}"
    path = output_dir / label / "scoring-results.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
        return data


def load_comparison_data(output_dir: Path, attempt_name: str) -> dict[str, Any] | None:
    """Load comparison-data.json for a specific attempt."""
    label = f"golden-vs-{attempt_name}"
    path = output_dir / label / "comparison-data.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
        return data


def load_llm_assessment(output_dir: Path) -> LLMAssessment | None:
    """Load llm-assessment.json if present.

    Filters out not_real issues (they have null severity and shouldn't
    contribute to scoring or problem areas).
    """
    path = output_dir / "llm-assessment.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter out not_real issues before validation — referees set severity
    # to null for disproved issues, which fails Severity enum validation.
    for fa in data.get("file_assessments", []):
        fa["issues"] = [
            issue for issue in fa.get("issues", [])
            if issue.get("referee_verdict") != "not_real"
        ]

    return LLMAssessment.model_validate(data)


def compute_attempt_score(
    scoring: dict[str, Any],
    llm_assessment: LLMAssessment | None,
    attempt_name: str,
) -> AttemptScore:
    """Compute individual attempt score from deterministic + optional LLM results."""
    score_data = scoring.get("score", {})
    components = score_data.get("components", {})

    det_percent = score_data.get("overall_percent", 0)
    det_grade = score_data.get("grade", "F")

    # Extract component scores
    fc_score = components.get("file_coverage", {}).get("score", 0.0)
    ps_score = components.get("pattern_score", {}).get("score", 0.0)
    np_penalty = components.get("noise_penalty", {}).get("raw_penalty", 0.0)
    np_capped = min(np_penalty, 1.0)

    # LLM score (if available)
    llm_score: float | None = None
    if llm_assessment:
        attempt_assessments = [
            fa for fa in llm_assessment.file_assessments
            if fa.attempt == attempt_name
        ]
        if attempt_assessments:
            llm_score = sum(fa.summary_score for fa in attempt_assessments) / len(attempt_assessments)

    # Composite score
    if llm_score is not None:
        composite = (
            WEIGHT_FILE_COVERAGE * fc_score
            + WEIGHT_DETERMINISTIC * ps_score
            + WEIGHT_NOISE * (1.0 - np_capped)
            + WEIGHT_LLM * llm_score
        )
    else:
        # Without LLM, redistribute weight to deterministic
        adjusted_det_weight = WEIGHT_DETERMINISTIC + WEIGHT_LLM
        composite = (
            WEIGHT_FILE_COVERAGE * fc_score
            + adjusted_det_weight * ps_score
            + WEIGHT_NOISE * (1.0 - np_capped)
        )

    composite_percent = int(round(composite * 100))
    composite_grade = grade_from_percent(composite_percent)

    return AttemptScore(
        overall_percent=det_percent,
        grade=det_grade,
        deterministic_percent=det_percent,
        llm_score=llm_score,
        composite_percent=composite_percent,
        composite_grade=composite_grade,
        components={
            "file_coverage": fc_score,
            "pattern_score": ps_score,
            "noise_penalty": np_capped,
            "llm_score": llm_score,
        },
    )


def compare_attempts(
    scoring_a: dict[str, Any],
    scoring_b: dict[str, Any],
    name_a: str,
    name_b: str,
) -> AttemptComparison:
    """Compare two attempts based on pattern results."""
    score_a = scoring_a.get("score", {})
    score_b = scoring_b.get("score", {})
    delta = score_a.get("overall_percent", 0) - score_b.get("overall_percent", 0)

    patterns_a = {p["pattern_id"]: p for p in scoring_a.get("pattern_results", [])}
    patterns_b = {p["pattern_id"]: p for p in scoring_b.get("pattern_results", [])}

    all_pattern_ids = sorted(set(patterns_a.keys()) | set(patterns_b.keys()))

    a_advantages: list[PatternAdvantage] = []
    b_advantages: list[PatternAdvantage] = []
    ties: list[str] = []
    neither: list[str] = []

    for pid in all_pattern_ids:
        pa = patterns_a.get(pid)
        pb = patterns_b.get(pid)
        status_a = pa["status"] if pa else "not_applicable"
        status_b = pb["status"] if pb else "not_applicable"
        name = pa["name"] if pa else (pb["name"] if pb else pid)

        if status_a == "not_applicable" and status_b == "not_applicable":
            continue

        a_correct = status_a == "correct"
        b_correct = status_b == "correct"

        if a_correct and b_correct:
            ties.append(pid)
        elif a_correct and not b_correct:
            a_advantages.append(PatternAdvantage(
                pattern_id=pid, name=name, a_status=status_a, b_status=status_b,
            ))
        elif b_correct and not a_correct:
            b_advantages.append(PatternAdvantage(
                pattern_id=pid, name=name, a_status=status_a, b_status=status_b,
            ))
        else:
            neither.append(pid)

    return AttemptComparison(
        delta=delta,
        a_advantages=a_advantages,
        b_advantages=b_advantages,
        ties=ties,
        neither=neither,
    )


def identify_problem_areas(
    scoring_data: dict[str, dict[str, Any]],
    llm_assessment: LLMAssessment | None,
) -> list[ProblemArea]:
    """Identify problem areas from deterministic and LLM sources."""
    problems: list[ProblemArea] = []

    # Deterministic problem areas: patterns that failed across attempts
    for attempt_name, scoring in scoring_data.items():
        pattern_results: list[dict[str, Any]] = scoring.get("pattern_results", [])

        for pr in pattern_results:
            status = pr.get("status", "not_applicable")
            if status in ("incorrect", "missing", "file_missing"):
                severity = Severity.high if pr.get("complexity") == "complex" else (
                    Severity.medium if pr.get("complexity") == "moderate" else Severity.low
                )
                if status == "incorrect":
                    severity = Severity.high

                affected_files = [d["file"] for d in pr.get("details", []) if d.get("status") != "correct"]

                problems.append(ProblemArea(
                    type=ProblemAreaType.pattern_cluster,
                    source=ProblemAreaSource.deterministic,
                    severity=severity,
                    attempt=attempt_name,
                    pattern_ids=[pr["pattern_id"]],
                    affected_files=affected_files,
                    description=f"{pr.get('name', pr['pattern_id'])}: {pr.get('message', status)}",
                    recommendation=_recommendation_for_pattern(pr),
                ))

    # LLM problem areas
    if llm_assessment:
        for fa in llm_assessment.file_assessments:
            confirmed_issues = [
                issue for issue in fa.issues
                if issue.referee_verdict.value == "real"
            ]
            if confirmed_issues:
                for issue in confirmed_issues:
                    problems.append(ProblemArea(
                        type=ProblemAreaType.llm_finding,
                        source=ProblemAreaSource.adversarial,
                        severity=issue.severity,
                        attempt=fa.attempt,
                        affected_files=[fa.file],
                        description=issue.description,
                        referee_confidence=issue.referee_confidence,
                    ))

    # Sort by severity
    severity_order = {Severity.critical: 0, Severity.high: 1, Severity.medium: 2, Severity.low: 3}
    problems.sort(key=lambda p: severity_order.get(p.severity, 3))

    return problems


def _recommendation_for_pattern(pr: dict[str, Any]) -> str:
    """Generate a recommendation for a failed pattern."""
    status = pr.get("status", "")
    name = pr.get("name", pr.get("pattern_id", ""))
    complexity = pr.get("complexity", "moderate")

    if status == "incorrect":
        return f"Review and fix the {name} migration — the pattern was applied incorrectly"
    elif status == "missing":
        if complexity == "complex":
            return f"Add targeted examples for {name} to the agent prompt — complex patterns need explicit guidance"
        return f"Ensure the {name} migration pattern is applied"
    elif status == "file_missing":
        return f"Ensure all relevant files are included in the migration output"
    return ""


def compute_llm_summary(llm_assessment: LLMAssessment) -> LLMSummary:
    """Compute summary statistics from LLM assessment."""
    total_issues = sum(len(fa.issues) for fa in llm_assessment.file_assessments)
    confirmed = sum(
        1 for fa in llm_assessment.file_assessments
        for issue in fa.issues
        if issue.referee_verdict.value == "real"
    )
    avg_score = 0.0
    if llm_assessment.file_assessments:
        avg_score = sum(fa.summary_score for fa in llm_assessment.file_assessments) / len(llm_assessment.file_assessments)

    return LLMSummary(
        files_assessed=llm_assessment.metadata.files_assessed,
        issues_found=total_issues,
        issues_confirmed=confirmed,
        average_file_score=round(avg_score, 4),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compose evaluation results from pairwise scoring and LLM assessment"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory containing pairwise artifacts and llm-assessment.json",
    )
    parser.add_argument(
        "--golden",
        required=True,
        help="Path to golden truth directory (for metadata)",
    )
    parser.add_argument(
        "--attempt",
        action="append",
        required=True,
        dest="attempts",
        help="Named attempt in 'name=/path' format",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Migration target (for metadata)",
    )

    args = parser.parse_args()
    output_dir = Path(args.output_dir)

    # Parse attempts
    attempt_map: dict[str, str] = {}
    for attempt_str in args.attempts:
        if "=" not in attempt_str:
            print(f"Error: --attempt must be 'name=/path', got: {attempt_str}", file=sys.stderr)
            sys.exit(1)
        name, path = attempt_str.split("=", 1)
        attempt_map[name.strip()] = path.strip()

    attempt_names = sorted(attempt_map.keys())

    # Load all scoring results
    scoring_data: dict[str, dict[str, Any]] = {}
    for name in attempt_names:
        scoring = load_scoring_results(output_dir, name)
        if scoring is None:
            print(f"Warning: No scoring results found for attempt '{name}'", file=sys.stderr)
            continue
        scoring_data[name] = scoring

    if not scoring_data:
        print("Error: No scoring results found for any attempt", file=sys.stderr)
        sys.exit(1)

    # Load LLM assessment (optional)
    llm_assessment = load_llm_assessment(output_dir)

    # Compute per-attempt scores
    attempt_scores: dict[str, AttemptScore] = {}
    for name in attempt_names:
        if name not in scoring_data:
            continue
        attempt_scores[name] = compute_attempt_score(
            scoring_data[name], llm_assessment, name,
        )

    # Cross-attempt comparisons
    comparisons: dict[str, AttemptComparison] = {}
    scored_names = [n for n in attempt_names if n in scoring_data]
    for name_a, name_b in combinations(scored_names, 2):
        key = f"{name_a}_vs_{name_b}"
        comparisons[key] = compare_attempts(
            scoring_data[name_a], scoring_data[name_b], name_a, name_b,
        )

    # Problem areas
    problem_areas = identify_problem_areas(scoring_data, llm_assessment)

    # LLM summary
    llm_summary: LLMSummary | None = None
    if llm_assessment:
        llm_summary = compute_llm_summary(llm_assessment)

    # Build pairwise data for report
    pairwise_data: dict[str, Any] = {}
    for name in scored_names:
        pairwise_data[name] = scoring_data[name]

    # Compose results
    results = EvaluationResults(
        metadata=EvaluationMetadata(
            golden_dir=str(Path(args.golden).resolve()),
            attempts=attempt_map,
            target=args.target,
        ),
        attempt_scores={name: score for name, score in attempt_scores.items()},
        comparisons={key: comp for key, comp in comparisons.items()},
        problem_areas=problem_areas,
        llm_summary=llm_summary,
        pairwise_data=pairwise_data,
    )

    # Write output
    output_path = output_dir / "evaluation-results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(results.model_dump_json(indent=2))

    print(f"Evaluation results written to: {output_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("  Composite Evaluation Summary")
    print(f"{'='*60}")
    for name, score in attempt_scores.items():
        composite_str = f" → Composite: {score.composite_grade} ({score.composite_percent}%)" if score.composite_percent is not None else ""
        llm_str = f", LLM: {score.llm_score:.0%}" if score.llm_score is not None else ""
        print(f"  {name}: Det: {score.grade} ({score.overall_percent}%){llm_str}{composite_str}")

    if problem_areas:
        print(f"\n  Problem areas identified: {len(problem_areas)}")
        for pa in problem_areas[:5]:
            print(f"    [{pa.severity.value.upper()}] {pa.attempt}: {pa.description}")
        if len(problem_areas) > 5:
            print(f"    ... and {len(problem_areas) - 5} more")

    print(str(output_path))


if __name__ == "__main__":
    main()
