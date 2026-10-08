"""Quality exercises: negative hours and console errors."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from catalog.search import search_courses

PROJECT = Path(__file__).resolve().parents[1]


def test_negative_hours(tmp_path: Path) -> None:
    # Un curso con horas negativas no pasa la validacion de Pydantic.
    path = tmp_path / "courses.json"
    path.write_text(json.dumps([{"code": "X1", "title": "Python", "hours": -5}]))
    with pytest.raises(ValueError):
        search_courses("python", path)


def test_console_missing_file(tmp_path: Path) -> None:
    # Ejecuta main.py como lo haria una persona desde la terminal.
    result = subprocess.run(
        [sys.executable, "main.py", "python", "--catalog", str(tmp_path / "x.json")],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert result.stdout == ""
