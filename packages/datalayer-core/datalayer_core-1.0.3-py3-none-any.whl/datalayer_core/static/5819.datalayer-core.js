"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[5819],{35819:(e,t,s)=>{s.r(t),s.d(t,{default:()=>V});var r=s(71995),n=s(47924),a=s(95994),i=s(71830),o=s(36349),c=s(92533),l=s(88286),u=s(87938);const g="third-party-licenses.json",p=new u.Token("@jupyterlite/licenses:ILicenses"),d=Object.freeze({packages:[]});class y{async get(){return{bundles:{...await this._getFederated(),[this.appName]:await this._getAppLicenses()}}}get appName(){return r.PageConfig.getOption("appName")||"JupyterLite"}get appLicensesUrl(){return r.URLExt.join(r.PageConfig.getBaseUrl(),"build",g)}get labExtensionsUrl(){return r.PageConfig.getOption("fullLabextensionsUrl")}async _getAppLicenses(){let e=d;try{e=(await fetch(this.appLicensesUrl)).json()}catch(e){console.warn("Could not resolve licenses for",this.appName)}return e}async _getFederated(){const e={};let t;try{t=JSON.parse(r.PageConfig.getOption("federated_extensions"))}catch{return e}const s=[];for(const r of t)s.push(this._getOneFederated(r,e));try{await Promise.all(s)}catch(e){console.warn("Error resolving licenses",e)}return e}async _getOneFederated(e,t){try{const s=r.URLExt.join(this.labExtensionsUrl,e.name,"static",g),n=await fetch(s);t[e.name]=await n.json()}catch{console.warn("Could not resolve licenses for",e),t[e.name]=d}}}var v=s(81650),w=s(9202);const f=r.PageConfig.getOption("appVersion");class h{constructor(e){var t;this.unregisterOldServiceWorkers=e=>{const t=`${e}-version`,s=localStorage.getItem(t);(s&&s!==f||!s)&&(console.info("New version, unregistering existing service workers."),navigator.serviceWorker.getRegistrations().then((e=>{for(const t of e)t.unregister()})).then((()=>{console.info("All existing service workers have been unregistered.")}))),localStorage.setItem(t,f)},this._registration=null,this._registrationChanged=new w.Signal(this),this._ready=new u.PromiseDelegate;const s=null!==(t=null==e?void 0:e.workerUrl)&&void 0!==t?t:r.URLExt.join(r.PageConfig.getBaseUrl(),v.o),n=new URL(s,window.location.href),a=r.PageConfig.getOption("enableServiceWorkerCache")||"false";n.searchParams.set("enableCache",a),this.initialize(n.href).catch(console.warn)}get registrationChanged(){return this._registrationChanged}get enabled(){return null!==this._registration}get ready(){return this._ready.promise}async initialize(e){const{serviceWorker:t}=navigator;let s=null;if(t){if(t.controller){const e=t.controller.scriptURL;this.unregisterOldServiceWorkers(e),s=await t.getRegistration(e)||null,console.info("JupyterLite ServiceWorker was already registered")}}else console.warn("ServiceWorkers not supported in this browser");if(!s&&t)try{console.info("Registering new JupyterLite ServiceWorker",e),s=await t.register(e),console.info("JupyterLite ServiceWorker was sucessfully registered")}catch(e){console.warn(e),console.warn(`JupyterLite ServiceWorker registration unexpectedly failed: ${e}`)}this._setRegistration(s),s?this._ready.resolve(void 0):this._ready.reject(void 0)}_setRegistration(e){this._registration=e,this._registrationChanged.emit(this._registration)}}var S=s(62202),O=s(77051);const m=new u.Token("@jupyterlite/settings:ISettings");var N=s(54010);const k="JupyterLite Storage";class _{constructor(e){this._storageName=k,this._storageDrivers=null,this._localforage=e.localforage,this._storageName=e.storageName||k,this._storageDrivers=e.storageDrivers||null,this._ready=new u.PromiseDelegate}get ready(){return this._ready.promise}get storage(){return this.ready.then((()=>this._storage))}async initialize(){await this.initStorage(),this._ready.resolve(void 0)}async initStorage(){this._storage=this.defaultSettingsStorage()}get defaultStorageOptions(){var e;const t=(null===(e=this._storageDrivers)||void 0===e?void 0:e.length)?this._storageDrivers:null;return{version:1,name:this._storageName,...t?{driver:t}:{}}}defaultSettingsStorage(){return this._localforage.createInstance({description:"Offline Storage for Settings",storeName:"settings",...this.defaultStorageOptions})}async get(e){return(await this.getAll()).settings.find((t=>t.id===e))}async getAll(){const e=await this._getAll("all.json");let t=[];try{t=await this._getAll("all_federated.json")}catch{}const s=e.concat(t),r=await this.storage;return{settings:await Promise.all(s.map((async e=>{var t;const{id:s}=e,n=null!==(t=await r.getItem(s))&&void 0!==t?t:e.raw;return{...R.override(e),raw:n,settings:N.parse(n)}})))}}async save(e,t){await(await this.storage).setItem(e,t)}async _getAll(e){var t;const s=null!==(t=r.PageConfig.getOption("settingsUrl"))&&void 0!==t?t:"/";return await(await fetch(r.URLExt.join(s,e))).json()}}var R;!function(e){const t=JSON.parse(r.PageConfig.getOption("settingsOverrides")||"{}");e.override=function(e){if(t[e.id]){e.schema.properties||(e.schema.properties={});for(const[s,r]of Object.entries(t[e.id]||{}))e.schema.properties[s].default=r}return e}}(R||(R={}));const j=new u.Token("@jupyterlite/translation:ITranslation");class J{constructor(){this._prevLocale=""}async get(e){const t=r.URLExt.join(r.PageConfig.getBaseUrl(),`api/translations/${e}.json`);try{const s=await fetch(t),r=JSON.parse(await s.text());if("all"!==this._prevLocale&&"all"===e){const e=this._prevLocale;r.data[e].displayName=r.data[e].nativeName,"en"!==e&&(r.data.en.displayName=`${r.data.en.nativeName} (default)`)}return this._prevLocale=e,r}catch(t){return e?{data:{},message:`Language pack '${e}' not installed!`}:{data:{en:{displayName:"English",nativeName:"English"}},message:""}}}}var x=s(42581),b=s(63439),C=s.n(b);const L={id:"@jupyterlite/server-extension:localforage",autoStart:!0,provides:x.A,activate:e=>({localforage:C()})},P={id:"@jupyterlite/server-extension:localforage-memory-storage",autoStart:!0,requires:[x.A],activate:async(e,t)=>{JSON.parse(r.PageConfig.getOption("enableMemoryStorage")||"false")&&(console.warn("Memory storage fallback enabled: contents and settings may not be saved"),await(0,x.$)(t.localforage))}},U={id:"@jupyterlite/server-extension:config-section-routes",autoStart:!0,activate:e=>{const t={};e.router.get("/api/config/(.*)",(async(e,s)=>{var r;const n=null!==(r=t[s])&&void 0!==r?r:JSON.stringify({});return new Response(n)})),e.router.patch("/api/config/(.*)",(async(e,s)=>{const r=e.body;return t[s]=r,new Response(r)}))}},q={id:"@jupyterlite/server-extension:contents",requires:[x.A],autoStart:!0,provides:n.Hv,activate:(e,t)=>{const s=r.PageConfig.getOption("contentsStorageName"),n=JSON.parse(r.PageConfig.getOption("contentsStorageDrivers")||"null"),{localforage:i}=t,o=new a.A({storageName:s,storageDrivers:n,localforage:i});return e.started.then((()=>o.initialize().catch(console.warn))),o}},A={id:"@jupyterlite/server-extension:contents-routes",autoStart:!0,requires:[n.Hv],activate:(e,t)=>{e.router.get("/api/contents/(.+)/checkpoints",(async(e,s)=>{const r=await t.listCheckpoints(s);return new Response(JSON.stringify(r))})),e.router.post("/api/contents/(.+)/checkpoints/(.*)",(async(e,s,r)=>{const n=await t.restoreCheckpoint(s,r);return new Response(JSON.stringify(n),{status:204})})),e.router.post("/api/contents/(.+)/checkpoints",(async(e,s)=>{const r=await t.createCheckpoint(s);return new Response(JSON.stringify(r),{status:201})})),e.router.delete("/api/contents/(.+)/checkpoints/(.*)",(async(e,s,r)=>{const n=await t.deleteCheckpoint(s,r);return new Response(JSON.stringify(n),{status:204})})),e.router.get("/api/contents(.*)",(async(e,s)=>{var r;const n={content:"1"===(null===(r=e.query)||void 0===r?void 0:r.content)},a=await t.get(s,n);return a?new Response(JSON.stringify(a)):new Response(null,{status:404})})),e.router.post("/api/contents(.*)",(async(e,s)=>{const r=e.body,n=null==r?void 0:r.copy_from;let a;return a=n?await t.copy(n,s):await t.newUntitled(r),a?new Response(JSON.stringify(a),{status:201}):new Response(null,{status:400})})),e.router.patch("/api/contents(.*)",(async(e,s)=>{var r,n;const a=null!==(n=null===(r=e.body)||void 0===r?void 0:r.path)&&void 0!==n?n:"";s="/"===s[0]?s.slice(1):s;const i=await t.rename(s,a);return new Response(JSON.stringify(i))})),e.router.put("/api/contents/(.+)",(async(e,s)=>{const r=e.body,n=await t.save(s,r);return new Response(JSON.stringify(n))})),e.router.delete("/api/contents/(.+)",(async(e,s)=>(await t.delete(s),new Response(null,{status:204}))))}},W={id:"@jupyterlite/server-extension:service-worker",autoStart:!0,provides:v.f,activate:e=>new h},D={id:"@jupyterlite/server-extension:emscripten-filesystem",autoStart:!0,optional:[v.f],provides:n.dC,activate:(e,t)=>{const{contents:s}=e.serviceManager,r=new i.Q({contents:s}),n="Kernel filesystem and JupyterLite contents";function a(e,t){t&&console.warn(t),e&&console.warn(e),t||e?console.warn(`${n} will NOT be synced`):console.info(`${n} will be synced`)}return t?t.ready.then((()=>{r.enable(),a()})).catch((e=>{a("JupyterLite ServiceWorker failed to become available",e)})):a("JupyterLite ServiceWorker not available"),r}},E={id:"@jupyterlite/server-extension:kernels",autoStart:!0,provides:o.Ll,requires:[o.qP],activate:(e,t)=>new c.x({kernelspecs:t})},$={id:"@jupyterlite/server-extension:kernels-routes",autoStart:!0,requires:[o.Ll],activate:(e,t)=>{e.router.get("/api/kernels",(async e=>{const s=await t.list();return new Response(JSON.stringify(s))})),e.router.post("/api/kernels/(.*)/restart",(async(e,s)=>{const r=await t.restart(s);return new Response(JSON.stringify(r))})),e.router.delete("/api/kernels/(.*)",(async(e,s)=>{const r=await t.shutdown(s);return new Response(JSON.stringify(r),{status:204})}))}},I={id:"@jupyterlite/server-extension:kernelspec",autoStart:!0,provides:o.qP,activate:e=>new l.X},z={id:"@jupyterlite/server-extension:kernelspec-routes",autoStart:!0,requires:[o.qP],activate:(e,t)=>{e.router.get("/api/kernelspecs",(async e=>{const{specs:s}=t;if(!s)return new Response(null);const r={},n=s.kernelspecs;Object.keys(n).forEach((e=>{const t=n[e],{resources:s}=null!=t?t:{};r[e]={name:e,spec:t,resources:s}}));const a={default:s.default,kernelspecs:r};return new Response(JSON.stringify(a))}))}},T={id:"@jupyterlite/server-extension:licenses",autoStart:!0,provides:p,activate:e=>new y},F={id:"@jupyterlite/server-extension:licenses-routes",autoStart:!0,requires:[p],activate(e,t){e.router.get("/api/licenses",(async e=>{const s=await t.get();return new Response(JSON.stringify(s))}))}},B={id:"@jupyterlite/server-extension:lsp-routes",autoStart:!0,activate:e=>{e.router.get("/lsp/status",(async e=>new Response(JSON.stringify({version:2,sessions:{},specs:{}}))))}},M={id:"@jupyterlite/server-extension:nbconvert-routes",autoStart:!0,activate:e=>{e.router.get("/api/nbconvert",(async e=>new Response(JSON.stringify({}))))}},H={id:"@jupyterlite/server-extension:sessions",autoStart:!0,provides:S.R,requires:[o.Ll],activate:(e,t)=>new O.R({kernels:t})},K={id:"@jupyterlite/server-extension:sessions-routes",autoStart:!0,requires:[S.R],activate:(e,t)=>{e.router.get("/api/sessions/(.+)",(async(e,s)=>{const r=await t.get(s);return new Response(JSON.stringify(r),{status:200})})),e.router.get("/api/sessions",(async e=>{const s=await t.list();return new Response(JSON.stringify(s),{status:200})})),e.router.patch("/api/sessions(.*)",(async(e,s)=>{const r=e.body,n=await t.patch(r);return new Response(JSON.stringify(n),{status:200})})),e.router.delete("/api/sessions/(.+)",(async(e,s)=>(await t.shutdown(s),new Response(null,{status:204})))),e.router.post("/api/sessions",(async e=>{const s=e.body,r=await t.startNew(s);return new Response(JSON.stringify(r),{status:201})}))}},Q={id:"@jupyterlite/server-extension:settings",autoStart:!0,requires:[x.A],provides:m,activate:(e,t)=>{const s=r.PageConfig.getOption("settingsStorageName"),n=JSON.parse(r.PageConfig.getOption("settingsStorageDrivers")||"null"),{localforage:a}=t,i=new _({storageName:s,storageDrivers:n,localforage:a});return e.started.then((()=>i.initialize().catch(console.warn))),i}},V=[U,q,A,D,E,$,I,z,T,F,P,L,B,M,W,H,K,Q,{id:"@jupyterlite/server-extension:settings-routes",autoStart:!0,requires:[m],activate:(e,t)=>{const s="/api/settings/((?:@([^/]+?)[/])?([^/]+?):([^:]+))$";e.router.get(s,(async(e,s)=>{const r=await t.get(s);return new Response(JSON.stringify(r))})),e.router.put(s,(async(e,s)=>{const r=e.body,{raw:n}=r;return await t.save(s,n),new Response(null,{status:204})})),e.router.get("/api/settings",(async e=>{const s=await t.getAll();return new Response(JSON.stringify(s))}))}},{id:"@jupyterlite/server-extension:translation",autoStart:!0,provides:j,activate:e=>{const t=new J;return e.router.get("/api/translations/?(.*)",(async(e,s)=>{"default"===s&&(s="en");const r=await t.get(s||"all");return new Response(JSON.stringify(r))})),t}},{id:"@jupyterlite/server-extension:translation-routes",autoStart:!0,requires:[j],activate:(e,t)=>{e.router.get("/api/translations/?(.*)",(async(e,s)=>{const r=await t.get(s||"all");return new Response(JSON.stringify(r))}))}}]}}]);