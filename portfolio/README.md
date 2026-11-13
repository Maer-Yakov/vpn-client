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
4. До первого деплоя задайте переменную `NEXT_PUBLIC_SITE_URL` — публичный адрес сайта, например `https://example.com`.
5. Нажмите Deploy.

Значение вшивается при сборке. Если адрес изменится, обновите переменную и задеплойте ещё раз. Без `NEXT_PUBLIC_SITE_URL` абсолютные ссылки для соцсетей не собираются: `localhost` подставляться не будет.

## Где менять тексты

- `data/site.ts` — имя в шапке, описание сайта, почта, GitHub, Telegram. Заголовок вкладки собирается из имени.
- `data/projects.ts` — кейсы. Тип только `SaaS`, `Сайт` или `Инструмент`. На главную попадают записи с `featured: true`.
- На страницах ищите комментарии `COPY:`.
