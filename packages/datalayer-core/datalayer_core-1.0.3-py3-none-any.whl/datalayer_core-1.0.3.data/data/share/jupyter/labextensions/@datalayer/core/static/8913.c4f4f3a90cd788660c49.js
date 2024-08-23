"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[8913],{8913:(e,t,a)=>{a.r(t),a.d(t,{CellEdit:()=>C,default:()=>B});var n=a(74512),s=a(66029),l=a(37704),r=a(99608),o=a(71082),i=a(23189),c=a(43712),u=a(42799),d=a(31131),p=a(75291),m=a(31620),h=a.n(m),x=a(86433);const g=()=>{const e=(0,u.qX)(),t=e.cell().cell,a=t?.outputCdnUrl||!t?.outputData?.startsWith(x.nf);return(0,n.jsx)(n.Fragment,{children:a?(0,n.jsx)(o.Button,{variant:"danger",onClick:()=>{e.cell().update({outputCdnUrl:"",outputData:x.D_})},children:"Remove outputshot"}):(0,n.jsx)(o.Button,{variant:"primary",onClick:()=>{e.layout().showBackdrop();const t=document.getElementsByClassName("jp-OutputArea")[0];h()(t).then((t=>{const a=document.createElement("canvas"),n=a.getContext("2d"),s=t.width,l=t.height;a.width=s,a.height=l,n?.drawImage(t,0,0);const r=a.toDataURL("",1);e.cell().update({outputCdnUrl:"",outputData:r})})).finally((()=>{e.layout().hideBackdrop()}))},children:"Take outputshot"})})};var j=a(25843);const y=()=>{const e=(0,u.qX)(),t=e.cell().cell;if(!t)return(0,n.jsx)(n.Fragment,{});const{updateCell:a}=(0,c.YT)(),l=(0,c.aF)(),{enqueueToast:r}=(0,c.pm)(),i=(0,p.useOutputsStore)(),d=e.layout().leftSidebarVariant,m=i.getInput("cell"),[h,x]=(0,s.useState)(!1),y=e.layout().organization,f=e.layout().space,[v,C]=(0,s.useState)({name:t.name,description:t.description}),[B,k]=(0,s.useState)({name:!0,description:!0});return(0,s.useEffect)((()=>{k({...B,name:void 0===v.name?void 0:v.name.length>2,description:void 0===v.description?void 0:v.description.length>2})}),[v]),(0,n.jsx)(n.Fragment,{children:(0,n.jsxs)(o.Box,{sx:{display:"grid",gridTemplateColumns:"1fr 1fr"},children:[(0,n.jsxs)(o.Box,{sx:{label:{marginTop:2}},children:[(0,n.jsxs)(o.FormControl,{children:[(0,n.jsx)(o.FormControl.Label,{children:"Name"}),(0,n.jsx)(o.TextInput,{block:!0,value:v.name,onChange:t=>{C((e=>({...e,name:t.target.value}))),e.cell().update({name:t.target.value})}}),!1===B.name&&(0,n.jsx)(o.FormControl.Validation,{variant:"error",children:"Name must have more than 2 characters."})]}),(0,n.jsxs)(o.FormControl,{children:[(0,n.jsx)(o.FormControl.Label,{children:"Description"}),(0,n.jsx)(o.Textarea,{block:!0,value:v.description,onChange:t=>{C((e=>({...e,description:t.target.value}))),e.cell().update({description:t.target.value})}}),!1===B.description&&(0,n.jsx)(o.FormControl.Validation,{variant:"error",children:"Description must have more than 2 characters."})]}),(0,n.jsxs)(o.FormControl,{children:[(0,n.jsx)(o.Button,{variant:"primary",disabled:h||!B.name||!B.description,sx:{marginTop:2},onClick:()=>{t?.outputData.length>3e5?r(`Output screenshot is too large (actual size is ${t?.outputData.length}, the maximum allowed is 300000)`,{variant:"error"}):(e.layout().showBackdrop(),x(!0),a({id:t?.id,name:t?.name,description:t?.description,source:m,outputCdnUrl:t.outputCdnUrl,outputData:t?.outputCdnUrl?void 0:t?.outputData,accountType:"organization-space"===d?"organization":"user",accountId:"organization-space"===d?y?.id:l?.id,spaceId:f?.id}).then((a=>{if(x(!1),a.success){const a={...t,public:t?.public,description:t?.description,source:m,outputCdnUrl:t?.outputCdnUrl,outputData:t?.outputData};e.layout().triggerItemsRefresh(),e.cell().update(a),r("The cell is successfully updated.",{variant:"success"})}})).finally((()=>{e.layout().hideBackdrop(),x(!1)})))},children:h?"Saving cell...":"Save cell"}),(0,n.jsx)(g,{})]})]}),(0,n.jsx)(o.Box,{ml:5,children:(0,n.jsx)(j.Z,{cell:t})})]})})},f=e=>{switch(e.contentType){case"application/vnd.ms-excel":case"text/csv":return`# --- ✅ Load the ${e.fileName}.${e.datasetExtension} dataset (${e.mimeType})\nimport pandas as pd\n${e.fileName}_${e.datasetExtension} = pd.read_csv("${e.cdnUrl}")\n${e.fileName}_${e.datasetExtension}\n\n`;case"image/png":case"image/jpg":case"image/jpeg":return`# --- ✅ Display the ${e.fileName}.${e.datasetExtension} dataset (${e.mimeType})\nfrom IPython.display import Image\nurl = "${e.cdnUrl}"\nImage(url, width=300)\n\n`;default:return`# --- 😞 File of type ${e.contentType} is not supported for now.\n`}},v=e=>{const{source:t,outputshotRef:a}=e,{defaultKernel:s}=(0,p.useJupyter)();return s?(0,n.jsx)("div",{ref:a,style:{marginTop:"8px"},children:(0,n.jsx)(p.Output,{showEditor:!0,autoRun:!0,kernel:s,code:t,id:"cell",insertText:f})}):(0,n.jsx)(n.Fragment,{})},C=()=>{const{cellId:e}=(0,r.UO)();if(!e)return(0,n.jsx)(n.Fragment,{});const t=(0,c.aF)(),a=(0,u.qX)(),p=(a.layout().organization,a.layout().space),m=a.cell().cell,h=(0,o.useConfirm)(),x=(0,c.s0)(),{enqueueToast:g}=(0,c.pm)(),{getCell:j,refreshCell:f,cloneCell:C}=(0,c.YT)(),[B,k]=(0,s.useState)(),[T,b]=(0,s.useState)(!1),F=(0,s.useMemo)((()=>(0,s.createRef)()),[]);(0,s.useEffect)((()=>{const t=document.getElementById("right-panel-id"),s=(0,l.createPortal)((0,n.jsx)(d.Z,{}),t);return a.layout().setRightPortal({portal:s,pinned:!1}),f(e).then((t=>{if(t.success){const t=j(e);t?(k(t.source),a.cell().update(t),a.layout().setItem(t),k(t.source)):x("/")}})),()=>{a.layout().setItem(void 0)}}),[e]);const I=(0,s.useCallback)((async n=>{h({title:"Are you sure?",content:"Please confirm you want to clone this cell in your private library."}).then((n=>{n&&C(e).then((e=>{e.success&&(g(e.message,{variant:"success"}),a.layout().triggerItemsRefresh(),x(`/${t?.handle}/library/cells`))}))}))}),[h,m]);return(0,n.jsx)(n.Fragment,{children:m&&B&&(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(o.Pagehead,{children:(0,n.jsxs)(o.Box,{display:"flex",children:[(0,n.jsx)(o.Box,{flex:1,children:(0,n.jsx)(o.Heading,{sx:{fontSize:3},children:"Cell editor"})}),(0,n.jsx)(o.Box,{children:T?(0,n.jsx)(o.Button,{variant:"invisible",size:"small",onClick:()=>b(!1),children:"Hide details"}):(0,n.jsx)(o.Button,{variant:"invisible",size:"small",onClick:()=>b(!0),children:"Show details"})}),(0,n.jsx)(o.Box,{ml:1,children:t&&p&&(0,n.jsx)(o.Button,{variant:"invisible",size:"small",leadingVisual:i.jcu,onClick:I,children:"Clone"})})]})}),(0,n.jsxs)(o.Box,{children:[T&&(0,n.jsx)(o.Box,{children:(0,n.jsx)(y,{})}),(0,n.jsx)(o.Box,{children:(0,n.jsx)(v,{source:B,outputshotRef:F,cellId:m?.id})})]})]})})},B=C}}]);