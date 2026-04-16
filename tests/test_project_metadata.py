import runpy
import tomllib
from pathlib import Path

import setuptools


ROOT = Path(__file__).resolve().parents[1]


def read_requirements() -> list[str]:
    return [
        line.strip()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def read_pyproject() -> dict:
    with (ROOT / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)


def read_setup_kwargs(monkeypatch) -> dict:
    captured = {}

    def fake_setup(**kwargs):
        captured.update(kwargs)

    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(setuptools, "setup", fake_setup)
    runpy.run_path(str(ROOT / "setup.py"), run_name="__main__")
    return captured


def test_runtime_requirements_match_pyproject_dependencies():
    requirements = read_requirements()
    pyproject_dependencies = read_pyproject()["project"]["dependencies"]

    assert requirements == pyproject_dependencies
    assert not any(item.lower().startswith("python") for item in requirements)


def test_setup_metadata_matches_pyproject(monkeypatch):
    setup_kwargs = read_setup_kwargs(monkeypatch)
    pyproject = read_pyproject()["project"]

    console_scripts = dict(
        item.split("=", 1) for item in setup_kwargs["entry_points"]["console_scripts"]
    )

    assert setup_kwargs["install_requires"] == pyproject["dependencies"]
    assert setup_kwargs["extras_require"]["dev"] == pyproject["optional-dependencies"]["dev"]
    assert console_scripts == pyproject["scripts"]


def test_console_scripts_use_shared_cli_module():
    scripts = read_pyproject()["project"]["scripts"]

    assert scripts == {
        "fraud-analyzer": "src.cli:analyze_main",
        "batch-fraud-analyzer": "src.cli:batch_main",
    }


def test_readme_documents_install_and_console_script_usage():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "pip install -r requirements.txt" in readme
    assert "pip install -e ." in readme
    assert "fraud-analyzer" in readme
    assert "batch-fraud-analyzer" in readme
