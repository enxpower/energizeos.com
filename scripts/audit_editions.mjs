import { chromium } from 'playwright';
import fs from 'node:fs';
const origin = process.argv[2] || 'http://127.0.0.1:8765';
const config = JSON.parse(fs.readFileSync('content/intelligence/config.json','utf8'));
const browser = await chromium.launch({headless:true});
fs.mkdirSync('build/visual',{recursive:true});
try {
  const api = await browser.newContext();
  const response = await api.request.get(origin + '/insights/intelligence/issues.json');
  if (!response.ok()) throw Error('Published English manifest unavailable');
  const manifest = await response.json();
  if (manifest.language !== 'en' || manifest.issues.length < 2) throw Error('Complete English publication history required');
  await api.close();
  for (const width of [390,768,1440]) {
    const context = await browser.newContext({viewport:{width,height:1000}});
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    for (const route of ['/insights/','/insights/intelligence/','/insights/intelligence/archive/',...manifest.issues.map(x=>x.url)]) {
      const result = await page.goto(origin + route,{waitUntil:'domcontentloaded'});
      if (!result || result.status() !== 200) throw Error('Unavailable route: ' + route);
      const info = await page.evaluate(()=>({
        width:document.documentElement.scrollWidth,client:document.documentElement.clientWidth,
        text:document.body.innerText,html:document.documentElement.outerHTML,
        canonical:document.querySelector('link[rel="canonical"]')?.href,
        h1:document.querySelectorAll('h1').length,
        currentTop:document.querySelector('.edition-current h3')?.getBoundingClientRect().top,
        sourceCount:document.querySelectorAll('.edition-sources li').length
      }));
      if (info.width > info.client + 1) throw Error('Overflow at '+width+' '+route);
      if (info.h1 !== 1 || info.canonical !== 'https://'+config.domain+route) throw Error('Document identity failed: '+route);
      if (/[\u3400-\u9fff]|\$\{|%%[A-Z_]+%%/.test(info.html)) throw Error('Language/template leakage: '+route);
      if (route === '/insights/') {
        if (info.currentTop > 1000) throw Error('Latest Intelligence is buried below first viewport at '+width);
        for (const label of ['Latest Intelligence','Current Edition','Previous Edition','Next Week’s Watchlist','Browse All Editions']) {
          if (!info.text.toLowerCase().includes(label.toLowerCase())) throw Error('Missing direct reading entry: '+label);
        }
      }
      if (manifest.issues.some(x=>x.url === route)) {
        if (info.sourceCount < 3) throw Error('Article evidence missing');
        await page.locator('.edition-ref').first().click();
        if (!page.url().includes('#source-')) throw Error('Source reference not usable');
      }
      await page.evaluate(()=>window.scrollTo(0,0));
      await page.screenshot({path:'build/visual/'+config.kind+'-'+route.replaceAll('/','_')+'-'+width+'.png',fullPage:true});
    }
    await page.goto(origin+'/insights/');
    await page.locator('.edition-current h3 a').click();
    if (!(new URL(page.url()).pathname === manifest.issues[0].url)) throw Error('Latest edition navigation is indirect or wrong');
    await page.locator('.edition-pagination a').first().click();
    if (!(new URL(page.url()).pathname === manifest.issues[1].url)) throw Error('Previous edition navigation failed');
    if (errors.length) throw Error('Browser errors: '+errors.join('; '));
    await context.close();
  }
  console.log('ENGLISH_EDITION_BROWSER_ACCEPTANCE=PASS viewports=390,768,1440');
} finally {await browser.close();}
