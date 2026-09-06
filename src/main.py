"""Main entrypoint for scheduled runs.

python -m src.main --mode daily|weekly|build|verify
"""

import argparse
import sys


def run(mode: str) -> int:
    if mode == "verify":
        from .verify import main as verify_main
        return verify_main()
    if mode == "daily":
        from .actions.daily_monitor import run as daily
        return daily()
    if mode == "weekly":
        from .actions.weekly_analysis import run as weekly
        return weekly()
    if mode == "build":
        from .actions.build_campaign import run as build
        return build()
    print(f"Unknown mode: {mode}")
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="SalesNexus Ads agent runner")
    parser.add_argument("--mode", choices=["daily", "weekly", "build", "verify"],
                        default="daily")
    args = parser.parse_args()
    return run(args.mode)


if __name__ == "__main__":
    sys.exit(main())