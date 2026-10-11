const { chromium } = require('playwright'); const fs=require('fs');
(async()=>{
  const html=fs.readFileSync(__dirname+'/../index.html','utf8');
  const a0=html.indexOf('function applauseBuffers'), a1=html.indexOf('function tone(type');
  const code=html.slice(a0,a1).replace('var a=ac();if(!a)return;','var a=window.__A;');
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'}); const p=await b.newPage();
  const res=await p.evaluate(async(code)=>{
    const ctx=new OfflineAudioContext(2,44100*3.2,44100); window.__A=ctx; eval(code+';window.__ap=applause;'); window.__ap(2.8);
    const buf=await ctx.startRendering(); const L=buf.getChannelData(0),R=buf.getChannelData(1);
    let pk=0,rms=0;for(let i=0;i<L.length;i++){pk=Math.max(pk,Math.abs(L[i]),Math.abs(R[i]));rms+=L[i]*L[i];}
    // wav
    const n=L.length,dv=new DataView(new ArrayBuffer(44+n*4));const w=(o,s)=>{for(let i=0;i<s.length;i++)dv.setUint8(o+i,s.charCodeAt(i));};
    w(0,'RIFF');dv.setUint32(4,36+n*4,true);w(8,'WAVE');w(12,'fmt ');dv.setUint32(16,16,true);dv.setUint16(20,1,true);dv.setUint16(22,2,true);dv.setUint32(24,44100,true);dv.setUint32(28,44100*4,true);dv.setUint16(32,4,true);dv.setUint16(34,16,true);w(36,'data');dv.setUint32(40,n*4,true);
    for(let i=0;i<n;i++){dv.setInt16(44+i*4,Math.max(-1,Math.min(1,L[i]))*32767,true);dv.setInt16(46+i*4,Math.max(-1,Math.min(1,R[i]))*32767,true);}
    return {pk,rms:Math.sqrt(rms/n),wav:Array.from(new Uint8Array(dv.buffer))};
  },code);
  fs.writeFileSync('/mnt/user-data/outputs/تصفيق-جديد.wav',Buffer.from(res.wav)); console.log('peak',res.pk.toFixed(3),'rms',res.rms.toFixed(3)); await b.close();
})();
