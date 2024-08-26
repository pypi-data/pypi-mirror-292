from __future__ import annotations

from pathlib import Path
from typing import NamedTuple


class DirTree(NamedTuple):
    name: Path
    files: list[Path]
    dirs: list[DirTree]


def get_dirtree(parent: Path, directory: Path = Path()) -> DirTree:
    full_dir = parent / directory

    files = []
    dirs = []
    for item in full_dir.iterdir():
        if item.is_file():
            files.append(item.relative_to(full_dir))
        elif item.is_dir():
            dirs.append(get_dirtree(full_dir, item.relative_to(full_dir)))

    return DirTree(name=directory, files=files, dirs=dirs)


def to_name(path: Path | str, kind: str = "") -> str:
    if isinstance(path, str):
        path = Path(path)
    if path.name:
        path = path.with_suffix("")
    if path.root.startswith("/"):
        path = path.relative_to("/")
    return str(Path(kind) / path).replace("/", ".").strip(".")


def to_url_path(path: Path) -> str:
    if path.name:
        path = path.with_suffix("")
    return str(Path("/") / path)
