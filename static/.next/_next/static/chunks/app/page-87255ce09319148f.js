(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[931],{4790:function(e,t,a){Promise.resolve().then(a.bind(a,8212))},8212:function(e,t,a){"use strict";a.r(t);var n=a(7437),s=a(2265),i=a(7818),c=a(2800);a(1918);let r=(0,i.default)(()=>a.e(75).then(a.bind(a,75)),{loadableGenerated:{webpack:()=>[75]},ssr:!1}),o=(0,i.default)(()=>a.e(259).then(a.bind(a,2259)),{loadableGenerated:{webpack:()=>[2259]},ssr:!1});t.default=()=>{let[e,t]=(0,s.useState)(null),[a,i]=(0,s.useState)(!0);(0,s.useEffect)(()=>{(async()=>{try{let e=await (0,c.Gg)();t(e)}catch(e){console.error("Failed to fetch session data:",e)}finally{i(!1)}})()},[]);let l=async a=>{if(e)try{await (0,c.F9)(a),t(e=>({...e,current_plan:a}))}catch(e){console.error("Failed to update plan:",e)}},d=async(a,n)=>{if(e)try{let s={...e.step_codes,[a]:n};await (0,c.IX)(s),t(e=>({...e,step_codes:s}))}catch(e){console.error("Failed to update code:",e)}};return a?(0,n.jsx)("div",{style:{display:"flex",justifyContent:"center",alignItems:"center",height:"100vh",backgroundColor:"#1a202c",color:"white"},children:"Loading..."}):e?(0,n.jsxs)("div",{style:{display:"flex",height:"100vh",backgroundColor:"#1a202c",color:"white"},children:[(0,n.jsx)("div",{style:{width:"30%",borderRight:"1px solid #4a5568"},children:(0,n.jsx)(r,{initialMessages:e.chat_history})}),(0,n.jsx)("div",{style:{width:"70%"},children:(0,n.jsx)(o,{currentPlan:e.current_plan,stepCodes:e.step_codes,onPlanUpdate:l,onCodeUpdate:d})})]}):(0,n.jsx)("div",{style:{display:"flex",justifyContent:"center",alignItems:"center",height:"100vh",backgroundColor:"#1a202c",color:"white"},children:"No session data available."})}},2800:function(e,t,a){"use strict";a.d(t,{F9:function(){return h},Gg:function(){return u},IX:function(){return p},MQ:function(){return d}});var n=a(8472),s=a(2649);let i="/api/sessions",c="session_id",r=e=>{s.Z.set(c,e,{expires:7})},o=()=>s.Z.get(c)||"",l=async()=>{let e=await n.Z.post(i);return r(e.data.session_id),e.data},d=async()=>{let e=o();return e||r(e=(await l()).session_id),e},u=async()=>{let e=await d();return(await n.Z.get("".concat(i,"/").concat(e))).data},h=async e=>{let t=await d();return(await n.Z.put("".concat(i,"/").concat(t,"/current_plan"),e)).data},p=async e=>{let t=await d();return(await n.Z.put("".concat(i,"/").concat(t,"/step_codes"),e)).data}},1918:function(){}},function(e){e.O(0,[725,135,971,23,744],function(){return e(e.s=4790)}),_N_E=e.O()}]);