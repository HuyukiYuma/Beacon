import json
from datetime import datetime
from pathlib import Path

import requests

from themes import THEMES


API_URL = "https://api.github.com/search/repositories"

# Repository名をキーにして、
# hits・stars・urlをまとめて保存します。
repository_profiles = {}


def search_github(query: str, limit: int = 5) -> None:
    """GitHubでRepositoryを検索し、結果を集計する。"""

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as error:
        print("GitHub APIとの通信に失敗しました。")
        print(error)
        print()
        return

    data = response.json()

    print(f"Searching GitHub for: {query}")
    print(f"Found {data['total_count']:,} repositories")
    print()

    for repository in data["items"]:
        repository_name = repository["full_name"]

        # すでに見つけたRepositoryなら、ヒット数だけ1増やします。
        if repository_name in repository_profiles:
            repository_profiles[repository_name]["hits"] += 1

        # 初めて見つけたRepositoryなら、プロフィールを作ります。
        else:
            repository_profiles[repository_name] = {
                "hits": 1,
                "stars": repository["stargazers_count"],
                "url": repository["html_url"],
            }

        print(f"📦 {repository_name}")
        print(f"⭐ Stars: {repository['stargazers_count']:,}")
        print(f"🔗 {repository['html_url']}")
        print()


def display_repository_ranking() -> None:
    """ヒット数が多い順にRepository情報を表示する。"""

def save_snapshot(theme_name: str) -> None:
    """現在のRepository情報をJSONファイルへ保存する。"""

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

    safe_theme_name = theme_name.replace(" ", "_")
    timestamp = collected_at.strftime("%Y-%m-%d_%H%M%S")

    file_path = (
        data_directory
        / f"github_{safe_theme_name}_{timestamp}.json"
    )

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            snapshot,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Snapshot saved: {file_path}")


    print("=" * 50)
    print("Beacon Repository Ranking")
    print("=" * 50)

    sorted_profiles = sorted(
        repository_profiles.items(),
        key=lambda item: (
            item[1]["hits"],
            item[1]["stars"],
        ),
        reverse=True,
    )

    for rank, (repository_name, profile) in enumerate(
        sorted_profiles,
        start=1,
    ):
        print(f"{rank}. {repository_name}")
        print(f"   Hits : {profile['hits']}")
        print(f"   Stars: {profile['stars']:,}")
        print(f"   URL  : {profile['url']}")
        print()


theme_name = "AI Agent"

print(f"Theme: {theme_name}")
print()

for keyword in THEMES[theme_name]:
    search_github(keyword)

display_repository_ranking()
save_snapshot(theme_name)