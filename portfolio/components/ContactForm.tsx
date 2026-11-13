"use client";

import { FormEvent } from "react";
import { site } from "@/data/site";

export function ContactForm() {
  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const name = String(data.get("name") ?? "").trim();
    // Заглушка: сервера нет. Замените alert на свой обработчик или оставьте mailto в контактах.
    window.alert(
      `${name ? `${name}, это` : "Это"} заглушка. Сообщение никуда не ушло. Напишите на ${site.email}`,
    );
    event.currentTarget.reset();
  }

  return (
    <form onSubmit={onSubmit} className="mt-8 max-w-xl space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm">
          <span className="mb-1.5 block text-[var(--muted)]">Имя</span>
          <input className="field" name="name" required autoComplete="name" />
        </label>
        <label className="block text-sm">
          <span className="mb-1.5 block text-[var(--muted)]">Почта</span>
          <input className="field" type="email" name="email" required autoComplete="email" />
        </label>
      </div>
      <label className="block text-sm">
        <span className="mb-1.5 block text-[var(--muted)]">Сообщение</span>
        <textarea
          className="field resize-y"
          name="message"
          required
          rows={5}
          placeholder="Кому это нужно и что сейчас делается руками"
        />
      </label>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <button type="submit" className="btn-primary">
          Отправить
        </button>
        <a href={`mailto:${site.email}`} className="text-sm text-[var(--muted)] hover:text-accent">
          Или напишите на почту
        </a>
      </div>
      <p className="text-xs leading-relaxed text-[var(--muted)]">
        Форма ничего не отправляет на сервер — это заглушка.
      </p>
    </form>
  );
}
