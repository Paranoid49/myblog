from unittest.mock import call, patch

from scripts.verify_phase12 import main


def test_verify_phase12_runs_frontend_build_and_pytest_and_cleans_db() -> None:
    with (
        patch("scripts.verify_phase12.run_command") as mock_run,
        patch("pathlib.Path.unlink") as mock_unlink,
    ):
        main([])

    assert mock_run.call_count == 2
    first_command = mock_run.call_args_list[0].args[0]
    second_command = mock_run.call_args_list[1].args[0]

    assert first_command[0] == "npm"
    assert first_command[1] == "--prefix"
    assert first_command[3:5] == ["run", "build"]

    assert second_command[1:4] == ["-m", "pytest", "-q"]
    assert "tests/test_api_v1_auth.py" in second_command
    assert "tests/test_api_v1_posts.py" in second_command
    assert "tests/test_public_pages.py" in second_command
    assert "tests/test_e2e_smoke.py" in second_command

    mock_unlink.assert_called_once_with(missing_ok=True)


def test_verify_phase12_can_skip_frontend_and_keep_test_db() -> None:
    with (
        patch("scripts.verify_phase12.run_command") as mock_run,
        patch("pathlib.Path.unlink") as mock_unlink,
    ):
        main(["--skip-frontend-build", "--keep-test-db"])

    assert mock_run.call_count == 1
    command = mock_run.call_args_list[0].args[0]
    assert command[1:4] == ["-m", "pytest", "-q"]

    mock_unlink.assert_not_called()
