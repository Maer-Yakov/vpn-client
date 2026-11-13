import { ArrowLeft, ArrowUpRight } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getProject, projects } from "@/data/projects";
import { pageMeta } from "@/lib/seo";

type ProjectPageProps = {
  params: { slug: string };
};

export function generateStaticParams() {
  return projects.map((project) => ({ slug: project.slug }));
}

export const dynamicParams = false;

export function generateMetadata({ params }: ProjectPageProps) {
  const project = getProject(params.slug);
  if (!project) {
    return { title: "Проект не найден" };
  }

  const description = `${project.pain}. ${project.result}`;
  return pageMeta({
    title: project.name,
    description,
    path: `/portfolio/${project.slug}`,
    type: "article",
  });
}

export default function ProjectPage({ params }: ProjectPageProps) {
  const project = getProject(params.slug);
  if (!project) {
    notFound();
  }

  const showLink = project.link !== "" && project.link !== "#";
  const external = project.link.startsWith("http");

  return (
    <article className="rise mx-auto max-w-3xl">
      <Link
        href="/portfolio"
        className="inline-flex items-center gap-2 text-sm text-[var(--muted)] transition duration-300 hover:text-accent"
      >
        <ArrowLeft size={16} aria-hidden />
        Все проекты
      </Link>

      <p className="mt-8 flex w-fit rounded-full bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent">
        {project.type}
      </p>
      <h1 className="mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">{project.name}</h1>
      <p className="mt-4 text-lg leading-relaxed">{project.offer}</p>
      <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">{project.audience}</p>

      <div className="mt-10 space-y-8">
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--muted)]">Задача</h2>
          <p className="mt-2 text-lg leading-relaxed">{project.pain}</p>
        </section>
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--muted)]">Что сделано</h2>
          <p className="mt-2 text-lg leading-relaxed">{project.built}</p>
        </section>
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--muted)]">Результат</h2>
          <p className="mt-2 text-lg leading-relaxed">{project.result}</p>
        </section>
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--muted)]">Стек</h2>
          <ul className="mt-3 flex flex-wrap gap-2">
            {project.stack.map((item) => (
              <li key={item} className="rounded-full border border-[var(--line)] px-3 py-1 text-sm">
                {item}
              </li>
            ))}
          </ul>
        </section>
      </div>

      {/* COPY: адрес кнопки — поле link в data/projects.ts. "#" и пустая строка кнопку не показывают. */}
      {showLink ? (
        <a
          href={project.link}
          className="btn-primary mt-10"
          {...(external ? { target: "_blank", rel: "noreferrer" } : {})}
        >
          Открыть проект
          <ArrowUpRight size={16} aria-hidden />
        </a>
      ) : null}
    </article>
  );
}
