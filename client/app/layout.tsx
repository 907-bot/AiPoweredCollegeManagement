import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./styles/globals.css";
import { AppLayout } from "@/components/layout/layout";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SecureExam Pro",
  description: "Enterprise AI-Powered Secure Online Exam Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}