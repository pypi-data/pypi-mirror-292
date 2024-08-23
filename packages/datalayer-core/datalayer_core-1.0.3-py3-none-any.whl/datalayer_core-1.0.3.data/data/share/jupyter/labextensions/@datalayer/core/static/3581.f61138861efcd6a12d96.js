/*! For license information please see 3581.f61138861efcd6a12d96.js.LICENSE.txt */
(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[3581],{63581:(e,t,n)=>{"use strict";n.r(t),n.d(t,{Twitter:()=>w,default:()=>x});var r=n(74512),o=n(66029),i=n.n(o),a=n(71082),l="https://platform.twitter.com/widgets.js",c="createTimeline",s=function(e){var t=i().useRef(null),r=i().useState(!0),o=r[0],a=r[1];return i().useEffect((function(){var r=!0;return n(98283)(l,"twitter-embed",(function(){if(window.twttr){if(r){if(!window.twttr.widgets[c])return void console.error("Method "+c+" is not present anymore in twttr.widget api");var n=function(){var n,r,o=Object.assign({},e.options);return null!=e&&e.autoHeight&&(o.height=null===(n=t.current)||void 0===n||null===(r=n.parentNode)||void 0===r?void 0:r.offsetHeight),Object.assign({},o,{theme:null==e?void 0:e.theme,linkColor:null==e?void 0:e.linkColor,borderColor:null==e?void 0:e.borderColor,lang:null==e?void 0:e.lang,tweetLimit:null==e?void 0:e.tweetLimit,ariaPolite:null==e?void 0:e.ariaPolite})}();n=function(t){return t.chrome="",e.noHeader&&(t.chrome=t.chrome+" noheader"),e.noFooter&&(t.chrome=t.chrome+" nofooter"),e.noBorders&&(t.chrome=t.chrome+" noborders"),e.noScrollbar&&(t.chrome=t.chrome+" noscrollbar"),e.transparent&&(t.chrome=t.chrome+" transparent"),t}(n),window.twttr.widgets[c]({sourceType:e.sourceType,screenName:e.screenName,userId:e.userId,ownerScreenName:e.ownerScreenName,slug:e.slug,id:e.id||e.widgetId,url:e.url},null==t?void 0:t.current,n).then((function(t){a(!1),e.onLoad&&e.onLoad(t)}))}}else console.error("Failure to load window.twttr, aborting load")})),function(){r=!1}}),[]),i().createElement(i().Fragment,null,o&&i().createElement(i().Fragment,null,e.placeholder),i().createElement("div",{ref:t}))},u="createTweet",d=function(e){var t=i().useRef(null),r=i().useState(!0),o=r[0],a=r[1];return i().useEffect((function(){var r=!0;return n(98283)(l,"twitter-embed",(function(){if(window.twttr){if(r){if(!window.twttr.widgets[u])return void console.error("Method "+u+" is not present anymore in twttr.widget api");window.twttr.widgets[u](e.tweetId,null==t?void 0:t.current,e.options).then((function(t){a(!1),e.onLoad&&e.onLoad(t)}))}}else console.error("Failure to load window.twttr, aborting load")})),function(){r=!1}}),[]),i().createElement(i().Fragment,null,o&&i().createElement(i().Fragment,null,e.placeholder),i().createElement("div",{ref:t}))},f=n(43712),h=n(42799),m=n(99900);const w=()=>{const e=(0,f.aF)(),t=(0,h.qX)(),n=(0,h.Ae)(),{tweet:i,unlinkTwitter:l}=(0,f.YT)(),{enqueueToast:c}=(0,f.pm)(),u=t.layout().screenCapture,[w,x]=(0,o.useState)(void 0!==e.twitter?.screenName),[v,p]=(0,o.useState)(),[g,j]=(0,o.useState)({text:void 0}),[b,y]=(0,o.useState)({text:void 0});return(0,o.useEffect)((()=>{y({...b,text:void 0===g.text?void 0:g.text.length>2&&g.text.length<280})}),[g]),(0,o.useEffect)((()=>{x(void 0!==e.twitter?.screenName)}),[e]),(0,r.jsxs)(r.Fragment,{children:[(0,r.jsx)(m.NX,{tab:"twitter"}),(0,r.jsxs)(a.Box,{display:"grid",gridTemplateColumns:"1fr 1fr",children:[(0,r.jsxs)(a.Box,{children:[(0,r.jsx)(a.Box,{children:w?(0,r.jsxs)(a.Box,{mt:3,children:[(0,r.jsx)(a.Box,{mb:3,children:(0,r.jsxs)(a.Text,{children:["Your Datalayer account is linked with the Twitter account ",(0,r.jsxs)(a.Link,{target:"_blank",href:`https://twitter.com/${e.twitter?.screenName}`,children:["@",e.twitter?.screenName]}),"."]})}),(0,r.jsx)(a.Button,{variant:"default",onClick:e=>{e.preventDefault(),l().then((e=>{e.success&&(x(!1),c("Your account is unlinked.",{variant:"success"}))}))},children:"Unlink your Twitter account"})]}):(0,r.jsx)(a.Box,{mt:3,children:(0,r.jsx)(a.Button,{variant:"primary",onClick:t=>{t.preventDefault(),window.location.href=`${n.configuration.iamRunUrl}/api/iam/v1/twitter/link/${e?.handle}`},children:"Link with your Twitter account"})})}),(0,r.jsx)(a.Box,{pt:3,children:w&&(0,r.jsxs)(r.Fragment,{children:[(0,r.jsxs)(a.FormControl,{children:[(0,r.jsx)(a.FormControl.Label,{children:"Your tweet"}),(0,r.jsx)(a.Textarea,{block:!0,value:g.text,onChange:e=>{j((t=>({...t,text:e.target.value})))}}),g.text&&g.text.length>0&&!1===b.text&&(0,r.jsx)(a.FormControl.Validation,{variant:"error",children:"Tweet characters count must be between 2 and 280."})]}),u&&(0,r.jsxs)(r.Fragment,{children:[(0,r.jsx)(a.Box,{pt:3,children:(0,r.jsx)("img",{src:u})}),(0,r.jsx)(a.Box,{pt:3,children:(0,r.jsx)(a.Link,{href:"",onClick:e=>{e.preventDefault(),t.layout().captureScreen(void 0)},children:"Remove image."})})]}),(0,r.jsx)(a.Box,{pt:3,children:(0,r.jsx)(a.Button,{variant:"primary",disabled:!b.text,onClick:e=>{e.preventDefault(),p(void 0),i(g.text,u).then((e=>{e.success&&(j({text:""}),p(e.status.id_str),t.layout().captureScreen(void 0),c("Your tweet has been posted.",{variant:"success"}))}))},children:"Tweet"})})]})})]}),(0,r.jsxs)(a.Box,{ml:3,children:[v&&(0,r.jsx)(d,{tweetId:v}),w&&(0,r.jsx)(s,{sourceType:"profile",screenName:e.twitter?.screenName,options:{height:400}})]})]})]})},x=w},98283:(e,t,n)=>{var r,o,i;i=function(){var e,t,n=document,r=n.getElementsByTagName("head")[0],o=!1,i="push",a="readyState",l="onreadystatechange",c={},s={},u={},d={};function f(e,t){for(var n=0,r=e.length;n<r;++n)if(!t(e[n]))return o;return 1}function h(e,t){f(e,(function(e){return t(e),1}))}function m(t,n,r){t=t[i]?t:[t];var o=n&&n.call,a=o?n:r,l=o?t.join(""):n,x=t.length;function v(e){return e.call?e():c[e]}function p(){if(! --x)for(var e in c[l]=1,a&&a(),u)f(e.split("|"),v)&&!h(u[e],v)&&(u[e]=[])}return setTimeout((function(){h(t,(function t(n,r){return null===n?p():(r||/^https?:\/\//.test(n)||!e||(n=-1===n.indexOf(".js")?e+n+".js":e+n),d[n]?(l&&(s[l]=1),2==d[n]?p():setTimeout((function(){t(n,!0)}),0)):(d[n]=1,l&&(s[l]=1),void w(n,p)))}))}),0),m}function w(e,o){var i,c=n.createElement("script");c.onload=c.onerror=c[l]=function(){c[a]&&!/^c|loade/.test(c[a])||i||(c.onload=c[l]=null,i=1,d[e]=2,o())},c.async=1,c.src=t?e+(-1===e.indexOf("?")?"?":"&")+t:e,r.insertBefore(c,r.lastChild)}return m.get=w,m.order=function(e,t,n){!function r(o){o=e.shift(),e.length?m(o,r):m(o,t,n)}()},m.path=function(t){e=t},m.urlArgs=function(e){t=e},m.ready=function(e,t,n){e=e[i]?e:[e];var r,o=[];return!h(e,(function(e){c[e]||o[i](e)}))&&f(e,(function(e){return c[e]}))?t():(r=e.join("|"),u[r]=u[r]||[],u[r][i](t),n&&n(o)),m},m.done=function(e){m([null],e)},m},e.exports?e.exports=i():void 0===(o="function"==typeof(r=i)?r.call(t,n,t,e):r)||(e.exports=o)}}]);