import { ProjectBrowser } from "@/components/ProjectBrowser";
import { projects } from "@/data/projects";
import { pageMeta } from "@/lib/seo";

export const metadata = pageMeta({
  title: "Портфолио",
  description: "Все проекты с фильтром по типу: SaaS, сайт или инструмент.",
  path: "/portfolio",
});

export default function PortfolioPage() {
  return (
    <div>
      <header className="rise max-w-2xl">
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Портфолио</h1>
        {/* COPY: вступление к списку работ */}
        <p className="mt-4 text-base leading-relaxed text-[var(--muted)] sm:text-lg">
          Шесть работ. Оставьте нужный тип — SaaS, сайт или инструмент.
        </p>
      </header>
      <div className="mt-10">
        <ProjectBrowser projects={projects} />
      </div>
    </div>
  );
}
