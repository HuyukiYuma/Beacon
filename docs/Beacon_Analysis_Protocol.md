# Beacon Analysis Protocol

## Mission

Beaconは新興技術の早期シグナルを検出するプロジェクトです。
Beaconは未来を予言せず、結果を保証しません。観測可能な変化を収集し、比較し、
説明することを目的とします（詳細は`CLAUDE.md`のProject Missionを参照）。

AI分析レイヤーも同じ原則の上に立ちます。AIの役割は、客観的な変化を
分かりやすい説明文に変換することであり、独自の予測や価値判断を加えることではありません。

## これは何か

AI分析レイヤーが「何をしてよいか／何をしてはいけないか」を定義する規約書です。

`signal_extraction.py`が生成する客観的な候補データ（Signal JSON）を、AIがどう解釈し、
どう説明文に変換してよいかのルールをここで固定します。

`Beacon_Prompt.md`はこの規約を守るように書かれたプロンプトであり、
このProtocolが変わればPromptも追従して更新される、という関係です。

## 入力データ（Signal JSON + Report Facts）

AI分析レイヤーへの入力は、`signal_extraction.py`が生成するSignal JSONと、
`report_facts.py`が生成するReport Facts（v2で追加）の2つです。

```json
{
  "theme": "AI Agent",
  "period": {
    "previous": "2026-07-17T00:52:54",
    "current": "2026-07-18T19:28:00"
  },
  "candidates": [
    {
      "name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "previous_stars": 0,
      "current_stars": 0,
      "star_growth": 0,
      "previous_hits": 0,
      "current_hits": 0,
      "hit_change": 0,
      "is_new": false,
      "selection_reasons": []
    }
  ]
}
```

Report Facts（v2、`report_facts.build_report_facts`が生成）:

```json
{
  "candidate_count": 10,
  "positive_star_growth_count": 10,
  "new_repository_count": 0,
  "multiple_keyword_match_count": 3,
  "tracked_repository_count": 22,
  "elapsed_hours": 23.8,
  "total_positive_star_growth": 1782,
  "largest_star_growth": 641,
  "second_largest_star_growth": 488,
  "largest_two_growth_sum": 1129,
  "largest_two_share_of_total": 0.63,
  "largest_growth_candidates": [
    {"name": "owner/repo", "star_growth": 641, "selection_reasons": ["top_star_growth"]}
  ],
  "reason_counts": {"new_repository": 0, "increased_keyword_hits": 0,
                     "top_star_growth": 10, "multiple_keyword_matches": 3}
}
```

AIはこの2つのJSON以外の情報（学習知識による推測、外部の株価・評判など）を
根拠として使ってはいけません。使えるのはこれらのJSONに書かれた数値・理由コード・
候補名のみです。

**`largest_growth_candidates`は`report_facts.py`がstar_growthの大きい順に
機械的に選んだ候補であり、AIが「重要な候補」を選び直すためのものではありません。**
Notable Observed ChangesでAIが観測文を書けるのは、ここに含まれる候補名だけです
（`ai_analysis.py`が候補名を検証し、含まれない名前はDaily Reportに反映されません）。

この構造は現在GitHubデータのみを前提としています。将来的に他のデータソースが
追加された場合も、本Protocolが定める4つの問い・Evidence Levelの考え方・禁止事項は
共通の原則として適用されます（フィールド名やスキーマはデータソースごとに個別定義します）。

## Daily Reportの責務分担（Python / AI）（v2）

Daily Report全文のうち、以下はすべて`report_markdown.py` /
`report_facts.py`がSignal JSONとReport Factsから**決定的に**組み立てます。
AIはこれらを生成しません。

- H1見出し・比較期間の各見出し
- **Notable Observed Changesの選定**（`report_facts.py`がstar_growthの大きい順に
  機械的に選ぶ。AIは選定に一切関与しない）と、そこに表示するStar growthの数値
- Data Summary（Candidates数・New repositories数・Tracked repositories数・
  Observation period）
- Candidate Evidenceの各候補のURL・How large（数値）・
  Persistent or temporary（留保文）・Evidence
- Notes（免責文）

AIが担当するのは、次の4種類の説明文**だけ**です。AIの出力はMarkdownではなく、
tool use経由の構造化データに限定します。

| フィールド | 内容 | 対応するMarkdownセクション |
|---|---|---|
| `today_picture` | 今回の観測全体を3〜5文で要約する文章 | Today's Picture |
| `notable_observations` | `largest_growth_candidates`の各候補についての短い観測文 | Notable Observed Changes |
| `broader_pattern` | 候補集合全体についての説明文 | Broader Pattern |
| `what_to_watch` | 次回Snapshotで比較すると意味がある観測点の列挙 | What to Watch |
| `observations` | 候補ごとの`What changed`に入る短い観測文（v1から継続） | Candidate Evidence |

数値・URL・selection_reasonsはAIの出力に含めず、Python側がSignal JSON /
Report Factsから直接使います（AIに再出力させると、桁のズレや誤記のリスクを
構造的に持ち込むため）。

AI出力が得られない項目（AI呼び出し自体の失敗、未知name、不足candidateなど）
には、`report_markdown.py`がfactsだけから組み立てた機械的なフォールバック文を
使います。これにより、AIが使えない場合でもPythonだけで最低限のDaily Report v2を
完成できます（`build_fallback_today_picture` / `build_fallback_broader_pattern` /
`build_fallback_what_to_watch` / `NOTABLE_CHANGE_FALLBACK_TEXT` /
`build_fallback_observation`）。

### なぜ`pattern_type`のような固定分類ラベルを導入しないか

「集中型」「分散型」のような分類をPython側で行うには、「何%以上なら集中か」
という新しい閾値・判断ルールを追加する必要があります。Beaconは
「観測された事実だけを計算する」という原則を優先し、そのような恣意的な
分類ルールを増やしません。代わりにPythonは`largest_two_share_of_total`のような
**割合そのもの**を計算し、AIまたはフォールバック文がその数値を言葉にするだけに
留めます。

### AIが言ってよい範囲・言ってはいけない範囲（例）

`largest_two_share_of_total = 0.72`が渡された場合:

- 言ってよい: 「Star増加量の約72%が2Repositoryに集中していた」
  （factsの数値をそのまま言い換えただけの観測）
- 言ってはいけない: 「AI Agent市場が2強に集約されつつある」
  （factsに存在しない「市場」「集約されつつある」という外挿・トレンド解釈）

AIはfactsの数値を言い換えることはできますが、その数値が示す以上の意味
（市場動向、将来性、勝者/敗者の構図など）を付け加えてはいけません。

## selection_reasonsの意味（客観的な事実としての解釈）

| コード | 意味 | AIが言ってよいこと | AIが言ってはいけないこと |
|---|---|---|---|
| `new_repository` | 前回Snapshotに存在しなかった | 「今回初めて検出された」 | 「急成長している」「将来有望」 |
| `increased_keyword_hits` | ヒットしたキーワード数が増えた | 「複数の検索観点で言及が増えた」 | 「注目度が高まっている」（主観） |
| `top_star_growth` | 新規Repositoryを除いたStar増加数の上位10件に入った | 「他の候補と比べてStar増加数が大きい」 | 「人気が出ている」「バズっている」 |
| `multiple_keyword_matches` | 現在2件以上のキーワードにヒットしている | 「複数のテーマキーワードに合致する」 | 「重要度が高い」 |

理由コードは**事実の記録**であり、価値判断のラベルではありません。
AIは理由コードをそのまま採点や順位付けの根拠として使ってはいけません。

## selection_reasons件数の集計（Data Summary / Report Facts用）

selection_reasons別の件数（新規Repository数、キーワードヒット増加数など）は、
`ai_analysis.py`の`count_selection_reasons`が集計します。この件数集計自体は
AIへ渡さず、AIの入出力に一切関与させません。「Pythonは事実と決定的な構造を
担当し、AIは説明・要約を担当する」という設計思想に基づく判断です。

v2では、この集計値は`report_facts.py`が計算する他のfacts
（`largest_two_share_of_total`等）と合わせてReport Factsとしてまとめられ、
Data Summaryの表示（Python直接生成）と、Broader Pattern等のAI入力
（factsとしてAIへ渡す説明材料）の両方に使われます。「件数そのものをAIに
計算させない」という原則は変わらず、AIは既に計算済みのfactsを受け取って
言い換えるだけです。

- 件数の算出はAIの役割ではありません（LLMによる計算は数え間違いのリスクが
  あり、Observationに求められる「検証可能で誰が見ても同じ結論に至る」という
  性質を損ないます）。
- `count_selection_reasons`は副作用のない純粋関数であり、どの候補がどの理由に
  該当するかという判定ロジック（`signal_extraction.py`の`select_candidates`）
  には一切関与しません。
- 集計対象は既知の4種類（`new_repository`, `increased_keyword_hits`,
  `top_star_growth`, `multiple_keyword_matches`）に限定します。未知の理由コードが
  含まれていた場合は、黙って無視せず例外を送出します（件数が静かに欠落して
  Summaryが実態と食い違うことを防ぐため）。

## Observation と Hypothesis

Beaconの分析には2種類の記述があり得ます。

- **Observation（観測事実）**: Signal JSONに記録された数値・フラグ・selection_reasonsを、
  そのまま言い換えたもの。検証可能で、誰が見ても同じ結論に至る記述。
- **Hypothesis（仮説）**: 観測事実から一歩踏み込んだ解釈（例：「OSSコミュニティの関心が
  高まっている可能性がある」など）。検証されておらず、断定を避けるべき記述。

現時点（v1.0）では、AIの出力は**Observationのみ**とします。Hypothesisの生成は行いません。
Hypothesisを扱う場合は、将来のバージョン（v1.1以降を想定）で、これが仮説であり
検証されていないことが明確にわかるラベル（例: 見出しを分ける、「Hypothesis:」という
接頭辞をつける）と共に導入します。それまでは、AIがObservationとHypothesisを
混在させることを禁止します。

## Evidence Level

候補ごとの根拠がどの程度の客観的なデータに基づいているかを、以下の分類で示します。
これは**証拠の質・重要度を採点するスコアではありません**。あくまで「どの種類の証拠に
基づく記述か」を透明にするための分類であり、この分類を使って候補同士を序列化しては
いけません（`README.md`のRoadmapにある将来の`Beacon Score`とは別の概念です）。

- **L1**: 単一の`selection_reasons`のみに基づく
- **L2**: 複数の`selection_reasons`が同時に該当している
- **L3**: 3件以上のSnapshotにわたり、継続して観測されている
  （現状は2件比較のみのため未実装。将来のフェーズで有効化する）

現在の実装（Snapshot2件比較）では、L1・L2のみが実際に使用されます。
L3は将来の拡張のために予約されたレベルです。

## 必ず答えるべき4つの問い（CLAUDE.md Product Principlesより）

各候補の説明は、以下4点をこの順番で満たさなければなりません。誰がどの問いに
答えるかは固定されています（AI observationは1のみを担当し、2〜4は
`report_markdown.py`が常にSignal JSONから直接生成します）。

1. **What changed?**（AI observation、またはフォールバック文）
   `star_growth`、`hit_change`、`is_new`など、JSONの数値・フラグで何が変化したかを述べる。
2. **How large was the change?**（Python: `report_markdown._format_how_large`）
   `previous_stars`→`current_stars`のような具体的な数値の変化量を明示する。
   「大きい／小さい」という主観的形容詞だけで済ませない。
3. **Is the change persistent or temporary?**（Python: `report_markdown.PERSISTENCE_NOTE`）
   現時点では比較対象がSnapshot2件のみのため、**単発の観測結果である旨を明示する**。
   「継続的なトレンドである」と断定してはいけない（3件以上のSnapshot比較が可能になった
   段階で、初めて「複数期間で継続」という表現が許される）。
4. **Which evidence supports the signal?**（Python: `report_markdown._format_evidence`）
   該当した`selection_reasons`を列挙し、それぞれがどのJSONフィールドに基づくかを示す。

## 禁止事項

- 総合スコア・ランキング・独自の重み付けを作らない（Python側でもAI側でも付けない）
- 「上がる」「投資すべき」「買い時」など将来の値動きを示唆する表現をしない
- 「将来性がある」「有望」など根拠のない期待を煽る表現をしない
- JSONに存在しない情報（学習知識・憶測）を事実として混ぜない
- 複数候補を比較して「一番良い」と序列化しない（客観的な数値の提示に留める）

## エッジケース

- `candidates`が空の場合：「今回の期間では、条件に該当する候補はありませんでした」とだけ述べる。
- `previous_stars`が存在しない（`is_new: true`）場合：Star増加量を「増加」として語らず、
  「新規検出のため、増加量ではなく総Star数として記録する」ことを明記する。

## Revision History

- **v1.0**: GitHubのSignal JSONのみを対象。AI出力はObservationのみ。
  Evidence LevelはL1・L2のみ使用（L3は予約）。Daily Report全文の決定的な部分
  （見出し・URL・数値・Evidence・Notes）は`report_markdown.py`が組み立て、
  AIは候補ごとの観測文（What changed）のみをtool use経由の構造化データで返す。
- **v2（現行、Day 25）**: `report_facts.py`を新設し、Signal JSONから
  横断的な決定論的facts（星増加分布・件数・割合）を計算するようにした。
  Daily Reportを「Today's Picture / Notable Observed Changes / Broader Pattern /
  What to Watch / Data Summary / Candidate Evidence」の構造に再設計し、
  AIの役割を「候補ごとのobservation」から「factsを横断して説明する4種類の
  文章（today_picture, notable_observations, broader_pattern,
  what_to_watch）+ 従来のobservations」に拡張した。「集中/分散」等の固定分類
  ラベル（pattern_type）は導入せず、割合等の生の数値のみを事実として扱う設計を
  維持した。Signal Extraction（`signal_extraction.py`）の候補選定ロジック・
  順序は変更していない。
- **v1.1以降（想定）**: 複数データソース（Multi-source）への対応、Hypothesis記述の解禁、
  Evidence Level L3（複数期間の継続観測、multi-day trend）の実運用化を検討する。
  Day 25時点ではsnapshot_history.jsonにRepository単位の時系列が無いため未着手。
