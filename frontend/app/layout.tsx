import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stewardship Sam",
  description: "Where should I spend Tuesday?",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
