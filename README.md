## Beacon Vision

Beacon is not a GitHub trend tracker.

Beacon is a signal detection engine.

Its purpose is to discover weak signals before they become obvious trends by collecting, comparing, and analyzing multiple independent sources.

Python is responsible for collecting and organizing objective facts.

AI is responsible for interpreting those facts and identifying meaningful signals.

## Philosophy

Don't predict the future.
Detect the signals.

## Development Philosophy

Beacon is built with an AI-assisted development workflow.

Roles:

- Product Owner: Yuma
- System Architect: ChatGPT
- Implementation Engineer: Claude Code

The goal is not only to build Beacon, but also to understand every major design decision throughout its development.



## Project Structure
Beacon/
│
├── main.py               # Application entry point
├── collect_github.py     # GitHub collection and ranking
├── storage.py            # Snapshot storage
├── comparison.py         # Snapshot comparison
├── themes.py             # Search themes
│
├── data/                 # Local snapshot storage
│
├── README.md
├── CLAUDE.md
└── .gitignore



## Roadmap

### Phase 1 - Collect

- ✅ GitHub API
- ✅ Multi-keyword Signal Pack
- ✅ Repository Profiles
- ✅ Ranking
- ✅ Snapshot Storage

Phase 2 - Analyze

✅ Historical Snapshot Comparison
✅ Signal Extraction
⬜ AI Analysis
⬜ Daily Beacon Report
⬜ Multi-source Correlation
⬜ Trend Detection

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