import json
from datetime import datetime
from pathlib import Path


def _safe_theme_name(theme_name: str) -> str:
    """ファイル名に使えるよう、テーマ名の空白をアンダースコアに置き換える。"""

    return theme_name.replace(" ", "_")


def save_snapshot(theme_name: str, repository_profiles: dict) -> Path:
    """現在のRepository情報をJSONファイルへ保存し、保存先のパスを返す。"""

    data_directory = Path("data")
    data_directory.mkdir(exist_ok=True)

    collected_at = datetime.now()

    sorted_profiles = sorted(
        repository_profiles.items(),
        key=lambda item: (
            item[1]["hits"],
            item[1]["stars"],
        ),
        reverse=True,
    )

    repositories = []

    for repository_name, profile in sorted_profiles:
        repositories.append(
            {
                "name": repository_name,
                "hits": profile["hits"],
                "stars": profile["stars"],
                "url": profile["url"],
            }
        )

    snapshot = {
        "theme": theme_name,
        "collected_at": collected_at.isoformat(timespec="seconds"),
        "repositories": repositories,
    }

    safe_theme_name = _safe_theme_name(theme_name)
    timestamp = collected_at.strftime("%Y-%m-%d_%H%M%S")

    file_path = data_directory / f"github_{safe_theme_name}_{timestamp}.json"

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(snapshot, file, ensure_ascii=False, indent=2)

    print(f"Snapshot saved: {file_path}")

    return file_path


def find_snapshot_files(theme_name: str) -> list[Path]:
    """保存済みスナップショットを、古い順に並べて返す。"""

    data_directory = Path("data")
    safe_theme_name = _safe_theme_name(theme_name)
    pattern = f"github_{safe_theme_name}_*.json"

    return sorted(data_directory.glob(pattern))


def load_snapshot(file_path: Path) -> dict:
    """指定したスナップショットファイルを読み込む。"""

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)
