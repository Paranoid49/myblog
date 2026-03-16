from unittest.mock import MagicMock, patch

import pytest

from scripts.start_fullstack import FRONTEND_DEV_ENV_FILE, main


def _mock_process(poll_return: int | None = None):
    process = MagicMock()
    process.poll.return_value = poll_return
    process.wait.return_value = 0
    return process


def test_start_fullstack_starts_backend_and_frontend_and_opens_browser(tmp_path) -> None:
    backend = _mock_process(poll_return=None)
    frontend = _mock_process(poll_return=None)
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()

    with (
        patch("scripts.start_fullstack.Path.resolve", return_value=tmp_path / "scripts" / "start_fullstack.py"),
        patch("scripts.start_fullstack.subprocess.Popen", side_effect=[backend, frontend]) as mock_popen,
        patch("scripts.start_fullstack._resolve_npm_command", return_value=["npm"]),
        patch("scripts.start_fullstack.webbrowser.open") as mock_open,
        patch("builtins.print") as mock_print,
    ):
        main(["--backend-port", "8000", "--frontend-port", "5173"])

    env_file = frontend_dir / FRONTEND_DEV_ENV_FILE
    assert not env_file.exists()

    assert mock_popen.call_count == 2
    backend_cmd = mock_popen.call_args_list[0].args[0]
    frontend_cmd = mock_popen.call_args_list[1].args[0]
    frontend_env = mock_popen.call_args_list[1].kwargs["env"]
    frontend_cwd = mock_popen.call_args_list[1].kwargs["cwd"]

    assert "start_blog.py" in " ".join(backend_cmd)
    assert frontend_cmd[0].lower().endswith("npm") or frontend_cmd[0].lower().endswith("npm.cmd")
    assert frontend_cmd[1:3] == ["run", "dev"]
    assert frontend_env["VITE_API_TARGET"] == "http://127.0.0.1:8000"
    assert frontend_cwd.endswith("frontend")

    mock_open.assert_called_once_with("http://127.0.0.1:8000/")
    mock_print.assert_any_call("FRONTEND_URL=http://127.0.0.1:5173/admin/login")
    assert backend.wait.call_count >= 1
    frontend.terminate.assert_called_once()


def test_start_fullstack_supports_no_browser() -> None:
    backend = _mock_process(poll_return=None)
    frontend = _mock_process(poll_return=None)

    with (
        patch("scripts.start_fullstack.subprocess.Popen", side_effect=[backend, frontend]),
        patch("scripts.start_fullstack._resolve_npm_command", return_value=["npm"]),
        patch("scripts.start_fullstack.webbrowser.open") as mock_open,
    ):
        main(["--no-browser"])

    mock_open.assert_not_called()


def test_start_fullstack_exits_when_npm_missing() -> None:
    backend = _mock_process(poll_return=None)

    with (
        patch("scripts.start_fullstack.subprocess.Popen", return_value=backend),
        patch("scripts.start_fullstack._resolve_npm_command", side_effect=RuntimeError("npm_not_found_in_path")),
        pytest.raises(SystemExit),
    ):
        main([])
