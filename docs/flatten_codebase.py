#!/usr/bin/env python3
"""
flatten_codebase.py
-------------------
Reusable helper that walks a code repository and returns one concatenated
string containing every (text) file, each preceded by a header line
with its path.

Works both as an *importable module* and as a CLI script.

Example
-------
>>> from flatten_codebase import flatten_codebase
>>> snapshot = flatten_codebase("/tmp/my_project")
>>> do_something(snapshot)
"""

from __future__ import annotations

import os
import pathlib
import sys
from typing import Iterable, Sequence, Set

# ──────────────────────────────────────────────────────────────────────────────
# Defaults – tweak from your calling code if you like
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_TEXT_EXTS: Set[str] = {
    ".py", ".pyx", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".hpp",
    ".go", ".rs", ".rb", ".php", ".sh", ".ps1",
    ".html", ".css", ".scss",
    ".json", ".yaml", ".yml", ".toml", ".ini",
    ".xml", ".md", ".txt",
}
DEFAULT_EXCLUDE_DIRS: Set[str] = {
    ".git", ".svn", ".hg",
    ".idea", ".vscode",
    "__pycache__", ".mypy_cache",
    ".tox", ".venv", "venv",
    "node_modules", "dist", "build",
}
HEADER_PREFIX = "## "      # Markdown-friendly; adjust as needed
HEADER_SUFFIX = "\n"


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────
def _iter_text_files(
    root: pathlib.Path,
    *,
    extensions: Set[str],
    exclude_dirs: Set[str],
) -> Iterable[pathlib.Path]:
    """Yield every file beneath *root* whose suffix is in *extensions*."""
    for dirpath, dirnames, filenames in os.walk(root):
        # prevent descend into excluded folders
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for fname in filenames:
            path = pathlib.Path(dirpath) / fname
            if not extensions or path.suffix in extensions:
                yield path


def _concat(
    files: Sequence[pathlib.Path],
    *,
    root: pathlib.Path,
    header_prefix: str,
    header_suffix: str,
) -> str:
    """Return big string of file headers + contents."""
    parts: list[str] = []
    for path in sorted(files):
        rel_path = path.relative_to(root)
        header = f"{header_prefix}{rel_path}{header_suffix}"
        try:
            body = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:  # binary or unreadable file – skip it
            sys.stderr.write(f"⚠️  Skipping {rel_path}: {exc}\n")
            continue
        parts.append(f"{header}{body}\n")  # blank line between files
    return "".join(parts)


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────
def flatten_codebase(
    root: str | os.PathLike,
    *,
    extensions: Set[str] | None = None,
    exclude_dirs: Set[str] | None = None,
    header_prefix: str = HEADER_PREFIX,
    header_suffix: str = HEADER_SUFFIX,
) -> str:
    """
    Walk *root* and return a single string that contains every text-based file.

    Parameters
    ----------
    root : str | Path
        Project directory to traverse.
    extensions : set[str] | None
        If supplied, only files whose suffix is in this set are included.
        Defaults to `DEFAULT_TEXT_EXTS`.
    exclude_dirs : set[str] | None
        Directory names to skip.  Defaults to `DEFAULT_EXCLUDE_DIRS`.
    header_prefix, header_suffix : str
        Strings placed before / after each relative path header.

    Returns
    -------
    str
        Concatenated codebase snapshot.
    """
    root_path = pathlib.Path(root).expanduser().resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"{root_path} is not a directory")

    files = list(
        _iter_text_files(
            root_path,
            extensions=extensions or DEFAULT_TEXT_EXTS,
            exclude_dirs=exclude_dirs or DEFAULT_EXCLUDE_DIRS,
        )
    )
    return _concat(
        files,
        root=root_path,
        header_prefix=header_prefix,
        header_suffix=header_suffix,
    )


# ──────────────────────────────────────────────────────────────────────────────
# CLI fallback
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python flatten_codebase.py /path/to/repo")
    print(flatten_codebase(sys.argv[1]))
