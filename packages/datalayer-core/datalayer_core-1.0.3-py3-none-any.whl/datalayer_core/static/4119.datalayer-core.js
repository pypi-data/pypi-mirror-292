"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[4119],{14119:(e,s,a)=>{a.r(s),a.d(s,{LessonPublic:()=>b,default:()=>g});var l=a(4565),n=a(89456),r=a(17168),t=a(41237),i=a(36088),c=a(66578),o=a(83773),d=a(43429),h=a(52333),u=a(20398),x=a(34441),f=a(18475),y=a(15847),j=a(36130),m=a(91899),p=a(78584);const b=()=>{const{lessonId:e}=(0,r.UO)();if(!e)return(0,l.jsx)(l.Fragment,{});const s=(0,p.qX)(),a=(0,f.qL)(),b=s.iam().user,{refreshLesson:g,getLesson:k,cloneLesson:v}=(0,m.YT)(),Z=(0,m.s0)(),w=(0,t.N)(),{enqueueToast:C}=(0,m.pm)(),[L,z]=(0,n.useState)();(0,n.useEffect)((()=>(s.layout().showBackdrop(),g(e).then((s=>{if(s.success){const s=k(e);s||Z("/"),z(s)}})).finally((()=>{s.layout().hideBackdrop()})),()=>{z(void 0),a.reset(),s.layout().setItem(void 0)})),[e]);const B=(0,n.useCallback)((async a=>{w({title:"Are you sure?",content:"Please confirm you want to clone this lesson in your private library."}).then((a=>{a&&(s.layout().showBackdrop(),v(e).then((e=>{e.success&&(C(e.message,{variant:"success"}),s.layout().triggerItemsRefresh(),Z(`/${b?.handle}/library/lessons`))})).finally((()=>{s.layout().hideBackdrop()})))}))}),[w,L]);return L?(0,l.jsxs)(l.Fragment,{children:[(0,l.jsx)(i.Z,{children:(0,l.jsxs)(c.Z,{display:"flex",children:[(0,l.jsx)(c.Z,{flex:1,children:(0,l.jsx)(o.Z,{sx:{fontSize:3},children:"Public lesson"})}),(0,l.jsx)(c.Z,{children:(0,l.jsxs)(d.Z,{children:[L&&b?.handle===L.owner.handle&&(0,l.jsx)(h.r,{variant:"default",size:"small",onClick:()=>Z(`/${L.organization?.handle??L.owner?.handle}/${L.space?.handle}/lesson/${L.id}`),children:"Edit"}),b&&(0,l.jsx)(h.r,{variant:"default",size:"small",leadingVisual:x.jcu,onClick:B,children:"Clone"})]})})]})}),(0,l.jsx)(c.Z,{children:(0,l.jsx)(u.Z,{children:L.description})}),(0,l.jsx)(c.Z,{children:L.nbformat&&(0,l.jsx)(y.a,{id:e,height:"calc(100vh - 240px)",maxHeight:"calc(100vh - 240px)",nbformat:L.nbformat,readOnly:!1,cellMetadataPanel:!1,CellSidebar:j.l})})]}):(0,l.jsx)(l.Fragment,{})},g=b}}]);