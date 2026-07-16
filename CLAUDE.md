# Beacon Development Guide

## Project Mission

Beacon detects early signals of emerging technologies.

Beacon does not claim to predict the future.
It collects, compares, and explains measurable changes.

## Current Scope

The current data source is GitHub.

The first monitored theme is:

- AI Agent

The theme keywords are managed in `themes.py`.

Current flow:

1. Search GitHub using multiple keywords
2. Merge duplicate repositories
3. Store repository profiles
4. Rank repositories
5. Save timestamped JSON snapshots
6. Compare the latest two snapshots

## Current Files

- `main.py`: temporary entry point
- `collect_github.py`: GitHub collection, ranking, snapshot, and comparison
- `themes.py`: monitored themes and search keywords
- `data/`: saved JSON snapshots
- `README.md`: project overview, roadmap, and development log

## Development Priorities

Implement features in this order:

1. Growth ranking based on star changes
2. Clear snapshot comparison output
3. Separate collection, storage, and analysis responsibilities
4. Make `main.py` the application entry point
5. Add tests
6. Support all ten themes
7. Add additional data sources later
8. Build a dashboard only after the analysis foundation is stable

## Coding Rules

- Use readable Python over clever or overly condensed code
- Use type hints for functions
- Give each function one clear responsibility
- Avoid duplicate logic
- Do not silently catch unexpected errors
- Add concise Japanese comments where they help beginners
- Keep output compatible with Windows consoles
- Do not use emoji in terminal output
- Preserve existing behavior unless a change is explicitly requested
- Never place secrets or API tokens directly in source files
- Never commit `.env` or credentials
- Do not redesign the whole project during a small feature task

## Working Procedure

Before changing code:

1. Read `CLAUDE.md`, `README.md`, and relevant source files
2. Explain the proposed implementation plan in Japanese
3. Identify files that will be changed
4. Wait for approval

After approval:

1. Make the smallest reasonable change
2. Explain what changed
3. Run relevant checks only after permission
4. Report errors honestly
5. Do not commit or push unless explicitly requested

## Git Rules

- Show `git status` before committing
- Never use destructive Git commands without explicit permission
- Never force-push
- Do not commit generated snapshots unless explicitly requested
- Suggested commit format:

  `Day N: Brief feature description`

## Product Principles

Beacon should answer:

- What changed?
- How large was the change?
- Is the change persistent or temporary?
- Which evidence supports the signal?

Beacon should not state that an investment will rise or guarantee future outcomes.