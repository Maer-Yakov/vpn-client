import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createElement as h } from "react";
import ts from "typescript";
import { createRequire } from "node:module";

const { ImageResponse } = createRequire(import.meta.url)("next/og");

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const source = await readFile(join(root, "data/projects.ts"), "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
}).outputText;
const temp = join(tmpdir(), `portfolio-projects-${process.pid}.mjs`);
await writeFile(temp, compiled);
const { projects } = await import(pathToFileURL(temp).href);
const font = await readFile(join(root, "fonts/Inter-600.ttf"));

function card({ kicker, title, line }) {
  return h(
    "div",
    {
      style: {
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        background: "#0a0a0a",
        color: "#fafafa",
        padding: "72px",
        fontFamily: "Inter",
      },
    },
    h(
      "div",
      { style: { display: "flex", alignItems: "center", fontSize: 28, color: "#a3a3a3" } },
      h("div", {
        style: { width: 14, height: 14, borderRadius: 99, background: "#6366f1", marginRight: 16 },
      }),
      "Портфолио",
    ),
    h(
      "div",
      { style: { display: "flex", flexDirection: "column", width: 1040 } },
      h("div", { style: { fontSize: 28, color: "#818cf8" } }, kicker),
      h("div", { style: { marginTop: 18, fontSize: 68, fontWeight: 600, lineHeight: 1.05 } }, title),
    ),
    h("div", { style: { fontSize: 32, lineHeight: 1.35, color: "#d4d4d4", width: 1040 } }, line),
  );
}

async function writeImage(name, input) {
  const response = new ImageResponse(card(input), {
    width: 1200,
    height: 630,
    fonts: [{ name: "Inter", data: font, weight: 600 }],
  });
  const bytes = Buffer.from(await response.arrayBuffer());
  const path = join(root, "public/og", name);
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, bytes);
}

await writeImage("home.png", {
  kicker: "Для фрилансеров и частных практик",
  title: "Сервис, инструмент или сайт под одну боль",
  line: "В каждом кейсе есть цифра, по которой видно результат.",
});

for (const project of projects) {
  await writeImage(`${project.slug}.png`, {
    kicker: `${project.type} · ${project.preview.stat}`,
    title: project.name,
    line: project.offer,
  });
}
