# Architecture (AI Analysis Layer)

## これは何か

Beaconに追加するAI分析レイヤーの位置づけと、モジュール構成の設計案です。
Day 10時点ではコードは実装せず、方針のみを固定します。

## 現在のパイプライン（実装済み）

```
themes.py
   |
   v
collect_github.py  --- GitHub検索、Repositoryプロフィール集計
   |
   v
storage.py         --- Snapshot保存 (data/*.json)
   |
   v
comparison.py      --- 直近2件のSnapshotを比較し、変化点を表示
   |
   v
signal_extraction.py --- 客観的な差分計算 + 候補選定
   |
   v
storage.py         --- Signal保存 (data/signals/*.json)
```

`main.py`がこの一連の流れを順番に呼び出す構成になっています。

## 追加するAI分析レイヤー（設計のみ、未実装）

```
signal_extraction.py の出力 (data/signals/*.json)
   |
   v
ai_analysis.py（未作成） --- Beacon_Prompt.md + Signal JSON をAI APIへ送信し、
   |                          Beacon_Analysis_Protocol.md のルールに沿った
   |                          説明文（Markdown）を受け取る
   v
report.py（未作成、または storage.py に追加） --- Daily_Report_Template.md の
   |                                              構成でレポートを保存
   v
data/reports/*.md
```

### `ai_analysis.py`（想定される責務）

- `data/signals/`から最新のSignal JSONを読み込む
- `Beacon_Prompt.md`の内容とSignal JSONを組み合わせ、AI APIへ送信する
- AIからの応答（Markdown文字列）をそのまま返す
- **Python側で数値の再解釈やスコアリングは行わない**（それは既に
  `signal_extraction.py`が担っており、AI分析レイヤーは説明文の生成に専念する）

### `report.py`（想定される責務。既存の`storage.py`に関数追加する案も可）

- AIの出力を`data/reports/report_{theme}_{timestamp}.md`として保存する
- 既存の`save_snapshot` / `save_signal_candidates`と同じ命名パターンに揃える

## 責務の分離方針

| レイヤー | 責務 | 価値判断をするか |
|---|---|---|
| `collect_github.py` | データ収集 | しない |
| `storage.py` | 保存・読込 | しない |
| `comparison.py` | 差分の表示 | しない |
| `signal_extraction.py` | 客観的な差分計算・候補選定 | しない（ルールベースの選定のみ） |
| `ai_analysis.py`（未実装） | 候補データを説明文に変換 | しない（Protocolで禁止） |
| `report.py`（未実装） | レポートとして保存 | しない |

Beacon全体を通して、「総合スコアをつける」「将来を予言する」工程はどこにも存在しません。
これは`CLAUDE.md`のProduct Principlesを、コード構成レベルで担保するための設計です。

## APIキー・秘密情報の扱い（実装時の方針）

- APIキーは`.env`で管理し、`python-dotenv`などで読み込む
- `.env`は`.gitignore`で除外済み（既存ルール）
- コード中にAPIキーを直書きしない（CLAUDE.mdのルールに準拠）

## エラーハンドリングの方針（実装時の方針）

- AI APIへの通信失敗時は、`collect_github.py`の`search_github`と同様に
  例外を握りつぶさず、エラー内容を表示した上で処理を中断する
- AIの応答がProtocolの禁止表現を含んでいるかどうかの自動検証は、
  Day 10時点では設計範囲外とする（将来的な検討事項）

## 未確定事項（次フェーズで決める）

- AI APIの種類・呼び出し方法（Day 11以降の実装タスク）
- `data/reports/`配下ファイルをGit管理対象にするかどうか
  （Signal/Snapshotと同様に除外する可能性が高いが、要確認）
- 複数テーマ（10テーマ）に対応する際の、レポート生成のループ構造
