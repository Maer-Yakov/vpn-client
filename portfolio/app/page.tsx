import Link from "next/link";
import { ProjectCard } from "@/components/ProjectCard";
import { featuredProjects } from "@/data/projects";
import { site, siteTitle } from "@/data/site";
import { pageMeta } from "@/lib/seo";

export const metadata = pageMeta({
  title: siteTitle,
  description: site.description,
  path: "/",
  absoluteTitle: true,
});

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
    </div>
  );
}
