"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[4213],{84213:(e,s,t)=>{t.r(s),t.d(s,{ExercisePublic:()=>v,default:()=>b});var n=t(91896),r=t(56769),i=t(59886),a=t(36705),l=t(64506),c=t(81457),o=t(31728),d=t(77402),u=t(13676),h=t(74151),x=t(39617),p=t(80299),f=t(35323),j=t(54515),g=t(96193),m=t(71124),Z=t(90673),y=t(45209);const v=()=>{const{exerciseId:e}=(0,i.UO)();if(!e)return(0,n.jsx)(n.Fragment,{});const s=(0,y.qX)(),t=(0,p.useOutputsStore)(),v=(s.layout().organization,s.iam().user),{kernelManager:b,defaultKernel:k}=(0,f.W$)(),{refreshExercise:E,getExercise:S,cloneExercise:$}=(0,Z.YT)(),C=(0,Z.s0)(),T=(0,a.N)(),{enqueueToast:w}=(0,Z.pm)(),[P]=(0,r.useState)("exercise-student"),[_,I]=(0,r.useState)(!1),[V,z]=(0,r.useState)(),[R,M]=(0,r.useState)((0,j.ZI)()),[q,D]=(0,r.useState)(!1),F=t.getInput(P),O=(0,r.useMemo)((()=>k),[b]),Y=t.getGradeSuccess(P);(0,r.useEffect)((()=>{Y&&(D(Y),setTimeout((()=>{D(!1)}),5e3))}),[Y]),(0,r.useEffect)((()=>{E(e).then((s=>{if(s.success){const s=S(e);s||C("/"),z(s)}}))}),[]);const G=(0,r.useCallback)((async t=>{T({title:"Are you sure?",content:"Please confirm you want to clone this exercise in your private library."}).then((t=>{t&&$(e).then((e=>{e.success&&(w(e.message,{variant:"success"}),s.layout().triggerItemsRefresh(),C(`/${v.handle}/library/exercises`))}))}))}),[T,V]);return V?(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(l.Z,{children:(0,n.jsxs)(c.Z,{display:"flex",children:[(0,n.jsx)(c.Z,{flex:1,children:(0,n.jsx)(o.Z,{sx:{fontSize:3},children:"Exercise"})}),(0,n.jsx)(c.Z,{children:(0,n.jsxs)(d.Z,{children:[v&&V&&(0,n.jsx)(u.r,{variant:"default",size:"small",onClick:()=>C(`/${V.organization?.handle??V.owner?.handle}/${V.space?.handle}/exercise/${V.id}`),children:"Edit"}),v&&V&&(0,n.jsx)(u.r,{variant:"default",size:"small",leadingVisual:x.jcu,onClick:G,children:"Clone"})]})})]})}),(0,n.jsxs)(c.Z,{children:[(0,n.jsx)(h.Z,{children:V.name}),(0,n.jsx)(h.Z,{as:"p",color:"fg.muted",bg:"neutral.muted",p:2,children:V.description})]}),(0,n.jsx)(c.Z,{children:(0,n.jsx)(g.r,{showEditor:!0,autoRun:!1,disableRun:!1,kernel:O,id:P,codePre:V.codePre,code:V.codeQuestion,receipt:R})}),(0,n.jsxs)(c.Z,{display:"flex",gridGap:3,pt:2,pb:2,children:[(0,n.jsx)(c.Z,{children:(0,n.jsx)(u.r,{variant:"danger",leadingVisual:x.UOT,onClick:e=>{e.preventDefault(),I(!_)},children:"Show help"})}),(0,n.jsx)(c.Z,{children:(0,n.jsx)(u.r,{variant:"default",leadingVisual:x.bnu,onClick:e=>{e.preventDefault(),t.setInput(P,V.codeQuestion)},children:"Reset"})})]}),_&&(0,n.jsx)(h.Z,{as:"p",color:"danger.fg",p:2,children:V.help??"No help available."}),(0,n.jsxs)(c.Z,{children:[(0,n.jsx)(u.r,{variant:"default",leadingVisual:x.Zi2,sx:{marginTop:2,marginBottom:2},onClick:e=>{e.preventDefault(),t.setExecuteRequest(P,`\nsetup_state(stu_code = """${V.codePre}\n${F}""", sol_code = """${V.codePre}\n${V.codeSolution}""")\n${V.codeTest}\nfrom IPython.core.display import HTML\nHTML('<div style="display: none">You have passed the exercise! Your receipt is ${R}</div><h1>🎉 Success!</h1>')\n`)},children:"Validate your solution"}),(0,n.jsx)(h.Z,{as:"p",color:"fg.onEmphasis",bg:"neutral.emphasis",p:2,children:"Validate your solution with this button."})]}),q&&(0,n.jsx)(m.Z,{})]}):(0,n.jsx)(n.Fragment,{})},b=v}}]);