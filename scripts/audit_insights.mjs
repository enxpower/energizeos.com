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
    await page.locator('#optical-form input[name="connectors"]').fill("2");
    await page.locator("#optical-form button").click();
    await page.locator('#dispatch-form input[name="power"]').fill("1");
    await page.locator("#dispatch-form button").click();
    if (!(await page.locator("#optical-result").innerText()).includes("10.00 dB required")) throw new Error("Valid optical case failed after recovery");
    if (!(await page.locator("#dispatch-result").innerText()).includes("PASS")) throw new Error("Valid EMS case failed after recovery");
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(100);
    await page.screenshot({ path: "build/visual/esi-tools-" + width + ".png", fullPage: true });
    const sourceResponse = await page.goto(origin + "/insights/intelligence/", { waitUntil:"networkidle" });
    if (!sourceResponse || sourceResponse.status() !== 200) throw new Error("Optical Intelligence not served at " + width);
    const research = await page.evaluate(() => ({
      width:document.documentElement.scrollWidth,
      client:document.documentElement.clientWidth,
      canonical:document.querySelector('link[rel="canonical"]')?.getAttribute("href") || "",
      brand:Boolean(document.querySelector('.brand svg[viewBox="0 0 48 48"]')),
      count:document.querySelectorAll(".indicator-card").length
    }));
    if (research.width > research.client + 1 || !research.brand || research.count !== 3) throw new Error("Optical research layout, brand or indicators invalid at " + width);
    if (research.canonical !== "https://energizeos.com/insights/intelligence/") throw new Error("Optical research canonical missing");
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({path:"build/visual/esi-optical-intelligence-" + width + ".png",fullPage:true});
    const microgridResponse = await page.goto(origin + "/insights/microgrid-ai/", { waitUntil: "domcontentloaded" });
    if (!microgridResponse || microgridResponse.status() !== 200) throw new Error("Microgrid AI reference unavailable at " + width);
    const architecture = await page.evaluate(() => ({
      scroll: document.documentElement.scrollWidth,
      client: document.documentElement.clientWidth,
      canonical: document.querySelector('link[rel="canonical"]')?.getAttribute("href") || "",
      title: document.querySelector("h1")?.textContent || "",
      logo: Boolean(document.querySelector('.brand svg[viewBox="0 0 48 48"]')),
      rows: document.querySelectorAll(".architecture-row").length,
      tables: document.querySelectorAll(".reference-table").length,
      main: document.querySelectorAll("main").length
    }));
    if (architecture.scroll > architecture.client + 1) throw new Error("Microgrid reference horizontal overflow at " + width);
    if (architecture.canonical !== "https://energizeos.com/insights/microgrid-ai/" || !architecture.logo || architecture.main !== 1) throw new Error("Microgrid brand or SEO structure invalid at " + width);
    if (!architecture.title.includes("Control remains deterministic") || architecture.rows !== 4 || architecture.tables !== 1) throw new Error("Microgrid engineering content incomplete at " + width);
    if (!(await page.locator("body").innerText()).includes("Private API integration")) throw new Error("Commercial API integration explanation missing at " + width);
    if (await page.locator('a[href^="/api/"], a[href*="api-key"], input[name*="api_key"]').count()) throw new Error("A prohibited public API onboarding control appeared");

    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({path:"build/visual/esi-microgrid-ai-" + width + ".png",fullPage:true});
    const contactResponse = await page.goto(origin + "/contact/", {waitUntil:"domcontentloaded"});
    if (!contactResponse || contactResponse.status() !== 200) throw new Error("ESI Contact unavailable at " + width);
    const contactState = await page.evaluate(() => ({
      scroll: document.documentElement.scrollWidth,
      client: document.documentElement.clientWidth,
      canonical: document.querySelector('link[rel="canonical"]')?.getAttribute("href"),
      mark: Boolean(document.querySelector('.brand svg[viewBox="0 0 48 48"]')),
      email: Boolean(document.querySelector('a[href^="mailto:info@energizeos.com"]'))
    }));
    if (contactState.scroll > contactState.client + 1 || contactState.canonical !== "https://energizeos.com/contact/" || !contactState.mark || !contactState.email) throw new Error("ESI Contact acceptance failed at " + width);
    await page.evaluate(() => window.scrollTo(0,0));
    await page.screenshot({path:"build/visual/esi-business-contact-" + width + ".png",fullPage:true});
    await context.close();
  }
  console.log("EnergizeOS Insights Chromium tests PASS at 390 / 768 / 1440 px");
} finally {
  await browser.close();
}
