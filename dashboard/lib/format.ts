/**
 * 表示用の書式変換だけを行う関数群。
 *
 * ここでは値の計算や判断は行いません。Pythonが出力した値を、
 * 読みやすい形に整えるだけです。
 */

/**
 * Dashboardで時刻を表示するタイムゾーン。
 *
 * 内部データ(collected_at等)はUTCのまま保持し、表示時にのみここへ変換する。
 * IANA timezone名を使うことでAEST/AEDT(DST)へ自動追従し、UTC+10/+11の
 * ハードコードを避けている。
 */
const DISPLAY_TIME_ZONE = "Australia/Sydney";

const displayDateTimeFormatter = new Intl.DateTimeFormat("en-CA", {
  timeZone: DISPLAY_TIME_ZONE,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

const displayTimeZoneNameFormatter = new Intl.DateTimeFormat("en-AU", {
  timeZone: DISPLAY_TIME_ZONE,
  timeZoneName: "short",
});

/** ISO文字列にタイムゾーンオフセット(Zまたは+HH:MM)が含まれているかどうか。 */
function hasTimeZoneOffset(isoText: string): boolean {
  return /[Zz]|[+-]\d{2}:?\d{2}$/.test(isoText);
}

/**
 * Pythonが出力したISO形式の日時(UTC、オフセット無し)を、
 * Australia/Sydneyのローカル時刻へ変換して読める形にする。
 *
 * 例: "2026-09-04T22:01:52" -> "2026-09-05 08:01:52 AEST"
 *
 * Python側のcollected_atはオフセット無しのISO文字列(内部はUTCで統一)なので、
 * 明示的にUTCとして解釈してから変換する。すでにオフセットが付与されている
 * 文字列(将来Python側が変更された場合)はそのまま解釈する。
 */
export function formatTimestamp(isoText: string): string {
  const parsedDate = new Date(
    hasTimeZoneOffset(isoText) ? isoText : `${isoText}Z`,
  );

  const dateTimeParts = displayDateTimeFormatter.formatToParts(parsedDate);
  const getPart = (type: string): string =>
    dateTimeParts.find((part) => part.type === type)?.value ?? "";

  const datePart = `${getPart("year")}-${getPart("month")}-${getPart("day")}`;
  const timePart = `${getPart("hour")}:${getPart("minute")}:${getPart("second")}`;

  const zoneName =
    displayTimeZoneNameFormatter
      .formatToParts(parsedDate)
      .find((part) => part.type === "timeZoneName")?.value ?? "";

  return `${datePart} ${timePart} ${zoneName}`;
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
