from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_TEST_TARGETS = [
    "tests/test_api_v1_auth.py",
    "tests/test_api_v1_posts.py",
    "tests/test_public_pages.py",
    "tests/test_e2e_smoke.py",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="阶段1/2一键验收脚本")
    parser.add_argument("--skip-frontend-build", action="store_true", help="跳过前端构建")
    parser.add_argument("--keep-test-db", action="store_true", help="保留 test.db，不自动清理")
    return parser


def run_command(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    project_root = Path(__file__).resolve().parents[1]
    frontend_dir = project_root / "frontend"
    test_db = project_root / "test.db"

    try:
        if not args.skip_frontend_build:
            run_command(["npm", "--prefix", str(frontend_dir), "run", "build"])

        run_command([sys.executable, "-m", "pytest", "-q", *DEFAULT_TEST_TARGETS])
    finally:
        if not args.keep_test_db:
            test_db.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
