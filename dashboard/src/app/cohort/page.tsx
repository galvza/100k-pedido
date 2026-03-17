import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Análise de Cohort",
};

export default function CohortPage() {
  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <h1 className="font-serif text-3xl font-bold">Análise de Cohort</h1>
    </main>
  );
}
