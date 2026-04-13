#!/usr/bin/env python3
"""
Isolated type checking for multi_search_service.py
"""

import subprocess
import sys


def check_multi_search_service() -> int:
    """Check only multi_search_service.py for type errors."""
    cmd = [
        sys.executable,
        "-m",
        "mypy",
        "app/services/multi_search_service.py",
        "--show-error-codes",
        "--no-error-summary",
        "--no-implicit-reexport",
        "--follow-imports",
        "silent",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd="/home/ishanp/Documents/GitHub/scrapecraft/backend",
    )

    # Filter only lines that contain multi_search_service.py
    multi_search_errors = []
    for line in result.stdout.split("\n"):
        if "multi_search_service.py:" in line:
            multi_search_errors.append(line)

    print("Multi Search Service Type Errors:")
    for error in multi_search_errors:
        print(error)

    return len(multi_search_errors)


if __name__ == "__main__":
    error_count = check_multi_search_service()
    print(f"\nTotal errors in multi_search_service.py: {error_count}")
