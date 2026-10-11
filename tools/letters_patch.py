# ---- letters with no questions: pick board letters from the chosen bank, and fall back gracefully ----
rep("""function drawQuestion(st,general){
  var L=st.letters[st.cell],pool=bankPool(general?null:st.bank).filter(function(q){return q.letter===L;});""",
"""function poolFor(b,L){return bankPool(b).filter(function(q){return q.letter===L;});}
function pickLetters(b){
  var cov={};bankPool(b).forEach(function(q){cov[q.letter]=(cov[q.letter]||0)+1;});
  var has=shuffle(LETTERS.filter(function(L){return cov[L];})),not=shuffle(LETTERS.filter(function(L){return !cov[L];}));
  if(has.length<10)return shuffle(LETTERS).slice(0,25);
  return shuffle(has.slice(0,25).concat(not).slice(0,25));
}
function drawQuestion(st,general){
  var L=st.letters[st.cell],b=st.bank||{},pool=general?poolFor(null,L):poolFor(b,L);
  if(!general&&!pool.length&&b.stage){
    var tries=[{stage:b.stage,grade:b.grade,term:0,subj:b.subj},{stage:b.stage,grade:b.grade,term:b.term,subj:""},{stage:b.stage,grade:b.grade,term:0,subj:""},null];
    for(var ti=0;ti<tries.length&&!pool.length;ti++)pool=poolFor(tries[ti],L);
  }""")
rep("""  start:function(){var n=clone(S);n.phase="pick";commit(n);},""",
"""  start:function(){var n=clone(S);if(n.owner.every(function(o){return !o;}))n.letters=pickLetters(n.bank);n.phase="pick";commit(n);},""")
rep("""n.letters=shuffle(LETTERS).slice(0,25);n.owner=new Array(25).fill("");n.turn=other(n.winner||n.turn);""",
"""n.letters=pickLetters(n.bank);n.owner=new Array(25).fill("");n.turn=other(n.winner||n.turn);""")
h=h.replace("""  if(!S.bank||n.bank.stage!==S.bank.stage||n.bank.grade!==S.bank.grade)n.bank.subj="";
  commit(n,true);""","""  if(!S.bank||n.bank.stage!==S.bank.stage||n.bank.grade!==S.bank.grade)n.bank.subj="";
  if(n.owner.every(function(o){return !o;})&&n.phase!=="open"&&n.phase!=="answer")setTimeout(function(){if(S&&S.owner.every(function(o){return !o;})&&S.phase!=="open"&&S.phase!=="answer"){var m=clone(S);m.letters=pickLetters(m.bank);commit(m,true);}},1500);
  commit(n,true);""")
