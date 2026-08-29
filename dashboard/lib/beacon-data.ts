/**
 * Beaconのデータ読み込み層。
 *
 * 【重要】このファイルはDashboardの公開用データ(dashboard/data/)への
 * 唯一の窓口です。
 *
 * - 先頭の`import "server-only"`により、Client Componentから読み込むと
 *   ビルドが失敗します。ファイルシステムへのアクセスがブラウザ側へ
 *   漏れることを、仕組みとして防いでいます。
 * - 読み込むのはpublish_dashboard.py(Python)がコピーした公開用データ
 *   (dashboard/data/)だけです。Pythonの内部生成物置き場である
 *   リポジトリ直下のdata/は直接読みません。.envやAPIキーもここでは
 *   一切読み込みません。
 * - ファイル名はすべて固定(latest_snapshot.json等)です。ディレクトリを
 *   一覧して最新ファイルを探す処理(fs.readdir)を行わないため、パスが
 *   ビルド時に静的解決でき、ファイルトレーサーの警告が発生しません。
 * - すべての関数をasyncにしています。将来この中身をAPIやDBへの問い合わせに
 *   差し替えても、呼び出し側のコンポーネントを修正せずに済むためです。
 */

import "server-only";

import { promises as fs } from "node:fs";
import path from "node:path";

import type {
  DailyReport,
  SignalData,
  Snapshot,
  SnapshotSummary,
} from "./types";

/** 公開用データの置き場所。dashboard/data/ 固定。 */
const PUBLISHED_DATA_DIRECTORY = path.join(process.cwd(), "data");

const SNAPSHOT_FILE_NAME = "latest_snapshot.json";
const SIGNAL_FILE_NAME = "latest_signal.json";
const REPORT_FILE_NAME = "latest_report.md";
const META_FILE_NAME = "latest_meta.json";
const HISTORY_FILE_NAME = "snapshot_history.json";

/** publish_dashboard.pyが書き出す、latest_meta.jsonの型。 */
type PublishedMeta = {
  theme: string;
  published_at: string;
  snapshot_file: string | null;
  signal_file: string | null;
  report_file: string | null;
};

/**
 * publish_dashboard.pyが書き出す、snapshot_history.jsonの要素1件分の型。
 *
 * 全Snapshot履歴ではなく、直近分だけがこの配列に入っている。
 */
type PublishedSnapshotHistoryEntry = {
  file_name: string;
  collected_at: string;
  repository_count: number;
};

/** ファイルやディレクトリが存在しないエラーかどうかを判定する。 */
function isNotFoundError(error: unknown): boolean {
  return (
    typeof error === "object" &&
    error !== null &&
    (error as { code?: string }).code === "ENOENT"
  );
}

/** JSONファイルを読み込む。ファイルが無ければnullを返す。 */
async function readJsonFileIfExists<T>(filePath: string): Promise<T | null> {
  try {
    const fileText = await fs.readFile(filePath, "utf-8");

    return JSON.parse(fileText) as T;
  } catch (error) {
    if (isNotFoundError(error)) {
      return null;
    }

    throw error;
  }
}

/** テキストファイルを読み込む。ファイルが無ければnullを返す。 */
async function readTextFileIfExists(filePath: string): Promise<string | null> {
  try {
    return await fs.readFile(filePath, "utf-8");
  } catch (error) {
    if (isNotFoundError(error)) {
      return null;
    }

    throw error;
  }
}

/**
 * ファイル名の末尾にあるタイムスタンプから、生成日時を取り出す。
 *
 * 例: "report_AI_Agent_2026-08-16_191234.md" -> "2026-08-16 19:12:34"
 *
 * publish_dashboard.pyがlatest_meta.jsonに記録した「コピー元の元ファイル名」
 * に対して使う(コピー先のファイル名は固定でタイムスタンプを含まないため)。
 * 想定の形式でなければnullを返し、エラーにはしない。
 */
function extractTimestampFromFileName(fileName: string): string | null {
  const matched = fileName.match(/_(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})(\d{2})\./);

  if (!matched) {
    return null;
  }

  const [, date, hour, minute, second] = matched;

  return `${date} ${hour}:${minute}:${second}`;
}

/**
 * 最新のSignal JSONを読み込む。
 *
 * まだ公開されていない場合はnullを返します(エラーにはしません)。
 */
export async function getLatestSignals(): Promise<SignalData | null> {
  return readJsonFileIfExists<SignalData>(
    path.join(PUBLISHED_DATA_DIRECTORY, SIGNAL_FILE_NAME),
  );
}

/**
 * 最新のSnapshotを読み込む。
 *
 * まだ公開されていない場合はnullを返します。
 */
export async function getLatestSnapshot(): Promise<Snapshot | null> {
  return readJsonFileIfExists<Snapshot>(
    path.join(PUBLISHED_DATA_DIRECTORY, SNAPSHOT_FILE_NAME),
  );
}

/**
 * Snapshotの履歴を返す。
 *
 * publish_dashboard.pyが書き出したsnapshot_history.json(直近分の要約のみ)
 * をそのまま読むだけで、UI側での再計算は行いません。全Snapshot履歴は
 * 公開されていないため、ここで取得できるのも直近分だけです。
 */
export async function getSnapshotHistory(
  limit: number,
): Promise<SnapshotSummary[]> {
  const entries = await readJsonFileIfExists<PublishedSnapshotHistoryEntry[]>(
    path.join(PUBLISHED_DATA_DIRECTORY, HISTORY_FILE_NAME),
  );

  if (!entries) {
    return [];
  }

  return entries.slice(0, limit).map((entry) => ({
    fileName: entry.file_name,
    collectedAt: entry.collected_at,
    repositoryCount: entry.repository_count,
  }));
}

/**
 * 最新のDaily Report(Markdown)を読み込む。
 *
 * 公開用データがまだ無い場合もnullを返すだけで、エラーにはしません。
 */
export async function getLatestReport(
  theme: string,
): Promise<DailyReport | null> {
  const [content, meta] = await Promise.all([
    readTextFileIfExists(path.join(PUBLISHED_DATA_DIRECTORY, REPORT_FILE_NAME)),
    readJsonFileIfExists<PublishedMeta>(
      path.join(PUBLISHED_DATA_DIRECTORY, META_FILE_NAME),
    ),
  ]);

  if (content === null) {
    return null;
  }

  const originalFileName = meta?.report_file ?? REPORT_FILE_NAME;

  return {
    fileName: originalFileName,
    theme,
    generatedAt: extractTimestampFromFileName(originalFileName),
    content,
  };
}
