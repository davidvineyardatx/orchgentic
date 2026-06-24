from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DEFAULT_REMOVE_FILES = [
    # Release-package-only tests. These validated our release artifacts but are
    # not useful starter tests for cloned user repos.
    "tests/test_rc1_docs_exist.py",
    "tests/test_rc1_clean_install_commands_documented.py",
    "tests/test_v1_release_docs.py",

    # Release package manifests/snippets that do not need to stay in a clean repo root.
    "manifest.json",
    "README_RC1_SNIPPET.md",
    "README_V1_SNIPPET.md",
    "README_BETA2_SNIPPET.md",

    # Version-specific changelogs/release notes can be moved to GitHub releases
    # or kept only if the maintainer wants a full historical release file set.
    "CHANGELOG_v0.9.0-beta.2.md",
    "CHANGELOG_v0.9.0-rc.1.md",
    "CHANGELOG_v1.0.0.md",
    "RELEASE_NOTES_v0.9.0-beta.1.md",
    "RELEASE_NOTES_v0.9.0-beta.2.md",
    "RELEASE_NOTES_v0.9.0-rc.1.md",
    "RELEASE_NOTES_v1.0.0.md",
]

DEFAULT_REMOVE_DIRS = [
    # Local/generated state should not be included in a clean starter clone.
    "memory",
    "knowledge",
    ".pytest_cache",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "*.egg-info",
]

DEFAULT_KEEP_DIRS = [
    "memory",
    "knowledge",
]


def _remove_path(path: Path, *, dry_run: bool) -> bool:
    if not path.exists():
        return False

    if dry_run:
        print(f"would remove: {path}")
        return True

    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()

    print(f"removed: {path}")
    return True


def _remove_glob(root: Path, pattern: str, *, dry_run: bool) -> int:
    count = 0
    for path in root.glob(pattern):
        if _remove_path(path, dry_run=dry_run):
            count += 1
    return count


def _ensure_clean_dirs(root: Path, *, dry_run: bool) -> None:
    for rel in DEFAULT_KEEP_DIRS:
        path = root / rel
        gitkeep = path / ".gitkeep"

        if dry_run:
            print(f"would ensure clean directory: {path}")
            print(f"would ensure placeholder: {gitkeep}")
            continue

        path.mkdir(parents=True, exist_ok=True)
        gitkeep.write_text("", encoding="utf-8")
        print(f"ensured clean directory: {path}")


def cleanup_repo(root: Path, *, dry_run: bool = False, keep_release_notes: bool = False) -> dict[str, int]:
    root = root.resolve()

    remove_files = list(DEFAULT_REMOVE_FILES)
    if keep_release_notes:
        remove_files = [
            path for path in remove_files
            if not path.startswith("RELEASE_NOTES_") and not path.startswith("CHANGELOG_")
        ]

    removed_files = 0
    removed_dirs = 0

    for rel in remove_files:
        if _remove_path(root / rel, dry_run=dry_run):
            removed_files += 1

    for rel in DEFAULT_REMOVE_DIRS:
        if "*" in rel:
            removed_dirs += _remove_glob(root, rel, dry_run=dry_run)
        else:
            if _remove_path(root / rel, dry_run=dry_run):
                removed_dirs += 1

    _ensure_clean_dirs(root, dry_run=dry_run)

    return {
        "files_removed": removed_files,
        "dirs_removed": removed_dirs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean release-only artifacts from an Orchgentic repo.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be removed without deleting.")
    parser.add_argument(
        "--keep-release-notes",
        action="store_true",
        help="Keep versioned release notes and changelogs in the repo.",
    )

    args = parser.parse_args()
    result = cleanup_repo(
        Path(args.root),
        dry_run=args.dry_run,
        keep_release_notes=args.keep_release_notes,
    )

    print(f"cleanup complete: {result}")


if __name__ == "__main__":
    main()
