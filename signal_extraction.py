from storage import find_snapshot_files, load_snapshot, save_signal_candidates


# star_growthの上位何件を注目候補にするか
TOP_STAR_GROWTH_LIMIT = 10

# この件数以上のキーワードにヒットしたRepositoryを注目候補にする
MIN_CURRENT_HITS_FOR_CANDIDATE = 2


def build_repository_diffs(previous_snapshot: dict, latest_snapshot: dict) -> list[dict]:
    """前回と最新のSnapshotから、Repositoryごとの客観的な差分情報を作る。"""

    previous_repositories = {
        repository["name"]: repository
        for repository in previous_snapshot["repositories"]
    }
    latest_repositories = {
        repository["name"]: repository
        for repository in latest_snapshot["repositories"]
    }

    all_names = set(previous_repositories) | set(latest_repositories)

    diffs = []

    for name in all_names:
        previous_repository = previous_repositories.get(name)
        latest_repository = latest_repositories.get(name)

        is_new = previous_repository is None
        is_removed = latest_repository is None

        previous_stars = previous_repository["stars"] if previous_repository else 0
        current_stars = latest_repository["stars"] if latest_repository else 0

        previous_hits = previous_repository["hits"] if previous_repository else 0
        current_hits = latest_repository["hits"] if latest_repository else 0

        # is_removedの場合はlatest側の情報がないので、previous側のURLを使う
        url = (latest_repository or previous_repository)["url"]

        diffs.append(
            {
                "name": name,
                "url": url,
                "previous_stars": previous_stars,
                "current_stars": current_stars,
                "star_growth": current_stars - previous_stars,
                "previous_hits": previous_hits,
                "current_hits": current_hits,
                "hit_change": current_hits - previous_hits,
                "is_new": is_new,
                "is_removed": is_removed,
            }
        )

    return diffs


def _select_top_star_growth_names(diffs: list[dict]) -> set[str]:
    """新規Repositoryを除いた中から、star_growthが上位のRepository名を選ぶ。

    新規Repositoryはprevious_starsが0として計算されるため、
    既存のStar総数がそのままstar_growthになってしまう。
    そのため新規Repositoryはこの上位選定の対象から除外する。
    """

    growth_candidates = [
        diff for diff in diffs if not diff["is_new"] and diff["star_growth"] > 0
    ]

    sorted_by_growth = sorted(
        growth_candidates,
        key=lambda diff: diff["star_growth"],
        reverse=True,
    )

    top_diffs = sorted_by_growth[:TOP_STAR_GROWTH_LIMIT]

    return {diff["name"] for diff in top_diffs}


def select_candidates(diffs: list[dict]) -> list[dict]:
    """客観的な差分情報から、注目候補となるRepositoryを抽出する。

    複数の条件に該当した場合もRepositoryは重複させず、
    該当した理由をselection_reasonsにまとめる。
    """

    # 削除されたRepositoryは現在存在しないため、候補の対象外とする
    active_diffs = [diff for diff in diffs if not diff["is_removed"]]

    top_star_growth_names = _select_top_star_growth_names(active_diffs)

    candidates = []

    for diff in active_diffs:
        selection_reasons = []

        if diff["is_new"]:
            selection_reasons.append("new_repository")

        if diff["hit_change"] > 0:
            selection_reasons.append("increased_keyword_hits")

        if diff["name"] in top_star_growth_names:
            selection_reasons.append("top_star_growth")

        if diff["current_hits"] >= MIN_CURRENT_HITS_FOR_CANDIDATE:
            selection_reasons.append("multiple_keyword_matches")

        if not selection_reasons:
            continue

        candidates.append(
            {
                "name": diff["name"],
                "url": diff["url"],
                "previous_stars": diff["previous_stars"],
                "current_stars": diff["current_stars"],
                "star_growth": diff["star_growth"],
                "previous_hits": diff["previous_hits"],
                "current_hits": diff["current_hits"],
                "hit_change": diff["hit_change"],
                "is_new": diff["is_new"],
                "selection_reasons": selection_reasons,
            }
        )

    return candidates


def build_signal_candidates(
    theme_name: str,
    previous_snapshot: dict,
    latest_snapshot: dict,
) -> dict:
    """前回と最新のSnapshotから、Signal Extractionの結果をまとめる。"""

    diffs = build_repository_diffs(previous_snapshot, latest_snapshot)
    candidates = select_candidates(diffs)

    return {
        "theme": theme_name,
        "period": {
            "previous": previous_snapshot["collected_at"],
            "current": latest_snapshot["collected_at"],
        },
        "candidates": candidates,
    }


def extract_and_save_signals(theme_name: str) -> None:
    """直近2つのSnapshotからSignal Extractionを行い、結果をJSONへ保存する。"""

    print("=" * 50)
    print("Beacon Signal Extraction")
    print("=" * 50)

    snapshot_files = find_snapshot_files(theme_name)

    if len(snapshot_files) < 2:
        print("Signal Extractionには2件以上のSnapshotが必要です。")
        print()
        return

    previous_file, latest_file = snapshot_files[-2], snapshot_files[-1]

    previous_snapshot = load_snapshot(previous_file)
    latest_snapshot = load_snapshot(latest_file)

    signal_data = build_signal_candidates(theme_name, previous_snapshot, latest_snapshot)

    save_signal_candidates(theme_name, signal_data)

    print(f"Candidates found: {len(signal_data['candidates'])}")
    print()
