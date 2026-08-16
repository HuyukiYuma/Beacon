/**
 * Beaconのバックエンド(Python)が出力するJSONの型定義。
 *
 * ここに書く型は、Python側が実際に書き出している構造をそのまま写したものです。
 * UI側で項目を足したり、数値を計算し直したりはしません。
 */

/** data/github_{theme}_{timestamp}.json に入っているRepository 1件分 */
export type SnapshotRepository = {
  name: string;
  hits: number;
  stars: number;
  url: string;
};

/** storage.py の save_snapshot が保存するSnapshot全体 */
export type Snapshot = {
  theme: string;
  collected_at: string;
  repositories: SnapshotRepository[];
};

/** signal_extraction.py が計算する観測期間 */
export type SignalPeriod = {
  previous: string;
  current: string;
  elapsed_seconds: number;
  elapsed_hours: number;
};

/**
 * signal_extraction.py が選んだ注目候補 1件分。
 *
 * selection_reasons には候補に選ばれた理由が入ります。
 * 現在Python側が出力する値は次の4種類です。
 * - new_repository
 * - increased_keyword_hits
 * - top_star_growth
 * - multiple_keyword_matches
 *
 * 将来Python側で理由が追加されてもUIが壊れないよう、string[]として扱います。
 */
export type SignalCandidate = {
  name: string;
  url: string;
  previous_stars: number;
  current_stars: number;
  star_growth: number;
  previous_hits: number;
  current_hits: number;
  hit_change: number;
  is_new: boolean;
  star_growth_per_hour: number;
  selection_reasons: string[];
};

/** storage.py の save_signal_candidates が保存するSignal JSON全体 */
export type SignalData = {
  theme: string;
  period: SignalPeriod;
  candidates: SignalCandidate[];
};

/**
 * Recent Activity表示用に、Snapshotファイルの概要だけをまとめたもの。
 *
 * Repository一覧そのものは表示に使わないため、件数だけを持たせています。
 */
export type SnapshotSummary = {
  fileName: string;
  collectedAt: string;
  repositoryCount: number;
};

/**
 * report.py が保存するDaily Report(Markdown)1件分。
 *
 * generatedAtはファイル名のタイムスタンプから取り出した生成日時。
 * ファイル名が想定の形式でなかった場合はnullになる。
 */
export type DailyReport = {
  fileName: string;
  theme: string;
  generatedAt: string | null;
  content: string;
};
