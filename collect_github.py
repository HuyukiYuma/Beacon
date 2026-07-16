import requests


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

        print(f"Repository : {repository_name}")
        print(f"Stars      : {repository['stargazers_count']:,}")
        print(f"URL        : {repository['html_url']}")
        print()


def display_repository_ranking() -> None:
    """ヒット数が多い順にRepository情報を表示する。"""

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


