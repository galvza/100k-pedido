"use client";

import Link from "next/link";
import { useState, useEffect, useRef } from "react";
import Navigation from "./Navigation";

/**
 * Cabeçalho global com logo e navegação.
 * Desktop: links horizontais inline.
 * Mobile: botão hamburger abre menu vertical.
 */
const Header = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const headerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!menuOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (headerRef.current && !headerRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [menuOpen]);

  return (
    <header ref={headerRef} className="sticky top-0 z-40 border-b border-border bg-white">
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
          <div className="hidden md:block">
            <Navigation />
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden p-2 min-h-[44px] min-w-[44px] flex items-center justify-center rounded-md text-muted hover:text-foreground transition-colors"
            onClick={() => setMenuOpen((v) => !v)}
            aria-label={menuOpen ? "Fechar menu" : "Abrir menu"}
            aria-expanded={menuOpen}
          >
            <span className="flex flex-col gap-[5px]" aria-hidden="true">
              <span className="block w-5 h-0.5 bg-current rounded-full" />
              <span className="block w-5 h-0.5 bg-current rounded-full" />
              <span className="block w-5 h-0.5 bg-current rounded-full" />
            </span>
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden border-t border-border pb-3 pt-2 bg-white">
            <Navigation onNavigate={() => setMenuOpen(false)} />
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
