"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[413],{80413:(e,t,n)=>{n.r(t),n.d(t,{smalltalk:()=>d});var a=/[+\-\/\\*~<>=@%|&?!.,:;^]/,i=/true|false|nil|self|super|thisContext/,r=function(e,t){this.next=e,this.parent=t},s=function(e,t,n){this.name=e,this.context=t,this.eos=n},o=function(){this.context=new r(l,null),this.expectVariable=!0,this.indentation=0,this.userIndentationDelta=0};o.prototype.userIndent=function(e,t){this.userIndentationDelta=e>0?e/t-this.indentation:0};var l=function(e,t,n){var o=new s(null,t,!1),l=e.next();return'"'===l?o=u(e,new r(u,t)):"'"===l?o=c(e,new r(c,t)):"#"===l?"'"===e.peek()?(e.next(),o=h(e,new r(h,t))):e.eatWhile(/[^\s.{}\[\]()]/)?o.name="string.special":o.name="meta":"$"===l?("<"===e.next()&&(e.eatWhile(/[^\s>]/),e.next()),o.name="string.special"):"|"===l&&n.expectVariable?o.context=new r(x,t):/[\[\]{}()]/.test(l)?(o.name="bracket",o.eos=/[\[{(]/.test(l),"["===l?n.indentation++:"]"===l&&(n.indentation=Math.max(0,n.indentation-1))):a.test(l)?(e.eatWhile(a),o.name="operator",o.eos=";"!==l):/\d/.test(l)?(e.eatWhile(/[\w\d]/),o.name="number"):/[\w_]/.test(l)?(e.eatWhile(/[\w\d_]/),o.name=n.expectVariable?i.test(e.current())?"keyword":"variable":null):o.eos=n.expectVariable,o},u=function(e,t){return e.eatWhile(/[^"]/),new s("comment",e.eat('"')?t.parent:t,!0)},c=function(e,t){return e.eatWhile(/[^']/),new s("string",e.eat("'")?t.parent:t,!1)},h=function(e,t){return e.eatWhile(/[^']/),new s("string.special",e.eat("'")?t.parent:t,!1)},x=function(e,t){var n=new s(null,t,!1);return"|"===e.next()?(n.context=t.parent,n.eos=!0):(e.eatWhile(/[^|]/),n.name="variable"),n};const d={name:"smalltalk",startState:function(){return new o},token:function(e,t){if(t.userIndent(e.indentation(),e.indentUnit),e.eatSpace())return null;var n=t.context.next(e,t.context,t);return t.context=n.context,t.expectVariable=n.eos,n.name},blankLine:function(e,t){e.userIndent(0,t)},indent:function(e,t,n){var a=e.context.next===l&&t&&"]"===t.charAt(0)?-1:e.userIndentationDelta;return(e.indentation+a)*n.unit},languageData:{indentOnInput:/^\s*\]$/}}}}]);