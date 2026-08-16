import { formatHours, formatNumber, formatTimestamp } from "@/lib/format";
import type { SignalData } from "@/lib/types";

type TodaysSignalsProps = {
  signals: SignalData | null;
  trackedRepositoryCount: number | null;
};

type StatTileProps = {
  label: string;
  value: string;
  unit?: string;
  note?: string;
};

/** 数値1つを見せるためのタイル。グラフにはしない。 */
function StatTile({ label, value, unit, note }: StatTileProps) {
  return (
    <div className="stat-tile">
      <div className="stat-label">{label}</div>
      <div className="stat-value">
        {value}
        {unit ? <span className="stat-unit">{unit}</span> : null}
      </div>
      {note ? <div className="stat-note">{note}</div> : null}
    </div>
  );
}

/**
 * 最新のSignal Extraction結果の要約。
 *
 * 表示している数値は、すべてPythonが出力したSignal JSONの値そのものです。
 */
export default function TodaysSignals({
  signals,
  trackedRepositoryCount,
}: TodaysSignalsProps) {
  if (!signals) {
    return (
      <section className="panel">
        <div className="panel-header">
          <h2 className="panel-title">Today&apos;s Signals</h2>
        </div>
        <div className="empty-state">
          <p className="empty-state-title">Signalがまだありません</p>
          <p className="empty-state-detail">
            <span className="code-path">python main.py</span>{" "}
            を2回以上実行すると、Signal Extractionの結果が表示されます。
          </p>
        </div>
      </section>
    );
  }

  // Pythonが新規と判定した候補の件数を数える(判定はしない)
  const newRepositoryCount = signals.candidates.filter(
    (candidate) => candidate.is_new,
  ).length;

  return (
    <section>
      <div className="panel-header">
        <h2 className="panel-title">Today&apos;s Signals</h2>
        <p className="panel-subtitle">
          観測期間 {formatTimestamp(signals.period.previous)} →{" "}
          {formatTimestamp(signals.period.current)}
        </p>
      </div>

      <div className="stat-row">
        <StatTile
          label="Signal候補"
          value={formatNumber(signals.candidates.length)}
          unit="件"
          note="signal_extraction.pyが選定"
        />
        <StatTile
          label="新規Repository"
          value={formatNumber(newRepositoryCount)}
          unit="件"
          note="前回のSnapshotに無かったもの"
        />
        <StatTile
          label="観測期間"
          value={formatHours(signals.period.elapsed_hours)}
          unit="時間"
          note="前回収集からの経過時間"
        />
        <StatTile
          label="追跡Repository"
          value={
            trackedRepositoryCount === null
              ? "-"
              : formatNumber(trackedRepositoryCount)
          }
          unit="件"
          note="最新Snapshotの収録件数"
        />
      </div>
    </section>
  );
}
