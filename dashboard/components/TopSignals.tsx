import {
  formatNumber,
  formatPerHour,
  formatSelectionReason,
  formatSignedNumber,
} from "@/lib/format";
import type { SignalCandidate, SignalData } from "@/lib/types";

/** signal_extraction.py が「Star増加が上位」と判定した理由の名前 */
const TOP_STAR_GROWTH_REASON = "top_star_growth";

type TopSignalsProps = {
  signals: SignalData | null;
};

/**
 * Star増加が上位の候補だけを取り出し、増加数の多い順に並べる。
 *
 * どの候補が上位かの判定はPython側が済ませており(selection_reasons)、
 * UIはその結果を絞り込んで並べ替えるだけです。UIで順位を計算し直したり、
 * 独自のスコアを付けたりはしません。
 */
function selectTopStarGrowth(candidates: SignalCandidate[]): SignalCandidate[] {
  const topCandidates = candidates.filter((candidate) =>
    candidate.selection_reasons.includes(TOP_STAR_GROWTH_REASON),
  );

  return topCandidates.toSorted(
    (left, right) => right.star_growth - left.star_growth,
  );
}

/** Star増加が上位のRepository一覧。件数が多いためグラフではなく表で示す。 */
export default function TopSignals({ signals }: TopSignalsProps) {
  const topCandidates = signals ? selectTopStarGrowth(signals.candidates) : [];

  return (
    <section className="panel">
      <div className="panel-header">
        <h2 className="panel-title">Top Signals</h2>
        <p className="panel-subtitle">
          signal_extraction.pyが Star増加 上位 と判定した候補
        </p>
      </div>

      {topCandidates.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">該当する候補がありません</p>
          <p className="empty-state-detail">
            Star増加が確認できるSnapshotが2件以上必要です。
          </p>
        </div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th scope="col">Repository</th>
              <th scope="col" className="numeric">
                Star増加
              </th>
              <th scope="col" className="numeric">
                現在のStar
              </th>
              <th scope="col" className="numeric">
                Star/時
              </th>
              <th scope="col">選定理由</th>
            </tr>
          </thead>
          <tbody>
            {topCandidates.map((candidate) => (
              <tr key={candidate.name}>
                <td>
                  <a
                    className="repository-name"
                    href={candidate.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {candidate.name}
                  </a>
                </td>
                <td className="numeric growth-positive">
                  {formatSignedNumber(candidate.star_growth)}
                </td>
                <td className="numeric">
                  {formatNumber(candidate.current_stars)}
                </td>
                <td className="numeric">
                  {formatPerHour(candidate.star_growth_per_hour)}
                </td>
                <td>
                  <div className="badge-list">
                    {candidate.selection_reasons.map((reason) => (
                      <span
                        key={reason}
                        className={
                          reason === "new_repository" ? "badge badge-new" : "badge"
                        }
                      >
                        {formatSelectionReason(reason)}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
