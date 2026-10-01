const { chromium } = require("playwright");

const pages = ["/", "/dashboard", "/builder", "/console", "/tools", "/history"];
const viewports = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "mobile", width: 375, height: 812 },
];

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  // Wait for dev server
  await page.goto("http://localhost:3000");
  await page.waitForSelector("body", { timeout: 30000 });

  for (const vp of viewports) {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    for (const route of pages) {
      try {
        await page.goto(`http://localhost:3000${route}`, { waitUntil: "networkidle", timeout: 15000 });
        await page.waitForTimeout(1500); // let fonts/animations settle
        const safe = route === "/" ? "root" : route.replace("/", "");
        await page.screenshot({ path: `D:/claude_code/OrchestrAI/frontend/screenshots/${vp.name}/${safe}.png`, fullPage: true });
        console.log(`Screenshot: ${vp.name}/${safe}.png`);
      } catch (err) {
        console.error(`Failed ${vp.name}${route}: ${err.message}`);
      }
    }
  }

  await browser.close();
  console.log("All screenshots captured.");
})();
