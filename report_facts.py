"""Report Facts

Daily Report v2の上部セクション(Today's Picture / Notable Observed Changes /
Broader Pattern / What to Watch / Data Summary)を組み立てるために必要な、
決定論的な事実(facts)だけをSignal JSONから計算する。

このモジュールは:

- AI呼び出し・ネットワーク呼び出しを一切行わない
- signal_extraction.pyのcandidatesの順序・内容を変更しない
  (star_growth降順のソートはこのモジュール内で作るコピーに対してのみ行い、
  Signal Extraction本体には反映しない)
- 「集中」「分散」のような分類ラベルは作らない。観測された数値そのものだけを返す
  (分類の言い換えはAIまたはreport_markdown.pyのフォールバック文が行う)
- 副作用のない純粋関数のみで構成する
"""

# Notable Observed Changesとして表示する、star_growthが大きい候補の件数。
# 総合ランキングではなく、表示件数を絞るための定数。
NOTABLE_CHANGE_LIMIT = 3


def _sorted_candidates_by_star_growth(candidates: list[dict]) -> list[dict]:
    """star_growth降順のコピーを返す。

    signal_extraction.pyが返す元のcandidatesリストは変更しない
    (Report表示専用の並べ替えを、Signal Extractionの意味に持ち込まないため)。
    """

    return sorted(candidates, key=lambda candidate: candidate["star_growth"], reverse=True)


def _select_largest_growth_candidates(
    sorted_candidates: list[dict], limit: int
) -> list[dict]:
    """star_growthが正の候補の中から、上位limit件を返す。

    star_growthが0以下の候補は「増加が観測された変化」ではないため対象外とする。
    """

    positive_growth_candidates = [
        candidate for candidate in sorted_candidates if candidate["star_growth"] > 0
    ]

    return positive_growth_candidates[:limit]


def build_report_facts(
    signal_data: dict,
    reason_counts: dict[str, int],
    tracked_repository_count: int,
) -> dict:
    """Signal JSONから、Daily Report v2に必要な決定論的事実を計算する。

    signal_data["candidates"]はここでは読み取るだけで、順序・内容を変更しない。
    """

    candidates = signal_data["candidates"]
    period = signal_data["period"]

    sorted_by_growth = _sorted_candidates_by_star_growth(candidates)
    positive_growth_values = [
        candidate["star_growth"] for candidate in sorted_by_growth if candidate["star_growth"] > 0
    ]

    total_positive_star_growth = sum(positive_growth_values)
    largest_star_growth = positive_growth_values[0] if positive_growth_values else 0
    second_largest_star_growth = (
        positive_growth_values[1] if len(positive_growth_values) > 1 else 0
    )
    largest_two_growth_sum = largest_star_growth + second_largest_star_growth

    if total_positive_star_growth > 0:
        largest_two_share_of_total = largest_two_growth_sum / total_positive_star_growth
    else:
        largest_two_share_of_total = 0.0

    largest_growth_candidates = [
        {
            "name": candidate["name"],
            "star_growth": candidate["star_growth"],
            "selection_reasons": candidate["selection_reasons"],
        }
        for candidate in _select_largest_growth_candidates(
            sorted_by_growth, NOTABLE_CHANGE_LIMIT
        )
    ]

    return {
        "candidate_count": len(candidates),
        "positive_star_growth_count": len(positive_growth_values),
        "new_repository_count": reason_counts["new_repository"],
        "multiple_keyword_match_count": reason_counts["multiple_keyword_matches"],
        "tracked_repository_count": tracked_repository_count,
        "elapsed_hours": period["elapsed_hours"],
        "total_positive_star_growth": total_positive_star_growth,
        "largest_star_growth": largest_star_growth,
        "second_largest_star_growth": second_largest_star_growth,
        "largest_two_growth_sum": largest_two_growth_sum,
        "largest_two_share_of_total": largest_two_share_of_total,
        "largest_growth_candidates": largest_growth_candidates,
        "reason_counts": reason_counts,
    }
