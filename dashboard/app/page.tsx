import BeaconHeader from "@/components/BeaconHeader";
import DailyReport from "@/components/DailyReport";
import RecentActivity from "@/components/RecentActivity";
import TodaysSignals from "@/components/TodaysSignals";
import TopSignals from "@/components/TopSignals";
import {
  getLatestReport,
  getLatestSignals,
  getLatestSnapshot,
  getSnapshotHistory,
} from "@/lib/beacon-data";
import { MONITORED_THEME, RECENT_ACTIVITY_LIMIT } from "@/lib/config";

/*
 * 毎回のアクセス時にdata/を読み直す設定。
 *
 * これを付けないとページがビルド時に固定されてしまい、
 * main.pyを実行してSnapshotが増えても画面が更新されません。
 */
export const dynamic = "force-dynamic";

/**
 * Beacon Dashboardの画面。
 *
 * このページはServer Componentです。data/の読み込みはサーバー側でのみ行われ、
 * ブラウザへはHTMLだけが送られます。
 */
export default async function DashboardPage() {
  const [signals, latestSnapshot, snapshots, report] = await Promise.all([
    getLatestSignals(MONITORED_THEME),
    getLatestSnapshot(MONITORED_THEME),
    getSnapshotHistory(MONITORED_THEME, RECENT_ACTIVITY_LIMIT),
    getLatestReport(MONITORED_THEME),
  ]);

  return (
    <main className="dashboard">
      <BeaconHeader
        theme={MONITORED_THEME}
        latestCollectedAt={latestSnapshot?.collected_at ?? null}
      />

      <TodaysSignals
        signals={signals}
        trackedRepositoryCount={latestSnapshot?.repositories.length ?? null}
      />

      <div className="dashboard-columns">
        <TopSignals signals={signals} />
        <RecentActivity snapshots={snapshots} />
      </div>

      <DailyReport report={report} />
    </main>
  );
}
