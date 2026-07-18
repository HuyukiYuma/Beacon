from datetime import datetime
from pathlib import Path


def _safe_theme_name(theme_name: str) -> str:
    """ファイル名に使えるよう、テーマ名の空白をアンダースコアに置き換える。"""

    return theme_name.replace(" ", "_")


def save_report(theme_name: str, report_text: str) -> Path:
    """AIが生成したDaily ReportをMarkdownファイルへ保存し、保存先のパスを返す。"""

    reports_directory = Path("data") / "reports"
    reports_directory.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now()
    safe_theme_name = _safe_theme_name(theme_name)
    timestamp = generated_at.strftime("%Y-%m-%d_%H%M%S")

    file_path = reports_directory / f"report_{safe_theme_name}_{timestamp}.md"

    file_path.write_text(report_text, encoding="utf-8")

    print(f"Daily Report saved: {file_path}")

    return file_path
