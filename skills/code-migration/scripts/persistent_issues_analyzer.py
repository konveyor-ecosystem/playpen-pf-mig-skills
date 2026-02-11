#!/usr/bin/env python3
"""
Persistent Issues Analyzer
Finds all Kantra output.yaml files and identifies issues appearing more than twice.
"""

import yaml
import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def load_kantra_output(yaml_file):
    """Load and parse a Kantra output.yaml file"""
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

            if data is None or not isinstance(data, list):
                return None

            return data

    except Exception:
        return None


def extract_issues_from_file(yaml_file):
    """Extract all issues from a Kantra output.yaml file"""
    data = load_kantra_output(yaml_file)
    if not data:
        return {}

    issues = {}

    for ruleset in data:
        if not isinstance(ruleset, dict) or 'violations' not in ruleset:
            continue

        violations = ruleset.get('violations')
        if not isinstance(violations, dict):
            continue

        ruleset_name = ruleset.get('name', 'Unknown')

        for rule_id, violation in violations.items():
            if not isinstance(violation, dict):
                continue

            incidents = violation.get('incidents', [])
            if not isinstance(incidents, list):
                continue

            files_affected = set()
            incident_messages = set()

            for incident in incidents:
                if not isinstance(incident, dict):
                    continue

                uri = incident.get('uri', '')
                if isinstance(uri, str) and uri.startswith('file://'):
                    file_path = uri[7:]
                    if file_path:
                        files_affected.add(file_path)

                message = incident.get('message', '')
                if isinstance(message, str) and message:
                    incident_messages.add(message)

            issues[rule_id] = {
                'description': violation.get('description', 'No description'),
                'category': violation.get('category', 'unknown'),
                'ruleset': ruleset_name,
                'incident_count': len(incidents),
                'files_affected': list(files_affected),
                'incident_messages': list(incident_messages)
            }

    return issues


def find_output_files(base_dir):
    """Find all output.yaml files recursively and return sorted by timestamp (descending)"""
    output_files = []
    base_path = Path(base_dir)

    if not base_path.exists():
        print(f"Error: Directory '{base_dir}' does not exist")
        return []

    for yaml_file in base_path.rglob('output.yaml'):
        try:
            stat = yaml_file.stat()
            output_files.append({
                'path': yaml_file,
                'timestamp': datetime.fromtimestamp(stat.st_mtime),
                'size': stat.st_size
            })
        except Exception as e:
            print(f"Warning: Could not get stats for {yaml_file}: {e}")
            continue

    # Sort by timestamp in DESCENDING order (newest first)
    output_files.sort(key=lambda x: x['timestamp'], reverse=True)

    return output_files


def analyze_persistent_issues(base_dir, min_occurrences=3):
    """Analyze issues appearing more than twice across output files"""
    output_files = find_output_files(base_dir)

    if not output_files:
        print(f"No output.yaml files found in '{base_dir}'")
        return

    print("=" * 80)
    print("PERSISTENT ISSUES ANALYSIS")
    print("=" * 80)
    print(f"Base directory: {base_dir}")
    print(f"Output files found: {len(output_files)}")
    print(f"Analyzing issues appearing in {min_occurrences}+ files")
    print()

    # Track issues across all files
    issue_occurrences = defaultdict(list)

    print("📁 ANALYZING FILES (newest to oldest):")
    print("-" * 80)

    for idx, file_info in enumerate(output_files, 1):
        yaml_path = file_info['path']
        timestamp = file_info['timestamp']

        print(f"{idx}. {yaml_path.relative_to(base_dir)}")
        print(f"   Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        issues = extract_issues_from_file(yaml_path)

        if not issues:
            print(f"   No issues found")
        else:
            print(f"   Issues: {len(issues)}")

            for rule_id, issue_data in issues.items():
                issue_occurrences[rule_id].append({
                    'file': yaml_path,
                    'timestamp': timestamp,
                    'incident_count': issue_data['incident_count'],
                    'files_affected': issue_data['files_affected'],
                    'issue_data': issue_data
                })

        print()

    # Find persistent issues (appearing more than twice = 3+ occurrences)
    persistent_issues = {
        rule_id: occurrences
        for rule_id, occurrences in issue_occurrences.items()
        if len(occurrences) >= min_occurrences
    }

    if not persistent_issues:
        print("=" * 80)
        print(f"✅ No persistent issues found!")
        print(f"All issues appeared in fewer than {min_occurrences} analysis runs.")
        print("=" * 80)
        return

    print("=" * 80)
    print(f"🔴 PERSISTENT ISSUES (appearing in {min_occurrences}+ files):")
    print("=" * 80)
    print()

    for rule_id, occurrences in sorted(persistent_issues.items(),
                                       key=lambda x: len(x[1]),
                                       reverse=True):
        latest = occurrences[0]  # Most recent occurrence (sorted descending)
        issue_data = latest['issue_data']

        print(f"Issue: {rule_id}")
        print(f"Occurrences: {len(occurrences)} times")
        print(f"Description: {issue_data['description']}")
        print(f"Category: {issue_data['category']}")
        print(f"Ruleset: {issue_data['ruleset']}")

        # Show incident messages from latest occurrence
        messages = issue_data.get('incident_messages', [])
        if messages:
            print(f"Latest messages:")
            for msg in messages[:3]:  # Show up to 3 messages
                print(f"  - {msg}")
        else:
            print(f"Messages: No specific messages available")

        # Show occurrence timeline
        print(f"Occurrence timeline:")
        for occ in occurrences[:5]:  # Show up to 5 most recent
            relative_path = occ['file'].relative_to(base_dir)
            timestamp = occ['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"  - {timestamp}: {relative_path} ({occ['incident_count']} incidents)")

        if len(occurrences) > 5:
            print(f"  ... and {len(occurrences) - 5} more occurrences")

        print()

    print("=" * 80)
    print(f"SUMMARY: {len(persistent_issues)} persistent issues found")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze persistent issues across Kantra output files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 persistent_issues_analyzer.py /tmp/migration-workspace
  python3 persistent_issues_analyzer.py /tmp/migration-workspace --min-occurrences 2
  python3 persistent_issues_analyzer.py . --min-occurrences 4

The script finds all output.yaml files recursively and identifies issues
appearing in multiple analysis runs, suggesting they may be difficult to fix.
        """
    )

    parser.add_argument('base_dir',
                       help='Base directory to search for output.yaml files')
    parser.add_argument('--min-occurrences', type=int, default=3,
                       help='Minimum occurrences to consider persistent (default: 3)')

    args = parser.parse_args()

    if not Path(args.base_dir).exists():
        print(f"Error: Directory '{args.base_dir}' not found")
        sys.exit(1)

    analyze_persistent_issues(args.base_dir, args.min_occurrences)


if __name__ == "__main__":
    main()
