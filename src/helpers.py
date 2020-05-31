from pathlib import Path


def ensure_directory(directory_in):
    """Check if folder exist and create it otherwise"""
    Path(directory_in).mkdir(parents=True, exist_ok=True)
