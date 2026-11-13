import Link from "next/link";
import type { Project } from "@/data/projects";

export function ProjectCard({ project }: { project: Project }) {
  return (
    <Link
      href={`/portfolio/${project.slug}`}
      className="group flex h-full flex-col rounded-xl border border-[var(--line)] bg-[var(--card)] p-5 shadow-none transition duration-300 hover:-translate-y-1 hover:shadow-[0_18px_40px_-24px_rgba(99,102,241,0.55)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent motion-reduce:transform-none"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-lg font-semibold tracking-tight">{project.name}</h3>
        <span className="shrink-0 rounded-full bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent">
          {project.type}
        </span>
      </div>
      <p className="mt-4 text-sm leading-relaxed text-[var(--muted)]">
        <span className="font-medium text-[var(--fg)]">Боль. </span>
        {project.pain}
      </p>
      <p className="mt-2 text-sm leading-relaxed text-[var(--muted)]">
        <span className="font-medium text-[var(--fg)]">Результат. </span>
        {project.result}
      </p>
    </Link>
  );
}
