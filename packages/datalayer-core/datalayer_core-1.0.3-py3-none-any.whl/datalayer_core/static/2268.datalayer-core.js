"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[2268],{72268:(e,a,o)=>{o.r(a),o.d(a,{NotebookPublic:()=>m,default:()=>p});var n=o(4565),s=o(89456),l=o(17168),t=o(41237),r=o(36088),i=o(66578),c=o(83773),d=o(43429),h=o(52333),u=o(20398),b=o(34441),x=o(18475),k=o(15847),f=o(36130),y=o(91899),j=o(78584);const m=()=>{const e=(0,j.qX)(),a=(0,x.qL)(),o=e.iam().user,m=e.layout().space,{notebookId:p}=(0,l.UO)();if(!p)return(0,n.jsx)(n.Fragment,{});const{refreshNotebook:g,getNotebook:v,cloneNotebook:Z}=(0,y.YT)(),w=(0,y.s0)(),C=(0,t.N)(),{enqueueToast:N}=(0,y.pm)(),[z,B]=(0,s.useState)();(0,s.useEffect)((()=>(e.layout().showBackdrop(),g(p).then((e=>{if(e.success){const e=v(p);e||w("/"),B(e)}})).finally((()=>{e.layout().hideBackdrop()})),()=>{B(void 0),a.reset(),e.layout().setItem(void 0)})),[p]);const P=(0,s.useCallback)((async a=>{C({title:"Are you sure?",content:"Please confirm you want to clone this notebook in your private library."}).then((a=>{a&&(e.layout().showBackdrop(),Z(p).then((a=>{a.success&&(N(a.message,{variant:"success"}),e.layout().triggerItemsRefresh(),w(`/${o?.handle}/library/notebooks`))})).finally((()=>{e.layout().hideBackdrop()})))}))}),[C,z]);return z?(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(r.Z,{children:(0,n.jsxs)(i.Z,{display:"flex",children:[(0,n.jsx)(i.Z,{flex:1,children:(0,n.jsx)(c.Z,{sx:{fontSize:3},children:"Public notebook"})}),(0,n.jsx)(i.Z,{children:(0,n.jsxs)(d.Z,{children:[z&&o?.handle===z.owner.handle&&(0,n.jsx)(h.r,{variant:"invisible",size:"small",onClick:()=>w(`/${z.organization?.handle??z.owner?.handle}/${z.space?.handle}/notebook/${z.id}`),children:"Edit"}),o&&m&&(0,n.jsx)(h.r,{variant:"default",size:"small",leadingVisual:b.jcu,onClick:P,children:"Clone"})]})})]})}),(0,n.jsx)(i.Z,{children:(0,n.jsx)(u.Z,{children:z.description})}),(0,n.jsx)(i.Z,{children:z.nbformat&&(0,n.jsx)(k.a,{id:p,height:"calc(100vh - 240px)",maxHeight:"calc(100vh - 240px)",nbformat:z.nbformat,readOnly:!1,cellMetadataPanel:!1,CellSidebar:f.l})})]}):(0,n.jsx)(n.Fragment,{})},p=m}}]);