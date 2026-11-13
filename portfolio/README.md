# Портфолио

Отдельный сайт на Next.js 14 (App Router). К Android-клиенту в корне репозитория не относится.

## Локально

Из каталога `portfolio`:

```bash
npm install
npm run dev
```

Сайт откроется на [http://localhost:3000](http://localhost:3000).

Проверка сборки:

```bash
npm run build
npm start
```

## Деплой на Vercel

1. Импортируйте этот git-репозиторий в [Vercel](https://vercel.com/new).
2. В настройках проекта укажите **Root Directory**: `portfolio`.
3. Framework Preset оставьте **Next.js**. Команда сборки — `npm run build`, Vercel подставит её сам.
4. Нажмите Deploy.

После деплоя задайте переменную `NEXT_PUBLIC_SITE_URL` со своим адресом, например `https://example.com`. Тогда ссылки Open Graph будут абсолютными. Без переменной метаданные собираются от `http://localhost:3000`.

## Где менять тексты

- `data/site.ts` — имя в шапке, описание сайта, почта, GitHub, Telegram.
- `data/projects.ts` — проекты. Тип только `SaaS`, `Сайт` или `Инструмент`.
- На страницах ищите комментарии `COPY:`.
