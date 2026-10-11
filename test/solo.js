const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const OUT = '/tmp/claude-0/-home-claude-huroof-app-github-io/f8dc82be-fff1-5272-ba4d-3f9390430d9e/scratchpad/';
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  await ctx.route('**/*', async route => {
    const u = route.request().url();
    if (u.includes('gstatic.com/firebasejs')) return route.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(path.join(__dirname, 'fakefb.js'), 'utf8') });
    if (u.startsWith('https://fonts.')) return route.fulfill({ contentType: 'text/css', body: '' });
    if (u.startsWith('http://app.test/')) return route.fulfill({ contentType: 'text/html', body: fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8') });
    return route.abort();
  });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('http://app.test/index.html');
  await p.evaluate(() => { window.__FB.users['a0545777031@gmail.com'] = { pw: 'x123456' }; });
  await p.click('[data-role=solo]'); await p.fill('[name=email]', 'a0545777031@gmail.com'); await p.fill('[name=password]', 'x123456'); await p.click('#gateForm button[type=submit]');
  await p.waitForSelector('#v-solo:not([hidden])'); await p.click('[data-act=start]'); await p.click('[data-cell]'); await p.waitForTimeout(400);
  const t1 = await p.textContent('#so-q'); if (!/إظهار الإجابة/.test(t1)) throw new Error('not hidden: ' + t1);
  await p.screenshot({ path: OUT + 'solo-hidden.png' });
  await p.keyboard.press('a'); await p.waitForTimeout(200);
  const t2 = await p.textContent('#so-q'); if (!/إخفاء الإجابة/.test(t2)) throw new Error('not shown');
  await p.click('[data-soans="0"]'); const t3 = await p.textContent('#so-q'); if (!/إظهار الإجابة/.test(t3)) throw new Error('not re-hidden');
  console.log('ok solo hide/show', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
