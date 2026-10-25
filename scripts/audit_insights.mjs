import { chromium } from "playwright";
import fs from "node:fs";

const origin = process.argv[2] || "http://127.0.0.1:8766";
const browser = await chromium.launch({ headless: true });
fs.mkdirSync("build/visual", { recursive: true });

try {
  for (const width of [390, 768, 1440]) {
    const context = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
    const page = await context.newPage();
    const response = await page.goto(origin + "/insights/", { waitUntil: "domcontentloaded" });
    if (!response || response.status() !== 200) throw new Error("ESI Insights unavailable at " + width);
    const state = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      pageTitle: document.title,
      heading: document.querySelector("h1")?.textContent || "",
      mainCount: document.querySelectorAll("main").length,
      canonical: document.querySelector('link[rel="canonical"]')?.getAttribute("href") || "",
      logoOk: Boolean(document.querySelector(".brand img")?.naturalWidth)
    }));
    if (state.scrollWidth > state.clientWidth + 1) throw new Error("Horizontal overflow at " + width);
    if (!state.logoOk) throw new Error("Official ESI mark failed to load at " + width);
    if (state.mainCount !== 1 || !state.heading.includes("Evidence-led engineering")) throw new Error("Broken Insights content at " + width);
    if (state.canonical !== "https://energizeos.com/insights/") throw new Error("Wrong canonical at " + width);
    if (await page.locator('a[href="/insights/"]').count() === 0) throw new Error("Insights navigation missing");
    await page.screenshot({ path: "build/visual/esi-insights-" + width + ".png", fullPage: true });
    await context.close();
  }
  console.log("EnergizeOS Insights Chromium tests PASS at 390 / 768 / 1440 px");
} finally {
  await browser.close();
}
