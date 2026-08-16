import { formatTimestamp } from "@/lib/format";

type BeaconHeaderProps = {
  theme: string;
  latestCollectedAt: string | null;
};

/** Dashboard上部のヘッダー。監視テーマと最終収集時刻を示す。 */
export default function BeaconHeader({
  theme,
  latestCollectedAt,
}: BeaconHeaderProps) {
  return (
    <header className="beacon-header">
      <div>
        <div className="beacon-wordmark">
          <span className="beacon-mark" aria-hidden="true" />
          <h1 className="beacon-title">BEACON</h1>
        </div>
        <p className="beacon-tagline">
          Don&apos;t predict the future. Detect the signals.
        </p>
      </div>

      <div className="beacon-meta">
        <div className="beacon-meta-item">
          <span className="beacon-meta-label">Theme</span>
          <span className="theme-chip">{theme}</span>
        </div>
        <div className="beacon-meta-item">
          <span className="beacon-meta-label">Last collected</span>
          <span className="beacon-meta-value">
            {latestCollectedAt ? formatTimestamp(latestCollectedAt) : "-"}
          </span>
        </div>
        <div className="beacon-meta-item">
          <span className="beacon-meta-label">Source</span>
          <span className="beacon-meta-value">GitHub</span>
        </div>
      </div>
    </header>
  );
}
