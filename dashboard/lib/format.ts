/**
 * 表示用の書式変換だけを行う関数群。
 *
 * ここでは値の計算や判断は行いません。Pythonが出力した値を、
 * 読みやすい形に整えるだけです。
 */

/**
 * Pythonが出力したISO形式の日時を、そのまま読める形にする。
 *
 * 例: "2026-08-16T18:11:39" -> "2026-08-16 18:11:39"
 *
 * タイムゾーン変換は意図的に行いません。Python側が記録した時刻と
 * 画面の表示を必ず一致させるためです。
 */
export function formatTimestamp(isoText: string): string {
  return isoText.replace("T", " ");
}

/** 3桁区切りの数値にする。例: 144316 -> "144,316" */
export function formatNumber(value: number): string {
  return value.toLocaleString("en-US");
}

/** 増減が分かるよう符号を必ず付ける。例: 187 -> "+187" */
export function formatSignedNumber(value: number): string {
  if (value > 0) {
    return `+${formatNumber(value)}`;
  }

  return formatNumber(value);
}

/** 経過時間を小数第1位までにする。例: 235.26777 -> "235.3" */
export function formatHours(hours: number): string {
  return hours.toFixed(1);
}

/** 1時間あたりのStar増加数を小数第2位までにする。例: 0.79483 -> "0.79" */
export function formatPerHour(value: number): string {
  return value.toFixed(2);
}

/**
 * signal_extraction.py が出力する選定理由を、日本語のラベルにする。
 *
 * Python側で理由が追加された場合は、変換せずそのまま表示します。
 */
const SELECTION_REASON_LABELS: Record<string, string> = {
  new_repository: "新規",
  increased_keyword_hits: "キーワード増加",
  top_star_growth: "Star増加 上位",
  multiple_keyword_matches: "複数キーワード一致",
};

export function formatSelectionReason(reason: string): string {
  return SELECTION_REASON_LABELS[reason] ?? reason;
}
