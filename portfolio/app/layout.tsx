import type { Metadata } from "next";
import localFont from "next/font/local";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { site, siteTitle } from "@/data/site";
import { configuredSiteUrl } from "@/lib/site-url";
import { themeInitScript } from "@/lib/theme-script";
import "./globals.css";

// Файл в репозитории: сборка не скачивает шрифт с fonts.google.com.
const inter = localFont({
  src: "../fonts/Inter-latin-cyrillic.woff2",
  display: "swap",
  weight: "100 900",
});

const metadataBase = configuredSiteUrl();

export const metadata: Metadata = {
  ...(metadataBase ? { metadataBase } : {}),
  title: {
    default: siteTitle,
    template: `%s — ${site.name}`,
  },
  description: site.description,
  openGraph: {
    type: "website",
    locale: "ru_RU",
    siteName: site.name,
    title: siteTitle,
    description: site.description,
  },
  twitter: {
    card: "summary",
    title: siteTitle,
    description: site.description,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="ru"
      className={`dark ${inter.className}`}
      style={{ colorScheme: "dark" }}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className="flex min-h-screen flex-col antialiased">
        <a
          href="#content"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[60] focus:rounded-full focus:bg-accent focus:px-4 focus:py-2 focus:text-white"
        >
          К содержанию
        </a>
        <Header />
        <main id="content" className="shell flex-1 py-12 md:py-16">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
