# Daily Report Template (v2)

## これは何か

Daily Report v2の構成テンプレートです。

v1は候補（Repository）ごとに同じ4行構造（What changed / How large /
Persistent or temporary / Evidence）を繰り返すだけで、「今日全体として何が
観測されたか」が読み取りにくいという課題がありました。v2はレポートを
二層構造にし、上部に横断的なSummary、下部に検証可能なEvidenceを配置します。

- **Summary層**（Today's Picture / Notable Observed Changes / Broader Pattern /
  What to Watch）: AIが`report_facts.py`のfactsを読んで自然言語化する。
  AIが使えない場合は、`report_markdown.py`内の決定論的なフォールバック文が
  factsだけから同じ構造を組み立てる。
- **Data Summary**: 完全にPython生成。AIは一切関与しない。
- **Evidence層**（Candidate Evidence）: v1の`## Candidates`と同じ内容
  （What changed / How large / Persistent or temporary / Evidence）を
  `## Candidate Evidence`という見出しでそのまま維持する。

`{{ }}`はプレースホルダーで、実装時に実データへ置き換えられます。

## テンプレート本体

```markdown
# Beacon Daily Report - {{theme}}

比較期間: {{period.previous}} 〜 {{period.current}}

## Today's Picture

{{AIが report_facts.py の facts を根拠に書く3〜5文程度の要約。
  factsに無い数値・傾向を書いてはいけない。
  AIが使えない場合は report_markdown.build_fallback_today_picture(facts) が
  同じ位置に決定論的な文章を生成する。}}

## Notable Observed Changes

{{report_facts.py が star_growth に基づいて機械的に選んだ上位候補
  （facts["largest_growth_candidates"]、既定で最大3件）だけを表示する。
  「総合的に重要」という評価ではなく、「観測されたstar_growthが大きい変化」
  という事実の提示に限定する。}}

### {{candidate.name}}

Star growth: +{{candidate.star_growth}}

{{AIによる短い観測文（notable_observations）。得られない場合は
  report_markdown.NOTABLE_CHANGE_FALLBACK_TEXT
  （「今回の観測期間で、観測されたstar_growthの大きい変化の一つ。」）を使う。}}

（facts["largest_growth_candidates"]の件数分、上記ブロックを繰り返す。
 該当が無い場合は report_markdown.NO_NOTABLE_CHANGES_TEXT を1行だけ表示する。）

## Broader Pattern

{{AIが report_facts.py の facts
  （candidate_count, new_repository_count, positive_star_growth_count,
  multiple_keyword_match_count, largest_two_share_of_total 等）を根拠に
  候補集合全体を説明する文章。「集中」「分散」等の固定分類ラベルは
  Python側では作らない。AIはfactsの数値をそのまま言い換える範囲に留め、
  数値が示す以上の解釈（市場動向・将来性等）を加えてはいけない。
  AIが使えない場合は build_fallback_broader_pattern(facts) を使う。}}

## What to Watch

{{予測ではなく、次回Snapshotで比較すると今回の観測を理解しやすい観測点の列挙。
  AIが使えない場合は build_fallback_what_to_watch(facts) が
  Notable Observed Changesの候補名 + 固定の観測点（新規Repository出現の有無、
  keyword coverageの変化）から機械的に組み立てる。}}

- {{観測点1}}
- {{観測点2}}

## Data Summary

- Candidates: {{facts.candidate_count}}
- New repositories: {{facts.new_repository_count}}
- Tracked repositories: {{facts.tracked_repository_count}}
- Observation period: {{facts.elapsed_hours（小数第1位）}} hours

## Candidate Evidence

候補ごとの見出しは`### {{candidate.name}}`のみとし、「1. 2. 3...」のような
順位を意味する連番を付けない。記載順は判定・順位付けを意味しない
（Signal JSONのcandidatesの元の順序をそのまま使う）。

### {{candidate.name}}

- URL: {{candidate.url}}
- What changed:
  {{AIによる観測文（observations）。得られない場合はstar_growth・hit_change・
    is_newからPython側が機械的に組み立てたフォールバック文}}
- How large:
  {{previous_stars}} → {{current_stars}}（{{star_growth}}）
  {{previous_hits}} → {{current_hits}}（{{hit_change}}）
- Persistent or temporary:
  {{2時点比較のみの場合の留保文。将来的にSnapshotが3件以上になった際は
    「n回連続で観測」のような継続性の表現に置き換える}}
- Evidence:
  {{selection_reasonsの列挙と、それぞれが指すJSONフィールド}}

（candidatesの件数分、上記ブロックを繰り返す）

## Notes

Beaconは将来の株価や評価が上がることを保証するものではありません。
本レポートは、観測された客観的な変化と、その根拠を示すものです。
```

## 候補が0件のときの出力例

```markdown
# Beacon Daily Report - {{theme}}

比較期間: {{period.previous}} 〜 {{period.current}}

## Data Summary

- Candidates: 0
- New repositories: 0
- Tracked repositories: {{facts.tracked_repository_count}}
- Observation period: {{facts.elapsed_hours}} hours

## Notes

今回の期間では、条件に該当する候補はありませんでした。

Beaconは将来の株価や評価が上がることを保証するものではありません。
本レポートは、観測された客観的な変化と、その根拠を示すものです。
```

## 保存先

`data/reports/report_{theme}_{timestamp}.md`
（Snapshot: `data/`、Signal候補: `data/signals/`と対になる構成、v1から変更なし）

## v1からの変更点

- `## Summary`（件数集計のみ）を廃止し、`## Today's Picture` /
  `## Notable Observed Changes` / `## Broader Pattern` / `## What to Watch` /
  `## Data Summary`の5セクションに置き換えた。
- `## Candidates`を`## Candidate Evidence`にリネームしたが、中身（What changed /
  How large / Persistent or temporary / Evidence）と候補の並び順はv1と同じ。
- Signal Extraction（`signal_extraction.py`）のcandidatesの順序・選定ロジックは
  一切変更していない。star_growth降順の並べ替えは`report_facts.py`が
  表示用のコピーに対してのみ行う。
- `pattern_type`のような固定分類ラベルは導入していない
  （Day 25の設計判断: 新しい閾値・分類ルールを増やさない）。
