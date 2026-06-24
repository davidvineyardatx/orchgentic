from __future__ import annotations

from pathlib import Path

from scripts.cleanup_release_artifacts import cleanup_repo


def test_cleanup_removes_release_only_files_and_keeps_placeholders(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_rc1_docs_exist.py").write_text("x", encoding="utf-8")
    (tmp_path / "tests" / "test_v1_release_docs.py").write_text("x", encoding="utf-8")

    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "agent_core.db").write_text("local", encoding="utf-8")

    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge" / "knowledge.db").write_text("local", encoding="utf-8")

    (tmp_path / "README_V1_SNIPPET.md").write_text("snippet", encoding="utf-8")
    (tmp_path / "RELEASE_NOTES_v1.0.0.md").write_text("notes", encoding="utf-8")

    result = cleanup_repo(tmp_path)

    assert result["files_removed"] >= 3
    assert not (tmp_path / "tests" / "test_rc1_docs_exist.py").exists()
    assert not (tmp_path / "tests" / "test_v1_release_docs.py").exists()
    assert not (tmp_path / "memory" / "agent_core.db").exists()
    assert not (tmp_path / "knowledge" / "knowledge.db").exists()
    assert (tmp_path / "memory" / ".gitkeep").exists()
    assert (tmp_path / "knowledge" / ".gitkeep").exists()


def test_cleanup_can_keep_release_notes(tmp_path: Path) -> None:
    notes = tmp_path / "RELEASE_NOTES_v1.0.0.md"
    changelog = tmp_path / "CHANGELOG_v1.0.0.md"

    notes.write_text("notes", encoding="utf-8")
    changelog.write_text("changelog", encoding="utf-8")

    cleanup_repo(tmp_path, keep_release_notes=True)

    assert notes.exists()
    assert changelog.exists()
