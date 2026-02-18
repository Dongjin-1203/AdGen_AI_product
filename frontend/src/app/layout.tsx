import type { Metadata } from "next";
import "./globals.css";
import ConditionalNavbar from "@/components/ConditionalNavbar";

export const metadata: Metadata = {
  title: "AdGen AI - AI 광고 생성",
  description: "AI로 자동으로 광고 이미지를 생성하세요",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="antialiased">
        <ConditionalNavbar />  
        {children}
      </body>
    </html>
  );
}