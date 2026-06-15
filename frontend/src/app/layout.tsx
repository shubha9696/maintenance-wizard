import type { Metadata } from "next";
import "./globals.css";
import FloatingAIButton from "@/components/FloatingAIButton";

export const metadata: Metadata = {
  title: "Maintenance Wizard | AI-Powered Industrial Equipment Management",
  description: "Intelligent maintenance decision-support system for steel manufacturing equipment. Diagnose issues, predict failures, and optimize maintenance with AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body>
        <div className="tata-bg-logo" />
        {children}
        <FloatingAIButton />
      </body>
    </html>
  );
}
