"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[1579],{21579:(e,l,s)=>{s.r(l),s.d(l,{CellPublic:()=>x,default:()=>h});var n=s(74512),r=s(66029),t=s(99608),a=s(71082),i=s(23189),c=s(75291),o=s(43712),d=s(42799),u=s(86433);const x=()=>{const{cellId:e}=(0,t.UO)();if(!e)return(0,n.jsx)(n.Fragment,{});const[l,s]=(0,r.useState)(!1),{enqueueToast:x}=(0,o.pm)(),{defaultKernel:h}=(0,c.useJupyter)(),{getCell:j,refreshCell:f,cloneCell:m}=(0,o.YT)(),p=(0,d.qX)(),y=p.iam().user,B=(p.layout().organization,p.layout().space),g=(0,o.s0)(),C=(0,a.useConfirm)(),k=p.cell().cell,w=k?k.outputCdnUrl?k.outputCdnUrl:k.outputData:u.D_;(0,r.useEffect)((()=>{k&&k.id===e&&s(!0),l||f(e).then((l=>{if(l.success){const l=j(e);l?p.cell().update(l):g("/")}})).finally((()=>{s(!0)}))}),[]);const b=(0,r.useCallback)((async l=>{C({title:"Are you sure?",content:"Please confirm you want to clone this cell in your private library."}).then((l=>{l&&m(e).then((e=>{e.success&&(x(e.message,{variant:"success"}),p.layout().triggerItemsRefresh(),g(`/${y?.handle}/library/cells`))}))}))}),[C,k]);return k&&l?(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(a.Pagehead,{children:(0,n.jsxs)(a.Box,{display:"flex",children:[(0,n.jsx)(a.Box,{flex:1,children:(0,n.jsx)(a.Heading,{sx:{fontSize:3},children:"Public cell"})}),(0,n.jsx)(a.Box,{children:(0,n.jsxs)(a.ButtonGroup,{children:[k&&y?.handle===k.owner.handle&&(0,n.jsx)(a.Button,{variant:"default",size:"small",onClick:()=>g(`/${k.organization?.handle??k.owner?.handle}/${k.space?.handle}/cell/${k.id}`),children:"Edit"}),y&&B&&(0,n.jsx)(a.Button,{variant:"default",size:"small",leadingVisual:i.jcu,onClick:b,children:"Clone"})]})})]})}),(0,n.jsxs)(a.Box,{children:[(0,n.jsxs)(a.Box,{children:[(0,n.jsx)(a.Box,{mb:3}),(0,n.jsxs)(a.Box,{sx:{display:"grid",gridTemplateColumns:"1fr 1fr"},children:[(0,n.jsxs)(a.Box,{children:[(0,n.jsx)(a.Box,{children:(0,n.jsx)(a.Text,{children:k.name})}),(0,n.jsx)(a.Box,{children:(0,n.jsxs)(a.Text,{children:["By ",k.owner.displayName," ",(0,n.jsxs)(a.Link,{href:"",onClick:e=>g(`/${k.owner.handle}`,e),children:["@",k.owner.handle]})]})}),(0,n.jsx)(a.Box,{mt:5,children:(0,n.jsx)(a.Text,{children:k.description})})]}),(0,n.jsx)(a.Box,{ml:3,children:(0,n.jsx)("img",{src:w,style:{maxHeight:400}})})]})]}),(0,n.jsx)(a.Box,{children:h&&(0,n.jsx)(c.Output,{showEditor:!0,autoRun:!0,kernel:h,code:k.source,id:"cell"})})]})]}):(0,n.jsx)(n.Fragment,{})},h=x}}]);