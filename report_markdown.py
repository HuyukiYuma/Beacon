"""Daily Report v2をMarkdownとして決定的に組み立てる。

このモジュールはAI・ネットワーク呼び出しを一切行わない。すべての関数は
副作用のない純粋関数であり、同じ引数からは常に同じMarkdown文字列を返す。

Daily Report v2は「上: 人間が読むSummary層」「下: 検証可能なEvidence層」の
二層構造。

- Today's Picture / Notable Observed Changes / Broader Pattern / What to Watch:
  AIが生成した説明文を使うが、AIが使えない場合はここで定義する決定論的な
  フォールバック文だけでも成立する（Signal JSONとreport_facts.pyが計算した
  factsだけから組み立てるため）。
- Data Summary: 完全にPython生成（AIは一切関与しない）。
- Candidate Evidence: v1と同じ構成（What changed / How large /
  Persistent or temporary / Evidence）を維持する。

「Notable」はAIの感覚では選ばない。report_facts.pyがstar_growthに基づいて
決定論的に選んだ`facts["largest_growth_candidates"]`をそのまま使う。
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

# Notable Observed Changesで、star_growthが正の候補が1件も無かった場合の文。
NO_NOTABLE_CHANGES_TEXT = "今回の観測期間では、star_growthが正の値となった候補はありませんでした。"

# Notable Observed Changesの各候補について、AI observationが無い場合に使う
# 機械的なフォールバック文。report_facts.pyが選んだ候補は「星増加数が大きい」
# という事実だけが確定しているため、それ以上の評価を含めない。
NOTABLE_CHANGE_FALLBACK_TEXT = "今回の観測期間で、観測されたstar_growthの大きい変化の一つ。"


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
    """候補1件分のMarkdownブロックを組み立てる（Candidate Evidence用）。

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


def build_fallback_today_picture(facts: dict) -> str:
    """AIが使えない場合の「Today's Picture」を、facts だけから機械的に組み立てる。

    分類や評価は行わず、factsの数値をそのまま文章化するだけ。
    """

    sentences = [
        f"今回の観測期間（約{facts['elapsed_hours']:.1f}時間）で、"
        f"Signal Candidateは{facts['candidate_count']}件検出されました。",
        f"新規Repositoryの出現は{facts['new_repository_count']}件でした。",
    ]

    largest_growth_candidates = facts["largest_growth_candidates"]

    if largest_growth_candidates:
        top = largest_growth_candidates[0]
        sentences.append(
            f"star_growthが最も大きかったのは{top['name']}"
            f"（+{top['star_growth']}）でした。"
        )

        if len(largest_growth_candidates) > 1:
            share_percent = round(facts["largest_two_share_of_total"] * 100)
            sentences.append(
                f"star_growthが正だった{facts['positive_star_growth_count']}件のうち、"
                f"上位2件で全体の増加量の約{share_percent}%を占めています。"
            )
    else:
        sentences.append("star_growthが正の値となった候補はありませんでした。")

    return " ".join(sentences)


def build_fallback_broader_pattern(facts: dict) -> str:
    """AIが使えない場合の「Broader Pattern」を、facts だけから機械的に組み立てる。

    「集中」「分散」などの分類ラベルは付けない。観測された数値のみを述べる。
    """

    sentences = [
        f"検出された候補数は{facts['candidate_count']}件で、"
        f"うちstar_growthが正だったのは{facts['positive_star_growth_count']}件でした。",
        f"新規Repositoryとして検出されたのは{facts['new_repository_count']}件です。",
        f"複数キーワードに一致した候補は{facts['multiple_keyword_match_count']}件でした。",
    ]

    if facts["total_positive_star_growth"] > 0:
        share_percent = round(facts["largest_two_share_of_total"] * 100)
        sentences.append(
            f"star_growthが正の候補のうち、上位2件で全体の増加量の約{share_percent}%を"
            f"占めています。"
        )

    return " ".join(sentences)


def build_fallback_what_to_watch(facts: dict) -> list[str]:
    """AIが使えない場合の「What to Watch」を、facts だけから機械的に組み立てる。

    予測ではなく、次回Snapshotで比較すると意味がある観測点の列挙のみ。
    """

    items = [
        f"{candidate['name']}のstar_growthが次回どう変化するか"
        for candidate in facts["largest_growth_candidates"]
    ]

    if len(facts["largest_growth_candidates"]) >= 2:
        items.append(
            f"今回大きな増加が見られた{len(facts['largest_growth_candidates'])}件の"
            f"Repository以外にも同様の変化が広がるか"
        )

    items.append("新規Repositoryが出現するか")
    items.append("keyword coverageに変化があるか")

    return items


def build_notable_observed_changes_section(
    facts: dict, notable_observations: dict[str, str]
) -> str:
    """Notable Observed Changesセクションの本文を組み立てる。

    表示対象はreport_facts.pyがstar_growthに基づいて決定論的に選んだ
    `facts["largest_growth_candidates"]`のみ。AIはここで選ばれた候補以外を
    語ることも、選定基準を変えることもできない。
    """

    largest_growth_candidates = facts["largest_growth_candidates"]

    if not largest_growth_candidates:
        return NO_NOTABLE_CHANGES_TEXT

    blocks = []

    for candidate in largest_growth_candidates:
        observation = notable_observations.get(candidate["name"]) or NOTABLE_CHANGE_FALLBACK_TEXT

        blocks.append(
            f"### {candidate['name']}\n"
            f"\n"
            f"Star growth: +{candidate['star_growth']}\n"
            f"\n"
            f"{observation}"
        )

    return "\n\n".join(blocks)


def build_data_summary_section(facts: dict) -> str:
    """Data Summaryセクションの本文を組み立てる。完全にPython生成。"""

    return (
        f"- Candidates: {facts['candidate_count']}\n"
        f"- New repositories: {facts['new_repository_count']}\n"
        f"- Tracked repositories: {facts['tracked_repository_count']}\n"
        f"- Observation period: {facts['elapsed_hours']:.1f} hours"
    )


def build_report_markdown(
    signal_json: dict,
    facts: dict,
    ai_content: dict,
) -> str:
    """Daily Report v2全文をMarkdownとして組み立てる。副作用のない純粋関数。

    ai_contentは以下のキーを持つ辞書（欠けているキーはフォールバックとして扱う）:

    - observations: {候補name: observation文} （Candidate Evidence用、v1と同じ）
    - today_picture: str | None
    - broader_pattern: str | None
    - what_to_watch: list[str]
    - notable_observations: {候補name: observation文} （Notable Observed Changes用）

    いずれのAI生成テキストが欠けていても、report_facts.pyが計算したfactsだけで
    Daily Report全体を完成できる。
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
        return (
            f"{header}\n"
            f"\n"
            f"## Data Summary\n"
            f"\n"
            f"{build_data_summary_section(facts)}\n"
            f"\n"
            f"## Notes\n"
            f"\n"
            f"{NO_CANDIDATES_TEXT}\n"
            f"\n"
            f"{NOTES_TEXT}\n"
        )

    observations = ai_content.get("observations") or {}
    today_picture = ai_content.get("today_picture") or build_fallback_today_picture(facts)
    broader_pattern = ai_content.get("broader_pattern") or build_fallback_broader_pattern(facts)
    what_to_watch = ai_content.get("what_to_watch") or build_fallback_what_to_watch(facts)
    notable_observations = ai_content.get("notable_observations") or {}

    what_to_watch_section = "\n".join(f"- {item}" for item in what_to_watch)

    candidate_blocks = "\n\n".join(
        build_candidate_block(candidate, observations.get(candidate["name"]))
        for candidate in candidates
    )

    return (
        f"{header}\n"
        f"\n"
        f"## Today's Picture\n"
        f"\n"
        f"{today_picture}\n"
        f"\n"
        f"## Notable Observed Changes\n"
        f"\n"
        f"{build_notable_observed_changes_section(facts, notable_observations)}\n"
        f"\n"
        f"## Broader Pattern\n"
        f"\n"
        f"{broader_pattern}\n"
        f"\n"
        f"## What to Watch\n"
        f"\n"
        f"{what_to_watch_section}\n"
        f"\n"
        f"## Data Summary\n"
        f"\n"
        f"{build_data_summary_section(facts)}\n"
        f"\n"
        f"## Candidate Evidence\n"
        f"\n"
        f"{candidate_blocks}\n"
        f"\n"
        f"## Notes\n"
        f"\n"
        f"{NOTES_TEXT}\n"
    )
