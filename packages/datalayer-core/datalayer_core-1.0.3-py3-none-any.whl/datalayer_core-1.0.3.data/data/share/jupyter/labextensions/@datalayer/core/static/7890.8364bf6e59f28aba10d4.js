"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[7890],{47890:(e,s,n)=>{n.r(s),n.d(s,{LessonPublic:()=>u,default:()=>h});var a=n(74512),l=n(66029),o=n(99608),t=n(71082),r=n(23189),i=n(75291),c=n(43712),d=n(42799);const u=()=>{const{lessonId:e}=(0,o.UO)();if(!e)return(0,a.jsx)(a.Fragment,{});const s=(0,d.qX)(),n=(0,i.useNotebookStore)(),u=s.iam().user,{refreshLesson:h,getLesson:x,cloneLesson:f}=(0,c.YT)(),y=(0,c.s0)(),j=(0,t.useConfirm)(),{enqueueToast:m}=(0,c.pm)(),[p,b]=(0,l.useState)();(0,l.useEffect)((()=>(s.layout().showBackdrop(),h(e).then((s=>{if(s.success){const s=x(e);s||y("/"),b(s)}})).finally((()=>{s.layout().hideBackdrop()})),()=>{b(void 0),n.reset(),s.layout().setItem(void 0)})),[e]);const g=(0,l.useCallback)((async n=>{j({title:"Are you sure?",content:"Please confirm you want to clone this lesson in your private library."}).then((n=>{n&&(s.layout().showBackdrop(),f(e).then((e=>{e.success&&(m(e.message,{variant:"success"}),s.layout().triggerItemsRefresh(),y(`/${u?.handle}/library/lessons`))})).finally((()=>{s.layout().hideBackdrop()})))}))}),[j,p]);return p?(0,a.jsxs)(a.Fragment,{children:[(0,a.jsx)(t.Pagehead,{children:(0,a.jsxs)(t.Box,{display:"flex",children:[(0,a.jsx)(t.Box,{flex:1,children:(0,a.jsx)(t.Heading,{sx:{fontSize:3},children:"Public lesson"})}),(0,a.jsx)(t.Box,{children:(0,a.jsxs)(t.ButtonGroup,{children:[p&&u?.handle===p.owner.handle&&(0,a.jsx)(t.Button,{variant:"default",size:"small",onClick:()=>y(`/${p.organization?.handle??p.owner?.handle}/${p.space?.handle}/lesson/${p.id}`),children:"Edit"}),u&&(0,a.jsx)(t.Button,{variant:"default",size:"small",leadingVisual:r.jcu,onClick:g,children:"Clone"})]})})]})}),(0,a.jsx)(t.Box,{children:(0,a.jsx)(t.Text,{children:p.description})}),(0,a.jsx)(t.Box,{children:p.nbformat&&(0,a.jsx)(i.Notebook,{id:e,height:"calc(100vh - 240px)",maxHeight:"calc(100vh - 240px)",nbformat:p.nbformat,readOnly:!1,cellMetadataPanel:!1,CellSidebar:i.CellSidebarRun})})]}):(0,a.jsx)(a.Fragment,{})},h=u}}]);