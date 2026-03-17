import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Playfair_Display } from "next/font/google";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: {
    default: "100k Pedidos — Raio-X do E-commerce Brasileiro",
    template: "%s | 100k Pedidos",
  },
  description:
    "Dashboard analítico com 100 mil pedidos do marketplace Olist. Pipeline completo: SQL analítico (DuckDB) → estatística e ML (Python) → visualização interativa (Next.js).",
  keywords: [
    "e-commerce",
    "análise de dados",
    "olist",
    "marketplace",
    "brasil",
    "dashboard",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className={`${inter.variable} ${playfair.variable}`}>
      <body className="antialiased">
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
