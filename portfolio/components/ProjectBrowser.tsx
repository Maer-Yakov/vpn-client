"use client";

import { useMemo, useState } from "react";
import { ProjectCard } from "@/components/ProjectCard";
import { projectTypes, type Project, type ProjectType } from "@/data/projects";

type Filter = "all" | ProjectType;

const filters: Filter[] = ["all", ...projectTypes];

const labels: Record<Filter, string> = {
  all: "Все",
  SaaS: "SaaS",
  Сайт: "Сайт",
  Инструмент: "Инструмент",
};

export function ProjectBrowser({ projects }: { projects: Project[] }) {
  const [filter, setFilter] = useState<Filter>("all");
  const visible = useMemo(
    () => (filter === "all" ? projects : projects.filter((project) => project.type === filter)),
    [filter, projects],
  );

  return (
    <div>
      <div className="flex flex-wrap gap-2" role="group" aria-label="Фильтр по типу">
        {filters.map((item) => {
          const selected = item === filter;
          return (
            <button
              key={item}
              type="button"
              aria-pressed={selected}
              onClick={() => setFilter(item)}
              className={`min-h-11 rounded-full px-4 py-2 text-sm transition duration-300 ${
                selected
                  ? "bg-accent text-white"
                  : "border border-[var(--line)] text-[var(--muted)] hover:border-accent hover:text-[var(--fg)]"
              }`}
            >
              {labels[item]}
            </button>
          );
        })}
      </div>

      <p className="sr-only" aria-live="polite">
        Показано: {visible.length}
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
