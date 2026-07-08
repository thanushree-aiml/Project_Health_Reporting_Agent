import argparse
from rich.console import Console

from config.settings import PROJECT_NAME, VERSION

console = Console()


def cmd_weekly(args: argparse.Namespace) -> None:
    from agent.weekly_reporter import run_weekly

    run_weekly(input_path=args.input, project_name=args.project_name)


def cmd_monthly(args: argparse.Namespace) -> None:
    from agent.monthly_synthesizer import run_monthly

    run_monthly(inputs_pattern=args.inputs, output_name=args.output)


def main() -> None:
    parser = argparse.ArgumentParser(prog="project-health-agent")
    parser.add_argument("--version", action="version", version=VERSION)

    sub = parser.add_subparsers(dest="command", required=True)

    p_weekly = sub.add_parser("weekly", help="Run weekly RAG health report for one project plan")
    p_weekly.add_argument("--input", required=True, help="Path to a project plan file (json/csv/txt)")
    p_weekly.add_argument("--project-name", default=None, help="Override project name")
    p_weekly.set_defaults(func=cmd_weekly)

    p_monthly = sub.add_parser("monthly", help="Synthesize monthly executive insights across multiple weekly outputs")
    p_monthly.add_argument("--inputs", required=True, help="Glob pattern for weekly json outputs")
    p_monthly.add_argument("--output", default="monthly_executive_presentation.pptx", help="Output PPTX filename")
    p_monthly.set_defaults(func=cmd_monthly)

    args = parser.parse_args()

    console.print("=" * 60, style="cyan")
    console.print(f"{PROJECT_NAME}", style="bold green")
    console.print(f"Version : {VERSION}", style="yellow")
    console.print("=" * 60, style="cyan")

    args.func(args)


if __name__ == "__main__":
    main()

