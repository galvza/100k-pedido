/**
 * Rodapé global com créditos, link do dataset e link do repositório.
 */
const Footer = () => (
  <footer className="border-t border-border mt-16 py-8 bg-surface">
    <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-sm font-sans text-muted">
      <p>
        Por{" "}
        <a
          href="https://www.linkedin.com/in/biel-als/"
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-foreground transition-colors"
        >
          Gabriel Alves
        </a>
      </p>
      <p>
        Dados:{" "}
        <a
          href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-foreground transition-colors"
        >
          Olist Brazilian E-Commerce (Kaggle)
        </a>
      </p>
      <p>
        Código:{" "}
        <a
          href="https://github.com/galvza/100k-pedidos"
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-foreground transition-colors"
        >
          GitHub
        </a>
      </p>
    </div>
  </footer>
);

export default Footer;
