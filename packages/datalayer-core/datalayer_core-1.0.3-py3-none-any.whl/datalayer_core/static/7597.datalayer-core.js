"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[7597],{97597:(e,n,t)=>{function r(e){return new RegExp("^(("+e.join(")|(")+"))\\b")}t.r(n),t.d(n,{octave:()=>k});var a=new RegExp("^[\\+\\-\\*/&|\\^~<>!@'\\\\]"),i=new RegExp("^[\\(\\[\\{\\},:=;\\.]"),o=new RegExp("^((==)|(~=)|(<=)|(>=)|(<<)|(>>)|(\\.[\\+\\-\\*/\\^\\\\]))"),c=new RegExp("^((!=)|(\\+=)|(\\-=)|(\\*=)|(/=)|(&=)|(\\|=)|(\\^=))"),m=new RegExp("^((>>=)|(<<=))"),s=new RegExp("^[\\]\\)]"),u=new RegExp("^[_A-Za-z¡-￿][_A-Za-z0-9¡-￿]*"),l=r(["error","eval","function","abs","acos","atan","asin","cos","cosh","exp","log","prod","sum","log10","max","min","sign","sin","sinh","sqrt","tan","reshape","break","zeros","default","margin","round","ones","rand","syn","ceil","floor","size","clear","zeros","eye","mean","std","cov","det","eig","inv","norm","rank","trace","expm","logm","sqrtm","linspace","plot","title","xlabel","ylabel","legend","text","grid","meshgrid","mesh","num2str","fft","ifft","arrayfun","cellfun","input","fliplr","flipud","ismember"]),f=r(["return","case","switch","else","elseif","end","endif","endfunction","if","otherwise","do","for","while","try","catch","classdef","properties","events","methods","global","persistent","endfor","endwhile","printf","sprintf","disp","until","continue","pkg"]);function p(e,n){return e.sol()||"'"!==e.peek()?(n.tokenize=h,h(e,n)):(e.next(),n.tokenize=h,"operator")}function d(e,n){return e.match(/^.*%}/)?(n.tokenize=h,"comment"):(e.skipToEnd(),"comment")}function h(e,n){if(e.eatSpace())return null;if(e.match("%{"))return n.tokenize=d,e.skipToEnd(),"comment";if(e.match(/^[%#]/))return e.skipToEnd(),"comment";if(e.match(/^[0-9\.+-]/,!1)){if(e.match(/^[+-]?0x[0-9a-fA-F]+[ij]?/))return e.tokenize=h,"number";if(e.match(/^[+-]?\d*\.\d+([EeDd][+-]?\d+)?[ij]?/))return"number";if(e.match(/^[+-]?\d+([EeDd][+-]?\d+)?[ij]?/))return"number"}if(e.match(r(["nan","NaN","inf","Inf"])))return"number";var t=e.match(/^"(?:[^"]|"")*("|$)/)||e.match(/^'(?:[^']|'')*('|$)/);return t?t[1]?"string":"error":e.match(f)?"keyword":e.match(l)?"builtin":e.match(u)?"variable":e.match(a)||e.match(o)?"operator":e.match(i)||e.match(c)||e.match(m)?null:e.match(s)?(n.tokenize=p,null):(e.next(),"error")}const k={name:"octave",startState:function(){return{tokenize:h}},token:function(e,n){var t=n.tokenize(e,n);return"number"!==t&&"variable"!==t||(n.tokenize=p),t},languageData:{commentTokens:{line:"%"}}}}}]);