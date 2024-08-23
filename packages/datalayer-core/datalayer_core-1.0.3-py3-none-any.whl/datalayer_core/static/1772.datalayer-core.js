"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[1772],{71772:(e,t,n)=>{n.r(t),n.d(t,{default:()=>T});var i=n(75497),r=n(24569),s=n(43995),a=n(71995),o=n(87938);const d=new o.Token("@jupyterlab/markdownviewer:IMarkdownViewerTracker","A widget tracker for markdown\n  document viewers. Use this if you want to iterate over and interact with rendered markdown documents.");var c=n(39941),h=n(92334),l=n(46717),g=n(6972),u=n(9202),p=n(80709);const m="text/markdown";class f extends p.$L{constructor(e){super(),this._config={...f.defaultConfig},this._fragment="",this._ready=new o.PromiseDelegate,this._isRendering=!1,this._renderRequested=!1,this._rendered=new u.Signal(this),this.context=e.context,this.translator=e.translator||g.Sr,this._trans=this.translator.load("jupyterlab"),this.renderer=e.renderer,this.node.tabIndex=0,this.addClass("jp-MarkdownViewer"),(this.layout=new p.Qb).addWidget(this.renderer),this.context.ready.then((async()=>{await this._render(),this._monitor=new a.ActivityMonitor({signal:this.context.model.contentChanged,timeout:this._config.renderTimeout}),this._monitor.activityStopped.connect(this.update,this),this._ready.resolve(void 0)}))}get ready(){return this._ready.promise}get rendered(){return this._rendered}setFragment(e){this._fragment=e,this.update()}setOption(e,t){if(this._config[e]===t)return;this._config[e]=t;const{style:n}=this.renderer.node;switch(e){case"fontFamily":n.setProperty("font-family",t);break;case"fontSize":n.setProperty("font-size",t?t+"px":null);break;case"hideFrontMatter":this.update();break;case"lineHeight":n.setProperty("line-height",t?t.toString():null);break;case"lineWidth":{const e=t?`calc(50% - ${t/2}ch)`:null;n.setProperty("padding-left",e),n.setProperty("padding-right",e);break}case"renderTimeout":this._monitor&&(this._monitor.timeout=t)}}dispose(){this.isDisposed||(this._monitor&&this._monitor.dispose(),this._monitor=null,super.dispose())}onUpdateRequest(e){this.context.isReady&&!this.isDisposed&&(this._render(),this._fragment="")}onActivateRequest(e){this.node.focus()}async _render(){if(this.isDisposed)return;if(this._isRendering)return void(this._renderRequested=!0);this._renderRequested=!1;const{context:e}=this,{model:t}=e,n=t.toString(),i={};i[m]=this._config.hideFrontMatter?v.removeFrontMatter(n):n;const r=new l.a({data:i,metadata:{fragment:this._fragment}});try{if(this._isRendering=!0,await this.renderer.renderModel(r),this._isRendering=!1,this._renderRequested)return this._render();this._rendered.emit()}catch(t){requestAnimationFrame((()=>{this.dispose()})),(0,c.UW)(this._trans.__("Renderer Failure: %1",e.path),t)}}}!function(e){e.defaultConfig={fontFamily:null,fontSize:null,lineHeight:null,lineWidth:null,hideFrontMatter:!0,renderTimeout:1e3}}(f||(f={}));class _ extends h.Ry{setFragment(e){this.content.setFragment(e)}}class w extends h.GA{constructor(e){super(v.createRegistryOptions(e)),this._fileType=e.primaryFileType,this._rendermime=e.rendermime}createNewWidget(e){var t,n,i,r,s;const a=this._rendermime.clone({resolver:e.urlResolver}).createRenderer(m),o=new f({context:e,renderer:a});return o.title.icon=null===(t=this._fileType)||void 0===t?void 0:t.icon,o.title.iconClass=null!==(i=null===(n=this._fileType)||void 0===n?void 0:n.iconClass)&&void 0!==i?i:"",o.title.iconLabel=null!==(s=null===(r=this._fileType)||void 0===r?void 0:r.iconLabel)&&void 0!==s?s:"",o.title.caption=this.label,new _({content:o,context:e})}}var v;!function(e){e.createRegistryOptions=function(e){return{...e,readOnly:!0}},e.removeFrontMatter=function(e){const t=e.match(/^---\n[^]*?\n(---|...)\n/);if(!t)return e;const{length:n}=t[0];return e.slice(n)}}(v||(v={}));var y=n(21823),k=n(89173),C=n(76263),x=n(90052);class b extends y.U{constructor(e,t,n){super(e,n),this.parser=t}get documentType(){return"markdown-viewer"}get isAlwaysActive(){return!0}get supportedOptions(){return["maximalDepth","numberingH1","numberHeaders"]}getHeadings(){const e=this.widget.context.model.toString(),t=k.tF(C.o3(e),{...this.configuration,baseNumbering:1});return Promise.resolve(t)}}class R extends x.w{constructor(e,t){super(e),this.parser=t}_createNew(e,t){const n=new b(e,this.parser,t);let i=new WeakMap;const r=(t,n)=>{if(n){const t=i.get(n);if(t){const n=e.content.node.getBoundingClientRect(),i=t.getBoundingClientRect();(i.top>n.bottom||i.bottom<n.top)&&t.scrollIntoView({block:"center"})}else console.warn("Heading element not found for heading",n,"in widget",e)}},s=()=>{this.parser&&(k.Zd(e.content.node),i=new WeakMap,n.headings.forEach((async t=>{var n;const r=await C.N4(this.parser,t.raw,t.level);if(!r)return;const s=`h${t.level}[id="${r}"]`;i.set(t,k.U9(e.content.node,s,null!==(n=t.prefix)&&void 0!==n?n:""))})))};return e.content.ready.then((()=>{s(),e.content.rendered.connect(s),n.activeHeadingChanged.connect(r),n.headingsChanged.connect(s),e.disposed.connect((()=>{e.content.rendered.disconnect(s),n.activeHeadingChanged.disconnect(r),n.headingsChanged.disconnect(s)}))})),n}}var H,A=n(6977),F=n(47459),P=n(42768),E=n(36751);!function(e){e.markdownPreview="markdownviewer:open",e.markdownEditor="markdownviewer:edit"}(H||(H={}));const M="Markdown Preview",S={activate:function(e,t,n,i,r,o,d){const c=n.load("jupyterlab"),{commands:h,docRegistry:l}=e;t.addFactory(F.xr);const g=new s.u({namespace:"markdownviewer-widget"});let u={...f.defaultConfig};function p(e){Object.keys(u).forEach((t=>{var n;e.setOption(t,null!==(n=u[t])&&void 0!==n?n:null)}))}if(r){const e=e=>{u=e.composite,g.forEach((e=>{p(e.content)}))};r.load(S.id).then((t=>{t.changed.connect((()=>{e(t)})),e(t)})).catch((e=>{console.error(e.message)}))}const m=new w({rendermime:t,name:M,label:c.__("Markdown Preview"),primaryFileType:l.getFileType("markdown"),fileTypes:["markdown"],defaultRendered:["markdown"]});return m.widgetCreated.connect(((e,t)=>{t.context.pathChanged.connect((()=>{g.save(t)})),p(t.content),g.add(t)})),l.addWidgetFactory(m),i&&i.restore(g,{command:"docmanager:open",args:e=>({path:e.context.path,factory:M}),name:e=>e.context.path}),h.addCommand(H.markdownPreview,{label:c.__("Markdown Preview"),execute:e=>{const t=e.path;if("string"==typeof t)return h.execute("docmanager:open",{path:t,factory:M,options:e.options})}}),h.addCommand(H.markdownEditor,{execute:()=>{const e=g.currentWidget;if(!e)return;const t=e.context.path;return h.execute("docmanager:open",{path:t,factory:"Editor",options:{mode:"split-right"}})},isVisible:()=>{const e=g.currentWidget;return e&&".md"===a.PathExt.extname(e.context.path)||!1},label:c.__("Show Markdown Editor")}),o&&o.add(new R(g,t.markdownParser,null!=d?d:t.sanitizer)),g},id:"@jupyterlab/markdownviewer-extension:plugin",description:"Adds markdown file viewer and provides its tracker.",provides:d,requires:[A.ZD,g.gv],optional:[i.L,P.O,E.wk,r.hd],autoStart:!0},T=S},90052:(e,t,n)=>{n.d(t,{w:()=>r});var i=n(71995);class r{constructor(e){this.tracker=e}isApplicable(e){return!!this.tracker.has(e)}createNew(e,t){const n=this._createNew(e,t),r=e.context,s=()=>{n.refresh().catch((e=>{console.error("Failed to update the table of contents.",e)}))},a=new i.ActivityMonitor({signal:r.model.contentChanged,timeout:1e3});a.activityStopped.connect(s);const o=()=>{n.title=i.PathExt.basename(r.localPath)};return r.pathChanged.connect(o),r.ready.then((()=>{o(),s()})).catch((e=>{console.error(`Failed to initiate headings for ${r.localPath}.`)})),e.disposed.connect((()=>{a.activityStopped.disconnect(s),r.pathChanged.disconnect(o)})),n}}},21823:(e,t,n)=>{n.d(t,{U:()=>o});var i=n(52980),r=n(87938),s=n(9202),a=n(36751);class o extends i.I_{constructor(e,t){super(),this.widget=e,this._activeHeading=null,this._activeHeadingChanged=new s.Signal(this),this._collapseChanged=new s.Signal(this),this._configuration=null!=t?t:{...a.o5.defaultConfig},this._headings=new Array,this._headingsChanged=new s.Signal(this),this._isActive=!1,this._isRefreshing=!1,this._needsRefreshing=!1}get activeHeading(){return this._activeHeading}get activeHeadingChanged(){return this._activeHeadingChanged}get collapseChanged(){return this._collapseChanged}get configuration(){return this._configuration}get headings(){return this._headings}get headingsChanged(){return this._headingsChanged}get isActive(){return this._isActive}set isActive(e){this._isActive=e,this._isActive&&!this.isAlwaysActive&&this.refresh().catch((e=>{console.error("Failed to refresh ToC model.",e)}))}get isAlwaysActive(){return!1}get supportedOptions(){return["maximalDepth"]}get title(){return this._title}set title(e){e!==this._title&&(this._title=e,this.stateChanged.emit())}async refresh(){if(this._isRefreshing)return this._needsRefreshing=!0,Promise.resolve();this._isRefreshing=!0;try{const e=await this.getHeadings();if(this._needsRefreshing)return this._needsRefreshing=!1,this._isRefreshing=!1,this.refresh();e&&!this._areHeadingsEqual(e,this._headings)&&(this._headings=e,this.stateChanged.emit(),this._headingsChanged.emit())}finally{this._isRefreshing=!1}}setActiveHeading(e,t=!0){this._activeHeading!==e&&(this._activeHeading=e,this.stateChanged.emit()),t&&this._activeHeadingChanged.emit(this._activeHeading)}setConfiguration(e){const t={...this._configuration,...e};r.JSONExt.deepEqual(this._configuration,t)||(this._configuration=t,this.refresh().catch((e=>{console.error("Failed to update the table of contents.",e)})))}toggleCollapse(e){var t,n;if(e.heading)e.heading.collapsed=null!==(t=e.collapsed)&&void 0!==t?t:!e.heading.collapsed,this.stateChanged.emit(),this._collapseChanged.emit(e.heading);else{const t=null!==(n=e.collapsed)&&void 0!==n?n:!this.headings.some((e=>{var t;return!(null!==(t=e.collapsed)&&void 0!==t&&t)}));this.headings.forEach((e=>e.collapsed=t)),this.stateChanged.emit(),this._collapseChanged.emit(null)}}isHeadingEqual(e,t){return e.level===t.level&&e.text===t.text&&e.prefix===t.prefix}_areHeadingsEqual(e,t){if(e.length===t.length){for(let n=0;n<e.length;n++)if(!this.isHeadingEqual(e[n],t[n]))return!1;return!0}return!1}}}}]);