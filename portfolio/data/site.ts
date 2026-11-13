/**
 * COPY: имя, описание и контакты.
 * Шапка, подвал, страница «Обо мне» и метаданные читают эти поля.
 * Заголовок вкладки — siteTitle, он собран из name.
 */
export const site = {
  name: "Моё имя",
  description:
    "Сервисы, инструменты и сайты для фрилансеров и частных практик. В кейсах — кому это нужно, что сделано и цифра результата.",
  email: "hello@example.com",
  github: "https://github.com/username",
  telegram: "https://t.me/username",
} as const;

export const siteTitle = `${site.name} — портфолио`;
