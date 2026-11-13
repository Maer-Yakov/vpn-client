import type { ProjectType } from "@/data/projects";

export const typeQuery = {
  SaaS: "saas",
  Сайт: "site",
  Инструмент: "tool",
} as const;

const filterByQuery: Record<string, ProjectType> = {
  saas: "SaaS",
  site: "Сайт",
  tool: "Инструмент",
};

export function portfolioTypeHref(type: ProjectType): string {
  return `/portfolio?type=${typeQuery[type]}`;
}

export function filterFromQuery(value: string | null): "all" | ProjectType {
  if (!value) return "all";
  return filterByQuery[value] ?? "all";
}
