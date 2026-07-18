## Beacon Vision

Beacon is not a GitHub trend tracker.

Beacon is a signal detection engine.

Its purpose is to discover weak signals before they become obvious trends by collecting, comparing, and analyzing multiple independent sources.

Python is responsible for collecting and organizing objective facts.

AI is responsible for interpreting those facts and identifying meaningful signals.

## Philosophy

Don't predict the future.
Detect the signals.

## Project Philosophy

Beacon is designed to discover weak signals before they become obvious trends.

The project intentionally separates objective signal collection from AI interpretation.

Beacon prioritizes evidence over speculation and observation over prediction.



## Project Structure
Beacon/
│
├── main.py               # Application entry point
├── collect_github.py     # GitHub collection and ranking
├── storage.py            # Snapshot storage
├── comparison.py         # Snapshot comparison
├── signal_extraction.py  # Signal candidate extraction
├── themes.py             # Search themes
│
├── ai_analysis.py        # AI Analysis (Planned - not yet implemented)
├── report.py             # Beacon Daily Report (Planned - not yet implemented)
│
├── data/                 # Local snapshot and signal storage
│
├── docs/                 # AI analysis design documents (see Documentation)
│
├── README.md
├── CLAUDE.md
└── .gitignore



## Documentation

Design documents for the upcoming AI analysis layer are kept in `docs/`.
These describe the intended design only; the AI analysis layer itself is not yet implemented.

- `Beacon_Analysis_Protocol.md` - Rules the AI analysis layer must follow: what it can and cannot claim, required evidence structure, and forbidden statements.
- `Beacon_Prompt.md` - Draft system/user prompt that applies the Protocol.
- `Daily_Report_Template.md` - Markdown structure the AI's output is expected to follow.
- `Architecture.md` - How the planned AI analysis layer connects to the existing collection and signal extraction pipeline.



## Roadmap

### Phase 1 - Collect

- ✅ GitHub API
- ✅ Multi-keyword Signal Pack
- ✅ Repository Profiles
- ✅ Ranking
- ✅ Snapshot Storage

Phase 2 - Analyze

 - ✅ Historical Snapshot Comparison
 - ✅ Signal Extraction
 - ✅ AI Analysis Design
 - ⬜ AI Analysis Implementation
 - ⬜ Daily Beacon Report
 - ⬜ Multi-source Correlation
 - ⬜ Trend Detection

### Phase 3 - Intelligence

- ⬜ Multi-source Analysis
- ⬜ Dashboard
- ⬜ Notifications


## Development Log

### Day 1 - Project Created
- Created the Beacon project folder
- Added `main.py`
- Added initial `README.md`
- Pushed the first version to GitHub

### Day 2 - First GitHub Signal
- Installed the `requests` library
- Connected Beacon to the GitHub API
- Retrieved live repository data for the first time
- Confirmed that the initial search query is too broad

### Day 3 - AI Agent Signal Pack
- Introduced `themes.py` to separate theme configuration from logic
- Added multiple GitHub search signals for the AI Agent theme
- Learned how Python loops iterate through keyword lists
- Confirmed Beacon can search multiple signals for a single concept

### Day 4 - Repository Hit Count

- Introduced the first Beacon scoring concept
- Counted how many search signals matched each GitHub repository
- Learned how to use Python dictionaries for data aggregation
- Learned basic `if/else` logic for counting repeated results

### Day 5 - Repository Profiles

- Replaced simple hit counts with structured repository profiles
- Stored hit count, GitHub stars, and repository URL together
- Added repository ranking by hit count and star count
- Learned how nested Python dictionaries manage related information

### Day 6 - Daily Snapshot

- Added JSON snapshot storage
- Created a `data` directory automatically
- Saved repository rankings with collection timestamps
- Prepared Beacon for historical trend comparison
- Learned basic JSON and file handling in Python

### Day 6.5 - Code Refactoring

- Introduced Claude Code into the Beacon development workflow
- Separated repository ranking from snapshot saving
- Improved function responsibilities
- Fixed Windows console compatibility by replacing emoji output
- Improved overall code readability and maintainability

### Day 7 - Snapshot Comparison

- Added historical snapshot comparison
- Detects new, removed, and changed repositories
- Automatically compares the latest two snapshots
- Prepared Beacon for trend detection and growth analysis
- Phase 2 (Analyze) officially started

### Day 8 - Architecture Refactoring

- Separated project responsibilities into dedicated modules
- Added `storage.py` for snapshot management
- Added `comparison.py` for historical analysis
- Moved `main.py` to the official application entry point
- Improved project structure for future expansion
- Added `CLAUDE.md` as the AI development guide
- Improved Git repository hygiene with `.gitignore`

### Day 9 - Signal Extraction Foundation

- Added signal_extraction.py
- Added objective repository difference generation
- Added rule-based signal candidate extraction
- Added Signal JSON storage
- Preserved existing collection and comparison workflow
- Verified generated data is excluded from Git

## Current Status

✅ GitHub API connection

✅ Multi-keyword Signal Pack

✅ Repository Hit Count

⬜ Repository Ranking

⬜ Beacon Score

⬜ Database

⬜ AI Analysis

⬜ Dashboard