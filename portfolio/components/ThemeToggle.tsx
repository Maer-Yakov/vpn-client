"use client";

import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

type Theme = "dark" | "light";

const themeKey = "theme";

function themeFromValue(value: string | null): Theme {
  return value === "light" ? "light" : "dark";
}

function applyDocumentTheme(theme: Theme) {
  document.documentElement.classList.toggle("dark", theme === "dark");
  document.documentElement.style.colorScheme = theme;
}

function persistTheme(theme: Theme) {
  try {
    localStorage.setItem(themeKey, theme);
  } catch {
    // Приватный режим или запрет на storage не должны ломать переключатель.
  }
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("dark");

  useEffect(() => {
    setTheme(document.documentElement.classList.contains("dark") ? "dark" : "light");

    function onStorage(event: StorageEvent) {
      if (event.key !== themeKey) return;
      const next = themeFromValue(event.newValue);
      applyDocumentTheme(next);
      setTheme(next);
    }

    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  function toggle() {
    const next: Theme = theme === "dark" ? "light" : "dark";
    setTheme(next);
    applyDocumentTheme(next);
    persistTheme(next);
  }

  const isDark = theme === "dark";

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={isDark ? "Включить светлую тему" : "Включить тёмную тему"}
      aria-pressed={isDark}
      className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[var(--line)] transition duration-300 hover:border-accent hover:text-accent"
    >
      {isDark ? <Sun size={18} aria-hidden /> : <Moon size={18} aria-hidden />}
    </button>
  );
}
