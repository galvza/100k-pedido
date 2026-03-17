/**
 * Utilitários para carregar JSONs estáticos de public/data/.
 *
 * Projetado para uso em Client Components. Todos os erros são
 * capturados internamente — nunca lança exceções para o chamador.
 */

/**
 * Carrega um JSON estático da pasta public/data/.
 *
 * Em caso de erro (404, JSON malformado, rede), retorna `fallback`
 * (padrão: array vazio).
 *
 * @param filename - Nome do arquivo (ex: "01_funil_conversao.json")
 * @param fallback - Valor retornado em caso de falha
 */
export async function loadChapterData<T>(
  filename: string,
  fallback: T = [] as unknown as T
): Promise<T> {
  try {
    const res = await fetch(`/data/${filename}`);
    if (!res.ok) return fallback;
    const data: T = await res.json();
    return data;
  } catch {
    return fallback;
  }
}
