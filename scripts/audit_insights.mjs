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
      logoOk: Boolean(document.querySelector(".brand svg[viewBox=\"0 0 48 48\"]"))
    }));
    if (state.scrollWidth > state.clientWidth + 1) throw new Error("Horizontal overflow at " + width);
    if (!state.logoOk) throw new Error("Official ESI mark failed to load at " + width);
    if (state.mainCount !== 1 || !state.heading.includes("Evidence-led engineering")) throw new Error("Broken Insights content at " + width);
    if (state.canonical !== "https://energizeos.com/insights/") throw new Error("Wrong canonical at " + width);
    if (await page.locator('a[href="/insights/"]').count() === 0) throw new Error("Insights navigation missing");
    await page.screenshot({ path: "build/visual/esi-insights-" + width + ".png", fullPage: true });
    const toolsResponse = await page.goto(origin + "/insights/tools/", { waitUntil: "networkidle" });
    if (!toolsResponse || toolsResponse.status() !== 200) throw new Error("Engineering tools unavailable at " + width);
    const toolsState = await page.evaluate(() => ({
      width: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      canonical: document.querySelector('link[rel="canonical"]')?.getAttribute("href"),
      hasMark: Boolean(document.querySelector('.brand svg[viewBox="0 0 48 48"]'))
    }));
    if (toolsState.width > toolsState.clientWidth + 1) throw new Error("Tools horizontal overflow at " + width);
    if (!toolsState.hasMark) throw new Error("Official ESI brand mark absent from engineering tools");
    if (toolsState.canonical !== "https://energizeos.com/insights/tools/") throw new Error("Wrong tool canonical");
    await page.locator("#optical-form button").click();
    const optical = await page.locator("#optical-result").innerText();
    if (!optical.includes("10.00 dB required") || !optical.includes("2.00 dB")) throw new Error("Optical loss budget calculation regression");
    await page.locator("#dispatch-form button").click();
    const dispatch = await page.locator("#dispatch-result").innerText();
    if (!dispatch.includes("PASS") || !dispatch.includes("2.03 MWh") || !dispatch.includes("2.00 MWh")) throw new Error("EMS dispatch calculation regression");
    await page.locator('#optical-form input[name="connectors"]').fill("1.5");
    await page.locator("#optical-form button").click();
    if ((await page.locator("#optical-result").getAttribute("data-invalid")) !== "true") throw new Error("Fractional connector count incorrectly accepted");
    await page.locator('#dispatch-form input[name="power"]').fill("2");
    await page.locator("#dispatch-form button").click();
    if (!(await page.locator("#dispatch-result").innerText()).includes("FAIL")) throw new Error("Inverter ceiling violation incorrectly accepted");
    await page.screenshot({ path: "build/visual/esi-tools-" + width + ".png", fullPage: true });
    await context.close();
  }
  console.log("EnergizeOS Insights Chromium tests PASS at 390 / 768 / 1440 px");
} finally {
  await browser.close();
}
