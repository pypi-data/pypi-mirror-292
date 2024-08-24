from pathlib import Path

import requests


def download_file(url: str, dest: Path):
    response = requests.get(url, stream=True)  # noqa: S113
    response.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Path.open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    dest.chmod(0o755)
