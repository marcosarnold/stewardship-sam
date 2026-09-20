import type { Metadata } from "next";
import AskSam from "./AskSam";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stewardship Sam",
  description: "Where should I spend Tuesday?",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>
        {children}
        <AskSam />
      </body>
    </html>
  );
}
