# ---- lively board: claim pop, question entrance, wrong shake, hurry timer, win path glow + confetti celebration ----
ANIM_CSS = """
/* Motion: cells pop when won, the question slides in, the winning path glows, confetti on a win. */
.cellg{transform-box:fill-box;transform-origin:center}
.cellg.pop{animation:cellpop .9s cubic-bezier(.2,1.6,.4,1)}
@keyframes cellpop{0%{transform:scale(.4) rotate(-25deg)}55%{transform:scale(1.22) rotate(6deg)}100%{transform:scale(1) rotate(0)}}
.cellg.pop .hex{filter:drop-shadow(0 0 10px rgba(255,255,255,.9))}
.cellg.winp .hex{animation:winglow 1.1s ease-in-out infinite alternate;animation-delay:var(--d,0s);stroke:#fff;stroke-width:3}
@keyframes winglow{from{filter:drop-shadow(0 0 2px rgba(255,255,255,.4)) brightness(1)}to{filter:drop-shadow(0 0 14px rgba(255,236,150,1)) brightness(1.35)}}
.cellg.dim{opacity:.35;transition:opacity .6s}
.qbar.enter{animation:qin .7s cubic-bezier(.2,1.2,.3,1)}
@keyframes qin{from{opacity:0;transform:translateY(24px) scale(.96)}to{opacity:1;transform:none}}
.qbar.enter .ltr{animation:ltrin .8s cubic-bezier(.2,1.8,.4,1)}
@keyframes ltrin{0%{transform:scale(0) rotate(-180deg)}100%{transform:scale(1) rotate(0)}}
.qbar.shake{animation:shake .5s}
@keyframes shake{20%,60%{transform:translateX(-14px)}40%,80%{transform:translateX(14px)}}
.qbar.good{animation:good .9s}
@keyframes good{30%{box-shadow:0 0 0 6px var(--green),0 0 40px var(--green)}}
.timer.hurry{color:var(--red)!important;animation:hurry .5s ease-in-out infinite alternate}
@keyframes hurry{to{transform:scale(1.18)}}
.plate.turn{animation:turnglow 1.4s ease-in-out infinite alternate}
@keyframes turnglow{to{box-shadow:0 0 28px rgba(224,163,18,.75)}}
body.proj{background:radial-gradient(1200px 800px at 20% 10%,#12363b 0%,#0b1f23 55%,#081619 100%)}
#celebrate{position:fixed;inset:0;z-index:40;pointer-events:none;display:none}
#celebrate canvas{position:absolute;inset:0;width:100%;height:100%}
#celebrate .ban{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) scale(.2);opacity:0;text-align:center;padding:4vh 5vw;border-radius:4vh;color:#fff;font-family:var(--display);box-shadow:0 30px 80px rgba(0,0,0,.45);animation:banin 1s cubic-bezier(.2,1.6,.3,1) forwards .15s;white-space:nowrap}
#celebrate .ban.g{background:linear-gradient(135deg,#17a877,#0b6f4f)} #celebrate .ban.r{background:linear-gradient(135deg,#e05346,#9d2a21)}
#celebrate .ban .cup{font-size:14vh;line-height:1;display:block;animation:cup 1.2s ease-in-out infinite alternate}
#celebrate .ban .t1{font-size:7vh;display:block;margin-top:1vh}
#celebrate .ban .t2{font-size:3.6vh;display:block;opacity:.95;font-family:var(--body);font-weight:600}
@keyframes banin{to{transform:translate(-50%,-50%) scale(1);opacity:1}}
@keyframes cup{to{transform:rotate(-8deg) scale(1.08)}}
@media (prefers-reduced-motion:reduce){.cellg.pop,.qbar.enter,.qbar.shake,.cellg.winp .hex,.timer.hurry,.plate.turn{animation:none}}
</style>"""
h=h.replace('</style>',ANIM_CSS,1)
rep('<div class="gate" id="gate" hidden>','<div id="celebrate" aria-hidden="true"><canvas id="confetti"></canvas><div class="ban" id="banner-win"></div></div>\n<div class="gate" id="gate" hidden>')

# board: pop on newly claimed cell, glow on winning path
rep("""    h+='<g class="cellg'+(can?" pick":"")+'"'+(can?""","""    var pop=FX.pop[i]&&FX.pop[i]>Date.now(),wp=st&&st.phase==="roundover"&&FX.path&&FX.path.indexOf(i)>=0,dim=st&&st.phase==="roundover"&&FX.path&&!wp;
    h+='<g class="cellg'+(can?" pick":"")+(pop?" pop":"")+(wp?" winp":"")+(dim?" dim":"")+'"'+(wp?' style="--d:'+(FX.path.indexOf(i)*0.12).toFixed(2)+'s"':'')+(can?""")

rep("""function boardSVG(st,pickable){""","""var FX={pop:{},path:null,qUntil:0,shakeUntil:0,goodUntil:0,lastSeq:null,celebKey:""};
function winPath(owner,t){
  var prev={},q=[],seen={};
  for(var i=0;i<25;i++){var r=Math.floor(i/5),c=i%5;if(owner[i]===t&&(t==="g"?c===0:r===0)){q.push(i);seen[i]=1;prev[i]=-1;}}
  while(q.length){var k=q.shift(),kr=Math.floor(k/5),kc=k%5;
    if(t==="g"?kc===4:kr===4){var p=[];while(k!==-1){p.unshift(k);k=prev[k];}return p;}
    neighbors(k).forEach(function(n){if(!seen[n]&&owner[n]===t){seen[n]=1;prev[n]=k;q.push(n);}});}
  return null;
}
function boardSVG(st,pickable){""")

# detect changes in onState
rep("""  S=st;
  var bk=""","""  var old=S;
  if(st&&old&&old.match===st.match&&old.round===st.round){for(var ci=0;ci<25;ci++)if(st.owner[ci]&&!old.owner[ci]){FX.pop[ci]=Date.now()+950;setTimeout(render,960);}}
  if(st&&(st.phase==="open")&&FX.lastSeq!==st.match+":"+st.seq&&(!old||old.seq!==st.seq||old.phase!=="open")){FX.lastSeq=st.match+":"+st.seq;if(!(old&&old.seq===st.seq&&old.phase==="answer")){FX.qUntil=Date.now()+750;setTimeout(render,780);}}
  if(st&&old&&st.fx&&old.fx&&st.fx.n!==old.fx.n){if(st.fx.t==="wrong"){FX.shakeUntil=Date.now()+520;setTimeout(render,540);}if(st.fx.t==="clap"){FX.goodUntil=Date.now()+900;setTimeout(render,920);}}
  FX.path=st&&st.phase==="roundover"&&st.winner?winPath(st.owner,st.winner):null;
  if(st&&st.phase==="roundover"&&st.winner){var ck=st.match+":"+st.round+":"+st.winner;if(FX.celebKey!==ck){FX.celebKey=ck;if(old&&old.phase!=="roundover"&&role!=="play"&&role!=="")celebrate(st);}}
  else if(st&&st.phase!=="roundover"){hideCelebrate();}
  S=st;
  var bk=""")

# question bar classes
rep("""  return '<div class="qbar"><div class="ltr">'+esc(L==="ه"?"هـ":L)+'</div>""","""  var qc=(Date.now()<FX.qUntil?" enter":"")+(Date.now()<FX.shakeUntil?" shake":"")+(Date.now()<FX.goodUntil?" good":"");
  return '<div class="qbar'+qc+'"><div class="ltr">'+esc(L==="ه"?"هـ":L)+'</div>""")

# hurry timer
rep("""  var els=document.querySelectorAll(".timer");for(var i=0;i<els.length;i++)els[i].textContent=left<10?"0"+left:String(left);""",
"""  var els=document.querySelectorAll(".timer");for(var i=0;i<els.length;i++){els[i].textContent=left<10?"0"+left:String(left);els[i].classList.toggle("hurry",left<=3);}""")

# celebration
rep("""function tick(){""","""var confAnim=null;
function hideCelebrate(){var c=$("celebrate");if(c&&c.style.display!=="none"){c.style.display="none";if(confAnim){cancelAnimationFrame(confAnim);confAnim=null;}}}
function celebrate(st){
  var c=$("celebrate"),cv=$("confetti"),ban=$("banner-win");if(!c)return;
  var champ=st.wins[st.winner]>=2;
  ban.className="ban "+st.winner;
  ban.innerHTML='<span class="cup">'+(champ?"🏆":"🎉")+'</span><span class="t1">'+(champ?"بطل المباراة":"فوز بالجولة")+'</span><span class="t2">الفريق '+TEAM[st.winner]+' أكمل التوصيل</span>';
  c.style.display="block";
  var dpr=Math.min(2,window.devicePixelRatio||1),W=cv.width=innerWidth*dpr,H=cv.height=innerHeight*dpr,ctx=cv.getContext("2d");
  var cols=st.winner==="g"?["#17a877","#e0a312","#ffffff","#7fe3bf","#ffd76a"]:["#e05346","#e0a312","#ffffff","#ff9d8f","#ffd76a"];
  var parts=[],N=champ?420:260;
  for(var i=0;i<N;i++){var side=i%2;parts.push({x:side?W*0.05:W*0.95,y:H*0.85,vx:(side?1:-1)*(4+Math.random()*12)*dpr,vy:-(12+Math.random()*16)*dpr,s:(5+Math.random()*7)*dpr,r:Math.random()*6,vr:(Math.random()-.5)*.3,c:cols[i%cols.length],sh:Math.random()<.5});}
  var t0=performance.now(),dur=champ?7000:5000;
  if(confAnim)cancelAnimationFrame(confAnim);
  (function frame(t){
    ctx.clearRect(0,0,W,H);var el=t-t0;
    parts.forEach(function(p){p.vy+=0.38*dpr;p.vx*=0.992;p.x+=p.vx;p.y+=p.vy;p.r+=p.vr;
      ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.r);ctx.fillStyle=p.c;ctx.globalAlpha=Math.max(0,1-el/dur);
      if(p.sh)ctx.fillRect(-p.s/2,-p.s/4,p.s,p.s/2);else{ctx.beginPath();ctx.arc(0,0,p.s/2.4,0,6.3);ctx.fill();}ctx.restore();});
    if(el<dur)confAnim=requestAnimationFrame(frame);else{ctx.clearRect(0,0,W,H);confAnim=null;}
  })(t0);
  setTimeout(function(){var b=$("banner-win");if(b)b.style.transition="opacity .8s",b.style.opacity="0";},dur-800);
  setTimeout(function(){hideCelebrate();var b=$("banner-win");if(b){b.style.opacity="";b.style.transition="";}},dur);
}
function tick(){""")
