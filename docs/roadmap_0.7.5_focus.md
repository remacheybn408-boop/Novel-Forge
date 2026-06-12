# Novel Forge v0.7.5 Focus Roadmap

## Goal

Make the existing writing engine directly usable by ordinary authors through a
stable writing page, without expanding the underlying architecture.

## Scope Freeze

v0.7.5 includes:

- Reliable chapter editing, autosave, and lightweight backups
- Four local-AI action entry points with preview-before-apply behavior
- Lightweight character, location, and setting linking
- Simple mode and a unified Novel Agent entry point
- Core API consistency, path safety, tests, and release documentation

v0.7.5 explicitly excludes:

- Workflow expansion
- Prompt workshop expansion
- New Agent categories or Agent frameworks
- Plugin systems
- Large Context Engine redesigns
- Vector search, token budgeting, or long-term memory systems
- Large-scale architecture rewrites

## Release Gates

- [x] Gate 0: Track and stabilize the Web UI/API baseline
- [x] Gate 1: Reliable editor, autosave, and backups
- [x] Gate 2: AI actions and lightweight knowledge linking
- [x] Gate 3: Simple mode and unified Novel Agent
- [x] Gate 4: API safety, documentation, versioning, and release validation

## Current Baseline

- Python tests: 300 passing before v0.7.5 work
- CLI status: operational, with DB/FTS warnings when no DB is resolved from config
- Web UI and API: present locally but previously excluded by the root `.gitignore`
- Frontend clean build: blocked by a missing Windows Rolldown optional native binding
- API version and launcher text: still report older versions and will be unified at Gate 4
- Existing user changes: `database/schema.sql` and untracked local additions must remain
  outside v0.7.5 commits

## Gate Acceptance Log

### Gate 0

- `python -m pytest -q`: 300 passed
- `npm ci && npm run build`: passed after locking the Windows Rolldown binding
- `python -c "from api.main import app; print(app.title, app.version)"`: API import passed
- Remaining non-blocking warning: the production bundle contains a chunk larger than
  Vite's default 500 kB warning threshold

### Gate 1

- `python -m pytest tests/test_api_write.py -q`: chapter save, backup rotation, and
  active-slot reads passed
- `python -m pytest -q`: 303 passed
- `npm run build`: passed
- Editor behavior: 1800 ms autosave, debounced word count, explicit save status,
  and save-before-switch/submit behavior implemented

### Gate 2

- `python -m pytest tests/test_api_write.py -q`: 7 passed
- `python -m pytest -q`: 307 passed
- `npm run build`: passed
- AI actions use a local-only adapter boundary and return a clear 503 until configured
- AI results require explicit preview actions and reject stale selection application
- Related settings are matched from the active slot database with debounced scanning

### Gate 3

- `python -m pytest -q`: 309 passed
- `npm run build`: passed
- Simple mode is the default and persists under `novelForge.advancedMode`
- Novel Agent reuses the existing full review pipeline through one API/UI entry point
- Dashboard now leads with continuing the current writing project

### Gate 4

- Core responses provide `ok` while preserving legacy `success`
- Unsafe slugs and upload filenames are rejected
- Version sources and user documentation updated to v0.7.5
- `python -m pytest -q`: 321 passed
- `npm ci && npm run build`: passed
- `python novel.py stability-check --full`: 95/100, P0=0, demo passed
- Remaining P1: current Story data reports two health warnings
