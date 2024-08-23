(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[9434,3158,2211],{33229:(e,t,r)=>{"use strict";r.r(t),r.d(t,{IServiceWorkerManager:()=>g,JupyterLiteServer:()=>u,Router:()=>a,ServiceWorkerManager:()=>p,WORKER_NAME:()=>d});var n=r(50953),i=r(77825),s=r(74901),o=r(2876);class a{constructor(){this._routes=[]}get(e,t){this._add("GET",e,t)}put(e,t){this._add("PUT",e,t)}post(e,t){this._add("POST",e,t)}patch(e,t){this._add("PATCH",e,t)}delete(e,t){this._add("DELETE",e,t)}async route(e){const t=new URL(e.url),{method:r}=e,{pathname:n}=t;for(const i of this._routes){if(i.method!==r)continue;const s=n.match(i.pattern);if(!s)continue;const o=s.slice(1);let a;if("PATCH"===i.method||"PUT"===i.method||"POST"===i.method)try{a=JSON.parse(await e.text())}catch{a=void 0}return i.callback.call(null,{pathname:n,body:a,query:Object.fromEntries(t.searchParams)},...o)}throw new Error("Cannot route "+e.method+" "+e.url)}_add(e,t,r){"string"==typeof t&&(t=new RegExp(t)),this._routes.push({method:e,pattern:t,callback:r})}}class c{constructor(e){this._stream=new s.Stream(this),this._serverSettings=e.serverSettings}async emit(e){}dispose(){}get isDisposed(){return!0}get stream(){return this._stream}get serverSettings(){return this._serverSettings}}class u extends i.Application{constructor(e){var t;super(e),this.name="JupyterLite Server",this.namespace=this.name,this.version="unknown",this._router=new a;const r={...n.ServerConnection.makeSettings(),WebSocket:o.WebSocket,fetch:null!==(t=this.fetch.bind(this))&&void 0!==t?t:void 0};this._serviceManager=new n.ServiceManager({standby:"never",serverSettings:r,events:new c({serverSettings:r})})}get router(){return this._router}get serviceManager(){return this._serviceManager}async fetch(e,t){if(!(e instanceof Request))throw Error("Request info is not a Request");return this._router.route(e)}attachShell(e){}evtResize(e){}registerPluginModule(e){let t=e.default;Object.prototype.hasOwnProperty.call(e,"__esModule")||(t=e),Array.isArray(t)||(t=[t]),t.forEach((e=>{try{this.registerPlugin(e)}catch(e){console.error(e)}}))}registerPluginModules(e){e.forEach((e=>{this.registerPluginModule(e)}))}}var l=r(97930);const h=r.p+"lite-service-worker.js",g=new l.Token("@jupyterlite/server-extension:IServiceWorkerManager"),d=`${h}`.split("/").slice(-1)[0];var f=r(67660);const v=f.PageConfig.getOption("appVersion");class p{constructor(e){var t;this.unregisterOldServiceWorkers=e=>{const t=`${e}-version`,r=localStorage.getItem(t);(r&&r!==v||!r)&&(console.info("New version, unregistering existing service workers."),navigator.serviceWorker.getRegistrations().then((e=>{for(const t of e)t.unregister()})).then((()=>{console.info("All existing service workers have been unregistered.")}))),localStorage.setItem(t,v)},this._registration=null,this._registrationChanged=new s.Signal(this),this._ready=new l.PromiseDelegate;const r=null!==(t=null==e?void 0:e.workerUrl)&&void 0!==t?t:f.URLExt.join(f.PageConfig.getBaseUrl(),d),n=new URL(r,window.location.href),i=f.PageConfig.getOption("enableServiceWorkerCache")||"false";n.searchParams.set("enableCache",i),this.initialize(n.href).catch(console.warn)}get registrationChanged(){return this._registrationChanged}get enabled(){return null!==this._registration}get ready(){return this._ready.promise}async initialize(e){const{serviceWorker:t}=navigator;let r=null;if(t){if(t.controller){const e=t.controller.scriptURL;this.unregisterOldServiceWorkers(e),r=await t.getRegistration(e)||null,console.info("JupyterLite ServiceWorker was already registered")}}else console.warn("ServiceWorkers not supported in this browser");if(!r&&t)try{console.info("Registering new JupyterLite ServiceWorker",e),r=await t.register(e),console.info("JupyterLite ServiceWorker was sucessfully registered")}catch(e){console.warn(e),console.warn(`JupyterLite ServiceWorker registration unexpectedly failed: ${e}`)}this._setRegistration(r),r?this._ready.resolve(void 0):this._ready.reject(void 0)}_setRegistration(e){this._registration=e,this._registrationChanged.emit(this._registration)}}},13158:e=>{var t,r,n=e.exports={};function i(){throw new Error("setTimeout has not been defined")}function s(){throw new Error("clearTimeout has not been defined")}function o(e){if(t===setTimeout)return setTimeout(e,0);if((t===i||!t)&&setTimeout)return t=setTimeout,setTimeout(e,0);try{return t(e,0)}catch(r){try{return t.call(null,e,0)}catch(r){return t.call(this,e,0)}}}!function(){try{t="function"==typeof setTimeout?setTimeout:i}catch(e){t=i}try{r="function"==typeof clearTimeout?clearTimeout:s}catch(e){r=s}}();var a,c=[],u=!1,l=-1;function h(){u&&a&&(u=!1,a.length?c=a.concat(c):l=-1,c.length&&g())}function g(){if(!u){var e=o(h);u=!0;for(var t=c.length;t;){for(a=c,c=[];++l<t;)a&&a[l].run();l=-1,t=c.length}a=null,u=!1,function(e){if(r===clearTimeout)return clearTimeout(e);if((r===s||!r)&&clearTimeout)return r=clearTimeout,clearTimeout(e);try{return r(e)}catch(t){try{return r.call(null,e)}catch(t){return r.call(this,e)}}}(e)}}function d(e,t){this.fun=e,this.array=t}function f(){}n.nextTick=function(e){var t=new Array(arguments.length-1);if(arguments.length>1)for(var r=1;r<arguments.length;r++)t[r-1]=arguments[r];c.push(new d(e,t)),1!==c.length||u||o(g)},d.prototype.run=function(){this.fun.apply(null,this.array)},n.title="browser",n.browser=!0,n.env={},n.argv=[],n.version="",n.versions={},n.on=f,n.addListener=f,n.once=f,n.off=f,n.removeListener=f,n.removeAllListeners=f,n.emit=f,n.prependListener=f,n.prependOnceListener=f,n.listeners=function(e){return[]},n.binding=function(e){throw new Error("process.binding is not supported")},n.cwd=function(){return"/"},n.chdir=function(e){throw new Error("process.chdir is not supported")},n.umask=function(){return 0}}}]);