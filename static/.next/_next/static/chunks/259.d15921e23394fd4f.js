"use strict";(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[259],{2259:function(e,l,n){n.r(l);var a=n(7437),o=n(2265),r=n(7818);let t=(0,r.default)(()=>n.e(173).then(n.bind(n,9927)),{loadableGenerated:{webpack:()=>[9927]},ssr:!1}),d=(0,r.default)(()=>Promise.all([n.e(401),n.e(170),n.e(101)]).then(n.bind(n,2101)),{loadableGenerated:{webpack:()=>[2101]},ssr:!1});l.default=e=>{let{currentPlan:l,stepCodes:n,onPlanUpdate:r,onCodeUpdate:i}=e,[s,c]=(0,o.useState)("plan"),p=(e,l)=>{i(e,l)},u={padding:"10px 15px",cursor:"pointer",backgroundColor:"#2d3748",color:"#a0aec0",border:"none",borderRadius:"5px 5px 0 0",marginRight:"5px"},h={...u,backgroundColor:"#4299e1",color:"white"};return(0,a.jsxs)("div",{style:{height:"100%",display:"flex",flexDirection:"column",backgroundColor:"#2d3748"},children:[(0,a.jsxs)("div",{style:{display:"flex",borderBottom:"1px solid #4a5568",padding:"10px"},children:[(0,a.jsx)("button",{style:"plan"===s?h:u,onClick:()=>c("plan"),children:"Plan"}),Object.keys(n).map((e,l)=>(0,a.jsxs)("button",{style:s===e?h:u,onClick:()=>c(e),children:["Step ",l+1]},e))]}),(0,a.jsx)("div",{style:{height:"calc(100% - 50px)",overflowY:"auto",padding:"20px",backgroundColor:"#1a202c",color:"white"},children:"plan"===s?(0,a.jsx)(t,{initialJson:l,onJsonChange:e=>{r(e)}}):(0,a.jsx)(d,{value:n[s],onChange:e=>p(s,e),language:"python"})})]})}}}]);