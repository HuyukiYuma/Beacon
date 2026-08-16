import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Beacon Dashboard",
  description: "Beacon detects early signals of emerging technologies.",
};

/*
 * フォントは端末標準のものを使います。
 * 外部フォントを読み込まないことで、オフラインでもDashboardが開けます。
 */
export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
