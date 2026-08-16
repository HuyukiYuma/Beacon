import type { DailyReport as DailyReportData } from "@/lib/types";

type DailyReportProps = {
  report: DailyReportData | null;
};

/**
 * AIが生成したDaily Report。
 *
 * 現時点ではPython側のレポート生成がmain.pyへ配線されていないため、
 * data/reports/にファイルがなく、空状態を表示します。
 * Markdownの整形表示はレポートが生成できるようになってから対応します。
 */
export default function DailyReport({ report }: DailyReportProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2 className="panel-title">Daily Report</h2>
        <p className="panel-subtitle">
          {report ? report.fileName : "AI分析によるレポート"}
        </p>
      </div>

      {report ? (
        <pre className="report-body">{report.content}</pre>
      ) : (
        <div className="empty-state">
          <p className="empty-state-title">レポートはまだ生成されていません</p>
          <p className="empty-state-detail">
            <span className="code-path">data/reports/</span>{" "}
            にMarkdownファイルが保存されると、ここに表示されます。
          </p>
        </div>
      )}
    </section>
  );
}
