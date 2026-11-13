"use client";

import { useMemo } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ProjectCard } from "@/components/ProjectCard";
import { projectTypes, type Project, type ProjectType } from "@/data/projects";
import { filterFromQuery, portfolioTypeHref } from "@/lib/portfolio-filter";

type Filter = "all" | ProjectType;

const filters: Filter[] = ["all", ...projectTypes];

const labels: Record<Filter, string> = {
  all: "Все",
  SaaS: "SaaS",
  Сайт: "Сайт",
  Инструмент: "Инструмент",
};

function workCount(count: number) {
  const mod10 = count % 10;
  const mod100 = count % 100;
  if (mod10 === 1 && mod100 !== 11) return `${count} работа`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${count} работы`;
  return `${count} работ`;
}

export function ProjectBrowser({ projects }: { projects: Project[] }) {
  const params = useSearchParams();
  const filter = filterFromQuery(params.get("type"));
  const visible = useMemo(
    () => (filter === "all" ? projects : projects.filter((project) => project.type === filter)),
    [filter, projects],
  );

  return (
    <div>
      <div className="flex flex-wrap gap-2" role="group" aria-label="Фильтр по типу">
        {filters.map((item) => {
          const selected = item === filter;
          const href = item === "all" ? "/portfolio" : portfolioTypeHref(item);
          return (
            <Link
              key={item}
              href={href}
              scroll={false}
              aria-current={selected ? "true" : undefined}
              className={`inline-flex min-h-11 items-center rounded-full px-4 py-2 text-sm transition duration-300 ${
                selected
                  ? "bg-accent text-white"
                  : "border border-[var(--line)] text-[var(--muted)] hover:border-accent hover:text-[var(--fg)]"
              }`}
            >
              {labels[item]}
            </Link>
          );
        })}
      </div>

      <p className="mt-4 text-sm text-[var(--muted)]" aria-live="polite">
        {workCount(visible.length)}
      </p>

      {visible.length === 0 ? (
        <p className="mt-8 text-sm text-[var(--muted)]">В этом типе пока нет проектов.</p>
      ) : (
        <ul className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {visible.map((project, index) => (
            <li key={project.slug} className="rise" style={{ animationDelay: `${index * 80}ms` }}>
              <ProjectCard project={project} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
