from themes import THEMES

import collect_github
import comparison
import signal_extraction
import storage


theme_name = "AI Agent"

print(f"Theme: {theme_name}")
print()

for keyword in THEMES[theme_name]:
    collect_github.search_github(keyword)

collect_github.display_repository_ranking()

storage.save_snapshot(theme_name, collect_github.repository_profiles)

comparison.display_snapshot_comparison(theme_name)

signal_extraction.extract_and_save_signals(theme_name)
