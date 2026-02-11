#!/usr/bin/env python3
"""
Kantra Output Helper
Analyze Kantra migration analysis results from output.yaml

Commands:
  analyze - Get overview of all issues (JSON by default)
  file    - Get detailed issues for a specific file

Use 'analyze' to understand the scope of migration work.
Use 'file' to drill down into issues for a specific file when ready to fix.
"""

import yaml
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict


def load_kantra_output(output_file):
    """Load and parse the Kantra output.yaml file

    Returns None if file cannot be loaded.
    Prints helpful error messages to guide the agent.
    """
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

            if data is None:
                print(f"Error: Kantra output file is empty: {output_file}", file=sys.stderr)
                print(f"Suggestion: Check that Kantra analysis completed successfully.", file=sys.stderr)
                return None

            if not isinstance(data, list):
                print(f"Error: Invalid Kantra output format in {output_file}", file=sys.stderr)
                print(f"Expected: List of rulesets with violations", file=sys.stderr)
                return None

            return data

    except FileNotFoundError:
        print(f"Error: Kantra output file not found: {output_file}", file=sys.stderr)
        print(f"Suggestion: Verify Kantra analysis completed. Expected path format: <workspace>/kantra-output/output.yaml", file=sys.stderr)
        return None
    except PermissionError:
        print(f"Error: Permission denied accessing: {output_file}", file=sys.stderr)
        print(f"Suggestion: Check file permissions", file=sys.stderr)
        return None
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML format in {output_file}: {e}", file=sys.stderr)
        print(f"Suggestion: File may be corrupted. Re-run Kantra analysis.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Unexpected error loading {output_file}: {e}", file=sys.stderr)
        return None


def analyze_issues(output_file, format_type='json'):
    """Analyze all issues in Kantra output

    Args:
        output_file: Path to Kantra output.yaml
        format_type: 'json' or 'text'

    Returns structured analysis of all migration issues.

    IMPORTANT: Do NOT prioritize based on simple metrics like file_count.
    Instead, analyze the full data to identify:
    - Which issues are interdependent (must be fixed together or in sequence)
    - Logical groupings that minimize rework and iterations
    - Dependencies between issues (which must be fixed before others)
    """
    data = load_kantra_output(output_file)
    if not data:
        sys.exit(1)

    issues = []

    for ruleset in data:
        if not isinstance(ruleset, dict) or 'violations' not in ruleset:
            continue

        violations = ruleset.get('violations')
        if not isinstance(violations, dict) or not violations:
            continue

        for rule_id, violation in violations.items():
            if not isinstance(violation, dict):
                continue

            description = violation.get('description', 'No description')
            incidents = violation.get('incidents', [])

            if not isinstance(incidents, list):
                continue

            # Collect unique files affected by this rule
            files_affected = set()
            for incident in incidents:
                if not isinstance(incident, dict):
                    continue
                uri = incident.get('uri', '')
                if isinstance(uri, str) and uri.startswith('file://'):
                    file_path = uri[7:]  # Remove 'file://' prefix
                    if file_path:
                        files_affected.add(file_path)

            if files_affected:  # Only include rules that affect files
                issues.append({
                    'rule_id': rule_id,
                    'description': description,
                    'file_count': len(files_affected),
                    'files': sorted(list(files_affected))
                })

    # Sort by file_count descending
    issues.sort(key=lambda x: x['file_count'], reverse=True)

    result = {
        'total_issues': len(issues),
        'issues': issues
    }

    if format_type == 'json':
        print(json.dumps(result, indent=2))
    else:
        # Text format
        print("=" * 80)
        print("KANTRA MIGRATION ISSUES ANALYSIS")
        print("=" * 80)
        print(f"Total Issues: {result['total_issues']}")
        print()

        if issues:
            print(f"{'Rule ID':<40} {'Files':<8} Description")
            print("-" * 80)
            for issue in issues:
                print(f"{issue['rule_id']:<40} {issue['file_count']:<8} {issue['description']}")
            print("=" * 80)
        else:
            print("No migration issues found.")


def analyze_file_issues(output_file, target_file, limit=10):
    """Get detailed issues for a specific file

    Args:
        output_file: Path to Kantra output.yaml
        target_file: File to analyze
        limit: Maximum number of distinct issues to return (default: 10)

    Returns detailed issues found in the target file.
    Shows description and message for each distinct rule, limited to help focus on priority issues.
    """
    data = load_kantra_output(output_file)
    if not data:
        sys.exit(1)

    issues_found = {}  # rule_id -> issue_data

    for ruleset in data:
        if not isinstance(ruleset, dict) or 'violations' not in ruleset:
            continue

        violations = ruleset.get('violations')
        if not isinstance(violations, dict):
            continue

        for rule_id, violation in violations.items():
            if not isinstance(violation, dict):
                continue

            description = violation.get('description', 'No description')
            incidents = violation.get('incidents', [])

            if not isinstance(incidents, list):
                continue

            # Check if this rule affects the target file
            file_incidents = []
            messages = set()

            for incident in incidents:
                if not isinstance(incident, dict):
                    continue

                uri = incident.get('uri', '')
                if isinstance(uri, str) and uri.startswith('file://'):
                    file_path = uri[7:]
                    # Match exact path or filename
                    if file_path == target_file or file_path.endswith(target_file):
                        file_incidents.append(incident)
                        message = incident.get('message', '')
                        if message:
                            messages.add(message)

            if file_incidents:
                issues_found[rule_id] = {
                    'rule_id': rule_id,
                    'description': description,
                    'messages': sorted(list(messages)) if messages else ['No specific message']
                }

    if not issues_found:
        print(json.dumps({
            'error': f'No issues found for file: {target_file}',
            'suggestion': 'Verify the file path. Try using just the filename if full path does not match.'
        }, indent=2))
        return

    # Limit to top N distinct issues
    limited_issues = list(issues_found.values())[:limit]

    result = {
        'file': target_file,
        'total_distinct_issues': len(issues_found),
        'returned': len(limited_issues),
        'has_more': len(issues_found) > limit,
        'issues': limited_issues
    }

    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Kantra migration output to identify issues requiring fixes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  analyze   Get overview of all issues. Use this FIRST to understand migration scope.
  file      Get detailed issues for specific file. Use when ready to fix that file.

Examples:
  # Get JSON summary of all issues (default)
  python3 kantra_output_helper.py analyze output.yaml

  # Get text summary
  python3 kantra_output_helper.py analyze output.yaml --format text

  # Get issues for specific file (shows top 10 by default)
  python3 kantra_output_helper.py file output.yaml src/Main.java

  # Get more issues for a file
  python3 kantra_output_helper.py file output.yaml src/Main.java --limit 20

Workflow:
  1. Run 'analyze' to understand all issues and their scope
  2. Use 'file' command to drill into specific files when ready to fix
  3. Apply fixes following rule recommendations
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Get overview of all migration issues'
    )
    analyze_parser.add_argument(
        'output_file',
        help='Path to Kantra output.yaml file'
    )
    analyze_parser.add_argument(
        '--format',
        choices=['json', 'text'],
        default='json',
        help='Output format (default: json)'
    )

    # file command
    file_parser = subparsers.add_parser(
        'file',
        help='Get detailed issues for specific file'
    )
    file_parser.add_argument(
        'output_file',
        help='Path to Kantra output.yaml file'
    )
    file_parser.add_argument(
        'target_file',
        help='File to analyze (full path or filename)'
    )
    file_parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum distinct issues to return (default: 10)'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Validate output file exists
    if not Path(args.output_file).exists():
        print(f"Error: Kantra output file not found: {args.output_file}", file=sys.stderr)
        print(f"Suggestion: Check that Kantra analysis completed successfully.", file=sys.stderr)
        sys.exit(1)

    # Execute command
    if args.command == 'analyze':
        analyze_issues(args.output_file, args.format)
    elif args.command == 'file':
        analyze_file_issues(args.output_file, args.target_file, args.limit)


if __name__ == "__main__":
    main()
