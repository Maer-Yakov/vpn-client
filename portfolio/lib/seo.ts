import type { Metadata } from "next";
import { site } from "@/data/site";
import { configuredSiteUrl } from "@/lib/site-url";

type PageMetaInput = {
  title: string;
  description: string;
  path: string;
  absoluteTitle?: boolean;
  type?: "website" | "article";
};

function shareImage(path: string): string {
  const slug = path.match(/^\/portfolio\/([^/]+)$/)?.[1];
  return slug ? `/og/${slug}.png` : "/og/home.png";
}

export function pageMeta(input: PageMetaInput): Metadata {
  const shareTitle = input.absoluteTitle ? input.title : `${input.title} — ${site.name}`;
  const hasPublicUrl = configuredSiteUrl() !== undefined;
  const image = shareImage(input.path);

  return {
    title: input.absoluteTitle ? { absolute: input.title } : input.title,
    description: input.description,
    ...(hasPublicUrl ? { alternates: { canonical: input.path } } : {}),
    openGraph: {
      title: shareTitle,
      description: input.description,
      ...(hasPublicUrl
        ? { url: input.path, images: [{ url: image, width: 1200, height: 630, alt: shareTitle }] }
        : {}),
      siteName: site.name,
      locale: "ru_RU",
      type: input.type ?? "website",
    },
    twitter: {
      card: hasPublicUrl ? "summary_large_image" : "summary",
      title: shareTitle,
      description: input.description,
      ...(hasPublicUrl ? { images: [image] } : {}),
    },
  };
}
