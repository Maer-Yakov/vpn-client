import { ArrowLeft, ArrowUpRight } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import { CaseMock } from "@/components/CaseMock";
import { projects, type Project } from "@/data/projects";

export function CaseStudy({ project }: { project: Project }) {
  switch (project.preview.kind) {
    case "inbox":
      return <InboxCase project={project} />;
    case "invoice":
      return <InvoiceCase project={project} />;
    case "landing":
      return <LandingCase project={project} />;
    case "schedule":
      return <ScheduleCase project={project} />;
    case "estimate":
      return <EstimateCase project={project} />;
    case "showcase":
      return <ShowcaseCase project={project} />;
    default: {
      const unreachable: never = project.preview;
      return unreachable;
    }
  }
}

function BackLink() {
  return (
    <Link
      href="/portfolio"
      className="inline-flex items-center gap-2 text-sm text-[var(--muted)] transition duration-300 hover:text-accent"
    >
      <ArrowLeft size={16} aria-hidden />
      Все проекты
    </Link>
  );
}

function CaseNeighbors({ project }: { project: Project }) {
  const index = projects.findIndex((item) => item.slug === project.slug);
  if (index < 0) return null;
  const previous = projects[(index - 1 + projects.length) % projects.length];
  const next = projects[(index + 1) % projects.length];

  return (
    <nav aria-label="Другие работы" className="mt-12 grid gap-3 sm:grid-cols-2">
      <NeighborLink label="Предыдущая" project={previous} />
      <NeighborLink label="Следующая" project={next} />
    </nav>
  );
}

function NeighborLink({ label, project }: { label: string; project: Project }) {
  return (
    <Link
      href={`/portfolio/${project.slug}`}
      className="rounded-xl border border-[var(--line)] p-4 transition duration-300 hover:border-accent"
    >
      <p className="text-xs text-[var(--muted)]">{label}</p>
      <p className="mt-1 font-medium">{project.name}</p>
      <p className="mt-1 text-sm text-[var(--muted)]">{project.preview.stat}</p>
    </Link>
  );
}

function HireClose() {
  return (
    <div className="mt-12 flex flex-col gap-4 border-t border-[var(--line)] pt-8 sm:flex-row sm:items-center sm:justify-between">
      <p className="max-w-md text-sm leading-relaxed text-[var(--muted)]">
        Нужна такая же вещь под свою задачу — напишите, кому это нужно и что сейчас делается руками.
      </p>
      <Link href="/about#contact" className="btn-primary shrink-0">
        Связаться
      </Link>
    </div>
  );
}

function OpenProject({ project }: { project: Project }) {
  const showLink = project.link !== "" && project.link !== "#";
  if (!showLink) return null;
  const external = project.link.startsWith("http");

  return (
    // COPY: адрес кнопки — поле link в data/projects.ts. "#" и пустая строка кнопку не показывают.
    <a
      href={project.link}
      className="btn-primary mt-8"
      {...(external ? { target: "_blank", rel: "noreferrer" } : {})}
    >
      Открыть проект
      <ArrowUpRight size={16} aria-hidden />
    </a>
  );
}

function StackRow({ stack }: { stack: string[] }) {
  return (
    <section>
      <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--muted)]">Стек</h2>
      <ul className="mt-3 flex flex-wrap gap-2">
        {stack.map((item) => (
          <li key={item} className="rounded-full border border-[var(--line)] px-3 py-1 text-sm">
            {item}
          </li>
        ))}
      </ul>
    </section>
  );
}

function Note({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <h2 className="text-sm font-medium uppercase tracking-wide text-[var(--muted)]">{title}</h2>
      <p className="mt-2 leading-relaxed">{children}</p>
    </section>
  );
}

function InboxCase({ project }: { project: Project }) {
  return (
    <article className="rise">
      <BackLink />
      <div className="mt-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-emerald-700 dark:text-emerald-300">{project.type}</p>
          <h1 className="mt-1 text-4xl font-semibold tracking-tight">{project.name}</h1>
        </div>
        <p className="max-w-sm text-sm text-[var(--muted)]">{project.audience}</p>
      </div>
      <div className="mt-6">
        <CaseMock project={project} size="page" />
      </div>
      <div className="mt-8 grid gap-8 md:grid-cols-2">
        <Note title="Задача">{project.pain}</Note>
        <Note title="Что сделано">{project.built}</Note>
      </div>
      <p className="mt-8 text-xl font-medium">{project.result}</p>
      <div className="mt-8">
        <StackRow stack={project.stack} />
      </div>
      <OpenProject project={project} />
      <CaseNeighbors project={project} />
      <HireClose />
    </article>
  );
}

function InvoiceCase({ project }: { project: Project }) {
  return (
    <article className="rise grid items-start gap-8 lg:grid-cols-[1.05fr_0.95fr]">
      <CaseMock project={project} size="page" />
      <div>
        <BackLink />
        <p className="mt-6 text-xs font-medium uppercase tracking-[0.16em] text-[#8a6a3b]">{project.type}</p>
        <h1 className="mt-2 text-4xl font-semibold tracking-tight">{project.name}</h1>
        <p className="mt-3 text-lg">{project.offer}</p>
        <p className="mt-2 text-sm text-[var(--muted)]">{project.audience}</p>
        <div className="mt-8 space-y-6">
          <Note title="Задача">{project.pain}</Note>
          <Note title="Что сделано">{project.built}</Note>
          <Note title="Результат">{project.result}</Note>
          <StackRow stack={project.stack} />
        </div>
        <OpenProject project={project} />
      <CaseNeighbors project={project} />
      <HireClose />
      </div>
    </article>
  );
}

function LandingCase({ project }: { project: Project }) {
  return (
    <article className="rise">
      <BackLink />
      <div className="mt-6">
        <CaseMock project={project} size="page" />
      </div>
      <div className="mt-8 flex flex-wrap items-end justify-between gap-4">
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">{project.name}</h1>
        <p className="max-w-md text-sm text-[var(--muted)]">{project.audience}</p>
      </div>
      <div className="mt-8 grid gap-6 md:grid-cols-3">
        <Note title="Задача">{project.pain}</Note>
        <Note title="Что сделано">{project.built}</Note>
        <Note title="Результат">{project.result}</Note>
      </div>
      <div className="mt-8">
        <StackRow stack={project.stack} />
      </div>
      <OpenProject project={project} />
      <CaseNeighbors project={project} />
      <HireClose />
    </article>
  );
}

function ScheduleCase({ project }: { project: Project }) {
  return (
    <article className="rise">
      <BackLink />
      <div className="mt-6 grid items-start gap-6 lg:grid-cols-[1.4fr_0.7fr]">
        <CaseMock project={project} size="page" />
        <div className="rounded-2xl border border-[var(--line)] p-5">
          <p className="text-xs font-medium text-sky-700 dark:text-sky-300">{project.type}</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">{project.name}</h1>
          <p className="mt-3 text-sm leading-relaxed">{project.offer}</p>
          <p className="mt-4 text-4xl font-semibold tracking-tight">
            {project.preview.kind === "schedule" ? project.preview.stat : null}
          </p>
          <p className="text-sm text-[var(--muted)]">неявки в месяц</p>
        </div>
      </div>
      <div className="mt-8 grid gap-8 md:grid-cols-2">
        <Note title="Задача">{project.pain}</Note>
        <Note title="Что сделано">{project.built}</Note>
      </div>
      <p className="mt-6 text-[var(--muted)]">{project.audience}</p>
      <p className="mt-2">{project.result}</p>
      <div className="mt-8">
        <StackRow stack={project.stack} />
      </div>
      <OpenProject project={project} />
      <CaseNeighbors project={project} />
      <HireClose />
    </article>
  );
}

function EstimateCase({ project }: { project: Project }) {
  return (
    <article className="rise mx-auto max-w-xl">
      <BackLink />
      <p className="mt-6 text-xs font-medium uppercase tracking-[0.16em] text-amber-700 dark:text-amber-300">
        {project.type}
      </p>
      <h1 className="mt-2 text-4xl font-semibold tracking-tight">{project.name}</h1>
      <p className="mt-3 text-[var(--muted)]">{project.audience}</p>
      <div className="mt-6">
        <CaseMock project={project} size="page" />
      </div>
      <div className="mt-8 space-y-6">
        <Note title="Задача">{project.pain}</Note>
        <Note title="Что сделано">{project.built}</Note>
        <Note title="Результат">{project.result}</Note>
        <StackRow stack={project.stack} />
      </div>
      <OpenProject project={project} />
      <CaseNeighbors project={project} />
      <HireClose />
    </article>
  );
}

function ShowcaseCase({ project }: { project: Project }) {
  return (
    <article className="rise">
      <BackLink />
      <p className="mt-8 text-xs font-medium uppercase tracking-[0.2em] text-[var(--muted)]">{project.type}</p>
      <h1 className="mt-3 max-w-3xl text-5xl font-semibold tracking-tight sm:text-6xl">{project.name}</h1>
      <p className="mt-4 max-w-xl text-xl leading-relaxed">{project.offer}</p>
      <div className="mt-8">
        <CaseMock project={project} size="page" />
      </div>
      <div className="mt-10 grid gap-8 border-t border-[var(--line)] pt-8 md:grid-cols-2">
        <Note title="Задача">{project.pain}</Note>
        <Note title="Что сделано">{project.built}</Note>
      </div>
      <p className="mt-8 text-2xl font-semibold tracking-tight">{project.result}</p>
      <p className="mt-2 text-sm text-[var(--muted)]">{project.audience}</p>
      <div className="mt-8">
        <StackRow stack={project.stack} />
      </div>
      <OpenProject project={project} />
      <CaseNeighbors project={project} />
      <HireClose />
    </article>
  );
}
