const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 1100, height: 900 } });
  const errs = [];
  await ctx.route('**/*', async route => {
    const u = route.request().url();
    if (u.includes('gstatic.com/firebasejs')) return route.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(path.join(__dirname, 'fakefb.js'), 'utf8') });
    if (u.startsWith('https://fonts.')) return route.fulfill({ contentType: 'text/css', body: '' });
    if (u.startsWith('http://app.test/')) { const f = u.replace('http://app.test/', '').split(/[?#]/)[0] || 'index.html'; return route.fulfill({ contentType: 'text/html', body: fs.readFileSync(path.join(__dirname, '..', f), 'utf8') }); }
    return route.abort();
  });
  const page = await ctx.newPage(); page.on('pageerror', e => errs.push(String(e))); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  page.on('dialog', d => d.accept());
  const step = async (name, fn) => { try { await fn(); console.log('ok  ', name); } catch (e) { console.log('FAIL', name, e.message); await page.screenshot({ path: '/tmp/claude-0/-home-claude/f8dc82be-fff1-5272-ba4d-3f9390430d9e/scratchpad/fail.png' }); throw e; } };
  await page.goto('http://app.test/admin.html');
  await step('non-admin rejected', async () => {
    await page.evaluate(() => { window.__FB.users['x@y.com'] = { pw: '123456' }; window.__FB.set('users/u_xycom', { email: 'x@y.com', name: 'زيد', createdAt: 1, room: '111111' }); });
    await page.fill('[name=email]', 'x@y.com'); await page.fill('[name=password]', '123456'); await page.click('#f button');
    await page.waitForSelector('#gateCard .msg.err'); await page.click('#so');
  });
  await step('admin login', async () => {
    await page.waitForSelector('#f');
    await page.evaluate(() => { window.__FB.users['a0545777031@gmail.com'] = { pw: 'secret1' }; });
    await page.fill('[name=email]', 'a0545777031@gmail.com'); await page.fill('[name=password]', 'secret1'); await page.click('#f button');
    await page.waitForSelector('#app:not([hidden])'); await page.waitForSelector('#users tr[data-id]');
  });
  await step('pending shown', async () => { const t = await page.textContent('#users tr[data-id=u_xycom]'); if (!/بانتظار التفعيل/.test(t)) throw new Error(t); });
  await step('activate 30 days with note', async () => {
    await page.fill('#users tr[data-id=u_xycom] [data-note]', 'تقناس #1042');
    await page.click('#users tr[data-id=u_xycom] [data-activate]');
    await page.waitForFunction(() => window.__FB.get('users/u_xycom/expiresAt') > Date.now() + 29 * 86400000);
    const subs = await page.evaluate(() => window.__FB.get('subs/u_xycom')); const v = Object.values(subs)[0]; if (v.days !== 30 || v.note !== 'تقناس #1042') throw new Error(JSON.stringify(v));
    await page.waitForFunction(() => /فعّال · 30/.test(document.querySelector('#users tr[data-id=u_xycom]').textContent));
  });
  await step('custom days adds to remaining', async () => {
    await page.selectOption('#users tr[data-id=u_xycom] [data-days]', 'custom');
    await page.fill('#users tr[data-id=u_xycom] [data-custom]', '10');
    await page.click('#users tr[data-id=u_xycom] [data-activate]');
    await page.waitForFunction(() => /فعّال · 40/.test(document.querySelector('#users tr[data-id=u_xycom]').textContent));
  });
  await step('end subscription', async () => {
    await page.click('#users tr[data-id=u_xycom] [data-end]');
    await page.waitForFunction(() => /منتهٍ/.test(document.querySelector('#users tr[data-id=u_xycom]').textContent));
  });
  await step('block / unblock', async () => {
    await page.click('#users tr[data-id=u_xycom] [data-block]'); await page.waitForSelector('#users tr[data-id=u_xycom] [data-unblock]');
    await page.click('#users tr[data-id=u_xycom] [data-unblock]'); await page.waitForSelector('#users tr[data-id=u_xycom] [data-block]');
  });
  await step('import bank', async () => {
    await page.click('[data-tab=bank]');
    await page.setInputFiles('#b-file', path.join(__dirname, 'banks-p4-6.json'));
    await page.waitForFunction(() => /جاهزًا للاستيراد/.test(document.querySelector('#b-msg').textContent));
    console.log('   ', await page.textContent('#b-msg'));
    await page.click('#b-import');
    await page.waitForFunction(() => /تم استيراد/.test(document.querySelector('#b-msg').textContent), null, { timeout: 60000 });
    const n = await page.evaluate(() => Object.keys(window.__FB.get('questions/p4')).length + Object.keys(window.__FB.get('questions/p5')).length + Object.keys(window.__FB.get('questions/p6')).length);
    console.log('   imported', n);
    const one = await page.evaluate(() => { const q = window.__FB.get('questions/p4'); return q[Object.keys(q)[0]]; }); console.log('   sample', JSON.stringify(one));
    await page.waitForFunction(() => document.querySelectorAll('#banks .stat').length === 3);
  });
  await page.screenshot({ path: '/tmp/claude-0/-home-claude/f8dc82be-fff1-5272-ba4d-3f9390430d9e/scratchpad/admin.png' });
  console.log('errors:', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
