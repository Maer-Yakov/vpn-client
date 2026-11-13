import Link from "next/link";
import { CaseMock } from "@/components/CaseMock";
import { ProjectCard } from "@/components/ProjectCard";
import { featuredProjects, otherProjects, projectTypes } from "@/data/projects";
import { portfolioTypeHref } from "@/lib/portfolio-filter";
import { site, siteTitle } from "@/data/site";
import { pageMeta } from "@/lib/seo";

export const metadata = pageMeta({
  title: siteTitle,
  description: site.description,
  path: "/",
  absoluteTitle: true,
});

/* COPY: короткая формулировка каждого типа на главной */
const typeOffer = {
  SaaS: "Сервис, который сам сортирует или напоминает",
  Сайт: "Страница, которую можно отправить в тот же день",
  Инструмент: "Счёт или смета без вечерней таблицы",
} as const;

export default function HomePage() {
  return (
    <div className="space-y-16">
      <section className="rise">
        <div className="mb-6 h-px w-12 bg-accent" />
        {/* COPY: кому предназначено предложение */}
        <p className="text-sm font-medium text-accent">Для фрилансеров и частных практик</p>
        {/* COPY: заголовок на главной */}
        <h1 className="mt-3 max-w-3xl text-4xl font-semibold tracking-tight sm:text-5xl sm:leading-[1.08]">
          Соберу сервис, инструмент или сайт под одну конкретную боль
        </h1>
        {/* COPY: что получает клиент */}
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-[var(--muted)] sm:text-lg">
          На выходе рабочая вещь, а не макет: меньше ручной работы или страница, которую можно
          отправить клиенту в тот же день. В каждом кейсе есть цифра, по которой видно результат.
        </p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <Link href="/about#contact" className="btn-primary">
            Связаться
          </Link>
          <Link href="/portfolio" className="btn-ghost">
            Смотреть работы
          </Link>
        </div>
        {/* COPY: три типа заказа. Ссылки открывают портфолио уже с фильтром. */}
        <ul className="mt-10 grid gap-3 sm:grid-cols-3">
          {projectTypes.map((type) => (
            <li key={type}>
              <Link
                href={portfolioTypeHref(type)}
                className="block h-full rounded-xl border border-[var(--line)] p-4 transition duration-300 hover:border-accent"
              >
                <p className="text-sm font-medium text-accent">{type}</p>
                <p className="mt-2 text-sm leading-relaxed">{typeOffer[type]}</p>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <div className="rise flex items-end justify-between gap-4">
          <h2 className="text-2xl font-semibold tracking-tight">Избранные проекты</h2>
          <Link href="/portfolio" className="text-sm text-[var(--muted)] transition duration-300 hover:text-accent">
            Все проекты
          </Link>
        </div>
        {/* COPY: избранные — проекты с featured: true в data/projects.ts */}
        <ul className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {featuredProjects().map((project, index) => (
            <li
              key={project.slug}
              className="rise"
              style={{ animationDelay: `${140 + index * 90}ms` }}
            >
              <ProjectCard project={project} />
            </li>
          ))}
        </ul>
      </section>

      <section className="rise">
        <h2 className="text-2xl font-semibold tracking-tight">Ещё работы</h2>
        {/* COPY: остальные — проекты без featured в data/projects.ts */}
        <ul className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          {otherProjects().map((project) => (
            <li key={project.slug}>
              <Link
                href={`/portfolio/${project.slug}`}
                className="block overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--card)] transition duration-300 hover:-translate-y-1 hover:border-accent motion-reduce:transform-none"
              >
                <CaseMock project={project} size="thumb" />
                <div className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <span className="font-medium">{project.name}</span>
                    <span className="text-xs text-[var(--muted)]">{project.type}</span>
                  </div>
                  <p className="mt-2 text-sm text-[var(--muted)]">{project.preview.stat}</p>
                </div>
              </Link>
            </li>
          ))}
        </ul>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="max-w-md text-sm leading-relaxed text-[var(--muted)]">
            Если одна из работ похожа на вашу задачу — напишите, кому это нужно.
          </p>
          <Link href="/about#contact" className="btn-primary shrink-0">
            Связаться
          </Link>
        </div>
      </section>
    </div>
  );
}
