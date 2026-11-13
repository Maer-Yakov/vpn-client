/**
 * COPY: примеры работ. Замените объекты своими — главная, список и страницы кейсов
 * читают только этот файл.
 * type: "SaaS" | "Сайт" | "Инструмент".
 * featured: true — работа попадает в блок на главной. Оставьте три сильных.
 * link: адрес проекта. "#" и пустая строка скрывают кнопку «Открыть проект».
 * preview — тексты макета на карточке и на странице кейса. Это рисунок интерфейса, не чужой скриншот.
 */
export type ProjectType = "SaaS" | "Сайт" | "Инструмент";

export type InboxPreview = {
  kind: "inbox";
  stat: string;
  before: string;
  messages: { from: string; text: string; kept: boolean }[];
};

export type InvoicePreview = {
  kind: "invoice";
  stat: string;
  number: string;
  client: string;
  lines: { title: string; amount: string }[];
  total: string;
};

export type LandingPreview = {
  kind: "landing";
  stat: string;
  title: string;
  price: string;
  fields: string[];
  works: string[];
};

export type SchedulePreview = {
  kind: "schedule";
  stat: string;
  reminder: string;
  columns: { day: string; items: { label: string; tone: "a" | "b" | "c" }[] }[];
};

export type EstimatePreview = {
  kind: "estimate";
  stat: string;
  accuracy: string;
  total: string;
  blocks: { title: string; hours: string }[];
};

export type ShowcasePreview = {
  kind: "showcase";
  stat: string;
  tiles: { index: string; title: string }[];
};

export type ProjectPreview =
  | InboxPreview
  | InvoicePreview
  | LandingPreview
  | SchedulePreview
  | EstimatePreview
  | ShowcasePreview;

export type Project = {
  slug: string;
  name: string;
  type: ProjectType;
  audience: string;
  pain: string;
  built: string;
  result: string;
  offer: string;
  stack: string[];
  link: string;
  featured?: boolean;
  preview: ProjectPreview;
};

export const projectTypes: ProjectType[] = ["SaaS", "Сайт", "Инструмент"];

export const projects: Project[] = [
  {
    slug: "chistyj-yaschik",
    name: "Чистый ящик",
    type: "SaaS",
    audience: "Фрилансеры, у которых во входящих больше 80 писем в день",
    pain: "Утро уходит на ручную чистку рассылок, а письма клиентов находятся к обеду",
    built: "Правила сортировки, отдельная папка «клиенты» и короткий отчёт по понедельникам",
    result: "Ручная разборка сократилась с 5 часов до 40 минут в месяц",
    offer: "Почта, где письмо клиента не тонет в рассылке",
    stack: ["Next.js", "TypeScript", "Postgres"],
    link: "#",
    featured: true,
    preview: {
      kind: "inbox",
      stat: "40 мин",
      before: "5 часов",
      messages: [
        { from: "Анна", text: "Правки по главной", kept: true },
        { from: "Рассылка", text: "Скидка только сегодня", kept: false },
        { from: "Игорь", text: "Счёт получил, спасибо", kept: true },
        { from: "Дайджест", text: "24 письма за ночь", kept: false },
      ],
    },
  },
  {
    slug: "schet-v-srok",
    name: "Счёт в срок",
    type: "Инструмент",
    audience: "Дизайнеры, которые работают одни и сдают 4–8 проектов в месяц",
    pain: "Счёт уходит через несколько дней, когда клиент уже переключился на следующую задачу",
    built: "Список сданных работ, напоминание в день сдачи и статус «выставлен / оплачен»",
    result: "Срок от сдачи макета до счёта сократился с 6 дней до 1",
    offer: "Счёт уходит в тот же день, когда работа сдана",
    stack: ["React", "TypeScript", "Node.js"],
    link: "#",
    featured: true,
    preview: {
      kind: "invoice",
      stat: "1 день",
      number: "18",
      client: "Студия на двоих",
      lines: [
        { title: "Главный экран", amount: "12 000 ₽" },
        { title: "Карточки услуг", amount: "8 000 ₽" },
      ],
      total: "20 000 ₽",
    },
  },
  {
    slug: "odna-stranica",
    name: "Одна страница",
    type: "Сайт",
    audience: "Мастера и частные практики, к которым записываются через три разных чата",
    pain: "Заявки теряются в переписке, а свободные окна приходится сверять вручную",
    built: "Одна страница с работами, ценой и формой: имя, услуга, удобный день",
    result: "9 из 10 записей приходят с сайта, а не из личных сообщений",
    offer: "Страница, которая записывает человека без длинной переписки",
    stack: ["Next.js", "Tailwind"],
    link: "#",
    featured: true,
    preview: {
      kind: "landing",
      stat: "9 из 10",
      title: "Запись без переписки",
      price: "4 500 ₽",
      fields: ["Имя", "Услуга", "Удобный день"],
      works: ["Чашка", "Ваза", "Тарелка"],
    },
  },
  {
    slug: "slot",
    name: "Слот",
    type: "SaaS",
    audience: "Репетиторы с 15–25 учениками и плавающим расписанием",
    pain: "Урок срывается, потому что подтверждение осталось во вчерашнем сообщении",
    built: "Расписание на неделю, напоминание ученику за 3 часа и отметка «оплачен»",
    result: "Неявки на группе из 20 учеников снизились с 8 до 3 в месяц",
    offer: "Расписание, которое само напоминает об уроке",
    stack: ["Next.js", "TypeScript", "Postgres"],
    link: "#",
    preview: {
      kind: "schedule",
      stat: "8 → 3",
      reminder: "Напоминание за 3 часа",
      columns: [
        { day: "Пн", items: [{ label: "Алгебра", tone: "a" }, { label: "Оплачен", tone: "a" }] },
        { day: "Вт", items: [{ label: "Английский", tone: "b" }] },
        { day: "Ср", items: [{ label: "Физика", tone: "c" }, { label: "Алгебра", tone: "a" }] },
        { day: "Чт", items: [{ label: "Эссе", tone: "b" }] },
        { day: "Пт", items: [{ label: "Разбор", tone: "c" }] },
      ],
    },
  },
  {
    slug: "smeta-blokami",
    name: "Смета блоками",
    type: "Инструмент",
    audience: "Небольшие студии из 2–3 человек, которые считают проект в таблице",
    pain: "Оценка занимает вечер, а в конце месяца факт расходится со сметой на треть",
    built: "Конструктор из блоков «дизайн, вёрстка, правки» с часами и итогом для клиента",
    result: "Смета собирается за 20 минут, расхождение с фактом держится в пределах 15%",
    offer: "Смета, которую клиент понимает без созвона",
    stack: ["React", "TypeScript"],
    link: "#",
    preview: {
      kind: "estimate",
      stat: "20 мин",
      accuracy: "±15%",
      total: "86 000 ₽",
      blocks: [
        { title: "Дизайн", hours: "6 ч" },
        { title: "Вёрстка", hours: "10 ч" },
        { title: "Правки", hours: "3 ч" },
      ],
    },
  },
  {
    slug: "vitrina-kejsov",
    name: "Витрина кейсов",
    type: "Сайт",
    audience: "Консультанты, которым перед созвоном нужно показать три работы, а не папку с файлами",
    pain: "Клиент просит примеры, и вместо одной ссылки уходит набор из разных документов",
    built: "Сайт с тремя кейсами, коротким описанием услуги и кнопкой записи на созвон",
    result: "Первая заявка с сайта пришла на 4-й день после публикации",
    offer: "Ссылка с кейсами, которую можно отправить в тот же вечер",
    stack: ["Next.js", "Tailwind"],
    link: "#",
    preview: {
      kind: "showcase",
      stat: "4-й день",
      tiles: [
        { index: "01", title: "Запуск услуги" },
        { index: "02", title: "Сервис записи" },
        { index: "03", title: "Страница с ценой" },
      ],
    },
  },
];

export function getProject(slug: string): Project | undefined {
  return projects.find((project) => project.slug === slug);
}

/** COPY: на главной только проекты с featured: true. */
export function featuredProjects(): Project[] {
  return projects.filter((project) => project.featured);
}

/** COPY: остальные работы — блок под избранными на главной. */
export function otherProjects(): Project[] {
  return projects.filter((project) => !project.featured);
}
