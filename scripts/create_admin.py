from __future__ import annotations

import argparse
import os


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create initial admin user placeholder.")
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL", "admin@example.com"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD", "change-me-please"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Admin bootstrap placeholder for {args.email}")


if __name__ == "__main__":
    main()
