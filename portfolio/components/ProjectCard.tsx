import Link from "next/link";
import { CaseMock } from "@/components/CaseMock";
import type { Project } from "@/data/projects";

export function ProjectCard({ project }: { project: Project }) {
  return (
    <Link
      href={`/portfolio/${project.slug}`}
      className="group flex h-full flex-col overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--card)] shadow-none transition duration-300 hover:-translate-y-1 hover:shadow-[0_18px_40px_-24px_rgba(99,102,241,0.55)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent motion-reduce:transform-none"
    >
      <CaseMock project={project} size="card" />
      <div className="flex flex-1 flex-col p-4">
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-lg font-semibold tracking-tight">{project.name}</h3>
          <span className="shrink-0 rounded-full bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent">
            {project.type}
          </span>
        </div>
        <p className="mt-3 text-sm font-medium leading-relaxed">{project.offer}</p>
        <p className="mt-auto pt-3 text-sm leading-relaxed text-[var(--muted)]">{project.result}</p>
      </div>
    </Link>
  );
}
