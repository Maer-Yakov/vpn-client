import { ContactForm } from "@/components/ContactForm";
import { HashScroll } from "@/components/HashScroll";
import { site } from "@/data/site";
import { pageMeta } from "@/lib/seo";
import { Github, Mail, Send } from "lucide-react";

export const metadata = pageMeta({
  title: "Обо мне",
  description: "Коротко о подходе, навыках, стеке и способах связи.",
  path: "/about",
});

/* COPY: биография */
const bio = [
  "Делаю небольшие продукты для людей, которые работают сами на себя. Беру одну конкретную боль — почта, счета, показ работ — и собираю вокруг неё понятный инструмент.",
  "Мне важно, чтобы результатом можно было пользоваться, а не только смотреть на макет.",
];

/* COPY: навыки */
const skills = ["Формулировка боли", "Интерфейсы", "Первая рабочая версия", "Тексты в продукте"];

/* COPY: стек */
const stackGroups = [
  { label: "Интерфейс", items: ["Next.js", "React", "TypeScript", "Tailwind CSS"] },
  { label: "Сервер и данные", items: ["Node.js", "Postgres"] },
];

/* COPY: как начинается работа */
const steps = [
  { title: "Боль", text: "Кому это нужно и что сейчас делается руками." },
  { title: "Первая версия", text: "Рабочий экран или страница, а не набор макетов." },
  { title: "Цифра", text: "Смотрим, стало ли меньше ручной работы." },
];

const contacts = [
  { href: `mailto:${site.email}`, label: site.email, icon: Mail, external: false },
  { href: site.github, label: "GitHub", icon: Github, external: true },
  { href: site.telegram, label: "Telegram", icon: Send, external: true },
];

export default function AboutPage() {
  return (
    <div className="space-y-16">
      <HashScroll />
      <header className="rise max-w-3xl">
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Обо мне</h1>
        <div className="mt-6 space-y-4 text-base leading-relaxed text-[var(--muted)] sm:text-lg">
          {bio.map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
        </div>
      </header>

      <section className="rise" style={{ animationDelay: "80ms" }}>
        <h2 className="text-2xl font-semibold tracking-tight">Навыки</h2>
        <ul className="mt-5 flex flex-wrap gap-2">
          {skills.map((skill) => (
            <li
              key={skill}
              className="rounded-full border border-[var(--line)] bg-[var(--soft)] px-3 py-1.5 text-sm"
            >
              {skill}
            </li>
          ))}
        </ul>
      </section>

      <section className="rise" style={{ animationDelay: "140ms" }}>
        <h2 className="text-2xl font-semibold tracking-tight">Стек</h2>
        <dl className="mt-5 grid gap-6 sm:grid-cols-2">
          {stackGroups.map((group) => (
            <div key={group.label}>
              <dt className="text-sm font-medium text-[var(--muted)]">{group.label}</dt>
              <dd className="mt-2 text-sm leading-relaxed">{group.items.join(", ")}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="rise" style={{ animationDelay: "200ms" }}>
        <h2 className="text-2xl font-semibold tracking-tight">Как начинается</h2>
        <ol className="mt-5 grid gap-4 sm:grid-cols-3">
          {steps.map((step, index) => (
            <li key={step.title} className="rounded-xl border border-[var(--line)] p-4">
              <p className="text-sm font-medium text-accent">0{index + 1}</p>
              <p className="mt-2 font-medium">{step.title}</p>
              <p className="mt-1 text-sm leading-relaxed text-[var(--muted)]">{step.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section id="contact" className="rise scroll-mt-24" style={{ animationDelay: "260ms" }}>
        <h2 className="text-2xl font-semibold tracking-tight">Контакты</h2>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-[var(--muted)] sm:text-base">
          Напишите, кому это нужно и какая боль. Если ближе почта или Telegram — они ниже формы.
        </p>
        {/* COPY: ссылки берутся из data/site.ts */}
        <ul className="mt-6 flex flex-col gap-3 text-sm sm:flex-row sm:flex-wrap sm:gap-6">
          {contacts.map((contact) => {
            const Icon = contact.icon;
            return (
              <li key={contact.label}>
                <a
                  href={contact.href}
                  className="inline-flex items-center gap-2 transition duration-300 hover:text-accent"
                  {...(contact.external ? { target: "_blank", rel: "noreferrer" } : {})}
                >
                  <Icon size={16} aria-hidden />
                  {contact.label}
                </a>
              </li>
            );
          })}
        </ul>
        <ContactForm />
      </section>
    </div>
  );
}
