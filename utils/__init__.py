from pathlib import Path

# Base directory of the project repository
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return PROJECT_ROOT