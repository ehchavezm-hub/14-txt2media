"""Tests básicos del CLI."""
import subprocess
import sys


def test_cli_version():
    result = subprocess.run(
        [sys.executable, "-m", "txt2media.cli.main", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "1.0.1" in result.stdout


def test_cli_sin_args():
    result = subprocess.run(
        [sys.executable, "-m", "txt2media.cli.main"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "txt2media" in result.stdout.lower() or "usage" in result.stdout.lower()


def test_cli_info():
    result = subprocess.run(
        [sys.executable, "-m", "txt2media.cli.main", "info"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "1.0.1" in result.stdout
