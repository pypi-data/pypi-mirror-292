"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[3106],{3106:(e,t,a)=>{a.r(t),a.d(t,{default:()=>r});var s=a(83243),o=a(2245),i=a(35909),c=a(68471),d=a(18168);const n="@jupyterlab/statusbar-extension:plugin",r={id:n,description:"Provides the application status bar.",requires:[d.gv],provides:c.WQ,autoStart:!0,activate:(e,t,a,s,o)=>{const i=t.load("jupyterlab"),d=new c.A_;d.id="jp-main-statusbar",e.shell.add(d,"bottom"),a&&a.layoutModified.connect((()=>{d.update()}));const r=i.__("Main Area"),l="statusbar:toggle";if(e.commands.addCommand(l,{label:i.__("Show Status Bar"),execute:()=>{d.setHidden(d.isVisible),s&&s.set(n,"visible",d.isVisible)},isToggled:()=>d.isVisible}),e.commands.commandExecuted.connect(((t,a)=>{"application:reset-layout"!==a.id||d.isVisible||e.commands.execute(l).catch((e=>{console.error("Failed to show the status bar.",e)}))})),o&&o.addItem({command:l,category:r}),s){const t=s.load(n),a=e=>{const t=e.get("visible").composite;d.setHidden(!t)};Promise.all([t,e.restored]).then((([e])=>{a(e),e.changed.connect((e=>{a(e)}))})).catch((e=>{console.error(e.message)}))}return d},optional:[s.r,i.O,o.WW]}}}]);