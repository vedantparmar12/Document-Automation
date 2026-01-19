#!/usr/bin/env python3
"""
Repository Analyzer Script

Analyzes a GitHub repository or local directory and outputs
a comprehensive analysis report.

Usage:
    python analyze-repo.py <path_or_url> [options]

Examples:
    python analyze-repo.py https://github.com/user/repo
    python analyze-repo.py /path/to/local/project --local
    python analyze-repo.py https://github.com/user/repo --output analysis.json
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.analyzers.codebase_analyzer import CodebaseAnalyzer
    from src.analyzers.framework_detector import FrameworkDetector
    from src.analyzers.enhanced_analyzer import EnhancedAnalyzer
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the Document-Automation directory")
    print("and have installed dependencies: pip install -r requirements.txt")
    sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Analyze a codebase and generate analysis report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://github.com/facebook/react
  %(prog)s /home/user/myproject --local
  %(prog)s https://github.com/user/repo --output report.json
  %(prog)s . --local --format markdown
        """
    )

    parser.add_argument(
        'path',
        help='GitHub repository URL or local directory path'
    )

    parser.add_argument(
        '--local', '-l',
        action='store_true',
        help='Treat path as local directory (default: auto-detect)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: stdout)'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['json', 'markdown', 'summary'],
        default='summary',
        help='Output format (default: summary)'
    )

    parser.add_argument(
        '--max-depth', '-d',
        type=int,
        default=5,
        help='Maximum directory depth to analyze (default: 5)'
    )

    parser.add_argument(
        '--include',
        help='Glob pattern for files to include (e.g., "*.py")'
    )

    parser.add_argument(
        '--exclude',
        help='Glob pattern for files to exclude (e.g., "**/test*")'
    )

    parser.add_argument(
        '--shallow',
        action='store_true',
        help='Perform shallow analysis (faster, less detailed)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    return parser.parse_args()


def detect_source_type(path: str, force_local: bool = False) -> str:
    """Detect if path is GitHub URL or local directory."""
    if force_local:
        return 'local'

    if path.startswith(('https://github.com/', 'git@github.com:', 'github.com/')):
        return 'github'

    if os.path.exists(path):
        return 'local'

    # Default to GitHub if it looks like a repo reference
    if '/' in path and not path.startswith('/'):
        return 'github'

    return 'local'


def format_as_summary(analysis: dict) -> str:
    """Format analysis as human-readable summary."""
    lines = []

    lines.append("=" * 60)
    lines.append(f"PROJECT ANALYSIS: {analysis.get('project_name', 'Unknown')}")
    lines.append("=" * 60)
    lines.append("")

    # Basic Info
    lines.append("OVERVIEW")
    lines.append("-" * 40)
    lines.append(f"  Type: {analysis.get('project_type', 'Unknown')}")
    lines.append(f"  Description: {analysis.get('description', 'N/A')}")
    lines.append("")

    # Languages
    languages = analysis.get('languages', [])
    if languages:
        lines.append("LANGUAGES")
        lines.append("-" * 40)
        for lang in languages[:10]:
            lines.append(f"  - {lang}")
        lines.append("")

    # Frameworks
    frameworks = analysis.get('frameworks', [])
    if frameworks:
        lines.append("FRAMEWORKS & LIBRARIES")
        lines.append("-" * 40)
        for fw in frameworks[:10]:
            lines.append(f"  - {fw}")
        lines.append("")

    # Key Features
    features = analysis.get('key_features', {})
    if features:
        lines.append("KEY FEATURES")
        lines.append("-" * 40)
        for category, items in list(features.items())[:5]:
            lines.append(f"  {category}:")
            if isinstance(items, list):
                for item in items[:5]:
                    lines.append(f"    - {item}")
            else:
                lines.append(f"    - {items}")
        lines.append("")

    # File Structure Summary
    structure = analysis.get('file_structure', {})
    if structure:
        lines.append("FILE STRUCTURE")
        lines.append("-" * 40)
        total_files = structure.get('total_files', 0)
        total_dirs = structure.get('total_directories', 0)
        lines.append(f"  Total Files: {total_files}")
        lines.append(f"  Total Directories: {total_dirs}")
        lines.append("")

    # Dependencies
    deps = analysis.get('dependencies', {})
    if deps:
        lines.append("DEPENDENCIES")
        lines.append("-" * 40)
        dep_count = len(deps) if isinstance(deps, dict) else 0
        lines.append(f"  Total: {dep_count}")
        if isinstance(deps, dict):
            for name, version in list(deps.items())[:10]:
                lines.append(f"  - {name}: {version}")
        lines.append("")

    lines.append("=" * 60)
    lines.append(f"Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)

    return "\n".join(lines)


def format_as_markdown(analysis: dict) -> str:
    """Format analysis as Markdown."""
    lines = []

    name = analysis.get('project_name', 'Unknown Project')
    lines.append(f"# {name}")
    lines.append("")
    lines.append(f"> {analysis.get('description', 'No description available')}")
    lines.append("")

    # Overview
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- **Type**: {analysis.get('project_type', 'Unknown')}")

    languages = analysis.get('languages', [])
    if languages:
        lines.append(f"- **Languages**: {', '.join(languages[:5])}")

    frameworks = analysis.get('frameworks', [])
    if frameworks:
        lines.append(f"- **Frameworks**: {', '.join(frameworks[:5])}")
    lines.append("")

    # Key Features
    features = analysis.get('key_features', {})
    if features:
        lines.append("## Key Features")
        lines.append("")
        for category, items in features.items():
            lines.append(f"### {category}")
            if isinstance(items, list):
                for item in items:
                    lines.append(f"- {item}")
            else:
                lines.append(f"- {items}")
            lines.append("")

    # Dependencies
    deps = analysis.get('dependencies', {})
    if deps and isinstance(deps, dict):
        lines.append("## Dependencies")
        lines.append("")
        lines.append("| Package | Version |")
        lines.append("|---------|---------|")
        for name, version in list(deps.items())[:20]:
            lines.append(f"| {name} | {version} |")
        lines.append("")

    # File Structure
    lines.append("## File Structure")
    lines.append("")
    lines.append("```")
    structure = analysis.get('file_structure', {})
    if 'tree' in structure:
        lines.append(structure['tree'])
    else:
        lines.append(f"Total Files: {structure.get('total_files', 'N/A')}")
        lines.append(f"Total Directories: {structure.get('total_directories', 'N/A')}")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point."""
    args = parse_args()

    # Detect source type
    source_type = detect_source_type(args.path, args.local)

    if args.verbose:
        print(f"Analyzing: {args.path}")
        print(f"Source type: {source_type}")
        print(f"Max depth: {args.max_depth}")
        print("")

    try:
        # Initialize analyzer
        analyzer = CodebaseAnalyzer()

        # Configure options
        options = {
            'max_depth': args.max_depth,
            'include_pattern': args.include,
            'exclude_pattern': args.exclude,
            'shallow': args.shallow
        }

        # Run analysis
        if args.verbose:
            print("Running analysis...")

        result = analyzer.analyze(args.path, source_type=source_type, **options)

        # Convert result to dict if needed
        if hasattr(result, 'dict'):
            analysis = result.dict()
        elif hasattr(result, '__dict__'):
            analysis = result.__dict__
        else:
            analysis = dict(result) if result else {}

        # Format output
        if args.format == 'json':
            output = json.dumps(analysis, indent=2, default=str)
        elif args.format == 'markdown':
            output = format_as_markdown(analysis)
        else:
            output = format_as_summary(analysis)

        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            if args.verbose:
                print(f"Output written to: {args.output}")
        else:
            print(output)

        return 0

    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
