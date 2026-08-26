"""Signal JSON・selection_reasons件数・AI observationsから、
Daily Report全文（Markdown）を決定的に組み立てる。

このモジュールはAI・ネットワーク呼び出しを一切行わない。
すべての関数は副作用のない純粋関数であり、同じ引数からは常に同じ
Markdown文字列を返す。AI observationが欠けている候補には、
Signal JSONの数値だけから機械的に組み立てたフォールバック文を使うため、
AIが使えない場合でもこのモジュールだけでDaily Reportを完成できる。

見出し・URL・Star数・Hits数・selection_reasons・Notesは、すべて
Signal JSONおよびPython側の集計値からここで直接生成する。AIが担当するのは
各候補の「What changed」に入る短い観測文（observation）だけであり、
それもフォールバック文で置き換え可能。
"""


# signal_extraction.pyのselect_candidatesが付与する理由コードと、
# Beacon_Analysis_Protocol.mdで定義された「AIが言ってよいこと」の説明文。
# この対応表は事実の言い換えであり、判定ロジックには関与しない。
SELECTION_REASON_LABELS = {
    "new_repository": "前回Snapshotに存在しなかった（今回初めて検出された）",
    "increased_keyword_hits": "ヒットしたキーワード数が増加した",
    "top_star_growth": "新規Repositoryを除いたStar増加数の上位10件に入った",
    "multiple_keyword_matches": "現在2件以上のキーワードにヒットしている",
}

# v1.0（Snapshot2件比較のみ）では、継続性に関する記述は常に同じ留保になる。
# 3件以上のSnapshot比較が可能になった段階で、この定数を条件分岐に置き換える。
PERSISTENCE_NOTE = (
    "今回は前回・今回の2時点比較のみに基づく単発の観測結果です。"
    "継続的な傾向であるかどうかは、複数回のSnapshot比較が蓄積された段階で判断します。"
)

NOTES_TEXT = (
    "Beaconは将来の株価や評価が上がることを保証するものではありません。\n"
    "本レポートは、観測された客観的な変化と、その根拠を示すものです。"
)

NO_CANDIDATES_TEXT = "今回の期間では、条件に該当する候補はありませんでした。"


def build_fallback_observation(candidate: dict) -> str:
    """AI observationが無い候補のために、Signal JSONの数値だけから
    機械的な「What changed」文を組み立てる。副作用のない純粋関数。
    """

    if candidate["is_new"]:
        return f"新規Repositoryとして検出されました（現在のStar数: {candidate['current_stars']}）。"

    star_growth = candidate["star_growth"]
    hit_change = candidate["hit_change"]

    if star_growth > 0 and hit_change > 0:
        return (
            f"Star数とヒット数がともに増加しました"
            f"（star_growth: {star_growth}, hit_change: {hit_change}）。"
        )

    if star_growth > 0:
        return f"Star数が増加しました（star_growth: {star_growth}）。"

    if hit_change > 0:
        return f"ヒット数が増加しました（hit_change: {hit_change}）。"

    if star_growth < 0:
        return f"Star数が減少しました（star_growth: {star_growth}）。"

    return (
        "Star数・ヒット数に変化はありませんでしたが、"
        "selection_reasonsに基づき候補として選出されています。"
    )


def _format_how_large(candidate: dict) -> str:
    """How large（変化の大きさ）の行を組み立てる。

    is_newの場合、Star数は「増加量」ではなく「新規検出時点の総数」として
    扱う（Beacon_Analysis_Protocol.mdのエッジケース定義に従う）。
    """

    if candidate["is_new"]:
        stars_line = (
            f"新規検出のため、増加量ではなく総Star数として記録: "
            f"{candidate['current_stars']}"
        )
    else:
        stars_line = (
            f"{candidate['previous_stars']} → {candidate['current_stars']}"
            f"（{candidate['star_growth']}）"
        )

    hits_line = (
        f"{candidate['previous_hits']} → {candidate['current_hits']}"
        f"（{candidate['hit_change']}）"
    )

    return f"  {stars_line}\n  {hits_line}"


def _format_evidence(candidate: dict) -> str:
    """Evidence（根拠）の行を、selection_reasonsの説明付きで組み立てる。"""

    lines = []

    for reason in candidate["selection_reasons"]:
        if reason not in SELECTION_REASON_LABELS:
            raise ValueError(f"未知のselection_reasonsコードです: '{reason}'")

        lines.append(f"  - {reason}: {SELECTION_REASON_LABELS[reason]}")

    return "\n".join(lines)


def build_candidate_block(candidate: dict, observation_text: str | None) -> str:
    """候補1件分のMarkdownブロックを組み立てる。

    observation_textがNone・空文字の場合は、フォールバック文を使う。
    """

    what_changed = observation_text or build_fallback_observation(candidate)

    return (
        f"### {candidate['name']}\n"
        f"\n"
        f"- URL: {candidate['url']}\n"
        f"- What changed:\n"
        f"  {what_changed}\n"
        f"- How large:\n"
        f"{_format_how_large(candidate)}\n"
        f"- Persistent or temporary:\n"
        f"  {PERSISTENCE_NOTE}\n"
        f"- Evidence:\n"
        f"{_format_evidence(candidate)}"
    )


def build_summary_section(candidate_count: int, reason_counts: dict[str, int]) -> str:
    """Summaryセクションの本文（見出しの中身）を組み立てる。"""

    return (
        f"- 検出された候補数: {candidate_count}\n"
        f"- 新規Repository: {reason_counts['new_repository']}\n"
        f"- キーワードヒット増加: {reason_counts['increased_keyword_hits']}\n"
        f"- Star増加上位: {reason_counts['top_star_growth']}\n"
        f"- 複数キーワード一致: {reason_counts['multiple_keyword_matches']}"
    )


def build_report_markdown(
    signal_json: dict,
    reason_counts: dict[str, int],
    observations: dict[str, str],
) -> str:
    """Daily Report全文をMarkdownとして組み立てる。副作用のない純粋関数。

    observationsは{候補name: observation文}の辞書。キーが存在しない、
    または値が空の候補にはbuild_fallback_observationのフォールバック文を使う。
    そのためobservationsが空辞書（AI呼び出しが完全に失敗した場合）でも、
    このモジュールだけで完結したDaily Reportを生成できる。
    """

    theme = signal_json["theme"]
    period = signal_json["period"]
    candidates = signal_json["candidates"]

    header = (
        f"# Beacon Daily Report - {theme}\n"
        f"\n"
        f"比較期間: {period['previous']} 〜 {period['current']}"
    )

    if not candidates:
        return f"{header}\n\n## Summary\n\n{NO_CANDIDATES_TEXT}\n"

    summary_section = build_summary_section(len(candidates), reason_counts)

    candidate_blocks = "\n\n".join(
        build_candidate_block(candidate, observations.get(candidate["name"]))
        for candidate in candidates
    )

    return (
        f"{header}\n"
        f"\n"
        f"## Summary\n"
        f"\n"
        f"{summary_section}\n"
        f"\n"
        f"## Candidates\n"
        f"\n"
        f"{candidate_blocks}\n"
        f"\n"
        f"## Notes\n"
        f"\n"
        f"{NOTES_TEXT}\n"
    )
