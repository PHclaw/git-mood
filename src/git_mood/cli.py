"""CLI entry point for git-mood."""

import argparse
import sys
from pathlib import Path

from .analyzer import MoodAnalyzer


def main():
    parser = argparse.ArgumentParser(
        prog="git-mood",
        description="🎮 Analyze your git commits to visualize your coding mood, energy, and work patterns.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  git-mood analyze                    # Analyze current repo (last 30 days)
  git-mood analyze /path/to/repo      # Analyze specific repo
  git-mood analyze --days 90          # Analyze last 90 days
  git-mood analyze --format html --output report.html
  git-mood analyze --contributors     # Show per-author mood breakdown
  git-mood trend                      # Show mood trend line chart
  git-mood compare alice bob          # Compare two contributors
  git-mood report --llm               # Full report with LLM mood analysis

License: MIT. Made with 😊 by PHclaw.
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze git commits for mood")
    analyze_parser.add_argument("path", nargs="?", default=".", help="Path to git repository (default: current directory)")
    analyze_parser.add_argument("--days", "-d", type=int, default=30, help="Number of days to analyze (default: 30)")
    analyze_parser.add_argument("--format", "-f", choices=["text", "json", "html"], default="text", help="Output format")
    analyze_parser.add_argument("--output", "-o", help="Write output to file")
    analyze_parser.add_argument("--no-emoji", action="store_true", help="Disable emoji output")
    analyze_parser.add_argument("--no-color", action="store_true", help="Disable color codes")
    analyze_parser.add_argument("--contributors", action="store_true", help="Show per-author breakdown")
    analyze_parser.add_argument("--llm", action="store_true", help="Use LLM for deeper mood analysis (requires OPENAI_API_KEY)")
    analyze_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    # compare command
    compare_parser = subparsers.add_parser("compare", help="Compare mood between authors or repos")
    compare_parser.add_argument("left", help="First author or repo path")
    compare_parser.add_argument("right", help="Second author or repo path")
    compare_parser.add_argument("--format", "-f", choices=["text", "json"], default="text")
    compare_parser.add_argument("--output", "-o")

    # trend command
    trend_parser = subparsers.add_parser("trend", help="Show mood trend over time")
    trend_parser.add_argument("path", nargs="?", default=".")
    trend_parser.add_argument("--days", "-d", type=int, default=90)
    trend_parser.add_argument("--format", "-f", choices=["text", "json"], default="text")

    # report command
    report_parser = subparsers.add_parser("report", help="Generate full mood report")
    report_parser.add_argument("path", nargs="?", default=".")
    report_parser.add_argument("--days", "-d", type=int, default=90)
    report_parser.add_argument("--output", "-o", required=True, help="Output file path")
    report_parser.add_argument("--format", choices=["html", "json"], default="html")
    report_parser.add_argument("--llm", action="store_true")

    args = parser.parse_args()

    if args.command is None:
        # Default: analyze current directory
        args.command = "analyze"
        args.path = "."
        args.format = "text"
        args.no_emoji = False
        args.no_color = False
        args.contributors = False
        args.llm = False
        args.verbose = False

    try:
        if args.command == "analyze":
            analyzer = MoodAnalyzer(
                repo_path=args.path,
                days=args.days,
                use_llm=args.llm,
                show_emoji=not args.no_emoji,
                use_color=not args.no_color,
                verbose=args.verbose,
            )
            result = analyzer.analyze()

            if args.format == "json":
                output = result.to_json()
            elif args.format == "html":
                output = result.to_html()
            else:
                output = result.to_text(show_contributors=args.contributors)

        elif args.command == "compare":
            from .comparator import MoodComparator
            comp = MoodComparator()
            result = comp.compare_authors(args.left, args.right)
            output = result.to_text() if args.format == "text" else result.to_json()

        elif args.command == "trend":
            analyzer = MoodAnalyzer(repo_path=args.path, days=args.days)
            result = analyzer.trend()
            output = result.to_text() if args.format == "text" else result.to_json()

        elif args.command == "report":
            analyzer = MoodAnalyzer(repo_path=args.path, days=args.days, use_llm=args.llm)
            result = analyzer.full_report()
            if args.format == "json":
                output = result.to_json()
            else:
                output = result.to_html()

        # Output
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"✓ Report written to {args.output}")
        else:
            print(output)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose or (hasattr(args, 'verbose') and args.verbose):
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()