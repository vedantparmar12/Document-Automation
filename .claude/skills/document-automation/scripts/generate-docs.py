#!/usr/bin/env python3
"""
Documentation Generator Script

Generates comprehensive documentation for a codebase.

Usage:
    python generate-docs.py <path> [options]

Examples:
    python generate-docs.py /path/to/project
    python generate-docs.py . --format html --output docs/
    python generate-docs.py https://github.com/user/repo --format pdf
"""

import argparse
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
    from src.generators.professional_doc_generator import ProfessionalDocumentationGenerator
    from src.schemas import CodeAnalysisResult
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the Document-Automation directory")
    print("and have installed dependencies: pip install -r requirements.txt")
    sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate documentation for a codebase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/project
  %(prog)s . --format html --output docs/
  %(prog)s https://github.com/user/repo --format pdf --output output.pdf
  %(prog)s . --include-diagrams --include-api
        """
    )

    parser.add_argument(
        'path',
        help='Project path or GitHub URL'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file or directory path'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'html', 'pdf', 'rst'],
        default='markdown',
        help='Output format (default: markdown)'
    )

    parser.add_argument(
        '--local', '-l',
        action='store_true',
        help='Treat path as local directory'
    )

    parser.add_argument(
        '--include-diagrams',
        action='store_true',
        default=True,
        help='Include architecture diagrams (default: true)'
    )

    parser.add_argument(
        '--no-diagrams',
        action='store_true',
        help='Exclude architecture diagrams'
    )

    parser.add_argument(
        '--include-api',
        action='store_true',
        default=True,
        help='Include API documentation (default: true)'
    )

    parser.add_argument(
        '--no-api',
        action='store_true',
        help='Exclude API documentation'
    )

    parser.add_argument(
        '--include-examples',
        action='store_true',
        default=True,
        help='Include code examples (default: true)'
    )

    parser.add_argument(
        '--theme',
        choices=['light', 'dark', 'professional'],
        default='professional',
        help='Documentation theme (default: professional)'
    )

    parser.add_argument(
        '--title',
        help='Custom documentation title'
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

    return 'local'


def get_output_path(args) -> str:
    """Determine output file path based on arguments."""
    if args.output:
        return args.output

    # Generate default output filename
    ext_map = {
        'markdown': '.md',
        'html': '.html',
        'pdf': '.pdf',
        'rst': '.rst'
    }
    ext = ext_map.get(args.format, '.md')

    # Use project name from path
    path_name = Path(args.path).name or 'documentation'
    if path_name.startswith('https://'):
        path_name = path_name.split('/')[-1]

    return f"{path_name}_documentation{ext}"


def main():
    """Main entry point."""
    args = parse_args()

    # Detect source type
    source_type = detect_source_type(args.path, args.local)

    if args.verbose:
        print(f"Analyzing: {args.path}")
        print(f"Source type: {source_type}")
        print(f"Output format: {args.format}")
        print("")

    try:
        # Step 1: Analyze the codebase
        if args.verbose:
            print("Step 1: Analyzing codebase...")

        analyzer = CodebaseAnalyzer()
        analysis_result = analyzer.analyze(args.path, source_type=source_type)

        if args.verbose:
            print(f"  Project: {getattr(analysis_result, 'project_name', 'Unknown')}")
            print(f"  Type: {getattr(analysis_result, 'project_type', 'Unknown')}")
            print("")

        # Step 2: Generate documentation
        if args.verbose:
            print("Step 2: Generating documentation...")

        generator = ProfessionalDocumentationGenerator()

        config = {
            'format': args.format,
            'theme': args.theme,
            'include_diagrams': not args.no_diagrams,
            'include_api_docs': not args.no_api,
            'include_examples': args.include_examples,
        }

        if args.title:
            config['title'] = args.title

        output_path = get_output_path(args)
        config['output_path'] = output_path

        if args.verbose:
            print(f"  Format: {args.format}")
            print(f"  Theme: {args.theme}")
            print(f"  Output: {output_path}")
            print("")

        result = generator.generate(analysis_result, config)

        # Step 3: Write output
        if args.verbose:
            print("Step 3: Writing output...")

        content = result.content if hasattr(result, 'content') else str(result)

        # Ensure output directory exists
        output_dir = Path(output_path).parent
        if output_dir and not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Documentation generated successfully!")
        print(f"Output: {output_path}")

        if hasattr(result, 'metadata'):
            metadata = result.metadata
            if metadata:
                print(f"Word count: {metadata.get('word_count', 'N/A')}")
                print(f"Sections: {metadata.get('sections', 'N/A')}")

        return 0

    except Exception as e:
        print(f"Error generating documentation: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
