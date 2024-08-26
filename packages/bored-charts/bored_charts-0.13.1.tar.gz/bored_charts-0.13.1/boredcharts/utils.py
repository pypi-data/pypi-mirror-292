from __future__ import annotations

import base64
import uuid
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


def uuid_to_urlid(uuid_: uuid.UUID) -> str:
    """Convert a UUID to a short URL-safe string.

    >>> import base64
    >>> import uuid
    >>> id_ = uuid.UUID('5d98d578-2731-4a4d-b666-70ca16f10aa2')
    >>> url_id = uuid_to_urlid(id_)
    >>> print(url_id)
    XZjVeCcxSk22ZnDKFvEKog
    """
    return base64.urlsafe_b64encode(uuid_.bytes).rstrip(b"=").decode("utf-8")


def urlid_to_uuid(url: str) -> uuid.UUID:
    """Convert a base64url encoded UUID string to a UUID.

    >>> import base64
    >>> import uuid
    >>> url_id = 'XZjVeCcxSk22ZnDKFvEKog'
    >>> id_ = urlid_to_uuid(url_id)
    >>> print(id_)
    5d98d578-2731-4a4d-b666-70ca16f10aa2
    """
    return uuid.UUID(bytes=base64.urlsafe_b64decode(url + "=" * (len(url) % 4)))
