import { formatNumber, formatTimestamp } from "@/lib/format";
import type { SnapshotSummary } from "@/lib/types";

type RecentActivityProps = {
  snapshots: SnapshotSummary[];
};

/** Snapshotの収集履歴。新しい順に並べる。 */
export default function RecentActivity({ snapshots }: RecentActivityProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2 className="panel-title">Recent Activity</h2>
        <p className="panel-subtitle">Snapshotの収集履歴</p>
      </div>

      {snapshots.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">Snapshotがまだありません</p>
          <p className="empty-state-detail">
            <span className="code-path">python main.py</span>{" "}
            を実行すると履歴が表示されます。
          </p>
        </div>
      ) : (
        <ul className="activity-list">
          {snapshots.map((snapshot, index) => (
            <li className="activity-item" key={snapshot.fileName}>
              <span className="activity-time">
                {formatTimestamp(snapshot.collectedAt)}
                {index === 0 ? <span className="latest-tag">LATEST</span> : null}
              </span>
              <span className="activity-count">
                {formatNumber(snapshot.repositoryCount)} repositories
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
