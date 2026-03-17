"use client";

import Link from "next/link";
import { useState } from "react";
import Navigation from "./Navigation";

/**
 * Cabeçalho global com logo e navegação.
 * Desktop: links horizontais inline.
 * Mobile: botão hamburger abre menu vertical.
 */
const Header = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-white">
      <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <Link
            href="/"
            className="font-serif text-lg font-bold text-primary hover:text-accent transition-colors"
          >
            100k Pedidos
          </Link>

          {/* Desktop nav */}
          <div className="hidden sm:block">
            <Navigation />
          </div>

          {/* Mobile hamburger */}
          <button
            className="sm:hidden p-2 text-muted hover:text-foreground transition-colors"
            onClick={() => setMenuOpen((v) => !v)}
            aria-label={menuOpen ? "Fechar menu" : "Abrir menu"}
            aria-expanded={menuOpen}
          >
            <span className="block w-5 h-0.5 bg-current mb-1" />
            <span className="block w-5 h-0.5 bg-current mb-1" />
            <span className="block w-5 h-0.5 bg-current" />
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="sm:hidden pb-3">
            <Navigation />
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
