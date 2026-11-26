// Browser-Test der Einwilligung (seit 0.28, tests/test_einwilligung_028.py startet ihn): prüft im echten Browser
// (Chromium über Playwright), dass vor der Zustimmung keine Anfrage an Google geht. Alle Anfragen ausser an den
// lokalen Testserver werden abgefangen, aufgezeichnet und abgebrochen (es geht nie etwas ins Internet).
// Aufruf: node tests/browser/einwilligung.js http://localhost:PORT/vorschau  → JSON mit den Beobachtungen.
const { chromium } = require('playwright');

(async () => {
  const basis = process.argv[2];
  const browser = await chromium.launch();
  const aus = {};
  const extern = [];
  async function kontext(js) {
    const ctx = await browser.newContext({ javaScriptEnabled: js });
    await ctx.route('**/*', (route) => {
      const url = route.request().url();
      if (url.startsWith(basis.split('/vorschau')[0])) { return route.continue(); }
      extern.push(url);
      return route.abort();
    });
    return ctx;
  }
  const google = () => extern.filter((u) => /google/.test(u));
  const keks = async (ctx) => Object.fromEntries((await ctx.cookies()).map((c) => [c.name, c.value]));

  const ctx = await kontext(true);
  const seite = await ctx.newPage();
  await seite.goto(basis + '/de/impressum/', { waitUntil: 'load' });
  await seite.waitForTimeout(300);
  aus.vorher_google = google().length;
  aus.vorher_hinweis = await seite.isVisible('[data-cookie-hinweis]');
  aus.vorher_cookies = Object.keys(await keks(ctx));
  aus.tab_reihenfolge = await seite.$$eval('[data-cookie-hinweis] button', (b) => b.map((x) => x.textContent.trim()));

  await seite.click('[data-cookie-hinweis] [data-cookie-wahl="zugestimmt"]');
  await seite.waitForTimeout(300);
  aus.nach_zustimmung_google = google();
  aus.nach_zustimmung_hinweis = await seite.isVisible('[data-cookie-hinweis]');
  aus.nach_zustimmung_wahl = (await keks(ctx)).cookie_wahl || '';

  await seite.reload({ waitUntil: 'load' });
  await seite.waitForTimeout(300);
  aus.neu_geladen_hinweis = await seite.isVisible('[data-cookie-hinweis]');
  aus.neu_geladen_google = google().length;

  // Widerruf auf der Seite Cookie-Einstellungen: Analyse-Cookies (hier nachgestellt) werden gelöscht
  const host = new URL(basis).hostname;
  await ctx.addCookies([{ name: '_ga', value: 'GA1.1.123', domain: host, path: '/' },
                        { name: '_ga_TEST12345', value: 'GS1.1.123', domain: host, path: '/' }]);
  await seite.goto(basis + '/de/cookie-einstellungen/', { waitUntil: 'load' });
  aus.einstellungen_status_vorher = (await seite.textContent('[data-cookie-status]')).trim();
  aus.einstellungen_hinweis = await seite.$$eval('[data-cookie-hinweis]', (h) => h.length);
  const zaehler = google().length;
  await seite.click('[data-cookie-seite] [data-cookie-wahl="abgelehnt"]');
  await seite.waitForTimeout(200);
  aus.widerruf_status = (await seite.textContent('[data-cookie-status]')).trim();
  aus.widerruf_gedrueckt = await seite.getAttribute('[data-cookie-wahl="abgelehnt"]', 'aria-pressed');
  aus.widerruf_cookies = await keks(ctx);
  await seite.goto(basis + '/de/methodik/', { waitUntil: 'load' });
  await seite.waitForTimeout(300);
  aus.nach_widerruf_google_neu = google().length - zaehler;
  aus.nach_widerruf_hinweis = await seite.isVisible('[data-cookie-hinweis]');
  await ctx.close();

  // Ohne JavaScript: kein Hinweis, nichts von Google; die Einstellungen funktionieren über das Formular
  const ohne = await kontext(false);
  const s2 = await ohne.newPage();
  const vorZaehler = google().length;
  await s2.goto(basis + '/de/impressum/', { waitUntil: 'load' });
  aus.ohne_js_hinweis = await s2.isVisible('[data-cookie-hinweis]');
  await s2.goto(basis + '/de/cookie-einstellungen/', { waitUntil: 'load' });
  await Promise.all([s2.waitForNavigation({ waitUntil: 'load' }), s2.click('[data-cookie-wahl="zugestimmt"]')]);
  aus.ohne_js_status = (await s2.textContent('[data-cookie-status]')).trim();
  aus.ohne_js_wahl = (await keks(ohne)).cookie_wahl || '';
  aus.ohne_js_google = google().length - vorZaehler;
  await ohne.close();

  await browser.close();
  console.log(JSON.stringify(aus));
})().catch((e) => { console.error(e); process.exit(1); });
