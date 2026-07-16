from storage import find_snapshot_files, load_snapshot


def compare_snapshots(previous_snapshot: dict, latest_snapshot: dict) -> dict:
    """2つのスナップショットを比較し、差分をまとめて返す。"""

    previous_repositories = {
        repository["name"]: repository
        for repository in previous_snapshot["repositories"]
    }
    latest_repositories = {
        repository["name"]: repository
        for repository in latest_snapshot["repositories"]
    }

    new_repositories = [
        repository
        for name, repository in latest_repositories.items()
        if name not in previous_repositories
    ]

    removed_repositories = [
        repository
        for name, repository in previous_repositories.items()
        if name not in latest_repositories
    ]

    changed_repositories = []

    for name, latest_repository in latest_repositories.items():
        previous_repository = previous_repositories.get(name)

        if previous_repository is None:
            continue

        if (
            latest_repository["hits"] != previous_repository["hits"]
            or latest_repository["stars"] != previous_repository["stars"]
        ):
            changed_repositories.append(
                {
                    "name": name,
                    "previous_hits": previous_repository["hits"],
                    "latest_hits": latest_repository["hits"],
                    "previous_stars": previous_repository["stars"],
                    "latest_stars": latest_repository["stars"],
                }
            )

    return {
        "new_repositories": new_repositories,
        "removed_repositories": removed_repositories,
        "changed_repositories": changed_repositories,
    }


def display_snapshot_comparison(theme_name: str) -> None:
    """直近2つのスナップショットを比較し、簡易な結果を表示する。"""

    print("=" * 50)
    print("Beacon Snapshot Comparison")
    print("=" * 50)

    snapshot_files = find_snapshot_files(theme_name)

    if len(snapshot_files) < 2:
        print("比較には2件以上のスナップショットが必要です。")
        print()
        return

    previous_file, latest_file = snapshot_files[-2], snapshot_files[-1]

    previous_snapshot = load_snapshot(previous_file)
    latest_snapshot = load_snapshot(latest_file)

    comparison = compare_snapshots(previous_snapshot, latest_snapshot)

    print(f"Previous file : {previous_file.name}")
    print(f"Latest file   : {latest_file.name}")
    print(f"New repositories     : {len(comparison['new_repositories'])}")
    print(f"Removed repositories : {len(comparison['removed_repositories'])}")
    print(f"Changed repositories : {len(comparison['changed_repositories'])}")
    print()
