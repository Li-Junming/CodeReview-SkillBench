import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CodeReview SkillBench",
  description: "Evidence-backed evaluation for Code Review Agent Skills",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}

