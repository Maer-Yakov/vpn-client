/**
 * COPY: имя, описание и контакты.
 * Шапка, подвал, страница «Обо мне» и метаданные читают эти поля.
 * Заголовок вкладки — siteTitle, он собран из name.
 */
export const site = {
  name: "Моё имя",
  description:
    "Небольшие SaaS, сайты и инструменты для фрилансеров. Три кейса: от боли клиента к результату.",
  email: "hello@example.com",
  github: "https://github.com/username",
  telegram: "https://t.me/username",
} as const;

export const siteTitle = `${site.name} — портфолио`;
