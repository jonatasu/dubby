# AI Commit Changes Prompt

## Overview

This prompt guides the AI assistant in managing commit changes for the Dubby project, ensuring consistent, atomic commits using Conventional Commits format.

## Context

- Project: Dubby (FastAPI-based media pipeline for ASR→Translate→TTS→Mux)
- Tech Stack: Python 3.11, FastAPI, Faster-Whisper, FFmpeg, Docker
- Workflow: GitHub Actions for CI, releases, and GHCR publishing

## Commit Guidelines

### Conventional Commits Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (deps, config, etc.)
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `build`: Build system changes

### Scopes (for Dubby)

- `api`: API endpoints and routing
- `web`: Web UI and templates
- `asr`: Automatic Speech Recognition
- `tts`: Text-to-Speech
- `translate`: Translation service
- `media`: Media processing (FFmpeg)
- `pipeline`: Main processing pipeline
- `config`: Configuration and settings
- `docker`: Docker and containerization
- `ci`: GitHub Actions and workflows
- `docs`: Documentation
- `deps`: Dependencies

## Workflow Steps

1. **Analyze Changes**: Review git diff to understand what changed
2. **Categorize**: Determine appropriate type and scope
3. **Write Description**: Clear, concise description in imperative mood
4. **Add Body**: If needed, explain why/what/how
5. **Breaking Changes**: Use `!` suffix for breaking changes, explain in footer
6. **Atomic Commits**: Keep commits focused on single concerns

## Examples

### Feature Addition

```
feat(api): add health endpoint for service monitoring

- Implements /health route with basic status check
- Returns JSON with service status and version
- Reference: app/routers/api.py
```

### Bug Fix

```
fix(media): handle missing ffmpeg gracefully

Fallback to audio-only processing when ffmpeg is unavailable.
Display warning banner in UI when video processing is disabled.

Closes #42
```

### Documentation

```
docs(readme): update deployment section with GHCR instructions

- Add Docker pull commands for GHCR images
- Include environment variable documentation
- Reference: docker-compose.yml, Dockerfile
```

### Refactoring

```
refactor(pipeline): extract media processing into separate service

- Move FFmpeg operations to app/services/media.py
- Improve error handling and logging
- No functional changes to API
```

## Best Practices

- Keep commits atomic (one logical change per commit)
- Use imperative mood: "add", "fix", "update", not "added", "fixed"
- Reference issues/PRs when applicable
- For large changes, consider multiple focused commits
- Test before committing (run `make test`)
- Use `git add -p` for selective staging when needed

## Reference Files

- `.github/workflows/ci.yml` - CI pipeline
- `.github/workflows/release.yml` - Release automation
- `Makefile` - Build and test commands
- `app/main.py` - Main application entry point
