import os

from themes import THEMES

import ai_analysis
import collect_github
import comparison
import report
import report_facts
import report_markdown
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


def build_report_ai_content(signal_data: dict, facts: dict) -> dict:
    """AIからDaily Report v2のAI担当分を取得し、Signal JSON / Report Factsと照合する。

    AI呼び出し自体が失敗した場合は、空の辞書を返す。この場合でも
    report_markdown.build_report_markdownがfactsだけからフォールバック文で
    Daily Reportを完成させるため、パイプライン全体は止まらない。
    （AI分析はベストエフォートであり、失敗してもレポート生成を
    ブロックしないという意図的な例外境界）
    """

    candidates = signal_data["candidates"]

    if not candidates:
        return {}

    try:
        raw_content = ai_analysis.request_report_ai_content(signal_data, facts)
    except Exception as error:
        print(f"AI Report Content生成に失敗しました。フォールバック文で補います: {error}")
        return {}

    result = ai_analysis.validate_report_ai_content(candidates, facts, raw_content)

    if result.unknown_observation_names:
        print(f"警告: Signal JSONに存在しないcandidate名を無視しました: {result.unknown_observation_names}")

    if result.duplicate_observation_names:
        print(f"警告: 重複したcandidate名は最初の1件のみ使用しました: {result.duplicate_observation_names}")

    if result.missing_observation_names:
        print(f"情報: 以下の候補はAI observationが得られずフォールバック文を使用します: {result.missing_observation_names}")

    if result.unknown_notable_names:
        print(f"警告: Notable Observed Changesの選定対象に無いcandidate名を無視しました: {result.unknown_notable_names}")

    if result.duplicate_notable_names:
        print(f"警告: 重複したnotable candidate名は最初の1件のみ使用しました: {result.duplicate_notable_names}")

    if result.missing_notable_names:
        print(f"情報: 以下のnotable candidateはAI observationが得られずフォールバック文を使用します: {result.missing_notable_names}")

    return {
        "today_picture": result.today_picture,
        "broader_pattern": result.broader_pattern,
        "what_to_watch": result.what_to_watch,
        "observations": result.observations,
        "notable_observations": result.notable_observations,
    }


def generate_and_save_report(
    theme_name: str, signal_data: dict, tracked_repository_count: int
) -> None:
    """Report Factsを計算し、AIによるDaily Report v2のAI担当分を取得して、
    Markdownを組み立てて保存する。

    Markdown全体の組み立てはreport_markdown.pyが決定的に行う。
    AI分析はToday's Picture / Notable Observed Changes / Broader Pattern /
    What to Watch / 候補ごとのobservationの生成のみを担当する。
    """

    print("=" * 50)
    print("Beacon AI Analysis")
    print("=" * 50)

    reason_counts = ai_analysis.count_selection_reasons(signal_data["candidates"])
    facts = report_facts.build_report_facts(signal_data, reason_counts, tracked_repository_count)
    ai_content = build_report_ai_content(signal_data, facts)

    report_text = report_markdown.build_report_markdown(signal_data, facts, ai_content)

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
    generate_and_save_report(
        theme_name, signal_data, len(collect_github.repository_profiles)
    )
