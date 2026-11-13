import type { Metadata } from "next";
import { site } from "@/data/site";

type PageMetaInput = {
  title: string;
  description: string;
  path: string;
  absoluteTitle?: boolean;
  type?: "website" | "article";
};

export function pageMeta(input: PageMetaInput): Metadata {
  const shareTitle = input.absoluteTitle ? input.title : `${input.title} — ${site.name}`;

  return {
    title: input.absoluteTitle ? { absolute: input.title } : input.title,
    description: input.description,
    alternates: { canonical: input.path },
    openGraph: {
      title: shareTitle,
      description: input.description,
      url: input.path,
      siteName: site.name,
      locale: "ru_RU",
      type: input.type ?? "website",
    },
    twitter: {
      card: "summary",
      title: shareTitle,
      description: input.description,
    },
  };
}
