"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[6318],{6318:(e,t,n)=>{n.r(t),n.d(t,{xQuery:()=>h});var r=function(){function e(e){return{type:e,style:"keyword"}}for(var t=e("operator"),n={type:"atom",style:"atom"},r={type:"axis_specifier",style:"qualifier"},a={",":{type:"punctuation",style:null}},i=["after","all","allowing","ancestor","ancestor-or-self","any","array","as","ascending","at","attribute","base-uri","before","boundary-space","by","case","cast","castable","catch","child","collation","comment","construction","contains","content","context","copy","copy-namespaces","count","decimal-format","declare","default","delete","descendant","descendant-or-self","descending","diacritics","different","distance","document","document-node","element","else","empty","empty-sequence","encoding","end","entire","every","exactly","except","external","first","following","following-sibling","for","from","ftand","ftnot","ft-option","ftor","function","fuzzy","greatest","group","if","import","in","inherit","insensitive","insert","instance","intersect","into","invoke","is","item","language","last","lax","least","let","levels","lowercase","map","modify","module","most","namespace","next","no","node","nodes","no-inherit","no-preserve","not","occurs","of","only","option","order","ordered","ordering","paragraph","paragraphs","parent","phrase","preceding","preceding-sibling","preserve","previous","processing-instruction","relationship","rename","replace","return","revalidation","same","satisfies","schema","schema-attribute","schema-element","score","self","sensitive","sentence","sentences","sequence","skip","sliding","some","stable","start","stemming","stop","strict","strip","switch","text","then","thesaurus","times","to","transform","treat","try","tumbling","type","typeswitch","union","unordered","update","updating","uppercase","using","validate","value","variable","version","weight","when","where","wildcards","window","with","without","word","words","xquery"],s=0,o=i.length;s<o;s++)a[i[s]]=e(i[s]);var c=["xs:anyAtomicType","xs:anySimpleType","xs:anyType","xs:anyURI","xs:base64Binary","xs:boolean","xs:byte","xs:date","xs:dateTime","xs:dateTimeStamp","xs:dayTimeDuration","xs:decimal","xs:double","xs:duration","xs:ENTITIES","xs:ENTITY","xs:float","xs:gDay","xs:gMonth","xs:gMonthDay","xs:gYear","xs:gYearMonth","xs:hexBinary","xs:ID","xs:IDREF","xs:IDREFS","xs:int","xs:integer","xs:item","xs:java","xs:language","xs:long","xs:Name","xs:NCName","xs:negativeInteger","xs:NMTOKEN","xs:NMTOKENS","xs:nonNegativeInteger","xs:nonPositiveInteger","xs:normalizedString","xs:NOTATION","xs:numeric","xs:positiveInteger","xs:precisionDecimal","xs:QName","xs:short","xs:string","xs:time","xs:token","xs:unsignedByte","xs:unsignedInt","xs:unsignedLong","xs:unsignedShort","xs:untyped","xs:untypedAtomic","xs:yearMonthDuration"];for(s=0,o=c.length;s<o;s++)a[c[s]]=n;var u=["eq","ne","lt","le","gt","ge",":=","=",">",">=","<","<=",".","|","?","and","or","div","idiv","mod","*","/","+","-"];for(s=0,o=u.length;s<o;s++)a[u[s]]=t;var l=["self::","attribute::","child::","descendant::","descendant-or-self::","parent::","ancestor::","ancestor-or-self::","following::","preceding::","following-sibling::","preceding-sibling::"];for(s=0,o=l.length;s<o;s++)a[l[s]]=r;return a}();function a(e,t,n){return t.tokenize=n,n(e,t)}function i(e,t){var n=e.next(),g=!1,h=function(e){return'"'===e.current()?e.match(/^[^\"]+\"\:/,!1):"'"===e.current()&&e.match(/^[^\"]+\'\:/,!1)}(e);if("<"==n){if(e.match("!--",!0))return a(e,t,l);if(e.match("![CDATA",!1))return t.tokenize=f,"tag";if(e.match("?",!1))return a(e,t,p);var k=e.eat("/");e.eatSpace();for(var v,b="";v=e.eat(/[^\s\u00a0=<>\"\'\/?]/);)b+=v;return a(e,t,function(e,t){return function(n,r){return n.eatSpace(),t&&n.eat(">")?(y(r),r.tokenize=i,"tag"):(n.eat("/")||d(r,{type:"tag",name:e,tokenize:i}),n.eat(">")?(r.tokenize=i,"tag"):(r.tokenize=u,"tag"))}}(b,k))}if("{"==n)return d(t,{type:"codeblock"}),null;if("}"==n)return y(t),null;if(m(t))return">"==n?"tag":"/"==n&&e.eat(">")?(y(t),"tag"):"variable";if(/\d/.test(n))return e.match(/^\d*(?:\.\d*)?(?:E[+\-]?\d+)?/),"atom";if("("===n&&e.eat(":"))return d(t,{type:"comment"}),a(e,t,s);if(h||'"'!==n&&"'"!==n){if("$"===n)return a(e,t,c);if(":"===n&&e.eat("="))return"keyword";if("("===n)return d(t,{type:"paren"}),null;if(")"===n)return y(t),null;if("["===n)return d(t,{type:"bracket"}),null;if("]"===n)return y(t),null;var z=r.propertyIsEnumerable(n)&&r[n];if(h&&'"'===n)for(;'"'!==e.next(););if(h&&"'"===n)for(;"'"!==e.next(););z||e.eatWhile(/[\w\$_-]/);var w=e.eat(":");!e.eat(":")&&w&&e.eatWhile(/[\w\$_-]/),e.match(/^[ \t]*\(/,!1)&&(g=!0);var I=e.current();return z=r.propertyIsEnumerable(I)&&r[I],g&&!z&&(z={type:"function_call",style:"def"}),function(e){return x(e,"xmlconstructor")}(t)?(y(t),"variable"):("element"!=I&&"attribute"!=I&&"axis_specifier"!=z.type||d(t,{type:"xmlconstructor"}),z?z.style:"variable")}return a(e,t,o(n))}function s(e,t){for(var n,r=!1,a=!1,i=0;n=e.next();){if(")"==n&&r){if(!(i>0)){y(t);break}i--}else":"==n&&a&&i++;r=":"==n,a="("==n}return"comment"}function o(e,t){return function(n,r){var a;if(function(e){return x(e,"string")}(r)&&n.current()==e)return y(r),t&&(r.tokenize=t),"string";if(d(r,{type:"string",name:e,tokenize:o(e,t)}),n.match("{",!1)&&g(r))return r.tokenize=i,"string";for(;a=n.next();){if(a==e){y(r),t&&(r.tokenize=t);break}if(n.match("{",!1)&&g(r))return r.tokenize=i,"string"}return"string"}}function c(e,t){var n=/[\w\$_-]/;if(e.eat('"')){for(;'"'!==e.next(););e.eat(":")}else e.eatWhile(n),e.match(":=",!1)||e.eat(":");return e.eatWhile(n),t.tokenize=i,"variable"}function u(e,t){var n=e.next();return"/"==n&&e.eat(">")?(g(t)&&y(t),m(t)&&y(t),"tag"):">"==n?(g(t)&&y(t),"tag"):"="==n?null:'"'==n||"'"==n?a(e,t,o(n,u)):(g(t)||d(t,{type:"attribute",tokenize:u}),e.eat(/[a-zA-Z_:]/),e.eatWhile(/[-a-zA-Z0-9_:.]/),e.eatSpace(),(e.match(">",!1)||e.match("/",!1))&&(y(t),t.tokenize=i),"attribute")}function l(e,t){for(var n;n=e.next();)if("-"==n&&e.match("->",!0))return t.tokenize=i,"comment"}function f(e,t){for(var n;n=e.next();)if("]"==n&&e.match("]",!0))return t.tokenize=i,"comment"}function p(e,t){for(var n;n=e.next();)if("?"==n&&e.match(">",!0))return t.tokenize=i,"processingInstruction"}function m(e){return x(e,"tag")}function g(e){return x(e,"attribute")}function x(e,t){return e.stack.length&&e.stack[e.stack.length-1].type==t}function d(e,t){e.stack.push(t)}function y(e){e.stack.pop();var t=e.stack.length&&e.stack[e.stack.length-1].tokenize;e.tokenize=t||i}const h={name:"xquery",startState:function(){return{tokenize:i,cc:[],stack:[]}},token:function(e,t){return e.eatSpace()?null:t.tokenize(e,t)},languageData:{commentTokens:{block:{open:"(:",close:":)"}}}}}}]);