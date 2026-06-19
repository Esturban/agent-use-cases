import argparse
import json

from src.workflow import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Brand news sentiment monitor")
    parser.add_argument("brand", help="Brand or company name to monitor")
    parser.add_argument(
        "--days", type=int, default=7, help="Number of days back to search (default: 7)"
    )
    args = parser.parse_args()

    digest = run(args.brand, args.days)
    print(json.dumps(digest.model_dump(), indent=2))


if __name__ == "__main__":
    main()
