const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 1100, height: 900 } });
  const page = await ctx.newPage();
  const errs = []; page.on('pageerror', e => errs.push(String(e))); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await ctx.route('**/*', async route => {
    const u = route.request().url();
    if (u.includes('gstatic.com/firebasejs')) return route.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(path.join(__dirname, 'fakefb.js'), 'utf8') });
    if (u.startsWith('https://fonts.')) return route.fulfill({ contentType: 'text/css', body: '' });
    if (u.startsWith('http://app.test/')) { const f = u.replace('http://app.test/', '').split(/[?#]/)[0] || 'index.html'; return route.fulfill({ contentType: f.endsWith('.html') ? 'text/html' : 'text/plain', body: fs.readFileSync(path.join(__dirname, '..', f), 'utf8') }); }
    return route.abort();
  });
  const step = async (name, fn) => { try { await fn(); console.log('ok  ', name); } catch (e) { console.log('FAIL', name, e.message); await page.screenshot({ path: '/tmp/claude-0/-home-claude/f8dc82be-fff1-5272-ba4d-3f9390430d9e/scratchpad/fail.png' }); throw e; } };
  await page.goto('http://app.test/index.html');
  await step('home renders', () => page.waitForSelector('#home-board svg'));
  await step('host click opens gate', async () => { await page.click('[data-role=host]'); await page.waitForSelector('#gate:not([hidden]) #gateForm'); });
  await step('register -> pending', async () => {
    await page.click('[data-mode=register]'); await page.fill('[name=name]', 'أستاذ'); await page.fill('[name=email]', 't@x.com'); await page.fill('[name=password]', '123456');
    await page.click('#gateForm button[type=submit]'); await page.waitForSelector('#gate:not([hidden]) .state');
    const t = await page.textContent('#gateCard'); if (!/بانتظار التفعيل/.test(t)) throw new Error(t);
    const p = await page.evaluate(() => window.__FB.get('users/u_txcom')); if (p.expiresAt) throw new Error('should have no expiry');
  });
  await step('admin activates -> host opens', async () => {
    await page.evaluate(() => window.__FB.set('users/u_txcom/expiresAt', Date.now() + 30 * 86400000));
    await page.waitForSelector('#v-host:not([hidden])');
  });
  let code;
  await step('room code shown', async () => { await page.waitForSelector('#h-room .roomcode'); code = await page.textContent('#h-room .roomcode'); if (!/^\d{6}$/.test(code)) throw new Error('bad code ' + code); });
  await step('acct chip', async () => { const t = await page.textContent('#acct'); if (!/30 يومًا/.test(t)) throw new Error(t); });
  await step('seed questions + start round', async () => {
    await page.evaluate(() => { window.__FB.set('questions/gen', { a1: { letter: 'ب', text: 'س؟', answer: 'بيروت', cat: 'جغرافيا' } }); });
    await page.click('#demo-add'); await page.click('[data-act=start]'); await page.waitForSelector('[data-cell]');
  });
  await step('add custom question', async () => {
    await page.selectOption('#q-letter', 'ت'); await page.fill('#q-text', 'سؤال مخصص؟'); await page.fill('#q-ans', 'تونس'); await page.click('#q-form button[type=submit]');
    await page.waitForFunction(() => document.querySelectorAll('#q-list li').length === 2);
    const c = await page.evaluate(() => window.__FB.get('custom/u_txcom/gen')); if (!c) throw new Error('not in custom path');
    await page.waitForSelector('#q-list [data-delq]');
  });
  await step('switch to play role joins by code', async () => {
    await page.evaluate(() => window.__FB.set('rooms/'+document.querySelector('#h-room .roomcode').textContent+'/players/demo3', null)); await page.waitForFunction(() => document.querySelectorAll('#h-players li').length === 3); await page.click('#chg'); await page.click('[data-role=play]'); await page.waitForSelector('#v-play:not([hidden])');
    const rv = await page.inputValue('#p-room'); if (rv !== code) throw new Error('room not prefilled ' + rv);
    await page.fill('#p-name', 'علي'); await page.click('[data-team=r]'); await page.click('#p-go'); await page.waitForSelector('#p-game:not([hidden])');
  });
  await step('account dialog has no code field', async () => {
    await page.click('#acct'); await page.waitForSelector('#acctdlg:not([hidden])');
    if (await page.$('#acctCard [name=code]')) throw new Error('code field present');
    const t = await page.textContent('#acctCard'); if (!/فعّال حتى/.test(t)) throw new Error(t);
  });
  await step('expired user blocked from host', async () => {
    await page.click('[data-close=acctdlg]');
    await page.evaluate(() => window.__FB.set('users/u_txcom/expiresAt', Date.now() - 1000));
    await page.waitForSelector('#gate:not([hidden]) .state');
    const t = await page.textContent('#gateCard'); if (!/انتهى الاشتراك/.test(t)) throw new Error(t);
  });
  await step('screen role with ?r=', async () => {
    const p2 = await ctx.newPage(); p2.on('pageerror', e => errs.push(String(e)));
    await p2.goto('http://app.test/index.html?r=' + code + '#screen'); await p2.waitForSelector('#v-screen:not([hidden])');
    await p2.waitForSelector('#sc-code:not([hidden])'); await p2.close();
  });
  await step('play role w/o code asks for it', async () => {
    const p3 = await ctx.newPage(); await p3.evaluate(() => 0).catch(() => 0);
    await p3.goto('http://app.test/index.html'); await p3.evaluate(() => { localStorage.clear(); location.hash = '#play'; }); await p3.reload();
    await p3.waitForSelector('#roomdlg:not([hidden])'); await p3.fill('#room-in', '654321'); await p3.click('#room-go'); await p3.waitForSelector('#v-play:not([hidden])'); await p3.close();
  });
  console.log('errors:', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
