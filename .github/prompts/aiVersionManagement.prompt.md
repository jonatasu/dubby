# Version Management (Tags & Releases)

Approach:

- Prefer Git tags using SemVer (vX.Y.Z). Use GitHub Releases to publish notes.
- Classify changes: MAJOR (breaking), MINOR (new features), PATCH (fixes/docs/tests/chore).

Flow:

1. Prepare release notes (highlights, changes categories, links).
2. Ensure CI green; Docker image builds on tag.
3. Create annotated tag `vX.Y.Z`; push tag.
4. Publish GitHub Release (auto by workflow if configured).

Reference Files:

- .github/workflows/release.yml
- .github/workflows/docker.yml
- README.md
