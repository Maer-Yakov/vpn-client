"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { site } from "@/data/site";

const links = [
  { href: "/", label: "Главная" },
  { href: "/portfolio", label: "Портфолио" },
  { href: "/about", label: "Обо мне" },
];

function isActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function Header() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <header className="header-bar sticky top-0 z-50 border-b border-[var(--line)] backdrop-blur-md">
      <div className="shell relative flex h-16 items-center justify-between">
        {/* COPY: текст логотипа — site.name в data/site.ts */}
        <Link href="/" className="inline-flex items-center gap-2 text-sm font-semibold tracking-tight">
          <span className="h-2 w-2 rounded-full bg-accent" aria-hidden />
          {site.name}
        </Link>

        <nav
          className="absolute left-1/2 hidden -translate-x-1/2 items-center gap-6 md:flex"
          aria-label="Основное меню"
        >
          {links.map((link) => {
            const active = isActive(pathname, link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={`text-sm transition duration-300 ${
                  active ? "text-[var(--fg)]" : "text-[var(--muted)] hover:text-[var(--fg)]"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <button
            type="button"
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[var(--line)] transition duration-300 hover:border-accent md:hidden"
            aria-expanded={open}
            aria-controls="mobile-nav"
            aria-label={open ? "Закрыть меню" : "Открыть меню"}
            onClick={() => setOpen((value) => !value)}
          >
            {open ? <X size={18} aria-hidden /> : <Menu size={18} aria-hidden />}
          </button>
        </div>
      </div>

      <nav
        id="mobile-nav"
        aria-label="Мобильное меню"
        className={open ? "border-t border-[var(--line)] px-4 py-3 md:hidden" : "hidden"}
      >
        <ul className="flex flex-col">
          {links.map((link) => {
            const active = isActive(pathname, link.href);
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  aria-current={active ? "page" : undefined}
                  className={`block rounded-lg px-3 py-3 text-base ${
                    active ? "bg-[var(--soft)] text-[var(--fg)]" : "text-[var(--muted)]"
                  }`}
                >
                  {link.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </header>
  );
}
