from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import webbrowser
from contextlib import suppress
from pathlib import Path


DEFAULT_HOST = "127.0.0.1"
DEFAULT_BACKEND_PORT = 8000
DEFAULT_FRONTEND_PORT = 5173


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="一键启动前后端开发服务")
    parser.add_argument("--backend-port", type=int, default=DEFAULT_BACKEND_PORT)
    parser.add_argument("--frontend-port", type=int, default=DEFAULT_FRONTEND_PORT)
    parser.add_argument("--no-browser", action="store_true", help="启动后不自动打开浏览器")
    return parser


def _start_backend(project_root: Path, backend_port: int) -> subprocess.Popen:
    command = [
        sys.executable,
        str(project_root / "scripts" / "start_blog.py"),
        "--port",
        str(backend_port),
    ]
    return subprocess.Popen(command)


def _resolve_npm_command() -> list[str]:
    npm_path = shutil.which("npm")
    if npm_path:
        return [npm_path]

    if sys.platform.startswith("win"):
        npm_cmd = shutil.which("npm.cmd")
        if npm_cmd:
            return [npm_cmd]

    raise RuntimeError("npm_not_found_in_path")


def _start_frontend(project_root: Path, frontend_port: int) -> subprocess.Popen:
    npm_command = _resolve_npm_command()
    command = [
        *npm_command,
        "--prefix",
        str(project_root / "frontend"),
        "run",
        "dev",
        "--",
        "--host",
        DEFAULT_HOST,
        "--port",
        str(frontend_port),
    ]
    return subprocess.Popen(command)


def _stop_process(process: subprocess.Popen | None) -> None:
    if process is None or process.poll() is not None:
        return
    with suppress(Exception):
        process.terminate()
    with suppress(Exception):
        process.wait(timeout=5)
    if process.poll() is None:
        with suppress(Exception):
            process.kill()


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    project_root = Path(__file__).resolve().parents[1]

    backend_process: subprocess.Popen | None = None
    frontend_process: subprocess.Popen | None = None

    backend_url = f"http://{DEFAULT_HOST}:{args.backend_port}/"
    frontend_url = f"http://{DEFAULT_HOST}:{args.frontend_port}/admin/login"

    try:
        backend_process = _start_backend(project_root, args.backend_port)
        frontend_process = _start_frontend(project_root, args.frontend_port)

        print(f"BACKEND_URL={backend_url}")
        print(f"FRONTEND_URL={frontend_url}")
        print("按 Ctrl+C 可停止前后端服务")

        if not args.no_browser:
            webbrowser.open(backend_url)

        backend_process.wait()
    except RuntimeError as exc:
        if str(exc) == "npm_not_found_in_path":
            raise SystemExit("未找到 npm，请先安装 Node.js 并确保 npm 在 PATH 中") from exc
        raise
    finally:
        _stop_process(frontend_process)
        _stop_process(backend_process)


if __name__ == "__main__":
    main()
