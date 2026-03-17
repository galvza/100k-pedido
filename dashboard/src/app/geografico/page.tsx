import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Análise Geográfica",
};

export default function GeograficoPage() {
  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <h1 className="font-serif text-3xl font-bold">Análise Geográfica</h1>
    </main>
  );
}
