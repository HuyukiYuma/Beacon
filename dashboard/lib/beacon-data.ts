/**
 * Beaconのデータ読み込み層。
 *
 * 【重要】このファイルはBeaconのdata/ディレクトリへ触る唯一の窓口です。
 *
 * - 先頭の`import "server-only"`により、Client Componentから読み込むと
 *   ビルドが失敗します。ファイルシステムへのアクセスがブラウザ側へ
 *   漏れることを、仕組みとして防いでいます。
 * - 読み込むのはPythonが生成した表示用データ(Snapshot / Signal / Report)だけです。
 *   .envやAPIキーはここでは一切読み込みません。
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

/**
 * data/ディレクトリの場所を決める。
 *
 * 通常はdashboard/の1つ上の階層にあるdata/を見ます。
 * BEACON_DATA_DIRを設定した場合はそちらを優先します(秘密情報ではありません)。
 */
function resolveDataDirectory(): string {
  const configuredDirectory = process.env.BEACON_DATA_DIR;

  if (configuredDirectory) {
    return path.resolve(configuredDirectory);
  }

  return path.resolve(process.cwd(), "..", "data");
}

/** storage.py の _safe_theme_name と同じ変換を行う。 */
function toSafeThemeName(theme: string): string {
  return theme.replaceAll(" ", "_");
}

/** ファイルやディレクトリが存在しないエラーかどうかを判定する。 */
function isNotFoundError(error: unknown): boolean {
  return (
    typeof error === "object" &&
    error !== null &&
    (error as { code?: string }).code === "ENOENT"
  );
}

/**
 * 指定ディレクトリから、条件に合うファイル名を古い順に並べて返す。
 *
 * Beaconのファイル名は`YYYY-MM-DD_HHMMSS`形式なので、
 * 文字列として並べ替えるだけで時系列順になります。
 * (storage.py の find_snapshot_files と同じ考え方)
 */
async function listFileNames(
  directory: string,
  prefix: string,
  extension: string,
): Promise<string[]> {
  let entries: string[];

  try {
    entries = await fs.readdir(directory);
  } catch (error) {
    // ディレクトリが未作成の場合だけ「0件」として扱う。
    // それ以外のエラーは握りつぶさず、そのまま呼び出し元へ伝える。
    if (isNotFoundError(error)) {
      return [];
    }

    throw error;
  }

  const matchedFileNames = entries.filter(
    (fileName) => fileName.startsWith(prefix) && fileName.endsWith(extension),
  );

  return matchedFileNames.sort();
}

/** JSONファイルを読み込む。 */
async function readJsonFile<T>(filePath: string): Promise<T> {
  const fileText = await fs.readFile(filePath, "utf-8");

  return JSON.parse(fileText) as T;
}

/**
 * 最新のSignal JSONを読み込む。
 *
 * まだSignalが1件も無い場合はnullを返します(エラーにはしません)。
 */
export async function getLatestSignals(
  theme: string,
): Promise<SignalData | null> {
  const signalsDirectory = path.join(resolveDataDirectory(), "signals");
  const prefix = `signals_${toSafeThemeName(theme)}_`;

  const fileNames = await listFileNames(signalsDirectory, prefix, ".json");
  const latestFileName = fileNames.at(-1);

  if (!latestFileName) {
    return null;
  }

  return readJsonFile<SignalData>(path.join(signalsDirectory, latestFileName));
}

/**
 * 最新のSnapshotを読み込む。
 *
 * まだSnapshotが1件も無い場合はnullを返します。
 */
export async function getLatestSnapshot(
  theme: string,
): Promise<Snapshot | null> {
  const dataDirectory = resolveDataDirectory();
  const prefix = `github_${toSafeThemeName(theme)}_`;

  const fileNames = await listFileNames(dataDirectory, prefix, ".json");
  const latestFileName = fileNames.at(-1);

  if (!latestFileName) {
    return null;
  }

  return readJsonFile<Snapshot>(path.join(dataDirectory, latestFileName));
}

/**
 * Snapshotの履歴を新しい順に返す。
 *
 * 全件読み込むと重くなるため、limit件だけを対象にします。
 */
export async function getSnapshotHistory(
  theme: string,
  limit: number,
): Promise<SnapshotSummary[]> {
  const dataDirectory = resolveDataDirectory();
  const prefix = `github_${toSafeThemeName(theme)}_`;

  const fileNames = await listFileNames(dataDirectory, prefix, ".json");
  const newestFirstFileNames = fileNames.reverse().slice(0, limit);

  const summaries: SnapshotSummary[] = [];

  for (const fileName of newestFirstFileNames) {
    const snapshot = await readJsonFile<Snapshot>(
      path.join(dataDirectory, fileName),
    );

    summaries.push({
      fileName,
      collectedAt: snapshot.collected_at,
      repositoryCount: snapshot.repositories.length,
    });
  }

  return summaries;
}

/**
 * 最新のDaily Report(Markdown)を読み込む。
 *
 * data/reports/がまだ存在しない場合もnullを返すだけで、エラーにはしません。
 */
export async function getLatestReport(
  theme: string,
): Promise<DailyReport | null> {
  const reportsDirectory = path.join(resolveDataDirectory(), "reports");
  const prefix = `report_${toSafeThemeName(theme)}_`;

  const fileNames = await listFileNames(reportsDirectory, prefix, ".md");
  const latestFileName = fileNames.at(-1);

  if (!latestFileName) {
    return null;
  }

  const content = await fs.readFile(
    path.join(reportsDirectory, latestFileName),
    "utf-8",
  );

  return { fileName: latestFileName, content };
}
