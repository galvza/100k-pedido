"use client";

import { useState, useEffect } from "react";

/**
 * Retorna true quando a viewport é menor que o breakpoint (default 640px = sm).
 * Seguro para SSR: retorna false no servidor, atualiza no client.
 */
export function useIsMobile(breakpoint = 640): boolean {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < breakpoint);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, [breakpoint]);

  return isMobile;
}
