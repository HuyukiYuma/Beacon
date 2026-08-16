import Markdown from "react-markdown";

import type { DailyReport as DailyReportData } from "@/lib/types";

type DailyReportProps = {
  report: DailyReportData | null;
};

/**
 * AIが生成したDaily Report。
 *
 * Markdownはreact-markdownで表示する。
 * react-markdownは既定で生HTMLを無視するため、AIの出力にHTMLタグが
 * 混ざっていてもそのまま実行されることはない。
 * （dangerouslySetInnerHTMLもrehype-rawも使わない）
 */
export default function DailyReport({ report }: DailyReportProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2 className="panel-title">Daily Report</h2>
        <p className="panel-subtitle">
          {report ? "AI分析によるレポート" : "AI分析によるレポート（未生成）"}
        </p>
      </div>

      {report ? (
        <>
          <div className="report-meta">
            <div className="report-meta-item">
              <span className="report-meta-label">Theme</span>
              <span className="report-meta-value">{report.theme}</span>
            </div>
            <div className="report-meta-item">
              <span className="report-meta-label">Generated at</span>
              <span className="report-meta-value">
                {report.generatedAt ?? "-"}
              </span>
            </div>
            <div className="report-meta-item">
              <span className="report-meta-label">Source file</span>
              <span className="report-meta-value">{report.fileName}</span>
            </div>
          </div>

          <div className="report-body">
            <Markdown>{report.content}</Markdown>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <p className="empty-state-title">レポートはまだ生成されていません</p>
          <p className="empty-state-detail">
            <span className="code-path">BEACON_AI_ANALYSIS=1</span>{" "}
            を設定して{" "}
            <span className="code-path">python main.py</span>{" "}
            を実行すると、AI分析によるレポートが生成されます。
          </p>
        </div>
      )}
    </section>
  );
}
