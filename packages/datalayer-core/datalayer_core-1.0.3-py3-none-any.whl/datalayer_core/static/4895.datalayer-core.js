"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[4895],{24895:(e,t,r)=>{function i(e){var t,r;e?(t=/^(exx?|(ld|cp)([di]r?)?|[lp]ea|pop|push|ad[cd]|cpl|daa|dec|inc|neg|sbc|sub|and|bit|[cs]cf|x?or|res|set|r[lr]c?a?|r[lr]d|s[lr]a|srl|djnz|nop|[de]i|halt|im|in([di]mr?|ir?|irx|2r?)|ot(dmr?|[id]rx|imr?)|out(0?|[di]r?|[di]2r?)|tst(io)?|slp)(\.([sl]?i)?[sl])?\b/i,r=/^(((call|j[pr]|rst|ret[in]?)(\.([sl]?i)?[sl])?)|(rs|st)mix)\b/i):(t=/^(exx?|(ld|cp|in)([di]r?)?|pop|push|ad[cd]|cpl|daa|dec|inc|neg|sbc|sub|and|bit|[cs]cf|x?or|res|set|r[lr]c?a?|r[lr]d|s[lr]a|srl|djnz|nop|rst|[de]i|halt|im|ot[di]r|out[di]?)\b/i,r=/^(call|j[pr]|ret[in]?|b_?(call|jump))\b/i);var i=/^(af?|bc?|c|de?|e|hl?|l|i[xy]?|r|sp)\b/i,n=/^(n?[zc]|p[oe]?|m)\b/i,a=/^([hl][xy]|i[xy][hl]|slia|sll)\b/i,l=/^([\da-f]+h|[0-7]+o|[01]+b|\d+d?)\b/i;return{name:"z80",startState:function(){return{context:0}},token:function(c,s){if(c.column()||(s.context=0),c.eatSpace())return null;var u;if(c.eatWhile(/\w/)){if(e&&c.eat(".")&&c.eatWhile(/\w/),u=c.current(),!c.indentation())return c.match(l)?"number":null;if((1==s.context||4==s.context)&&i.test(u))return s.context=4,"variable";if(2==s.context&&n.test(u))return s.context=4,"variableName.special";if(t.test(u))return s.context=1,"keyword";if(r.test(u))return s.context=2,"keyword";if(4==s.context&&l.test(u))return"number";if(a.test(u))return"error"}else{if(c.eat(";"))return c.skipToEnd(),"comment";if(c.eat('"')){for(;(u=c.next())&&'"'!=u;)"\\"==u&&c.next();return"string"}if(c.eat("'")){if(c.match(/\\?.'/))return"number"}else if(c.eat(".")||c.sol()&&c.eat("#")){if(s.context=5,c.eatWhile(/\w/))return"def"}else if(c.eat("$")){if(c.eatWhile(/[\da-f]/i))return"number"}else if(c.eat("%")){if(c.eatWhile(/[01]/))return"number"}else c.next()}return null}}}r.r(t),r.d(t,{ez80:()=>a,z80:()=>n});const n=i(!1),a=i(!0)}}]);