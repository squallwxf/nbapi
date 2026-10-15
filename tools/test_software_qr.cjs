// Run with NODE_PATH pointing to Playwright and jsQR installations.
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const os = require('node:os');
const root = path.resolve(__dirname, '..');
const item = {
  id: 'a'.repeat(32), name: 'NB Mobile', version: '1.0', platform: '跨平台',
  category: 'AI 创作', summary: 'Mobile release', description: 'Install package',
  screenshots: [], published: true, updated_at: 1791849600,
  installers: ['Android', 'iOS', 'Windows'].map((platform, i) => ({
    id: String(i + 1).repeat(32), platform, filename: `tool.${['apk','ipa','exe'][i]}`,
    size: 1024, sha256: '0'.repeat(64),
    downloadUrl: `/api/software/${'a'.repeat(32)}/download/${String(i + 1).repeat(32)}`,
  })),
};
(async () => {
  const browser = await chromium.launch({ headless: true, ...(process.env.QR_TEST_CHROME ? { executablePath: process.env.QR_TEST_CHROME } : {}) });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    let published = true;
    await page.route('https://nbapi.win/**', async route => {
      const url = new URL(route.request().url());
      if (url.pathname === '/api/software') return route.fulfill({ json: { items: [{ ...item, published }] } });
      if (url.pathname.startsWith('/assets/')) {
        return route.fulfill({ path: path.join(root, url.pathname), contentType: url.pathname.endsWith('.css') ? 'text/css; charset=utf-8' : 'text/javascript; charset=utf-8' });
      }
      const source = fs.readFileSync(path.join(root, 'api-website.html'), 'utf8');
      const section = source.slice(source.indexOf('<section id="downloads"'), source.indexOf('</section>', source.indexOf('id="softwareEditor"')) + 10);
      return route.fulfill({ contentType: 'text/html; charset=utf-8', body: `<html><head><meta charset="utf-8"><link rel="stylesheet" href="/assets/nbapi.css"></head><body><main>${section}</main><button id="authLogout" hidden></button><script src="/assets/qrcode.js"></script><script src="/assets/software.js"></script></body></html>` });
    });
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.goto('https://nbapi.win/#downloads');
      await page.waitForSelector('.software-qr img');
      assert.equal(await page.locator('#softwareGrid .software-qr').count(), 2);
      assert.equal(await page.locator('#softwareGrid .software-download a').count(), 3);
      await page.addScriptTag({ path: require.resolve('jsqr/dist/jsQR.js') });
      const decoded = await page.locator('#softwareGrid .software-qr img').evaluateAll(async imgs => {
        return Promise.all(imgs.map(async img => {
          await img.decode();
          const canvas = document.createElement('canvas');
          canvas.width = img.naturalWidth; canvas.height = img.naturalHeight;
          const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0);
          return jsQR(ctx.getImageData(0, 0, canvas.width, canvas.height).data, canvas.width, canvas.height)?.data;
        }));
      });
      assert.deepEqual(decoded, item.installers.slice(0, 2).map(p => 'https://nbapi.win' + p.downloadUrl));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      await page.locator('[data-detail]').click();
      assert.equal(await page.locator('#softwareDetail .software-qr').count(), 2);
      assert.match(await page.locator('#softwareDetail').innerText(), /IPA 安装需有效签名/);
      await page.screenshot({ path: path.join(os.tmpdir(), `nbapi-software-qr-${width}.png`), fullPage: true });
    }
    published = false;
    await page.reload();
    await page.waitForSelector('[data-detail]');
    assert.equal(await page.locator('.software-qr').count(), 0);
    assert.deepEqual(errors, []);
    console.log('PASS: desktop/mobile QR decoding, layout, detail and draft visibility');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
