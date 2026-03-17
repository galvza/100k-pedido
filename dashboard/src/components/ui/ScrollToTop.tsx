"use client";

import { useState, useEffect } from "react";

/**
 * Botão fixo de "voltar ao topo". Aparece após 300px de scroll,
 * some ao chegar no topo. Posicionado no canto inferior direito.
 */
export default function ScrollToTop() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 300);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <button
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      aria-label="Voltar ao topo"
      className={[
        "fixed bottom-6 right-4 sm:bottom-8 sm:right-8 z-50",
        "w-10 h-10 rounded-full flex items-center justify-center",
        "bg-gray-800/70 text-white hover:bg-gray-800/90 transition-all duration-300",
        visible ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none",
      ].join(" ")}
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M8 12V4M8 4L4 8M8 4L12 8"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </button>
  );
}
