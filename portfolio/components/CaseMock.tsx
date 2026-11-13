import type {
  EstimatePreview,
  InboxPreview,
  InvoicePreview,
  LandingPreview,
  Project,
  SchedulePreview,
  ShowcasePreview,
} from "@/data/projects";

type MockSize = "thumb" | "card" | "page";

const frame = {
  thumb: "h-[88px] overflow-hidden",
  card: "h-[188px] overflow-hidden",
  page: "overflow-hidden rounded-2xl border border-black/10 shadow-[0_24px_50px_-32px_rgba(0,0,0,0.45)] dark:border-white/10",
} as const;

export function CaseMock({ project, size }: { project: Project; size: MockSize }) {
  const preview = project.preview;
  switch (preview.kind) {
    case "inbox":
      return <InboxMock preview={preview} size={size} />;
    case "invoice":
      return <InvoiceMock preview={preview} size={size} />;
    case "landing":
      return <LandingMock preview={preview} size={size} />;
    case "schedule":
      return <ScheduleMock preview={preview} size={size} />;
    case "estimate":
      return <EstimateMock preview={preview} size={size} />;
    case "showcase":
      return <ShowcaseMock preview={preview} size={size} />;
    default: {
      const unreachable: never = preview;
      return unreachable;
    }
  }
}

function InboxMock({ preview, size }: { preview: InboxPreview; size: MockSize }) {
  const compact = size !== "page";
  const kept = preview.messages.filter((message) => message.kept).length;
  const dropped = preview.messages.length - kept;

  return (
    <div aria-hidden className={`${frame[size]} bg-zinc-100 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100`}>
      <div className="flex items-center justify-between border-b border-black/10 px-3 py-2 dark:border-white/10">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          <span className="text-xs font-semibold">Входящие</span>
        </div>
        <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-[11px] font-semibold text-emerald-800 dark:text-emerald-300">
          {compact ? preview.stat : `${preview.stat} вместо ${preview.before}`}
        </span>
      </div>
      <div className={compact ? "" : "grid lg:grid-cols-[150px_1fr_200px]"}>
        {compact ? null : (
          <div className="hidden border-black/10 p-4 dark:border-white/10 lg:block lg:border-r">
            <p className="text-xs font-medium">Клиенты</p>
            <p className="text-[11px] text-zinc-500">{kept}</p>
            <p className="mt-3 text-xs font-medium">Рассылки</p>
            <p className="text-[11px] text-zinc-500">{dropped}</p>
          </div>
        )}
        <ul>
          {(compact ? preview.messages.slice(0, 3) : preview.messages).map((message, index) => (
            <li
              key={`${message.from}-${message.text}`}
              className={`flex items-center gap-2 border-b border-black/5 px-3 py-2 last:border-b-0 dark:border-white/10 ${
                !compact && index === 0 ? "bg-emerald-500/10" : ""
              }`}
            >
              <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${message.kept ? "bg-emerald-500" : "bg-zinc-400"}`} />
              <span className={`w-16 shrink-0 truncate text-[11px] font-medium ${message.kept ? "" : "text-zinc-400 line-through"}`}>
                {message.from}
              </span>
              <span className={`min-w-0 flex-1 truncate text-[11px] ${message.kept ? "text-zinc-600 dark:text-zinc-300" : "text-zinc-400 line-through"}`}>
                {message.text}
              </span>
              {compact ? null : (
                <span className="hidden text-[10px] text-zinc-400 sm:inline">{message.kept ? "клиенты" : "скрыть"}</span>
              )}
            </li>
          ))}
        </ul>
        {compact ? null : (
          <div className="hidden border-t border-black/10 p-4 dark:border-white/10 lg:block lg:border-l lg:border-t-0">
            <p className="text-[10px] uppercase tracking-[0.14em] text-zinc-500">Понедельник</p>
            <p className="mt-3 text-3xl font-semibold tracking-tight">{preview.stat}</p>
            <p className="mt-1 text-xs text-zinc-500">было {preview.before}</p>
            <p className="mt-4 text-xs leading-relaxed text-zinc-600 dark:text-zinc-300">
              Письма клиентов отдельно, рассылки сняты правилом.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function InvoiceMock({ preview, size }: { preview: InvoicePreview; size: MockSize }) {
  const compact = size !== "page";
  const steps = ["Сдано", "Счёт", "Оплачен"];

  return (
    <div aria-hidden className={`${frame[size]} bg-[#f3eee4] text-[#2a241b]`}>
      <div className={`flex items-start justify-between ${compact ? "px-3 pt-3" : "px-6 pt-6"}`}>
        <div>
          <p className="text-[10px] uppercase tracking-[0.16em]">Счёт</p>
          <p className={`font-semibold tracking-tight ${compact ? "text-lg" : "text-3xl"}`}>№ {preview.number}</p>
          <p className="mt-1 text-[11px]">{preview.client}</p>
        </div>
        <div className="text-right">
          <p className={`font-semibold tracking-tight ${compact ? "text-lg" : "text-4xl"}`}>{preview.stat}</p>
          <p className="text-[10px] uppercase tracking-wider">после сдачи</p>
        </div>
      </div>
      {compact ? null : (
        <div className="mx-6 mt-5 flex gap-2">
          {steps.map((step, index) => (
            <div
              key={step}
              className={`flex-1 rounded-full px-2 py-1 text-center text-[10px] font-medium ${
                index < 2 ? "bg-[#2a241b] text-[#f3eee4]" : "border border-[#2a241b]/20"
              }`}
            >
              {step}
            </div>
          ))}
        </div>
      )}
      <ul className={`${compact ? "mx-3 mt-2" : "mx-6 mt-5"} divide-y divide-[#2a241b]/15 border-y border-[#2a241b]/15`}>
        {preview.lines.map((line) => (
          <li key={line.title} className="flex items-center justify-between py-1.5 text-[11px]">
            <span>{line.title}</span>
            <span className="font-medium">{line.amount}</span>
          </li>
        ))}
      </ul>
      <div className={`flex items-center justify-between ${compact ? "px-3 py-2" : "px-6 py-4"}`}>
        <span className="text-[11px]">Итого</span>
        <span className={`font-semibold ${compact ? "text-sm" : "text-xl"}`}>{preview.total}</span>
      </div>
      {compact ? null : (
        <p className="mx-6 mb-6 w-fit rounded-full bg-[#2a241b] px-3 py-1 text-xs text-[#f3eee4]">
          Выставлен в день сдачи
        </p>
      )}
    </div>
  );
}

const workSwatch = ["bg-rose-300", "bg-amber-200", "bg-stone-300"];

function LandingMock({ preview, size }: { preview: LandingPreview; size: MockSize }) {
  const compact = size !== "page";

  return (
    <div aria-hidden className={`${frame[size]} bg-[#4a2030] text-white`}>
      <div className="flex items-center justify-between border-b border-white/10 px-3 py-1.5 text-[10px] text-rose-100">
        <span className="flex items-center gap-2">
          <span className="h-1.5 w-1.5 rounded-full bg-rose-200" />
          мастерская.site
        </span>
        {compact ? null : <span>Цена · Запись</span>}
      </div>
      <div className={compact ? "px-3 py-3" : "px-6 py-8 sm:px-8"}>
        <p className="text-[10px] uppercase tracking-[0.18em] text-rose-200">Мастерская</p>
        <p className={`mt-1 max-w-md font-semibold leading-tight ${compact ? "text-base" : "text-4xl"}`}>{preview.title}</p>
        <div className="mt-3 flex items-end justify-between gap-3">
          <p className={compact ? "text-sm font-medium" : "text-2xl font-medium"}>{preview.price}</p>
          <p className="rounded-full bg-white px-2 py-0.5 text-[11px] font-semibold text-[#4a2030]">{preview.stat}</p>
        </div>
      </div>
      {compact ? (
        <div className="mx-3 rounded-full bg-white py-1.5 text-center text-[11px] font-semibold text-[#4a2030]">
          Записаться
        </div>
      ) : (
        <div className="bg-[#f8efe9] text-[#4a2030]">
          <div className="grid grid-cols-3 gap-2 px-4 pt-4">
            {preview.works.map((work, index) => (
              <div key={work}>
                <div className={`h-14 rounded-md ${workSwatch[index] ?? "bg-stone-300"}`} />
                <p className="mt-1 text-[11px]">{work}</p>
              </div>
            ))}
          </div>
          <div className="grid gap-2 p-4 sm:grid-cols-3">
            {preview.fields.map((field) => (
              <div key={field} className="rounded-lg border border-[#4a2030]/15 bg-white px-3 py-2 text-xs">
                {field}
              </div>
            ))}
            <div className="rounded-full bg-[#4a2030] py-2 text-center text-sm font-medium text-white sm:col-span-3">
              Записаться
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const lessonTone = {
  a: "bg-sky-500 text-white",
  b: "bg-amber-300 text-zinc-900",
  c: "bg-violet-500 text-white",
} as const;

function ScheduleMock({ preview, size }: { preview: SchedulePreview; size: MockSize }) {
  const compact = size !== "page";
  const rows = compact ? 1 : 2;

  return (
    <div aria-hidden className={`${frame[size]} bg-white text-zinc-900 dark:bg-zinc-900 dark:text-zinc-100`}>
      <div className="flex items-center justify-between border-b border-zinc-200 px-3 py-2 dark:border-white/10">
        <span className="text-xs font-semibold">Неделя</span>
        <span className="text-xs font-semibold text-sky-700 dark:text-sky-300">{preview.stat} неявки</span>
      </div>
      <div className={compact ? "p-2" : "p-4"}>
        <div className={`grid gap-1 ${compact ? "grid-cols-5" : "grid-cols-[36px_repeat(5,1fr)]"}`}>
          {compact ? null : <span />}
          {preview.columns.map((column) => (
            <p key={column.day} className="text-center text-[10px] text-zinc-500">
              {column.day}
            </p>
          ))}
        </div>
        {Array.from({ length: rows }, (_, row) => (
          <div key={row} className={`mt-1 grid gap-1 ${compact ? "grid-cols-5" : "grid-cols-[36px_repeat(5,1fr)]"}`}>
            {compact ? null : (
              <p className="self-center text-[10px] text-zinc-400">{row === 0 ? "10:00" : "14:00"}</p>
            )}
            {preview.columns.map((column) => {
              const item = column.items[row];
              if (!item) {
                return <div key={`${column.day}-${row}`} className="h-7 rounded bg-zinc-100 dark:bg-white/5" />;
              }
              return (
                <p
                  key={`${column.day}-${item.label}`}
                  className={`truncate rounded px-1 py-1.5 text-center text-[10px] font-medium ${lessonTone[item.tone]}`}
                >
                  {item.label}
                </p>
              );
            })}
          </div>
        ))}
      </div>
      {compact ? null : (
        <p className="mx-4 mb-4 w-fit rounded-full bg-sky-500/10 px-3 py-1 text-xs font-medium text-sky-800 dark:text-sky-200">
          {preview.reminder}
        </p>
      )}
    </div>
  );
}

function barWidth(hours: string) {
  const value = Number.parseInt(hours, 10);
  if (value >= 10) return "w-full";
  if (value >= 6) return "w-3/5";
  return "w-1/3";
}

function EstimateMock({ preview, size }: { preview: EstimatePreview; size: MockSize }) {
  const compact = size !== "page";

  return (
    <div aria-hidden className={`${frame[size]} bg-neutral-950 text-white`}>
      <div className="flex items-center justify-between px-3 py-2 text-[11px] text-neutral-400">
        <span>Смета для клиента</span>
        <span className="font-semibold text-amber-300">{preview.stat}</span>
      </div>
      <div className={`space-y-1.5 ${compact ? "px-3" : "px-4 pt-2"}`}>
        {preview.blocks.map((block) => (
          <div key={block.title} className="flex items-center justify-between rounded-md bg-white/5 px-2 py-1.5">
            <span className="w-16 shrink-0 text-[11px]">{block.title}</span>
            <span className="mx-3 h-1.5 flex-1 rounded-full bg-white/10">
              <span className={`block h-1.5 rounded-full bg-amber-300 ${barWidth(block.hours)}`} />
            </span>
            <span className="text-[11px] font-medium">{block.hours}</span>
          </div>
        ))}
      </div>
      {compact ? null : (
        <div className="mx-4 mt-3 flex items-end justify-between border-t border-white/10 pt-3">
          <span className="text-[11px] text-neutral-400">Итого для клиента</span>
          <span className="text-2xl font-semibold">{preview.total}</span>
        </div>
      )}
      <div
        className={`flex items-center justify-between bg-amber-300 text-neutral-950 ${
          compact ? "mx-3 mt-2 rounded-md px-2 py-1.5" : "mx-4 mb-4 mt-3 rounded-lg px-3 py-3"
        }`}
      >
        <span className="text-[11px] font-semibold">Расхождение с фактом</span>
        <span className={`font-semibold ${compact ? "text-sm" : "text-2xl"}`}>{preview.accuracy}</span>
      </div>
    </div>
  );
}

function ShowcaseMock({ preview, size }: { preview: ShowcasePreview; size: MockSize }) {
  const compact = size !== "page";
  const [lead, ...rest] = preview.tiles;

  return (
    <div aria-hidden className={`${frame[size]} bg-[#f6f3ee] text-[#161616] dark:bg-[#101010] dark:text-white`}>
      {compact ? null : (
        <div className="flex items-center justify-between border-b border-black/10 px-5 py-3 dark:border-white/10">
          <span className="text-xs font-semibold">Кейсы</span>
          <span className="rounded-full bg-[#161616] px-3 py-1 text-[11px] font-medium text-white dark:bg-white dark:text-[#161616]">
            Созвон
          </span>
        </div>
      )}
      <div className={`grid grid-cols-5 gap-2 ${compact ? "p-3" : "p-5"}`}>
        <div className="col-span-3 flex flex-col justify-between rounded-md bg-[#161616] p-3 text-white dark:bg-white dark:text-[#161616]">
          <p className={`font-semibold leading-none ${compact ? "text-3xl" : "text-6xl"}`}>{lead?.index}</p>
          <p className={`font-medium ${compact ? "mt-3 text-[11px]" : "mt-6 text-lg"}`}>{lead?.title}</p>
        </div>
        <div className="col-span-2 flex flex-col gap-2">
          {rest.map((tile) => (
            <div key={tile.index} className="flex-1 rounded-md border border-black/10 p-2 dark:border-white/15">
              <p className="text-[10px] text-black/50 dark:text-white/50">{tile.index}</p>
              <p className={`font-medium ${compact ? "text-[11px]" : "mt-2 text-sm"}`}>{tile.title}</p>
            </div>
          ))}
        </div>
      </div>
      <p className={`font-semibold uppercase tracking-[0.14em] ${compact ? "px-3 pb-2 text-[10px]" : "px-5 pb-5 text-xs"}`}>
        Заявка на {preview.stat}
      </p>
    </div>
  );
}
