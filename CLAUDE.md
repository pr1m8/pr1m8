# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is the **pr1m8/pr1m8** GitHub special-named profile repository. Its primary deliverable is `README.md` (rendered at github.com/pr1m8). It is **not** a typical software project — most files are content (Markdown, SVG) or automation that regenerates that content. The Python code in `scripts/` is auxiliary tooling for previewing the rendered profile locally.

## Architecture

There are three independent layers, none of which import from each other:

1. **`README.md` (the product)** — A single hand-edited Markdown file using HTML `<details>`, `<table>`, and `<picture>` for layout. It references images from three sources:
   - Local SVGs in `images/` (e.g. `ai-icon.svg`) referenced via raw.githubusercontent URLs so they render on github.com.
   - Generated SVGs committed to `main` by GitHub Actions (`metrics.svg`, `profile-stats.svg`, `projects-metrics.svg`, `repository-metrics.svg`).
   - Generated SVGs pushed to the `output` branch by the snake workflow (`github-contribution-grid-snake.svg`, `-dark.svg`).

2. **`.github/workflows/` (the regeneration pipeline)** — Six independent cron-driven workflows, each writing a different SVG. They commit back to `main` (or push to the `output` branch in the snake case) without coordination, which is why the repo's recent commit history is dominated by `chore: update *.svg` commits. Two of them generate snake animations (`snake.yml` and `contribution-snake.yml`) — `snake.yml` is the live one with the project's purple palette.
   - `metrics.yml` — `lowlighter/metrics` comprehensive dashboard, every 12h. Requires `secrets.METRICS_TOKEN` (a PAT, **not** the default `GITHUB_TOKEN` — the other workflows use `GITHUB_TOKEN`).
   - `profile-stats.yml` — secondary metrics card, every 8h.
   - `projects.yml` / `repo-cards.yml` — repository card SVGs, every 6h / daily.
   - `snake.yml` — purple-themed snake animation pushed to `output` branch.

3. **`scripts/` (local preview tooling)** — Two standalone Playwright scripts used for previewing the profile locally; not invoked by any workflow. `view_profile.py` opens github.com/pr1m8 in a browser; `render_markdown.py` rasterizes a Markdown file to PNG using GitHub's CSS. Neither is required to update the profile.

### Theme constants (must stay consistent across all three layers)

- Primary purple: `#A855F7`
- Secondary purple: `#8B5CF6`
- Accent mint: `#A7F3D0`
- Background: `#0D1117`
- Surface: `#30363d`

Shield badge format used throughout `README.md`:
`https://img.shields.io/badge/[NAME]-0D1117?style=for-the-badge&logo=[LOGO]&logoColor=A855F7&color=30363d`

## Common commands

This repo has no test suite, no build, and no lint configured in `pyproject.toml`'s scripts. Useful commands:

```bash
# Local preview tooling (requires `pip install -e .` or `pip install playwright && playwright install chromium`)
python scripts/view_profile.py                    # Opens pr1m8 profile in headed browser
python scripts/view_profile.py --headless -s      # Headless + screenshot to images/screenshots/
python scripts/render_markdown.py README.md       # Render README.md to PNG in images/rendered/
python scripts/render_markdown.py --all-readmes   # Render every README*.md

# Manually trigger a workflow (instead of waiting for cron)
gh workflow run metrics.yml
gh workflow run snake.yml
```

## Editing notes

- **Don't touch the auto-generated SVGs** (`metrics.svg`, `profile-stats.svg`, `projects-metrics.svg`, `repository-metrics.svg`, anything on the `output` branch). The next workflow run will overwrite them. To change their appearance, edit the corresponding workflow YAML.
- **`README_*_backup.md`** files in the root are historical snapshots, not active variants. Don't update them when editing `README.md`.
- The four files in `images/` (`ai-icon.svg`, `quant-icon.svg`, `graph-icon.svg`, `auto-icon.svg`) are referenced by `README.md` via absolute github.com URLs (`https://github.com/pr1m8/pr1m8/blob/main/images/...?raw=true`). If you rename or move them, update those references — relative paths will look fine in a local renderer but break on github.com.
- `metrics.yml` requires a `METRICS_TOKEN` secret (a personal access token with extra scopes); the default `GITHUB_TOKEN` is insufficient for several of the enabled plugins. If metrics stop updating, that secret has likely expired.
