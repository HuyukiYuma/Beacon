"""Beacon Dashboard Publish

data/配下にPythonが生成した最新のSnapshot・Signal JSON・Daily Report、および
直近のSnapshot履歴(Recent Activity表示用)だけを、dashboard/data/へ
固定ファイル名でコピー・生成する。

このモジュールはmain.pyの収集・分析ロジックから独立した「公開処理」専用であり、
意図的にstorage.py等へは依存させず、単体で完結させている。

- GitHub収集・AI分析・ネットワーク呼び出しは一切行わない
- 元のdata/配下のファイルは変更しない(読み取り専用)
- コピー先のファイル名は常に固定(latest_snapshot.json等)。
  Dashboard(Next.js)側が最新ファイルを探すためのディレクトリ一覧処理を
  行わずに済むようにするため。
- 全Snapshot履歴は公開せず、直近HISTORY_LIMIT件の要約(収集日時と件数)
  だけをsnapshot_history.jsonとして公開する。Dashboard側はこの要約を
  そのまま表示するだけで、再計算は行わない。

Dashboardはdashboard/data/だけを読み、Pythonの内部生成物置き場である
リポジトリ直下のdata/を直接参照しない。
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

DATA_DIRECTORY = Path("data")
SIGNALS_DIRECTORY = DATA_DIRECTORY / "signals"
REPORTS_DIRECTORY = DATA_DIRECTORY / "reports"

PUBLISH_DIRECTORY = Path("dashboard") / "data"

SNAPSHOT_DEST_NAME = "latest_snapshot.json"
SIGNAL_DEST_NAME = "latest_signal.json"
REPORT_DEST_NAME = "latest_report.md"
META_DEST_NAME = "latest_meta.json"
HISTORY_DEST_NAME = "snapshot_history.json"

# Recent Activityで公開するSnapshot履歴の件数
HISTORY_LIMIT = 5


def _safe_theme_name(theme_name: str) -> str:
    """ファイル名に使えるよう、テーマ名の空白をアンダースコアに置き換える。

    storage.pyの同名関数と同じ変換だが、公開処理を独立させるためあえて
    ここでも定義している(依存させない設計上の判断)。
    """

    return theme_name.replace(" ", "_")


def _find_latest_file(directory: Path, pattern: str) -> Path | None:
    """指定ディレクトリから、パターンに一致する最新のファイルを1件返す。

    ファイル名の末尾がタイムスタンプ形式のため、文字列ソートで
    時系列順になる。該当ファイルが無い場合はNoneを返す。
    """

    matched_files = sorted(directory.glob(pattern))

    if not matched_files:
        return None

    return matched_files[-1]


def _find_recent_files(directory: Path, pattern: str, limit: int) -> list[Path]:
    """指定ディレクトリから、パターンに一致する直近limit件のファイルを新しい順で返す。"""

    matched_files = sorted(directory.glob(pattern))
    recent_files = matched_files[-limit:]

    return list(reversed(recent_files))


def _build_snapshot_history_entry(snapshot_file: Path) -> dict:
    """1件のSnapshotファイルから、Recent Activity表示に必要な要約だけを取り出す。

    Repository一覧そのものは表示に使わないため、件数だけを取り出す。
    """

    with snapshot_file.open("r", encoding="utf-8") as file:
        snapshot = json.load(file)

    return {
        "file_name": snapshot_file.name,
        "collected_at": snapshot["collected_at"],
        "repository_count": len(snapshot["repositories"]),
    }


def publish_snapshot_history(theme_name: str) -> list[dict]:
    """直近HISTORY_LIMIT件のSnapshotの要約を、dashboard/data/へJSONとして書き出す。

    全Snapshot履歴を公開するのではなく、Recent Activity表示に必要な
    直近分だけに絞る。新しい順(先頭が最新)で書き出す。
    """

    safe_theme_name = _safe_theme_name(theme_name)

    PUBLISH_DIRECTORY.mkdir(parents=True, exist_ok=True)

    recent_snapshot_files = _find_recent_files(
        DATA_DIRECTORY, f"github_{safe_theme_name}_*.json", HISTORY_LIMIT
    )

    history = [
        _build_snapshot_history_entry(snapshot_file)
        for snapshot_file in recent_snapshot_files
    ]

    history_path = PUBLISH_DIRECTORY / HISTORY_DEST_NAME

    with history_path.open("w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=2)

    print(f"Published history   : {len(history)} snapshot(s) -> {history_path}")

    return history


def publish_dashboard_data(theme_name: str) -> dict[str, str | None]:
    """最新のSnapshot・Signal・Daily Reportを、dashboard/data/へコピーする。

    元のdata/配下のファイルは一切変更しない。存在しない種類はコピーを
    スキップし、結果にNoneを記録する。戻り値はコピー元ファイル名の記録。
    """

    safe_theme_name = _safe_theme_name(theme_name)

    PUBLISH_DIRECTORY.mkdir(parents=True, exist_ok=True)

    latest_snapshot = _find_latest_file(
        DATA_DIRECTORY, f"github_{safe_theme_name}_*.json"
    )
    latest_signal = _find_latest_file(
        SIGNALS_DIRECTORY, f"signals_{safe_theme_name}_*.json"
    )
    latest_report = _find_latest_file(
        REPORTS_DIRECTORY, f"report_{safe_theme_name}_*.md"
    )

    published: dict[str, str | None] = {
        "snapshot": None,
        "signal": None,
        "report": None,
    }

    if latest_snapshot is not None:
        shutil.copyfile(latest_snapshot, PUBLISH_DIRECTORY / SNAPSHOT_DEST_NAME)
        published["snapshot"] = latest_snapshot.name
        print(f"Published snapshot : {latest_snapshot.name}")
    else:
        print("Published snapshot : (none found)")

    if latest_signal is not None:
        shutil.copyfile(latest_signal, PUBLISH_DIRECTORY / SIGNAL_DEST_NAME)
        published["signal"] = latest_signal.name
        print(f"Published signal    : {latest_signal.name}")
    else:
        print("Published signal    : (none found)")

    if latest_report is not None:
        shutil.copyfile(latest_report, PUBLISH_DIRECTORY / REPORT_DEST_NAME)
        published["report"] = latest_report.name
        print(f"Published report    : {latest_report.name}")
    else:
        print("Published report    : (none found)")

    # generatedAt等の表示に必要な「元ファイル名のタイムスタンプ」を
    # Dashboard側で復元できるよう、コピー元ファイル名を記録しておく。
    # (コピー先はlatest_report.md等の固定名になり、タイムスタンプ情報が
    #  ファイル名から失われるため)
    meta = {
        "theme": theme_name,
        "published_at": datetime.now().isoformat(timespec="seconds"),
        "snapshot_file": published["snapshot"],
        "signal_file": published["signal"],
        "report_file": published["report"],
    }

    meta_path = PUBLISH_DIRECTORY / META_DEST_NAME

    with meta_path.open("w", encoding="utf-8") as file:
        json.dump(meta, file, ensure_ascii=False, indent=2)

    print(f"Published meta      : {meta_path}")

    publish_snapshot_history(theme_name)

    return published


if __name__ == "__main__":
    theme_name = "AI Agent"

    print("=" * 50)
    print("Beacon Dashboard Publish")
    print("=" * 50)

    publish_dashboard_data(theme_name)
    print()
