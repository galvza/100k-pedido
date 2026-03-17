"use client";

import { useEffect, useState } from "react";
import { loadChapterData } from "@/lib/data";
import type { ReviewsPalavras } from "@/types";

interface WordListProps {
  faixa: "positiva" | "negativa";
  label: string;
  color: string;
}

/**
 * Lista de palavras frequentes carregada do JSON gerado pelo pipeline.
 * Exibe barras horizontais proporcionais à contagem de cada palavra.
 */
export default function WordList({ faixa, label, color }: WordListProps) {
  const [words, setWords] = useState<ReviewsPalavras[] | null>(null);

  useEffect(() => {
    loadChapterData<ReviewsPalavras[]>("06_reviews_palavras.json").then(
      (data) => {
        const filtered = data.filter((d) => d.faixa === faixa);
        setWords(filtered);
      }
    );
  }, [faixa]);

  if (words === null) {
    return (
      <div className="h-48 bg-secondary animate-pulse rounded" />
    );
  }

  if (!words.length) {
    return <p className="text-muted text-sm">Sem dados disponíveis.</p>;
  }

  const max = words[0].contagem;

  return (
    <div>
      <p className={`font-sans text-xs font-semibold uppercase tracking-wide mb-3 ${color}`}>
        {label}
      </p>
      <ul className="space-y-1.5">
        {words.map(({ palavra, contagem }) => (
          <li key={palavra} className="flex items-center gap-2">
            <span className="font-sans text-xs text-foreground w-24 shrink-0">{palavra}</span>
            <div className="flex-1 bg-secondary rounded-full h-2 overflow-hidden">
              <div
                className={`h-full rounded-full ${faixa === "positiva" ? "bg-emerald-500" : "bg-red-400"}`}
                style={{ width: `${(contagem / max) * 100}%` }}
              />
            </div>
            <span className="font-sans text-xs text-muted tabular-nums w-14 text-right shrink-0">
              {contagem.toLocaleString("pt-BR")}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
