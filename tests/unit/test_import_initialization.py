"""Regression coverage for concurrent application imports and ORM setup."""

import os
import subprocess
import sys


def test_concurrent_package_imports_register_models_once() -> None:
    script = """
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module

modules = [
    "db.models.organization",
    "db.models.asset",
    "db.models.brand",
    "db.repositories.user_repo",
    "services.brand_service",
    "services.auth",
    "detection.normalization",
    "jobs.scan_runner",
] * 4
with ThreadPoolExecutor(max_workers=12) as executor:
    list(executor.map(import_module, modules))

from db.session import engine, init_db
from sqlalchemy import inspect
init_db()
assert len(inspect(engine).get_table_names()) == 21
"""
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///:memory:"
    env["APP_ENV"] = "development"
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
