import { Github, Mail, Send } from "lucide-react";
import { site } from "@/data/site";

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-[var(--line)]">
      <div className="shell flex flex-col gap-8 py-10 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold">{site.name}</p>
          <p className="mt-1 max-w-sm text-sm leading-relaxed text-[var(--muted)]">
            Небольшие продукты с понятным результатом.
          </p>
          <p className="mt-4 text-xs text-[var(--muted)]">© {year}</p>
        </div>
        {/* COPY: почта, GitHub и Telegram — data/site.ts */}
        <ul className="flex flex-col gap-3 text-sm">
          <li>
            <a
              href={`mailto:${site.email}`}
              className="inline-flex items-center gap-2 transition duration-300 hover:text-accent"
            >
              <Mail size={16} aria-hidden />
              {site.email}
            </a>
          </li>
          <li>
            <a
              href={site.github}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 transition duration-300 hover:text-accent"
            >
              <Github size={16} aria-hidden />
              GitHub
            </a>
          </li>
          <li>
            <a
              href={site.telegram}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 transition duration-300 hover:text-accent"
            >
              <Send size={16} aria-hidden />
              Telegram
            </a>
          </li>
        </ul>
      </div>
    </footer>
  );
}
