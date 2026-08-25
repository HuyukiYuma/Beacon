import {
  formatNumber,
  formatSelectionReason,
  formatSignedNumber,
} from "@/lib/format";
import type { SignalData } from "@/lib/types";

type AllCandidatesProps = {
  signals: SignalData | null;
};

/**
 * signal_extraction.py が抽出した候補の全件一覧。
 *
 * Top Signalsはtop_star_growthの候補だけを表示するため、
 * new_repositoryなど他の理由だけで選ばれた候補はTop Signalsには現れない。
 * このパネルはcandidatesを絞り込まずそのまま表示し、
 * どの候補がどの理由で選ばれたのかをユーザーが辿れるようにする。
 *
 * 並び順はSignal JSONのcandidates配列の順番そのまま。
 * UI側で新しい順位付けやスコアリングは行わない。
 */
export default function AllCandidates({ signals }: AllCandidatesProps) {
  const candidates = signals?.candidates ?? [];

  return (
    <section className="panel">
      <div className="panel-header">
        <h2 className="panel-title">All Signal Candidates</h2>
        <p className="panel-subtitle">
          signal_extraction.pyが選定した候補の全件(Signal JSONの並び順のまま)
        </p>
      </div>

      {candidates.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">該当する候補がありません</p>
          <p className="empty-state-detail">
            Signal Extractionの結果が無いか、候補が0件でした。
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
                現在のHits
              </th>
              <th scope="col">選定理由</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((candidate) => (
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
                <td
                  className={
                    candidate.star_growth > 0
                      ? "numeric growth-positive"
                      : "numeric"
                  }
                >
                  {formatSignedNumber(candidate.star_growth)}
                </td>
                <td className="numeric">
                  {formatNumber(candidate.current_stars)}
                </td>
                <td className="numeric">
                  {formatNumber(candidate.current_hits)}
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
