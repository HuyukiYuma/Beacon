# Daily Report Template

## これは何か

Daily Reportの構成テンプレートです。

`report_markdown.py`が、このテンプレートの構造をSignal JSONと
selection_reasons件数から決定的に組み立てます。AIが担当するのは
各Candidateブロックの`What changed`に入る観測文（observation）だけであり、
それ以外（見出し・URL・How large・Persistent or temporary・Evidence・
Summary集計・Notes）はすべてPython側が生成します。AI observationが
得られない場合も、`report_markdown.py`はSignal JSONの数値だけから
機械的なフォールバック文を`What changed`に使い、レポート全体を完成させます。

`{{ }}`はプレースホルダーで、実装時に実データへ置き換えられます。

## テンプレート本体

```markdown
# Beacon Daily Report - {{theme}}

比較期間: {{period.previous}} 〜 {{period.current}}

## Summary

- 検出された候補数: {{candidates数}}
- 新規Repository: {{new_repository該当数}}
- キーワードヒット増加: {{increased_keyword_hits該当数}}
- Star増加上位: {{top_star_growth該当数}}
- 複数キーワード一致: {{multiple_keyword_matches該当数}}

## Candidates

候補ごとの見出しは`### {{candidate.name}}`のみとし、「1. 2. 3...」のような
順位を意味する連番を付けない。記載順は判定・順位付けを意味しない。

### {{candidate.name}}

- URL: {{candidate.url}}
- What changed:
  {{AIによる観測文。得られない場合はstar_growth・hit_change・is_newから
    Python側が機械的に組み立てたフォールバック文}}
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

## Summary

今回の期間では、条件に該当する候補はありませんでした。
```

## 保存先（実装時の想定）

`data/reports/report_{theme}_{timestamp}.md` のような形式を想定しています
（Snapshot: `data/`、Signal候補: `data/signals/`と対になる構成）。
実際のディレクトリ名・命名規則は実装時に`Architecture.md`との整合性を確認して決定します。
