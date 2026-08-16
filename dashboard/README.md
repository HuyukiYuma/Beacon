# Beacon Dashboard

Beaconが収集したSignalを表示するWeb UIです。

Beacon本体(Python)とは独立していて、Pythonのコードを一切変更せずに動きます。

## 起動方法

```bash
cd dashboard
npm install
npm run dev
```

起動後 http://localhost:3000 を開きます。

表示するデータはBeacon本体が生成するため、先に一度Beaconを実行してください。

```bash
python main.py
```

## 何を表示するか

| パネル | 読み込むデータ |
|---|---|
| Beacon Header | 最新Snapshotの`collected_at` |
| Today's Signals | 最新のSignal JSON |
| Top Signals | Signal JSONのうち`top_star_growth`と判定された候補 |
| Daily Report | `data/reports/`の最新Markdown |
| Recent Activity | `data/`のSnapshot履歴 |

## 構成

```
dashboard/
├── app/
│   ├── layout.tsx     全体の枠組み
│   ├── page.tsx       4パネルの組み立て
│   └── globals.css    ダークテーマ(色は役割ごとのCSS変数)
├── components/        パネルごとの表示部品
└── lib/
    ├── beacon-data.ts data/を読む唯一の窓口(server-only)
    ├── types.ts       Pythonが出力するJSONの型
    ├── format.ts      表示用の書式変換
    └── config.ts      監視テーマなどの設定
```

## 設計上のルール

- **`data/`へ触るのは`lib/beacon-data.ts`だけ**です。
  先頭の`import "server-only"`により、Client Componentから読み込むと
  ビルドが失敗します。ファイルシステムへのアクセスがブラウザ側へ
  漏れないよう、仕組みで防いでいます。

- **UIは数値を計算し直しません。**
  Star増加数も1時間あたりの増加数も、Pythonが出力した値をそのまま表示します。
  UIで独自のスコアを付けることは、Beaconの原則に反するため行いません。

- **APIキーはUI側で扱いません。**
  ブラウザもこのUIも、GitHub APIやAI APIを直接呼びません。
  Pythonが生成し終えたJSON/Markdownを読むだけです。
  そのため`dashboard/`配下に`.env`は置かず、`NEXT_PUBLIC_`も使いません。

- **`lib/beacon-data.ts`の関数はすべて`async`**です。
  将来ファイル読み込みをAPIやDBへの問い合わせに差し替えても、
  呼び出し側のコンポーネントを修正せずに済むようにしています。

## 参照するデータの場所

既定では`dashboard/`の1つ上にある`data/`を読みます。

別の場所を読ませたい場合は環境変数`BEACON_DATA_DIR`を指定します
(秘密情報ではありません)。
