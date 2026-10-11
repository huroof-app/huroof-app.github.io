# ---- projector view for the display screen (#screen) ----
PROJ_CSS = """
/* Projector screen: fills the viewport, big type, dark high-contrast stage. */
body.proj{background:#0b1f23;overflow:hidden}
body.proj #v-screen>*{min-width:0}
body.proj .wrap{max-width:none;height:100vh;padding:2.2vh 2vw;gap:0;box-sizing:border-box}
body.proj header.top,body.proj #banner{display:none!important}
body.proj #v-screen{height:100%;display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);grid-template-rows:auto minmax(0,1fr);grid-template-areas:"board score" "board q";gap:2.2vh 2.2vw}
body.proj #sc-board{grid-area:board;display:flex;align-items:center;justify-content:center;min-height:0}
body.proj #sc-board svg{max-height:95vh;width:100%;height:100%}
body.proj #sc-score{grid-area:score;grid-template-columns:1fr auto 1fr;gap:1.2vw}
body.proj #sc-q{grid-area:q;display:flex;min-height:0}
body.proj .plate{border-radius:2vh;padding:1.6vh 1.4vw;gap:.6vh}
body.proj .plate .tname{font-size:4.2vh}
body.proj .plate .dir{font-size:2.3vh}
body.proj .plate .ppl{font-size:2.4vh}
body.proj .plate .wins{font-size:9vh}
body.proj .plate.turn{outline-width:.6vh;outline-offset:.4vh}
body.proj .mid{color:#e9f3f1;font-size:2.6vh}
body.proj .mid b{font-size:6vh;color:#fff}
body.proj .hl{font-size:40px}
body.proj .hex{stroke-width:2.5}
body.proj .qbar{flex:1;background:#14353a;border:none;border-radius:2.4vh;padding:3vh 2vw;display:grid;grid-template-columns:minmax(0,1fr);justify-items:center;align-content:center;gap:2.2vh;color:#fff;min-width:0;overflow:hidden}
body.proj .qbar .ltr{width:15vh;height:15vh;font-size:10vh}
body.proj .qbar .qt{text-align:center;width:100%}
body.proj .qbar .qt small{color:#a9c7c2;font-size:2.6vh}
body.proj .qbar .qt p{font-size:clamp(26px,4.6vh,72px);line-height:1.45;font-weight:600}
body.proj .qbar .who{font-size:3vh;color:#cfe3df}
body.proj .qbar .who .muted{color:#cfe3df}
body.proj .who .tag{font-size:3.6vh;padding:.8vh 1.6vw;border-radius:1.4vh}
body.proj .timer{font-size:12vh;color:var(--gold);min-width:0}
body.proj .sc-code{position:fixed;top:auto;bottom:2vh;left:2vw;font-size:2.6vh;padding:1vh 1.4vw;border-radius:1.6vh;background:#fff;color:#12282d}
body.proj .sc-code b{font-size:5.5vh}
.fsbtn{position:fixed;bottom:2vh;right:2vw;z-index:6;font-size:2.2vh;padding:1vh 1.4vw;border-radius:1.4vh;background:#ffffffde;color:#12282d;border:none;cursor:pointer}
body:not(.proj) .fsbtn{display:none}
@media (max-aspect-ratio:3/2){
  body.proj #v-screen{grid-template-columns:minmax(0,1.15fr) minmax(0,1fr)}
  body.proj .plate .tname{font-size:3.4vh} body.proj .plate .dir{display:none} body.proj .plate .ppl{font-size:2vh} body.proj .plate .wins{font-size:7vh}
  body.proj .qbar{gap:1.4vh;padding:2.4vh 1.6vw}
  body.proj .qbar .ltr{width:10vh;height:10vh;font-size:6.5vh}
  body.proj .qbar .qt p{font-size:clamp(20px,3.8vh,60px)}
  body.proj .who .tag{font-size:2.8vh}
  body.proj .timer{font-size:8vh}
}
@media (max-aspect-ratio:1/1){
  body.proj #v-screen{grid-template-columns:1fr;grid-template-rows:auto minmax(0,1fr) auto;grid-template-areas:"score" "board" "q"}
  body.proj .qbar .ltr{width:9vh;height:9vh;font-size:6vh}
  body.proj .qbar .qt p{font-size:3.4vh}
}
</style>"""
h=h.replace('</style>',PROJ_CSS,1)
rep('<div class="sc-code" id="sc-code" hidden></div>','<div class="sc-code" id="sc-code" hidden></div>\n    <button class="fsbtn" id="fsbtn" type="button">⛶ ملء الشاشة</button>')
rep("""  role=r;
  location.hash=r?"#"+r:"";""","""  role=r;
  location.hash=r?"#"+r:"";
  document.body.classList.toggle("proj",r==="screen");""")
rep('$("chg").addEventListener("click",function(){setRole("");});',
'$("chg").addEventListener("click",function(){setRole("");});\n'
'function toggleFS(){try{if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen();}catch(e){}}\n'
'$("fsbtn").addEventListener("click",toggleFS);\n'
'document.addEventListener("fullscreenchange",function(){$("fsbtn").textContent=document.fullscreenElement?"✕ خروج من ملء الشاشة":"⛶ ملء الشاشة";$("fsbtn").style.opacity=document.fullscreenElement?"0.25":"1";});\n'
'document.addEventListener("keydown",function(e){if(role==="screen"&&(e.key==="f"||e.key==="F"||e.key==="ب")&&!/^(INPUT|TEXTAREA)$/.test(e.target.tagName))toggleFS();});')
