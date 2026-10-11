const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const OUT = '/tmp/claude-0/-home-claude-huroof-app-github-io/f8dc82be-fff1-5272-ba4d-3f9390430d9e/scratchpad/';
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 } });
  await ctx.route('**/*', async route => {
    const u = route.request().url();
    if (u.includes('gstatic.com/firebasejs')) return route.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(path.join(__dirname, 'fakefb.js'), 'utf8') });
    if (u.startsWith('https://fonts.')) return route.fulfill({ contentType: 'text/css', body: '' });
    if (u.startsWith('http://app.test/')) return route.fulfill({ contentType: 'text/html', body: fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8') });
    return route.abort();
  });
  const p = await ctx.newPage(); const errs=[]; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('http://app.test/index.html?r=123456#screen');
  await p.waitForSelector('#v-screen:not([hidden])');
  const L=["أ","ب","ت","ث","ج","ح","خ","د","ذ","ر","ز","س","ش","ص","ض","ط","ظ","ع","غ","ف","ق","ك","ل","م","ن"];
  const base={match:"m1",round:1,letters:L,owner:Array(25).fill(""),phase:"open",turn:"g",cell:7,qid:"x",qtext:"ما الطائر الذي يرمز إلى السلام؟",qcat:"عام",seq:3,pickN:1,openTo:"all",tried:[],answering:"",ansTeam:"",secs:10,wins:{g:0,r:0},used:[],fx:{t:"",n:1},winner:"",reused:false,bank:{stage:"",grade:1,term:0,subj:""}};
  const own=base.owner.slice(); [5,6,8,9].forEach(i=>own[i]="g"); [0,12,17].forEach(i=>own[i]="r");
  await p.evaluate(s=>window.__FB.set('rooms/123456/state',s),{...base,owner:own,seq:2,phase:"pick"}); await p.waitForTimeout(300);
  await p.evaluate(s=>window.__FB.set('rooms/123456/state',s),{...base,owner:own}); await p.waitForTimeout(250);
  await p.screenshot({ path: OUT + 'anim-question.png' });
  const own2=own.slice(); own2[7]="g";
  await p.evaluate(s=>window.__FB.set('rooms/123456/state',s),{...base,owner:own2,phase:"roundover",winner:"g",wins:{g:1,r:0},fx:{t:"win",n:2}});
  await p.waitForTimeout(350); await p.screenshot({ path: OUT + 'anim-win1.png' });
  await p.waitForTimeout(1300); await p.screenshot({ path: OUT + 'anim-win2.png' });
  console.log('errors', errs); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
