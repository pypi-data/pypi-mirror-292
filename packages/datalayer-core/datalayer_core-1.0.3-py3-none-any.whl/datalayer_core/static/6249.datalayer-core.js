"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[6249],{26249:(e,n,t)=>{t.r(n),t.d(n,{apl:()=>o});var l={"+":["conjugate","add"],"−":["negate","subtract"],"×":["signOf","multiply"],"÷":["reciprocal","divide"],"⌈":["ceiling","greaterOf"],"⌊":["floor","lesserOf"],"∣":["absolute","residue"],"⍳":["indexGenerate","indexOf"],"?":["roll","deal"],"⋆":["exponentiate","toThePowerOf"],"⍟":["naturalLog","logToTheBase"],"○":["piTimes","circularFuncs"],"!":["factorial","binomial"],"⌹":["matrixInverse","matrixDivide"],"<":[null,"lessThan"],"≤":[null,"lessThanOrEqual"],"=":[null,"equals"],">":[null,"greaterThan"],"≥":[null,"greaterThanOrEqual"],"≠":[null,"notEqual"],"≡":["depth","match"],"≢":[null,"notMatch"],"∈":["enlist","membership"],"⍷":[null,"find"],"∪":["unique","union"],"∩":[null,"intersection"],"∼":["not","without"],"∨":[null,"or"],"∧":[null,"and"],"⍱":[null,"nor"],"⍲":[null,"nand"],"⍴":["shapeOf","reshape"],",":["ravel","catenate"],"⍪":[null,"firstAxisCatenate"],"⌽":["reverse","rotate"],"⊖":["axis1Reverse","axis1Rotate"],"⍉":["transpose",null],"↑":["first","take"],"↓":[null,"drop"],"⊂":["enclose","partitionWithAxis"],"⊃":["diclose","pick"],"⌷":[null,"index"],"⍋":["gradeUp",null],"⍒":["gradeDown",null],"⊤":["encode",null],"⊥":["decode",null],"⍕":["format","formatByExample"],"⍎":["execute",null],"⊣":["stop","left"],"⊢":["pass","right"]},a=/[\.\/⌿⍀¨⍣]/,r=/⍬/,u=/[\+−×÷⌈⌊∣⍳\?⋆⍟○!⌹<≤=>≥≠≡≢∈⍷∪∩∼∨∧⍱⍲⍴,⍪⌽⊖⍉↑↓⊂⊃⌷⍋⍒⊤⊥⍕⍎⊣⊢]/,i=/←/,s=/[⍝#].*$/;const o={name:"apl",startState:function(){return{prev:!1,func:!1,op:!1,string:!1,escape:!1}},token:function(e,n){var t,o,c;return e.eatSpace()?null:'"'===(t=e.next())||"'"===t?(e.eatWhile((o=t,c=!1,function(e){return c=e,e!==o||"\\"===c})),e.next(),n.prev=!0,"string"):/[\[{\(]/.test(t)?(n.prev=!1,null):/[\]}\)]/.test(t)?(n.prev=!0,null):r.test(t)?(n.prev=!1,"atom"):/[¯\d]/.test(t)?(n.func?(n.func=!1,n.prev=!1):n.prev=!0,e.eatWhile(/[\w\.]/),"number"):a.test(t)||i.test(t)?"operator":u.test(t)?(n.func=!0,n.prev=!1,l[t]?"variableName.function.standard":"variableName.function"):s.test(t)?(e.skipToEnd(),"comment"):"∘"===t&&"."===e.peek()?(e.next(),"variableName.function"):(e.eatWhile(/[\w\$_]/),n.prev=!0,"keyword")}}}}]);