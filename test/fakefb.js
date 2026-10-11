/* Minimal in-memory Firebase compat shim for UI tests (shared via window.__FB on the page). */
(function(){
  if(window.firebase)return;
  var root={};var listeners=[];var users={};var cur=null;var authCbs=[];
  function get(path){var p=path.split("/").filter(Boolean),n=root;for(var i=0;i<p.length;i++){if(n==null||typeof n!=="object")return null;n=n[p[i]];}return n===undefined?null:n;}
  function clean(v){if(v===null||v===undefined)return null;if(Array.isArray(v)){var o={};v.forEach(function(x,i){var c=clean(x);if(c!==null)o[i]=c;});return Object.keys(o).length?v.map(function(x){var c=clean(x);return c;}):null;}
    if(typeof v==="object"){if(v[".sv"])return Date.now();var r={};Object.keys(v).forEach(function(k){var c=clean(v[k]);if(c!==null)r[k]=c;});return Object.keys(r).length?r:null;}return v;}
  function set(path,v){var p=path.split("/").filter(Boolean);v=clean(JSON.parse(JSON.stringify(v===undefined?null:v)));
    if(!p.length){root=v||{};}else{var n=root;for(var i=0;i<p.length-1;i++){if(n[p[i]]==null||typeof n[p[i]]!=="object")n[p[i]]={};n=n[p[i]];}if(v===null)delete n[p[p.length-1]];else n[p[p.length-1]]=v;}
    fire();}
  function fire(){listeners.slice().forEach(function(l){var v=get(l.path);var s=JSON.stringify(v);if(s!==l.last){l.last=s;setTimeout(function(){l.cb(snap(l.path,v));},0);}});}
  function snap(path,v){return {key:path.split("/").filter(Boolean).pop()||null,val:function(){return v==null?null:JSON.parse(JSON.stringify(v));},exists:function(){return v!=null;}};}
  function Ref(path){this.path=path;}
  Ref.prototype.child=function(c){return new Ref(this.path.replace(/\/$/,"")+"/"+c);};
  Ref.prototype.on=function(ev,cb,err){var l={path:this.path,cb:cb,last:undefined};listeners.push(l);var v=get(this.path);l.last=JSON.stringify(v);setTimeout(function(){cb(snap(l.path,v));},0);return cb;};
  Ref.prototype.off=function(ev,cb){var p=this.path;listeners=listeners.filter(function(l){return !(l.path===p&&(!cb||l.cb===cb)) && !(!ev&&l.path.indexOf(p)===0);});};
  Ref.prototype.set=function(v){set(this.path,v);return Promise.resolve();};
  Ref.prototype.update=function(o){var self=this;Object.keys(o).forEach(function(k){set(self.path+"/"+k,o[k]);});return Promise.resolve();};
  Ref.prototype.remove=function(){set(this.path,null);return Promise.resolve();};
  Ref.prototype.get=function(){return Promise.resolve(snap(this.path,get(this.path)));};
  Ref.prototype.push=function(v){var k="k"+Math.random().toString(36).slice(2,10);set(this.path+"/"+k,v);var r=new Ref(this.path+"/"+k);r.key=k;return Object.assign(Promise.resolve(r),{key:k});};
  Ref.prototype.transaction=function(fn){var curv=get(this.path);var nv=fn(curv);if(nv===undefined)return Promise.resolve({committed:false,snapshot:snap(this.path,curv)});set(this.path,nv);return Promise.resolve({committed:true,snapshot:snap(this.path,nv)});};
  var db={ref:function(p){return new Ref(p||"");}};
  function user(email,name){return {uid:"u_"+email.replace(/[^a-z0-9]/gi,""),email:email,displayName:name||"",updateProfile:function(o){this.displayName=o.displayName;return Promise.resolve();}};}
  function emitAuth(){authCbs.forEach(function(cb){setTimeout(function(){cb(cur);},0);});}
  var auth={languageCode:"",get currentUser(){return cur;},
    onAuthStateChanged:function(cb){authCbs.push(cb);setTimeout(function(){cb(cur);},0);},
    createUserWithEmailAndPassword:function(e,p){if(users[e])return Promise.reject({code:"auth/email-already-in-use"});users[e]={pw:p};cur=user(e);emitAuth();return Promise.resolve({user:cur});},
    signInWithEmailAndPassword:function(e,p){if(!users[e]||users[e].pw!==p)return Promise.reject({code:"auth/invalid-credential"});cur=user(e);emitAuth();return Promise.resolve({user:cur});},
    signOut:function(){cur=null;emitAuth();return Promise.resolve();},
    sendPasswordResetEmail:function(){return Promise.resolve();}};
  window.firebase={initializeApp:function(){},auth:function(){return auth;},database:function(){return db;}};
  window.firebase.database.ServerValue={TIMESTAMP:{".sv":"timestamp"}};
  window.__FB={set:set,get:get,users:users,signInAs:function(e){cur=user(e);emitAuth();}};
})();
