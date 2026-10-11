#!/usr/bin/env python3
"""Port huroof.html (artifact DB) to a standalone Firebase site: site/index.html"""
import re, pathlib
SRC = pathlib.Path("/tmp/claude-0/-home-claude/f8dc82be-fff1-5272-ba4d-3f9390430d9e/scratchpad/huroof.html")
OUT = pathlib.Path("/home/claude/site/index.html")
h = SRC.read_text(encoding="utf-8")

def rep(old, new, count=1):
    global h
    assert h.count(old) >= 1, "pattern not found: " + old[:80]
    if count == 1:
        assert h.count(old) == 1, "pattern not unique: " + old[:80]
    h = h.replace(old, new)

FB_CONFIG = '{apiKey:"AIzaSyA-AuuHDYeLBylqqfgB5NmCHYVTm9A4rIg",authDomain:"huroof-6fdad.firebaseapp.com",databaseURL:"https://huroof-6fdad-default-rtdb.europe-west1.firebasedatabase.app",projectId:"huroof-6fdad",storageBucket:"huroof-6fdad.firebasestorage.app",messagingSenderId:"958424781295",appId:"1:958424781295:web:66eda2ed26295fce94a61a"}'

# ---- head: meta + firebase scripts ----
rep('<title>حروف التوصيل</title>',
    '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="theme-color" content="#0f8a62">\n<title>حروف التوصيل</title>')

GATE_CSS = r"""
/* ---- account gate / modals ---- */
.gate{position:fixed;inset:0;background:var(--bg);z-index:50;display:flex;align-items:center;justify-content:center;padding:16px;overflow:auto}
.gate[hidden]{display:none}
.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:22px;width:100%;max-width:400px;box-shadow:0 10px 40px rgba(0,0,0,.08)}
.card .logo{font-family:var(--display);font-size:2rem;color:var(--green);margin:0;text-align:center}
.card .sub{color:var(--muted);text-align:center;margin:4px 0 14px}
.card label{display:block;font-size:.9rem;color:var(--muted);margin:10px 0 4px}
.card input{width:100%;box-sizing:border-box}
.card .alt{text-align:center;margin-top:12px;font-size:.92rem;color:var(--muted)}
.card .alt button{background:none;border:0;color:var(--green);font-weight:600;cursor:pointer;padding:0 4px;font:inherit}
.card .msg{margin-top:10px;padding:8px 10px;border-radius:8px;font-size:.92rem}
.card .msg.err{background:var(--red-soft);color:var(--red)}
.card .msg.ok{background:var(--green-soft);color:var(--green)}
.card .block{width:100%;margin-top:12px;min-height:46px;font-size:1.05rem}
.card .state{text-align:center}
.card .state .big{font-size:3rem}
.card .state h3{margin:6px 0}
.card .state p{color:var(--muted)}
.card .code{display:flex;gap:8px;margin-top:8px}
.card .code input{flex:1;text-align:center;letter-spacing:2px;font-size:1.05rem;direction:ltr;text-transform:uppercase}
.card hr{border:0;border-top:1px solid var(--line);margin:14px 0}
.card .x{position:absolute;top:10px;left:12px;background:none;border:0;font-size:1.4rem;cursor:pointer;color:var(--muted)}
.card{position:relative}
.roomcode{font-family:var(--display);font-size:2.2rem;letter-spacing:4px;direction:ltr;display:inline-block;background:var(--cell);border:1px solid var(--cell-line);border-radius:12px;padding:2px 16px;color:var(--cell-fg)}
.roomline{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:6px 0}
.roomline small{color:var(--muted)}
.linkbox{font-size:.85rem;direction:ltr;text-align:left;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:6px 8px;word-break:break-all}
.sc-code{position:fixed;top:10px;left:12px;z-index:5;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:6px 14px;font-size:1rem}
.sc-code b{font-family:var(--display);letter-spacing:3px;direction:ltr;display:inline-block;font-size:1.4rem}
</style>"""
rep('</style>', GATE_CSS)

# ---- header: account chip ----
rep('<button id="chg" class="btn-quiet" type="button" hidden>تغيير الدور</button>',
    '<button id="chg" class="btn-quiet" type="button" hidden>تغيير الدور</button>\n    <button id="acct" class="btn-quiet" type="button" hidden>حسابي</button>')

# ---- home copy: open page on each device -> room code explanation ----
rep('<p>افتح هذه الصفحة نفسها على كل جهاز، ثم اختر الدور.</p>',
    '<p>المدير أو المعلم يسجّل دخوله ويحصل على <b>رمز مسابقة</b> من 6 أرقام. المتسابقون وشاشة العرض يفتحون هذه الصفحة نفسها ويدخلون الرمز، بلا تسجيل.</p>')

# ---- players panel: room code + links ----
rep('<h3>المتسابقون</h3>\n          <ul class="plist" id="h-players"></ul>',
    '<h3>المتسابقون</h3>\n          <div id="h-room"></div>\n          <ul class="plist" id="h-players"></ul>')

# ---- screen: code badge ----
rep('<section id="v-screen" class="col" hidden>',
    '<section id="v-screen" class="col" hidden>\n    <div class="sc-code" id="sc-code" hidden></div>')

# ---- play join: room field ----
rep('<h2>انضم إلى المسابقة</h2>',
    '<h2>انضم إلى المسابقة</h2>\n      <label>رمز المسابقة<input id="p-room" type="text" inputmode="numeric" maxlength="6" autocomplete="off" placeholder="123456" dir="ltr" style="text-align:center;letter-spacing:3px"></label>')

# ---- gate + dialogs before closing wrap ----
GATE_HTML = r"""
<div class="gate" id="gate" hidden><div class="card" id="gateCard"></div></div>
<div class="gate" id="roomdlg" hidden><div class="card">
  <button class="x" type="button" data-close="roomdlg" aria-label="إغلاق">×</button>
  <p class="logo">حروف التوصيل</p>
  <p class="sub">اكتب رمز المسابقة الذي يعرضه المدير</p>
  <input id="room-in" type="text" inputmode="numeric" maxlength="6" dir="ltr" style="text-align:center;letter-spacing:4px;font-size:1.4rem" placeholder="123456" autocomplete="off">
  <button class="btn-gold block" type="button" id="room-go">متابعة</button>
  <p class="err" id="room-err" role="alert"></p>
</div></div>
<div class="gate" id="acctdlg" hidden><div class="card" id="acctCard"></div></div>
</div>"""
# the wrap closes right before the script
rep('</div>\n\n<script>\n(function(){', GATE_HTML + '\n<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js"></script>\n<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-auth-compat.js"></script>\n<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-database-compat.js"></script>\n<script>\n(function(){')

# ---- firebase init after helpers ----
rep('function lsSet(k,v){try{localStorage.setItem(k,v);}catch(e){}}',
    'function lsSet(k,v){try{localStorage.setItem(k,v);}catch(e){}}\n'
    'var FB_CONFIG=' + FB_CONFIG + ';\n'
    'var ADMIN_EMAIL="a0545777031@gmail.com",DAY=86400000;\n'
    'firebase.initializeApp(FB_CONFIG);var auth=firebase.auth(),fdb=firebase.database();auth.languageCode="ar";\n'
    'var TS=firebase.database.ServerValue.TIMESTAMP;\n'
    'var ERR={"auth/invalid-email":"البريد الإلكتروني غير صحيح","auth/user-not-found":"لا يوجد حساب بهذا البريد","auth/wrong-password":"كلمة المرور غير صحيحة","auth/invalid-credential":"البريد أو كلمة المرور غير صحيحة","auth/email-already-in-use":"هذا البريد مسجّل مسبقًا — سجّل الدخول","auth/weak-password":"كلمة المرور قصيرة (6 أحرف على الأقل)","auth/too-many-requests":"محاولات كثيرة، حاول لاحقًا","auth/network-request-failed":"تعذّر الاتصال بالإنترنت"};\n'
    'function errMsg(e){return ERR[e&&e.code]||("حدث خطأ: "+(e&&(e.code||e.message)||e));}\n'
    'function fmtDate(ms){return ms?new Date(ms).toLocaleDateString("ar-SA-u-nu-latn",{year:"numeric",month:"long",day:"numeric"}):"—";}\n'
    'var me={user:null,profile:null,admin:false,room:""};\n'
    'function subscribed(){return me.admin||(me.profile&&!me.profile.blocked&&me.profile.expiresAt>Date.now());}\n'
    'function daysLeft(){return me.profile&&me.profile.expiresAt?Math.max(0,Math.ceil((me.profile.expiresAt-Date.now())/DAY)):0;}')

# ---- replace makeDb with makeFb ----
start = h.index('function makeDb(db){')
end = h.index('function onWriteError(e){')
MAKEFB = r'''function bankKey(b){return b&&b.stage?b.stage+(+b.grade||1):"gen";}
function makeFb(code){
  var R=fdb.ref("rooms/"+code),chain=Promise.resolve(),qsub=null;
  function q(fn){chain=chain.then(fn,fn);return chain;}
  function w(fn){var p=q(fn);p.catch(onWriteError);return p;}
  function dead(e){onWriteError(e);}
  function list(snap){var v=snap.val()||{};return Object.keys(v).map(function(id){return Object.assign({id:id},v[id]);});}
  function uid(){return auth.currentUser?auth.currentUser.uid:"";}
  return {mode:"db",room:code,
    watchState:function(f){R.child("state").on("value",function(s){f(s.exists()?clone(s.val()):null);},dead);},
    setState:function(s){var body=clone(s);return w(function(){return R.child("state").set(body);});},
    watchPlayers:function(f){R.child("players").on("value",function(s){f(list(s));},dead);},
    setPlayer:function(id,d){return q(function(){return R.child("players/"+id).set(clone(d));});},
    updatePlayer:function(id,d){return q(function(){return R.child("players/"+id).update(clone(d));});},
    delPlayer:function(id){return w(function(){return R.child("players/"+id).remove();});},
    watchQuestions:function(f,bank){
      if(qsub){qsub.forEach(function(u){u();});qsub=null;}
      if(!uid()){f([]);return;}
      var key=bankKey(bank),base=[],mine=[];
      function emit(){f(base.concat(mine));}
      var r1=fdb.ref("questions/"+key),r2=fdb.ref("custom/"+uid()+"/"+key);
      var h1=function(s){base=list(s);emit();},h2=function(s){mine=list(s).map(function(x){x.mine=true;x._k=key;return x;});emit();};
      r1.on("value",h1,function(e){base=[];emit();dead(e);});r2.on("value",h2,dead);
      qsub=[function(){r1.off("value",h1);},function(){r2.off("value",h2);}];
    },
    addQuestion:function(x){return fdb.ref("custom/"+uid()+"/"+bankKey(x)).push(clone(x)).then(function(){});},
    delQuestion:function(id){var x=custom.filter(function(c){return c.id===id;})[0];if(!x||!x.mine)return Promise.reject(new Error("not-mine"));return fdb.ref("custom/"+uid()+"/"+x._k+"/"+id).remove();},
    lock:function(id,holder){return R.child("locks/"+id).transaction(function(cur){return cur===null?holder:undefined;}).then(function(r){return !!r.committed;});}
  };
}
'''
h = h[:start] + MAKEFB + h[end:]

rep('''  showBanner(code==="invalid_argument"||code==="not_granted"||code==="revoked"
    ?"تعذّر الحفظ: هذا الحساب لا يملك صلاحية الكتابة في المسابقة. اطلب من صاحب الصفحة منحك صلاحية «مساهم»."
    :"تعذّر الاتصال بالخادم. تحقق من الإنترنت ثم أعد المحاولة.");''',
    '''  var m=String(e&&(e.code||e.message)||"");
  showBanner(/PERMISSION_DENIED|permission/i.test(m)
    ?"تعذّر الحفظ: انتهى اشتراكك أو لا تملك صلاحية هذا الإجراء. افتح «حسابي» للتفعيل."
    :"تعذّر الاتصال بالخادم. تحقق من الإنترنت ثم أعد المحاولة.");''')

# ---- state normalisation (RTDB drops empty arrays) ----
rep('function onState(st){\n  S=st;',
    'function onState(st){\n  if(st){st.tried=st.tried||[];st.used=st.used||[];st.owner=st.owner||new Array(25).fill("");st.wins=st.wins||{g:0,r:0};st.fx=st.fx||{t:"",n:0};for(var i=0;i<25;i++)if(st.owner[i]==null)st.owner[i]="";}\n  S=st;')

# ---- delete button only for own questions ----
rep('''</span></span><button type="button" class="btn-quiet" data-delq="'+esc(q.id)+'">حذف</button></li>';''',
    '''</span></span>'+(q.mine?'<button type="button" class="btn-quiet" data-delq="'+esc(q.id)+'">حذف</button>':'')+'</li>';''')
rep('"في البنك العام "+BANK.length+" سؤالًا أساسيًا. المحمّل الآن من بنك المناهج: "+custom.length+" سؤالًا"',
    '"في البنك العام "+BANK.length+" سؤالًا أساسيًا. المحمّل الآن من البنك المختار: "+custom.length+" سؤالًا (منها "+custom.filter(function(q){return q.mine;}).length+" من إضافتك)"')

# ---- host: room code + links in players panel ----
rep('function renderHost(){\n  if(!S)return;',
    'function renderHost(){\n  if(!S)return;\n  $("h-room").innerHTML=roomHTML();')
rep('function renderQList(){',
    '''function siteURL(){return location.origin+location.pathname;}
function roomHTML(){
  var c=Store.room||"";if(!c)return "";
  return '<div class="roomline"><span>رمز المسابقة</span><span class="roomcode">'+esc(c)+'</span></div>'
    +'<p class="muted">يفتح المتسابقون الرابط من جوالاتهم ويكتبون الرمز، أو يستخدمون الرابط المباشر:</p>'
    +'<div class="linkbox">'+esc(siteURL()+"?r="+c+"#play")+'</div>'
    +'<p class="muted">شاشة العرض (تلفاز أو بروجكتر):</p><div class="linkbox">'+esc(siteURL()+"?r="+c+"#screen")+'</div>';
}
function renderQList(){''')

# screen code badge
rep('''  if(role==="screen"){$("sc-score").innerHTML=scoreHTML(S);$("sc-board").innerHTML=boardSVG(S,false);$("sc-q").innerHTML=qbarHTML(S);}''',
    '''  if(role==="screen"){$("sc-score").innerHTML=scoreHTML(S);$("sc-board").innerHTML=boardSVG(S,false);$("sc-q").innerHTML=qbarHTML(S);
    var sb=$("sc-code");sb.hidden=!(Store.room&&(!S||S.phase==="lobby"||S.phase==="roundover"));if(!sb.hidden)sb.innerHTML='رمز المسابقة <b>'+esc(Store.room)+'</b>';}''')

# ---- setRole: auth / room gating ----
rep('''function setRole(r){
  role=r;''',
    '''function setRole(r){
  if((r==="host"||r==="solo")&&!(me.user&&subscribed())){pendingRole=r;openGate();return;}
  if((r==="screen"||r==="play")&&Store.mode!=="db"){pendingRole=r;openRoom();return;}
  role=r;
  location.hash=r?"#"+r:"";''')
rep('''  if(r==="solo")$("banner").hidden=true; else if(Store.mode==="local")$("banner").hidden=false;''',
    '''  $("banner").hidden=true;''')
rep('''    if(Store.mode==="db"&&!lsGet("huroof-snd")){soundOn=false;syncSnd();}''',
    '''    if(!lsGet("huroof-snd")){soundOn=false;syncSnd();}''')

# ---- play join: read room field ----
rep('''$("p-go").addEventListener("click",function(){
  var name=$("p-name").value.trim(),err=$("p-err");''',
    '''$("p-go").addEventListener("click",function(){
  var name=$("p-name").value.trim(),err=$("p-err"),rc=$("p-room").value.trim();
  if(!/^\\d{6}$/.test(rc)){err.textContent="اكتب رمز المسابقة (6 أرقام).";return;}
  if(rc!==Store.room){connect(rc);err.textContent="";return $("p-go").click();}''')

# ---- replace boot ----
start = h.index('/* ---------- boot ---------- */')
end = h.index('})();\n</script>')
BOOT = r'''/* ---------- boot: account, room, connection ---------- */
$("q-letter").innerHTML=LETTERS.map(function(L){return '<option value="'+L+'">'+(L==="ه"?"هـ":L)+'</option>';}).join("");
myId=lsGet("huroof-pid")||rid("p");lsSet("huroof-pid",myId);
if(lsGet("huroof-snd")==="0")soundOn=false;
syncSnd();render();renderQList();
var pendingRole="",gateMode="login",userRef=null,wired=false;
Store=makeLocal();Store.mode="wait";
$("mode-chip").textContent="غير متصل بمسابقة";

function connect(code){
  code=String(code||"").trim();if(!/^\d{6}$/.test(code))return;
  if(Store.mode==="db"&&Store.room===code)return;
  if(Store.mode==="db"){fdb.ref("rooms/"+Store.room).off();}
  Store=makeFb(code);lsSet("huroof-room",code);S=null;players=[];custom=[];lastBankKey="";fxSeen=null;
  $("mode-chip").textContent="مسابقة "+code;
  Store.watchState(onState);
  Store.watchPlayers(function(list){players=list;render();hostReact();});
  $("p-room").value=code;render();
}
function openRoom(){var d=$("roomdlg");d.hidden=false;$("room-in").value=lsGet("huroof-room")||"";$("room-err").textContent="";setTimeout(function(){$("room-in").focus();},50);}
$("room-go").addEventListener("click",function(){
  var v=$("room-in").value.trim();if(!/^\d{6}$/.test(v)){$("room-err").textContent="الرمز 6 أرقام.";return;}
  connect(v);$("roomdlg").hidden=true;if(pendingRole){var r=pendingRole;pendingRole="";setRole(r);}
});
$("room-in").addEventListener("keydown",function(e){if(e.key==="Enter")$("room-go").click();});
document.addEventListener("click",function(e){var t=e.target.closest("[data-close]");if(t){$(t.dataset.close).hidden=true;pendingRole="";}});

/* --- account gate --- */
function lastEmail(){return lsGet("huroof-email")||"";}
function gateHTML(mode,msg){
  var isReg=mode==="register";
  return '<button class="x" type="button" data-close="gate" aria-label="إغلاق">×</button><p class="logo">حروف التوصيل</p><p class="sub">'+(isReg?"أنشئ حسابك — يُفعَّل بعد إتمام الاشتراك":"سجّل دخول المدير أو المعلم")+'</p>'
  +'<form id="gateForm">'+(isReg?'<label>الاسم</label><input name="name" required autocomplete="name" placeholder="اسمك الكامل">':'')
  +'<label>البريد الإلكتروني</label><input name="email" type="email" dir="ltr" required autocomplete="username email" autocapitalize="none" spellcheck="false" placeholder="name@example.com" inputmode="email" value="'+esc(isReg?"":lastEmail())+'">'
  +'<label>كلمة المرور</label><input name="password" type="password" dir="ltr" required minlength="6" autocomplete="'+(isReg?"new-password":"current-password")+'" placeholder="••••••••">'
  +'<button class="btn-gold block" type="submit">'+(isReg?"إنشاء الحساب":"دخول")+'</button>'
  +(msg?'<div class="msg '+msg.cls+'">'+esc(msg.text)+'</div>':'')+'</form>'
  +'<div class="alt">'+(isReg?'لديك حساب؟ <button type="button" data-mode="login">سجّل الدخول</button>':'ليس لديك حساب؟ <button type="button" data-mode="register">سجّل الآن</button> · <button type="button" data-mode="reset">نسيت كلمة المرور</button>')+'</div>'
  +'<p class="alt" style="margin-top:14px">المتسابقون وشاشة العرض لا يحتاجون حسابًا، يكفيهم رمز المسابقة.</p>';
}
function openGate(){$("gate").hidden=false;renderGate();}
function renderGate(msg){
  var c=$("gateCard");c.innerHTML=gateHTML(gateMode,msg);
  c.querySelector("#gateForm").onsubmit=function(e){
    e.preventDefault();var f=e.target,email=f.email.value.trim(),pw=f.password.value,b=f.querySelector("button[type=submit]");b.disabled=true;b.textContent="…";
    var p=gateMode==="register"
      ?auth.createUserWithEmailAndPassword(email,pw).then(function(cred){
          return cred.user.updateProfile({displayName:f.name.value.trim()}).then(function(){
            return fdb.ref("users/"+cred.user.uid).update({email:email.toLowerCase(),name:f.name.value.trim(),createdAt:TS});});})
      :auth.signInWithEmailAndPassword(email,pw);
    p.then(function(){lsSet("huroof-email",email);},function(err){renderGate({cls:"err",text:errMsg(err)});});
  };
  c.querySelectorAll("[data-mode]").forEach(function(b){b.onclick=function(){
    if(b.dataset.mode==="reset"){var em=c.querySelector("[name=email]").value.trim();if(!em)return renderGate({cls:"err",text:"اكتب بريدك أولًا ثم اضغط «نسيت كلمة المرور»"});
      auth.sendPasswordResetEmail(em).then(function(){renderGate({cls:"ok",text:"أرسلنا رابط إعادة التعيين إلى بريدك"});},function(err){renderGate({cls:"err",text:errMsg(err)});});return;}
    gateMode=b.dataset.mode;renderGate();};});
}
function stateHTML(icon,title,text,extra){return '<button class="x" type="button" data-close="gate" aria-label="إغلاق">×</button><p class="logo">حروف التوصيل</p><div class="state"><div class="big">'+icon+'</div><h3>'+esc(title)+'</h3><p>'+esc(text)+'</p>'+(extra||"")+'<button class="btn-quiet block" id="signOut" type="button">تسجيل الخروج</button></div>';}
function payNote(){return '<p class="muted" style="font-size:.92rem">للاشتراك أو التجديد: أتمّ الطلب من متجر تقناس، وبعد تأكيد السداد يُفعَّل حسابك بالمدة التي اخترتها. البريد المسجّل: <b dir="ltr">'+esc(me.user?me.user.email:"")+'</b></p>';}
function showState(html){var c=$("gateCard");$("gate").hidden=false;c.innerHTML=html;var so=c.querySelector("#signOut");if(so)so.onclick=function(){auth.signOut();};}
function renderAcct(){
  var c=$("acctCard"),p=me.profile||{};
  c.innerHTML='<button class="x" type="button" data-close="acctdlg" aria-label="إغلاق">×</button><p class="logo">حسابي</p>'
    +'<p class="sub">'+esc(me.user.email)+(me.admin?' · مدير المنصة':'')+'</p>'
    +(me.admin?'<p class="msg ok">صلاحية مدير المنصة — بلا انتهاء. <a href="admin.html">لوحة التحكم</a></p>'
      :'<p class="msg '+(subscribed()?"ok":"err")+'">'+(subscribed()?"الاشتراك فعّال حتى "+fmtDate(p.expiresAt)+" (متبقٍ "+daysLeft()+" يومًا)":p.expiresAt?"انتهى الاشتراك بتاريخ "+fmtDate(p.expiresAt):"الحساب بانتظار التفعيل")+'</p>'+payNote())
    +'<button class="btn-quiet block" id="signOut" type="button">تسجيل الخروج</button>';
  c.querySelector("#signOut").onclick=function(){auth.signOut();$("acctdlg").hidden=true;};
}
$("acct").addEventListener("click",function(){if(!me.user){openGate();return;}renderAcct();$("acctdlg").hidden=false;});

function ensureRoom(){
  var uid=me.user.uid,ref=fdb.ref("users/"+uid+"/room");
  return ref.get().then(function(s){
    var code=s.val();
    if(code&&/^\d{6}$/.test(code))return code;
    code=String(Math.floor(100000+Math.random()*900000));
    return ref.set(code).then(function(){return code;});
  }).then(function(code){return fdb.ref("rooms/"+code+"/host").set(uid).then(function(){return code;});});
}
function afterAuthOK(){
  $("gate").hidden=true;$("acct").hidden=false;$("acct").textContent=me.admin?"حسابي · مدير":"حسابي · "+daysLeft()+" يومًا";
  ensureRoom().then(function(code){
    connect(code);
    if(pendingRole){var r=pendingRole;pendingRole="";setRole(r);}
    else{var hsh=(location.hash||"").replace("#","");if(hsh==="host"||hsh==="solo")setRole(hsh);}
  },function(e){showBanner("تعذّر تهيئة المسابقة: "+errMsg(e));});
}
auth.onAuthStateChanged(function(u){
  if(userRef){userRef.off();userRef=null;}
  me.user=u;me.profile=null;me.admin=false;
  if(!u){$("acct").hidden=true;if(role==="host"||role==="solo"){role="";setRole("");}return;}
  var adminP=(u.email||"").toLowerCase()===ADMIN_EMAIL?Promise.resolve(true):fdb.ref("admins/"+u.uid).get().then(function(s){return s.val()===true;},function(){return false;});
  adminP.then(function(isAdmin){
    me.admin=isAdmin;
    userRef=fdb.ref("users/"+u.uid);
    userRef.on("value",function(s){
      var d=s.val();
      if(!d){userRef.update({email:(u.email||"").toLowerCase(),name:u.displayName||"",createdAt:TS}).catch(function(e){showState(stateHTML("⚠️","تعذر إنشاء ملفك",errMsg(e)));});return;}
      me.profile=d;
      if(subscribed()){afterAuthOK();if(!$("acctdlg").hidden)renderAcct();return;}
      $("acct").hidden=false;$("acct").textContent=d.expiresAt?"حسابي · منتهٍ":"حسابي · بانتظار التفعيل";
      if(role==="host"||role==="solo"){role="";setRole("");}
      if(d.blocked)showState(stateHTML("⛔","الحساب موقوف","تم إيقاف حسابك من قِبل إدارة المنصة. تواصل معها لمزيد من التفاصيل."));
      else if(d.expiresAt)showState(stateHTML("⏳","انتهى الاشتراك","انتهى اشتراكك بتاريخ "+fmtDate(d.expiresAt)+".",payNote()));
      else showState(stateHTML("🕒","تم إنشاء حسابك","حسابك بانتظار التفعيل من إدارة المنصة.",payNote()));
    },function(err){showState(stateHTML("⚠️","تعذر التحقق",errMsg(err)));});
  });
});

/* --- URL: ?r=CODE#role --- */
(function(){
  var m=/[?&]r=(\d{6})/.exec(location.search),h0=(location.hash||"").replace("#","");
  var code=m?m[1]:"";
  if(code){connect(code);}
  if(h0==="screen"||h0==="play"){if(code||lsGet("huroof-room")){if(!code)connect(lsGet("huroof-room"));setRole(h0);}else{pendingRole=h0;openRoom();}}
  else if(h0==="host"||h0==="solo"){pendingRole=h0;setTimeout(function(){if(!me.user)openGate();},1500);}
})();
'''
h = h[:start] + BOOT + h[end:]


# ---- teacher mode: hide answer until the teacher reveals it (screen is projected) ----
rep("""  if((S.phase==="open"||S.phase==="answer")&&q)hq+='<div class="ans"><small class="muted">الإجابة'+(q.src?' · '+esc(q.src):'')+'</small><br><b>'+esc(q.answer)+'</b>'+(q.alt?' <span class="muted">أو: '+esc(q.alt)+'</span>':'')+'</div>';""",
"""  if(soQid!==S.qid){soQid=S.qid;soShow=false;}
  if((S.phase==="open"||S.phase==="answer")&&q)hq+=soShow
    ?'<div class="ans"><small class="muted">الإجابة'+(q.src?' · '+esc(q.src):'')+'</small><br><b>'+esc(q.answer)+'</b>'+(q.alt?' <span class="muted">أو: '+esc(q.alt)+'</span>':'')+'<br><button type="button" class="btn-quiet" data-soans="0">إخفاء الإجابة</button></div>'
    :'<div class="ans"><button type="button" class="btn-quiet" data-soans="1">👁 إظهار الإجابة</button> <small class="muted">مخفية عن الطلاب · اختصار: حرف A</small></div>';""")
rep("function renderSolo(){","var soShow=false,soQid=\"\";\nfunction renderSolo(){")
rep("""  var t=e.target.closest("[data-role],[data-act],[data-cell],[data-grant],[data-kick],[data-buzz],[data-delq],[data-pick],[data-team]");""",
"""  var sa=e.target.closest("[data-soans]");if(sa){soShow=sa.dataset.soans==="1";renderSolo();return;}
  var t=e.target.closest("[data-role],[data-act],[data-cell],[data-grant],[data-kick],[data-buzz],[data-delq],[data-pick],[data-team]");""")
rep("""    if(S.phase==="open"&&(e.key==="ArrowRight"||e.key==="g"||e.key==="G")){Act.team("g");return;}""",
"""    if((S.phase==="open"||S.phase==="answer")&&(e.key==="a"||e.key==="A"||e.key==="ش")){soShow=!soShow;renderSolo();return;}
    if(S.phase==="open"&&(e.key==="ArrowRight"||e.key==="g"||e.key==="G")){Act.team("g");return;}""")

OUT.write_text(h, encoding="utf-8")
print("written", len(h))
