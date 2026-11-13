/** Публичный адрес сайта. Без переменной абсолютные ссылки не собираются. */
export function configuredSiteUrl(): URL | undefined {
  const raw = process.env.NEXT_PUBLIC_SITE_URL?.trim();
  if (!raw) return undefined;
  return new URL(raw);
}
