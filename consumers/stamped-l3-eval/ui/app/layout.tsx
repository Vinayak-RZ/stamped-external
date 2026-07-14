import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stamped L3 Eval Lab",
  description: "Internal forensic lab for L3 engines, rules, and ML shadow",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
