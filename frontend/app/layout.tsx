import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Merchant-to-Agent Commerce Gateway",
  description: "Permissioned AI-powered commerce gateway",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}