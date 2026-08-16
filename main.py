import os

from themes import THEMES

import ai_analysis
import collect_github
import comparison
import report
import signal_extraction
import storage


# AI分析はAPI料金が発生するため、明示的に有効化したときだけ実行する
AI_ANALYSIS_ENV_VAR = "BEACON_AI_ANALYSIS"


def is_ai_analysis_enabled() -> bool:
    """環境変数でAI分析が有効化されているかを判定する。

    .envではなく実行時の環境変数で判定する。
    .envに書くと常に有効になってしまい、明示的な有効化の意味がなくなるため。
    """

    return os.environ.get(AI_ANALYSIS_ENV_VAR) == "1"


def generate_and_save_report(theme_name: str, signal_data: dict) -> None:
    """SignalデータからAIレポートを生成し、Markdownとして保存する。"""

    print("=" * 50)
    print("Beacon AI Analysis")
    print("=" * 50)

    report_text = ai_analysis.generate_report(signal_data)

    report.save_report(theme_name, report_text)
    print()


theme_name = "AI Agent"

print(f"Theme: {theme_name}")
print()

for keyword in THEMES[theme_name]:
    collect_github.search_github(keyword)

collect_github.display_repository_ranking()

storage.save_snapshot(theme_name, collect_github.repository_profiles)

comparison.display_snapshot_comparison(theme_name)

signal_data = signal_extraction.extract_and_save_signals(theme_name)

# AI分析はここまでの収集結果を保存し終えたあとに実行する。
# AI分析が失敗しても、SnapshotとSignalは既にディスクへ保存されている。
if not is_ai_analysis_enabled():
    print(f"AI analysis skipped ({AI_ANALYSIS_ENV_VAR}=1 で実行)")
    print()
elif signal_data is None:
    print("AI analysis skipped (Signalがまだありません)")
    print()
else:
    generate_and_save_report(theme_name, signal_data)
