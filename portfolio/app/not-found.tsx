import Link from "next/link";

export default function NotFound() {
  return (
    <div className="rise mx-auto max-w-xl py-10">
      <p className="text-sm font-medium text-accent">404</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight">Страница не найдена</h1>
      <p className="mt-4 text-[var(--muted)]">Такой страницы нет. Вернитесь на главную или откройте портфолио.</p>
      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <Link href="/" className="btn-primary">
          На главную
        </Link>
        <Link href="/portfolio" className="btn-ghost">
          Портфолио
        </Link>
      </div>
    </div>
  );
}
