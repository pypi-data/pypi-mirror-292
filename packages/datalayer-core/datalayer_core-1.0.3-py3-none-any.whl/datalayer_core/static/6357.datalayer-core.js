"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[6357],{6357:(e,n,a)=>{a.r(n),a.d(n,{default:()=>s});var t,r=a(2245),o=a(58722),d=a(97491),i=a(81631),l=a(55204),c=a(18168);!function(e){e.handleLink="rendermime:handle-local-link"}(t||(t={}));const s={id:"@jupyterlab/rendermime-extension:plugin",description:"Provides the render mime registry.",optional:[o.T,d._y,r.hd,d.sc,c.gv],provides:d.ZD,activate:function(e,n,a,r,o,d){const s=(null!=d?d:c.Sr).load("jupyterlab");return n&&e.commands.addCommand(t.handleLink,{label:s.__("Handle Local Link"),execute:a=>{const t=a.path,r=a.id,o=a.scope||"server";if(t)return"kernel"===o?e.commands.hasCommand(u)?e.commands.execute(u,{path:t}):void console.warn("Cannot open kernel file: debugger sources provider not available"):n.services.contents.get(t,{content:!1}).then((()=>{const e=n.registry.defaultRenderedWidgetFactory(t),a=n.openOrReveal(t,e.name);a&&r&&a.setFragment(r)}))}}),new i.D({initialFactories:l.Nf,linkHandler:n?{handleLink:(n,a,r)=>{"A"===n.tagName&&n.hasAttribute("download")||e.commandLinker.connectNode(n,t.handleLink,{path:a,id:r})},handlePath:(n,a,r,o)=>{e.commandLinker.connectNode(n,t.handleLink,{path:a,id:o,scope:r})}}:void 0,latexTypesetter:null!=a?a:void 0,markdownParser:null!=o?o:void 0,translator:null!=d?d:void 0,sanitizer:null!=r?r:void 0})},autoStart:!0},u="debugger:open-source"}}]);