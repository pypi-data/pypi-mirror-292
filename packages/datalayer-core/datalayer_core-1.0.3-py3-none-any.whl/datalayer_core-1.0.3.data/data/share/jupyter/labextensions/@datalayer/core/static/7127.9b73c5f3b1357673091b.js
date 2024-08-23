"use strict";(self.webpackChunk_datalayer_core=self.webpackChunk_datalayer_core||[]).push([[7127],{85868:(n,e,t)=>{t.d(e,{Z:()=>a});var r=t(84983),o=t.n(r),i=t(79872),s=t.n(i)()(o());s.push([n.id,"/*-----------------------------------------------------------------------------\n| Copyright (c) Jupyter Development Team.\n| Distributed under the terms of the Modified BSD License.\n|----------------------------------------------------------------------------*/\n\n.jp-Terminal {\n  min-width: 240px;\n  min-height: 120px;\n}\n\n.jp-Terminal-body {\n  padding: 8px;\n}\n\n[data-term-theme='inherit'] .xterm .xterm-screen canvas {\n  border: 1px solid var(--jp-layout-color0);\n}\n\n[data-term-theme='light'] .xterm .xterm-screen canvas {\n  border: 1px solid #fff;\n}\n\n[data-term-theme='dark'] .xterm .xterm-screen canvas {\n  border: 1px solid #000;\n}\n",""]);const a=s},71794:(n,e,t)=>{t.d(e,{Z:()=>a});var r=t(84983),o=t.n(r),i=t(79872),s=t.n(i)()(o());s.push([n.id,'/**\n * Copyright (c) 2014 The xterm.js authors. All rights reserved.\n * Copyright (c) 2012-2013, Christopher Jeffrey (MIT License)\n * https://github.com/chjj/term.js\n * @license MIT\n *\n * Permission is hereby granted, free of charge, to any person obtaining a copy\n * of this software and associated documentation files (the "Software"), to deal\n * in the Software without restriction, including without limitation the rights\n * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n * copies of the Software, and to permit persons to whom the Software is\n * furnished to do so, subject to the following conditions:\n *\n * The above copyright notice and this permission notice shall be included in\n * all copies or substantial portions of the Software.\n *\n * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN\n * THE SOFTWARE.\n *\n * Originally forked from (with the author\'s permission):\n *   Fabrice Bellard\'s javascript vt100 for jslinux:\n *   http://bellard.org/jslinux/\n *   Copyright (c) 2011 Fabrice Bellard\n *   The original design remains. The terminal itself\n *   has been extended to include xterm CSI codes, among\n *   other features.\n */\n\n/**\n *  Default styles for xterm.js\n */\n\n.xterm {\n    cursor: text;\n    position: relative;\n    user-select: none;\n    -ms-user-select: none;\n    -webkit-user-select: none;\n}\n\n.xterm.focus,\n.xterm:focus {\n    outline: none;\n}\n\n.xterm .xterm-helpers {\n    position: absolute;\n    top: 0;\n    /**\n     * The z-index of the helpers must be higher than the canvases in order for\n     * IMEs to appear on top.\n     */\n    z-index: 5;\n}\n\n.xterm .xterm-helper-textarea {\n    padding: 0;\n    border: 0;\n    margin: 0;\n    /* Move textarea out of the screen to the far left, so that the cursor is not visible */\n    position: absolute;\n    opacity: 0;\n    left: -9999em;\n    top: 0;\n    width: 0;\n    height: 0;\n    z-index: -5;\n    /** Prevent wrapping so the IME appears against the textarea at the correct position */\n    white-space: nowrap;\n    overflow: hidden;\n    resize: none;\n}\n\n.xterm .composition-view {\n    /* TODO: Composition position got messed up somewhere */\n    background: #000;\n    color: #FFF;\n    display: none;\n    position: absolute;\n    white-space: nowrap;\n    z-index: 1;\n}\n\n.xterm .composition-view.active {\n    display: block;\n}\n\n.xterm .xterm-viewport {\n    /* On OS X this is required in order for the scroll bar to appear fully opaque */\n    background-color: #000;\n    overflow-y: scroll;\n    cursor: default;\n    position: absolute;\n    right: 0;\n    left: 0;\n    top: 0;\n    bottom: 0;\n}\n\n.xterm .xterm-screen {\n    position: relative;\n}\n\n.xterm .xterm-screen canvas {\n    position: absolute;\n    left: 0;\n    top: 0;\n}\n\n.xterm .xterm-scroll-area {\n    visibility: hidden;\n}\n\n.xterm-char-measure-element {\n    display: inline-block;\n    visibility: hidden;\n    position: absolute;\n    top: 0;\n    left: -9999em;\n    line-height: normal;\n}\n\n.xterm.enable-mouse-events {\n    /* When mouse events are enabled (eg. tmux), revert to the standard pointer cursor */\n    cursor: default;\n}\n\n.xterm.xterm-cursor-pointer,\n.xterm .xterm-cursor-pointer {\n    cursor: pointer;\n}\n\n.xterm.column-select.focus {\n    /* Column selection mode */\n    cursor: crosshair;\n}\n\n.xterm .xterm-accessibility,\n.xterm .xterm-message {\n    position: absolute;\n    left: 0;\n    top: 0;\n    bottom: 0;\n    z-index: 10;\n    color: transparent;\n}\n\n.xterm .live-region {\n    position: absolute;\n    left: -9999px;\n    width: 1px;\n    height: 1px;\n    overflow: hidden;\n}\n\n.xterm-dim {\n    opacity: 0.5;\n}\n\n.xterm-underline-1 { text-decoration: underline; }\n.xterm-underline-2 { text-decoration: double underline; }\n.xterm-underline-3 { text-decoration: wavy underline; }\n.xterm-underline-4 { text-decoration: dotted underline; }\n.xterm-underline-5 { text-decoration: dashed underline; }\n\n.xterm-strikethrough {\n    text-decoration: line-through;\n}\n\n.xterm-screen .xterm-decoration-container .xterm-decoration {\n\tz-index: 6;\n\tposition: absolute;\n}\n\n.xterm-decoration-overview-ruler {\n    z-index: 7;\n    position: absolute;\n    top: 0;\n    right: 0;\n    pointer-events: none;\n}\n\n.xterm-decoration-top {\n    z-index: 2;\n    position: relative;\n}\n',""]);const a=s},17127:(n,e,t)=>{t.r(e),t(45996),t(19965);var r=t(13989),o=t.n(r),i=t(90299),s=t.n(i),a=t(32433),l=t.n(a),d=t(1889),m=t.n(d),c=t(10342),h=t.n(c),p=t(99638),u=t.n(p),x=t(71794),f={};f.styleTagTransform=u(),f.setAttributes=m(),f.insert=l().bind(null,"head"),f.domAPI=s(),f.insertStyleElement=h(),o()(x.Z,f),x.Z&&x.Z.locals&&x.Z.locals;var T=t(85868),b={};b.styleTagTransform=u(),b.setAttributes=m(),b.insert=l().bind(null,"head"),b.domAPI=s(),b.insertStyleElement=h(),o()(T.Z,b),T.Z&&T.Z.locals&&T.Z.locals}}]);