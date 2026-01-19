#!/usr/bin/env python3
"""
analyze-pr.py - Analyze PR complexity and provide review recommendations
Usage: python analyze-pr.py <PR_NUMBER> <REPO>
"""

import sys
import json
import subprocess
import re
from collections import defaultdict


def run_gh_command(args):
    """Run GitHub CLI command and return output"""
    result = subprocess.run(
        ['gh'] + args,
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout


def get_pr_data(pr_number, repo):
    """Get PR metadata"""
    output = run_gh_command([
        'pr', 'view', pr_number,
        '--repo', repo,
        '--json', 'title,body,additions,deletions,changedFiles,files,author,state'
    ])
    return json.loads(output)


def categorize_files(files):
    """Categorize files by type and priority"""
    categories = {
        'critical': [],
        'high': [],
        'medium': [],
        'low': [],
        'tests': [],
        'docs': [],
        'config': []
    }

    patterns = {
        'critical': [
            r'auth', r'security', r'password', r'token', r'crypto',
            r'payment', r'billing'
        ],
        'high': [
            r'src/.*\.(js|ts|py|java|go|rs)$',
            r'lib/', r'core/', r'api/'
        ],
        'tests': [
            r'test/', r'spec/', r'\\.test\\.', r'\\.spec\\.',
            r'__tests__/', r'_test\\.', r'_spec\\.'
        ],
        'docs': [
            r'\\.md$', r'docs/', r'README', r'CHANGELOG'
        ],
        'config': [
            r'\\.json$', r'\\.ya?ml$', r'\\.toml$', r'\\.ini$',
            r'config/', r'\\.config\\.', r'Dockerfile', r'\\.env'
        ]
    }

    for file_info in files:
        path = file_info['path']
        additions = file_info.get('additions', 0)
        deletions = file_info.get('deletions', 0)

        # Check critical patterns first
        is_critical = any(re.search(p, path, re.I) for p in patterns['critical'])
        if is_critical:
            categories['critical'].append((path, additions, deletions))
            continue

        # Check other categories
        is_test = any(re.search(p, path, re.I) for p in patterns['tests'])
        if is_test:
            categories['tests'].append((path, additions, deletions))
            continue

        is_doc = any(re.search(p, path, re.I) for p in patterns['docs'])
        if is_doc:
            categories['docs'].append((path, additions, deletions))
            continue

        is_config = any(re.search(p, path, re.I) for p in patterns['config'])
        if is_config:
            categories['config'].append((path, additions, deletions))
            continue

        is_high = any(re.search(p, path, re.I) for p in patterns['high'])
        if is_high:
            categories['high'].append((path, additions, deletions))
            continue

        # Default to medium
        categories['medium'].append((path, additions, deletions))

    return categories


def calculate_complexity_score(pr_data):
    """Calculate complexity score (0-100)"""
    additions = pr_data['additions']
    deletions = pr_data['deletions']
    files_changed = pr_data['changedFiles']

    # Base score components
    size_score = min(additions + deletions, 5000) / 5000 * 40  # Max 40 points
    file_score = min(files_changed, 50) / 50 * 30  # Max 30 points

    # Complexity multipliers
    avg_changes_per_file = (additions + deletions) / max(files_changed, 1)
    complexity_multiplier = min(avg_changes_per_file, 200) / 200 * 30  # Max 30 points

    total_score = size_score + file_score + complexity_multiplier

    return round(total_score, 2)


def estimate_review_time(pr_data, categories):
    """Estimate review time in minutes"""
    # Base time per line of code (minutes)
    time_per_line = 0.1

    # Category time multipliers
    multipliers = {
        'critical': 3.0,  # 3x time for critical files
        'high': 2.0,
        'medium': 1.5,
        'low': 1.0,
        'tests': 0.5,  # Faster to review tests
        'docs': 0.2,   # Very fast to review docs
        'config': 0.3
    }

    total_time = 0

    for category, files in categories.items():
        if not files:
            continue

        multiplier = multipliers.get(category, 1.0)

        for path, additions, deletions in files:
            lines = additions + deletions
            total_time += lines * time_per_line * multiplier

    # Add overhead time
    overhead = 10  # 10 minutes for context switching, PR description, etc.
    total_time += overhead

    return round(total_time)


def get_review_strategy(complexity_score, files_changed, categories):
    """Recommend review strategy"""
    if complexity_score < 20:
        strategy = "Quick Review"
        description = "Small, focused change. Review all files in one session."
    elif complexity_score < 50:
        strategy = "Standard Review"
        description = "Medium-sized PR. Review by category, starting with critical files."
    else:
        strategy = "Phased Review"
        description = "Large PR. Break into multiple review sessions by priority."

    # Build review order
    review_order = []
    if categories['critical']:
        review_order.append("1. Critical files (security, auth, payments)")
    if categories['high']:
        review_order.append("2. High-priority files (core functionality)")
    if categories['medium']:
        review_order.append("3. Medium-priority files (utilities, helpers)")
    if categories['tests']:
        review_order.append("4. Tests (verify coverage)")
    if categories['config']:
        review_order.append("5. Configuration changes")
    if categories['docs']:
        review_order.append("6. Documentation")

    return {
        'strategy': strategy,
        'description': description,
        'order': review_order
    }


def print_analysis(pr_data, categories, complexity_score, review_time, strategy):
    """Print formatted analysis"""
    print("\n" + "="*70)
    print(f"PR #{pr_data['number']} Analysis: {pr_data['title']}")
    print("="*70 + "\n")

    # Basic info
    print(f"Author: @{pr_data['author']['login']}")
    print(f"State: {pr_data['state']}")
    print(f"Changes: +{pr_data['additions']} / -{pr_data['deletions']}")
    print(f"Files: {pr_data['changedFiles']}")
    print()

    # Complexity assessment
    print(f"Complexity Score: {complexity_score}/100")
    if complexity_score < 20:
        level = "LOW 🟢"
    elif complexity_score < 50:
        level = "MEDIUM 🟡"
    else:
        level = "HIGH 🔴"
    print(f"Complexity Level: {level}")
    print()

    # Time estimate
    print(f"Estimated Review Time: {review_time} minutes ({review_time/60:.1f} hours)")
    print()

    # File categories
    print("File Breakdown:")
    print("-" * 70)
    for category, files in categories.items():
        if not files:
            continue

        total_changes = sum(additions + deletions for _, additions, deletions in files)
        icon = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '⚪',
            'tests': '🧪',
            'docs': '📄',
            'config': '⚙️'
        }.get(category, '📁')

        print(f"{icon} {category.upper()}: {len(files)} files, {total_changes} lines")

        if category in ['critical', 'high']:
            for path, additions, deletions in files[:5]:  # Show top 5
                print(f"    - {path} (+{additions}/-{deletions})")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")
        print()

    # Review strategy
    print("Recommended Review Strategy:")
    print("-" * 70)
    print(f"Strategy: {strategy['strategy']}")
    print(f"Description: {strategy['description']}")
    print()
    print("Review Order:")
    for step in strategy['order']:
        print(f"  {step}")
    print()

    # Warnings
    warnings = []
    if categories['critical']:
        warnings.append("⚠️  Contains security-sensitive files - thorough review required")
    if pr_data['additions'] + pr_data['deletions'] > 1000:
        warnings.append("⚠️  Large changeset - consider requesting breakdown into smaller PRs")
    if pr_data['changedFiles'] > 30:
        warnings.append("⚠️  Many files changed - verify this is intentional")
    if not categories['tests'] and (categories['high'] or categories['critical']):
        warnings.append("⚠️  No test files modified - verify test coverage")

    if warnings:
        print("Warnings:")
        print("-" * 70)
        for warning in warnings:
            print(warning)
        print()

    print("="*70 + "\n")


def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze-pr.py <PR_NUMBER> <REPO>")
        print("Example: python analyze-pr.py 123 owner/repo")
        sys.exit(1)

    pr_number = sys.argv[1]
    repo = sys.argv[2]

    try:
        # Get PR data
        pr_data = get_pr_data(pr_number, repo)

        # Analyze files
        categories = categorize_files(pr_data.get('files', []))

        # Calculate metrics
        complexity_score = calculate_complexity_score(pr_data)
        review_time = estimate_review_time(pr_data, categories)
        strategy = get_review_strategy(
            complexity_score,
            pr_data['changedFiles'],
            categories
        )

        # Print analysis
        print_analysis(pr_data, categories, complexity_score, review_time, strategy)

        # Output JSON for programmatic use
        if '--json' in sys.argv:
            output = {
                'pr_number': pr_number,
                'complexity_score': complexity_score,
                'review_time_minutes': review_time,
                'strategy': strategy,
                'categories': {k: len(v) for k, v in categories.items()}
            }
            print(json.dumps(output, indent=2))

    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to run GitHub CLI command", file=sys.stderr)
        print(f"Details: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
