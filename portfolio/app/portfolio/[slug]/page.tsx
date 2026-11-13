import { notFound } from "next/navigation";
import { CaseStudy } from "@/components/CaseStudy";
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

  return <CaseStudy project={project} />;
}
