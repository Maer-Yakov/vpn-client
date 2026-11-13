import Link from "next/link";
import { ProjectCard } from "@/components/ProjectCard";
import { projects } from "@/data/projects";
import { site } from "@/data/site";
import { pageMeta } from "@/lib/seo";

export const metadata = pageMeta({
  title: site.title,
  description: site.description,
  path: "/",
  absoluteTitle: true,
});

export default function HomePage() {
  return (
    <div className="space-y-20">
      <section className="rise">
        <div className="mb-6 h-px w-12 bg-accent" />
        <p className="text-sm font-medium text-accent">Портфолио</p>
        {/* COPY: заголовок на главной */}
        <h1 className="mt-3 max-w-3xl text-4xl font-semibold tracking-tight sm:text-6xl sm:leading-[1.05]">
          Продукты, которые убирают ручную работу
        </h1>
        {/* COPY: короткое интро */}
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-[var(--muted)] sm:text-lg">
          Делаю небольшие SaaS, сайты и инструменты для тех, кто работает один.
          Ниже — три кейса: какая была боль и что изменилось.
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
        {/* COPY: избранные. Сейчас показаны все записи из data/projects.ts */}
        <ul className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project, index) => (
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
