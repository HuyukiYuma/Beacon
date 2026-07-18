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

## 入力データ（Signal JSON）

AI分析レイヤーへの入力は、`signal_extraction.py`が生成する以下の構造です。

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

AIはこのJSON以外の情報（学習知識による推測、外部の株価・評判など）を
根拠として使ってはいけません。使えるのはこのJSONに書かれた数値と理由コードのみです。

この構造は現在GitHubデータのみを前提としています。将来的に他のデータソースが
追加された場合も、本Protocolが定める4つの問い・Evidence Levelの考え方・禁止事項は
共通の原則として適用されます（フィールド名やスキーマはデータソースごとに個別定義します）。

## selection_reasonsの意味（客観的な事実としての解釈）

| コード | 意味 | AIが言ってよいこと | AIが言ってはいけないこと |
|---|---|---|---|
| `new_repository` | 前回Snapshotに存在しなかった | 「今回初めて検出された」 | 「急成長している」「将来有望」 |
| `increased_keyword_hits` | ヒットしたキーワード数が増えた | 「複数の検索観点で言及が増えた」 | 「注目度が高まっている」（主観） |
| `top_star_growth` | 新規Repositoryを除いたStar増加数の上位10件に入った | 「他の候補と比べてStar増加数が大きい」 | 「人気が出ている」「バズっている」 |
| `multiple_keyword_matches` | 現在2件以上のキーワードにヒットしている | 「複数のテーマキーワードに合致する」 | 「重要度が高い」 |

理由コードは**事実の記録**であり、価値判断のラベルではありません。
AIは理由コードをそのまま採点や順位付けの根拠として使ってはいけません。

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

AIによる各候補の説明は、以下4点をこの順番で満たさなければなりません。

1. **What changed?**
   `star_growth`、`hit_change`、`is_new`など、JSONの数値・フラグで何が変化したかを述べる。
2. **How large was the change?**
   `previous_stars`→`current_stars`のような具体的な数値の変化量を明示する。
   「大きい／小さい」という主観的形容詞だけで済ませない。
3. **Is the change persistent or temporary?**
   現時点では比較対象がSnapshot2件のみのため、**単発の観測結果である旨を明示する**。
   「継続的なトレンドである」と断定してはいけない（3件以上のSnapshot比較が可能になった
   段階で、初めて「複数期間で継続」という表現が許される）。
   情報が不十分でこれを判断できない場合は、推測で埋めず「十分な証拠がない」
   「継続観測が必要」と明記する。
4. **Which evidence supports the signal?**
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

- **v1.0**（現行）: GitHubのSignal JSONのみを対象。AI出力はObservationのみ。
  Evidence LevelはL1・L2のみ使用（L3は予約）。
- **v1.1以降（想定）**: 複数データソース（Multi-source）への対応、Hypothesis記述の解禁、
  Evidence Level L3（複数期間の継続観測）の実運用化を検討する。
