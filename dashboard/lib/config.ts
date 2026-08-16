/**
 * Dashboardの表示設定。
 *
 * themes.py と同じ考え方で、設定値をロジックから切り離しています。
 */

/** 現在Dashboardが表示する監視テーマ。将来はテーマ切替に対応する予定。 */
export const MONITORED_THEME = "AI Agent";

/** Recent Activityに表示するSnapshotの最大件数 */
export const RECENT_ACTIVITY_LIMIT = 8;
