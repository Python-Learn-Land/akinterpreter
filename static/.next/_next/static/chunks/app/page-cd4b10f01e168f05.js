(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[931],{4790:function(e,s,t){Promise.resolve().then(t.bind(t,8212))},8212:function(e,s,t){"use strict";t.r(s);var n=t(7437),a=t(2265),o=t(7818),i=t(2800),l=t(1505);let r=(0,o.default)(()=>Promise.all([t.e(370),t.e(197)]).then(t.bind(t,3197)),{loadableGenerated:{webpack:()=>[3197]},ssr:!1}),d=(0,o.default)(()=>Promise.all([t.e(690),t.e(401),t.e(203),t.e(84)]).then(t.bind(t,8084)),{loadableGenerated:{webpack:()=>[8084]},ssr:!1}),c=(0,o.default)(()=>t.e(861).then(t.bind(t,861)),{loadableGenerated:{webpack:()=>[861]},ssr:!1});s.default=()=>{let[e,s]=(0,a.useState)(null),[t,o]=(0,a.useState)({}),[u,h]=(0,a.useState)({}),[f,p]=(0,a.useState)([]);(0,a.useEffect)(()=>{(async()=>{let e=await (0,i.Gg)();console.log("Session data:",e),s(e),p(e.chat_history),o(e.current_plan),h(e.step_codes)})()},[]);let _=(0,a.useCallback)(e=>{console.log("SSE Message:",e),"plan"===e.type?o(e.plan):"code"===e.type&&h(e.step_codes)},[]);return e?(0,n.jsx)("div",{style:{height:"100vh",overflow:"hidden",backgroundColor:"#282a36",color:"#f8f8f2"},children:(0,n.jsxs)(l.eh,{direction:"horizontal",children:[(0,n.jsx)(l.s_,{style:{height:"100%",overflow:"hidden"},children:(0,n.jsxs)("div",{style:{height:"100%",overflowY:"auto"},children:[(0,n.jsx)(r,{chatHistory:f}),(0,n.jsx)(c,{sessionId:e.session_id,onMessage:_})]})}),(0,n.jsx)(l.OT,{style:{backgroundColor:"#44475a",width:"5px",cursor:"col-resize"}}),(0,n.jsx)(l.s_,{style:{height:"100%",overflow:"hidden"},children:(0,n.jsx)(d,{currentPlan:t,stepCodes:u})})]})}):(0,n.jsx)("div",{children:"Loading..."})}},2800:function(e,s,t){"use strict";t.d(s,{Gg:function(){return u},MQ:function(){return c}});var n=t(8472),a=t(2649);let o="/api/sessions",i="session_id",l=e=>{a.Z.set(i,e,{expires:7})},r=()=>a.Z.get(i)||"",d=async()=>{let e=await n.Z.post(o);return l(e.data.session_id),e.data},c=async()=>{let e=r();return e||l(e=(await d()).session_id),e},u=async()=>{let e=await c();return(await n.Z.get("".concat(o,"/").concat(e))).data}}},function(e){e.O(0,[642,971,23,744],function(){return e(e.s=4790)}),_N_E=e.O()}]);