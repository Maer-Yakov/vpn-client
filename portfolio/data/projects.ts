/**
 * COPY: проекты. Замените объекты своими — главная, список и страницы кейсов
 * читают только этот файл.
 * Поле type должно остаться одним из: "SaaS" | "Сайт" | "Инструмент".
 * Поле link — адрес проекта. Пока стоит заглушка "#".
 */
export type ProjectType = "SaaS" | "Сайт" | "Инструмент";

export type Project = {
  slug: string;
  name: string;
  type: ProjectType;
  pain: string;
  result: string;
  stack: string[];
  link: string;
};

export const projectTypes: ProjectType[] = ["SaaS", "Сайт", "Инструмент"];

export const projects: Project[] = [
  {
    slug: "junk-mail-cleaner",
    name: "Junk Mail Cleaner",
    type: "SaaS",
    pain: "Фрилансеры тратят часы на ручную чистку спама в почте",
    result: "Автоматическая очистка, экономия 3 часов в месяц",
    stack: ["Next.js", "Supabase", "Stripe"],
    link: "#",
  },
  {
    slug: "freelance-tracker",
    name: "Freelance Invoice Tracker",
    type: "Инструмент",
    pain: "Дизайнеры-одиночки забывают выставлять счета",
    result: "Напоминания и трекинг оплат в одном месте",
    stack: ["React", "Node.js"],
    link: "#",
  },
  {
    slug: "portfolio-site",
    name: "Portfolio Site",
    type: "Сайт",
    pain: "Нужен быстрый способ показать работы клиентам",
    result: "Сайт-визитка с кейсами за 1 вечер",
    stack: ["Next.js", "Tailwind"],
    link: "#",
  },
];

export function getProject(slug: string): Project | undefined {
  return projects.find((project) => project.slug === slug);
}
