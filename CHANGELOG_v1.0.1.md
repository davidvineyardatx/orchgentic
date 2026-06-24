# Changelog

## v1.0.1

### Added

- `scripts/cleanup_release_artifacts.py`
- `.gitignore` cleanup rules for local runtime state
- `memory/.gitkeep`
- `knowledge/.gitkeep`
- `docs/v1.0.1-cleanup.md`
- `docs/release-checklist-v1.0.1-cleanup.md`
- `RELEASE_NOTES_v1.0.1.md`

### Changed

- Repository cleanup guidance for cloned user repos.

### Removed by cleanup script

- Release-only documentation tests
- Local/generated memory and knowledge contents
- Cache/build artifacts
- Release packaging snippets/manifests

### Notes

This is cleanup-only. It does not add runtime features or expand scope.
