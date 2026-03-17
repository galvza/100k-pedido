import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Reviews e Satisfação",
};

export default function ReviewsPage() {
  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <h1 className="font-serif text-3xl font-bold">Reviews e Satisfação</h1>
    </main>
  );
}
