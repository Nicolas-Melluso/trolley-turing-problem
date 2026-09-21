"use strict";
const $ = id => document.getElementById(id);
const canvas = $("scene"), ctx = canvas.getContext("2d");
const state = {main:5, branch:1, mode:"manual", criterion:"minimize", divert:false, phase:"ready", x:80, locked:false, decision:null, history:[], request:0};
let remote = false;
const seenRemoteRuns = new Set();
const help = {
  minimize:"Compara ambos recuentos. En empate, mantiene la vía principal.",
  nonintervention:"Siempre mantiene la vía. Esta regla no considera el número de personas.",
  protect_main:"Desvía si hay personas en la vía principal, incluso si hay más en el desvío."
};
const active = () => ["running", "paused", "loading"].includes(state.phase);
const routeName = () => state.divert ? "DESVÍO" : "VÍA PRINCIPAL";
const colors = {lime:"#c5ee85", blue:"#8ab8df", orange:"#e9b48a"};
let view = {scale:1, x:0, y:0}, last = performance.now();

function resize() {
  const rect = canvas.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
  canvas.width = Math.round(rect.width * dpr); canvas.height = Math.round(rect.height * dpr);
  const scale = Math.min(rect.width / 1000, rect.height / 460);
  view = {scale:scale*dpr, x:(canvas.width-1000*scale*dpr)/2, y:(canvas.height-460*scale*dpr)/2};
}
new ResizeObserver(resize).observe(canvas);

function point(x, branch=false) {
  const t = Math.max(0,Math.min(1,(x-430)/280));
  const y = 295 - (branch ? 148*t*t*(3-2*t) : 0);
  const slope = branch && x>430 && x<710 ? -148*6*t*(1-t)/280 : 0;
  return {x,y,angle:Math.atan(slope)};
}
function line(x1,y1,x2,y2,color,width=1) {
  ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();
}
function round(x,y,w,h,r,fill,stroke) {
  ctx.beginPath();ctx.roundRect(x,y,w,h,r);if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.stroke();}
}
function text(value,x,y,color="#97a5ae",size=12,font="Consolas, monospace") {
  ctx.fillStyle=color;ctx.font=`${size}px ${font}`;ctx.fillText(value,x,y);
}
function track(branch,selected) {
  const path = offset => {ctx.beginPath();for(let x=15;x<=975;x+=3){const p=point(x,branch);if(x===15)ctx.moveTo(x,p.y+offset);else ctx.lineTo(x,p.y+offset);}};
  path(0);ctx.lineWidth=40;ctx.strokeStyle="#0d171e";ctx.stroke();
  for(let x=20;x<975;x+=18){const p=point(x,branch);ctx.save();ctx.translate(x,p.y);ctx.rotate(p.angle);ctx.fillStyle="#43504f";ctx.fillRect(-3,-23,6,46);ctx.restore();}
  for(const offset of [-12,12]){path(offset);ctx.strokeStyle="#74807c";ctx.lineWidth=3;ctx.stroke();}
  if(selected){path(0);ctx.strokeStyle="#c5ee8540";ctx.lineWidth=5;ctx.stroke();}
}
function tree(x,y,r=17) {
  ctx.fillStyle="#0d171d66";ctx.beginPath();ctx.ellipse(x+7,y+10,r,r*.7,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#30483d";ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
  ctx.fillStyle="#385344";ctx.beginPath();ctx.arc(x-4,y-4,r*.7,0,Math.PI*2);ctx.fill();
  line(x,y+6,x,y-7,"#527057",2);
}
function people(count,branch) {
  const y=branch?147:295;
  const affected=state.phase==="finished" && state.divert===branch;
  for(let i=0;i<count;i++){
    const x=837+Math.floor(i/3)*22, py=y-22+(i%3)*21;
    ctx.save();ctx.globalAlpha=affected?.22:1;
    ctx.fillStyle="#0005";ctx.beginPath();ctx.ellipse(x+3,py+7,8,4,0,0,Math.PI*2);ctx.fill();
    round(x-5,py-1,10,13,3,branch?colors.orange:colors.blue);
    ctx.fillStyle="#e8d6bc";ctx.beginPath();ctx.arc(x,py-5,4.5,0,Math.PI*2);ctx.fill();
    ctx.restore();
  }
  round(760,y-81,196,30,5,"#111c23",branch?"#785e48":"#49647a");
  text(`${branch?"DESVÍO":"VÍA PRINCIPAL"} · ${count}`,773,y-61,branch?colors.orange:colors.blue,11);
}
function carriage(x,front) {
  const p=point(x,state.divert);ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.angle);
  round(-57,-15,65,38,7,"#0005");
  round(-60,-22,67,42,7,"#94b661","#d9f4b5");
  round(-51,-16,39,30,4,"#d9e4cb");
  round(-47,-12,31,22,3,"#aebfa1");
  for(const side of [-1,1])for(let i=0;i<3;i++)round(-52+i*15,side===1?16:-21,10,5,1,"#25433e");
  if(front){round(-5,-15,9,28,3,"#294b45");for(const y of [-14,12])round(5,y,4,4,1,"#f7f0ba");}
  else round(-5,-14,7,26,2,"#66834d");
  ctx.restore();
}
function draw() {
  ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.setTransform(view.scale,0,0,view.scale,view.x,view.y);
  // A small, entirely code-drawn railway landscape. No remote assets.
  ctx.strokeStyle="#ffffff04";ctx.lineWidth=1;
  for(let x=0;x<1000;x+=40)line(x,0,x,460,"#ffffff04");
  for(let y=0;y<460;y+=40)line(0,y,1000,y,"#ffffff04");
  round(30,34,235,110,9,"#203039");round(42,43,211,89,5,"#2b3d44");
  round(66,62,158,55,4,"#36474d");
  for(let i=0;i<7;i++)line(70+i*23,64,70+i*23,114,"#51626a",2);
  text("ESTACIÓN / ORIGEN",51,168,"#738992",10);
  for(const [x,y,r] of [[302,72,20],[349,83,14],[571,45,16],[626,62,21],[947,404,20],[900,398,15],[105,410,21],[151,390,16],[708,397,23]])tree(x,y,r);
  round(505,362,145,53,7,"#24363d");text("MUNDO HIPOTÉTICO",516,386,"#82958f",10);text("CONSECUENCIAS CIERTAS",516,403,"#657f7a",8);
  track(true,state.divert);track(false,!state.divert);
  // Highlight the selected route after drawing both tracks.
  ctx.beginPath();for(let x=20;x<965;x+=4){const p=point(x,state.divert);x===20?ctx.moveTo(x,p.y):ctx.lineTo(x,p.y);}ctx.strokeStyle="#c5ee8555";ctx.lineWidth=4;ctx.stroke();
  people(state.main,false);people(state.branch,true);
  const signalX=442,signalY=335;
  line(signalX,signalY,signalX,signalY+28,"#71857c",4);round(signalX-9,signalY-18,18,27,4,"#0e181e","#56665f");
  ctx.fillStyle=state.locked?colors.orange:colors.lime;ctx.beginPath();ctx.arc(signalX,signalY-5,4,0,Math.PI*2);ctx.fill();
  round(336,351,80,64,10,"#273936","#52694d");
  const leverX=state.divert?395:355;
  line(375,393,leverX,367,colors.lime,6);ctx.beginPath();ctx.arc(leverX,367,8,0,Math.PI*2);ctx.fillStyle=colors.lime;ctx.fill();
  text(state.locked?"BLOQUEADA":"PALANCA",342,434,state.locked?colors.orange:colors.lime,10);
  carriage(state.x-73,false);
  carriage(state.x,true);
  if(state.phase==="ready") {text("01",44,248,colors.lime,12);text("EL RECORRIDO EMPIEZA ACÁ",69,248,"#81938f",10);}
}

function refresh() {
  $("main-value").value=state.main;$("branch-value").value=state.branch;
  $("main-count").value=state.main;$("branch-count").value=state.branch;
  $("state-code").textContent=`personas_principal = ${state.main}\npersonas_desvio = ${state.branch}\npalanca = "${state.divert?"desviar":"mantener"}"`;
  $("keep-count").textContent=state.main;$("divert-count").textContent=state.branch;
  $("route-label").textContent=`RECORRIDO · ${routeName()}`;
  const labels={ready:"LISTO PARA DECIDIR",loading:"EVALUANDO EN PYTHON",running:state.locked?"DECISIÓN EJECUTADA":"EN MOVIMIENTO",paused:"EN PAUSA",finished:"RECORRIDO COMPLETADO"};
  $("phase").textContent=labels[state.phase];
  $("manual").setAttribute("aria-pressed",state.mode==="manual");$("automatic").setAttribute("aria-pressed",state.mode==="auto");
  $("manual-info").hidden=state.mode!=="manual";$("auto-settings").hidden=state.mode!=="auto";
  $("criterion-help").textContent=help[state.criterion];
  for(const el of document.querySelectorAll("#main-count,#branch-count,#criterion,#manual,#automatic,[data-preset]"))el.disabled=active()||remote;
  $("agent-info").hidden=!remote;
  $("mechanism-tag").textContent=remote?"DECISIÓN DE AGENTE · MCP":"REGLAS EXPLÍCITAS · SIN LLM";
  $("speed").disabled=remote;
  $("start").disabled=state.phase!=="ready"||remote;$("pause").disabled=!["running","paused"].includes(state.phase)||remote;
  $("pause").textContent=state.phase==="paused"?"Continuar":"Pausar";
  $("lever").disabled=state.mode!=="manual"||state.locked||["loading","finished"].includes(state.phase);
  $("outcome").hidden=state.phase!=="finished";
}
function showDecision(data) {
  state.decision=data;state.divert=data.action==="divert";
  $("rule-code").textContent=data.rule;$("reason-text").textContent=data.reason;refresh();
}
async function evaluate() {
  const request=++state.request;
  const response=await fetch("/api/decide",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({main:state.main,branch:state.branch,criterion:state.criterion})});
  const data=await response.json();if(!response.ok)throw new Error(data.error||"No se pudo evaluar la regla.");
  if(request!==state.request)return null;
  showDecision(data);return data;
}
function showError(error) {$("error").hidden=false;$("error").textContent=`No se pudo consultar Python. Verificá que app.py siga ejecutándose. ${error.message}`;}
async function preview() {
  $("error").hidden=true;
  if(state.mode==="auto"){try{await evaluate();}catch(error){showError(error);}}
  else {++state.request;state.decision=null;$("rule-code").textContent="accion = decision_humana";$("reason-text").textContent="La persona selecciona la vía. El programa ejecuta esa selección.";}
  refresh();
}
function reset() {if(remote){releaseAgent();return;}++state.request;state.phase="ready";state.x=80;state.locked=false;state.divert=false;state.decision=null;refresh();preview();}
function setMode(mode) {if(active())return;state.mode=mode;reset();}
function toggleLever() {if($("lever").disabled)return;state.divert=!state.divert;refresh();}
function pause() {if(remote)return;if(state.phase==="running")state.phase="paused";else if(state.phase==="paused")state.phase="running";refresh();}
async function start() {
  if(state.phase!=="ready"||remote)return;
  state.phase="loading";$("error").hidden=true;refresh();
  if(state.mode==="auto"){
    try{const result=await evaluate();if(!result||state.phase!=="loading")return;}
    catch(error){if(state.phase==="loading"){state.phase="ready";showError(error);refresh();}return;}
  }
  state.phase="running";refresh();
}
function finish() {
  state.phase="finished";
  const victims=state.divert?state.branch:state.main,safe=state.divert?state.main:state.branch;
  const criterion=state.mode==="manual"?"Decisión manual":state.decision.label;
  const record={timestamp:new Date().toISOString(),main:state.main,branch:state.branch,mode:state.mode,criterion,action:state.divert?"divert":"keep",victims,safe,reason:state.decision?.reason||"Selección manual de la persona."};
  state.history.push(record);
  $("outcome-title").textContent=`${victims} ${victims===1?"persona afectada":"personas afectadas"}`;
  $("outcome-text").textContent=`${safe} ${safe===1?"persona quedó":"personas quedaron"} fuera del recorrido. ${state.divert?"Se accionó la palanca.":"Se mantuvo la vía principal."}`;
  const item=document.createElement("li"),title=document.createElement("strong"),detail=document.createElement("span");
  title.textContent=`${String(state.history.length).padStart(2,"0")} / ${criterion}`;
  detail.textContent=`${state.main}:${state.branch} → ${state.divert?"Desviar":"Mantener"} · ${victims} ${victims===1?"afectada":"afectadas"} · ${safe} a salvo`;
  item.append(title,detail);$("history-list").prepend(item);$("empty-history").hidden=true;$("export").disabled=false;refresh();
}
$("main-count").addEventListener("input",event=>{state.main=Number(event.target.value);state.phase="ready";state.x=80;state.locked=false;preview();});
$("branch-count").addEventListener("input",event=>{state.branch=Number(event.target.value);state.phase="ready";state.x=80;state.locked=false;preview();});
document.querySelectorAll("[data-preset]").forEach(button=>button.addEventListener("click",()=>{[state.main,state.branch]=button.dataset.preset.split(",").map(Number);reset();}));
$("criterion").addEventListener("change",event=>{state.criterion=event.target.value;reset();});
$("manual").addEventListener("click",()=>setMode("manual"));$("automatic").addEventListener("click",()=>setMode("auto"));
$("start").addEventListener("click",start);$("pause").addEventListener("click",pause);$("reset").addEventListener("click",reset);$("again").addEventListener("click",reset);$("lever").addEventListener("click",toggleLever);
canvas.addEventListener("click",event=>{const rect=canvas.getBoundingClientRect(),dpr=window.devicePixelRatio||1;const x=((event.clientX-rect.left)*dpr-view.x)/view.scale,y=((event.clientY-rect.top)*dpr-view.y)/view.scale;if(x>=325&&x<=420&&y>=340&&y<=435)toggleLever();});
$("presentation").addEventListener("click",()=>{const on=document.body.classList.toggle("presentation");$("presentation").textContent=on?"Salir de presentación ↙":"Modo presentación ↗";resize();});
$("export").addEventListener("click",()=>{const blob=new Blob([JSON.stringify({app:"tranvia-lab",version:1,experiments:state.history},null,2)],{type:"application/json"});const url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download="tranvia-experimentos.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
document.addEventListener("keydown",event=>{if(["INPUT","SELECT","TEXTAREA","BUTTON"].includes(event.target.tagName)||event.ctrlKey||event.metaKey||event.altKey||event.repeat)return;if(event.key.toLowerCase()==="l")toggleLever();if(event.key.toLowerCase()==="r")reset();if(event.code==="Space"){event.preventDefault();if(state.phase==="ready")start();else pause();}});
async function sceneRequest(path, body) {
  const response=await fetch(path,body===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  const data=await response.json();if(!response.ok)throw new Error(data.error||"No se pudo conectar con el simulador.");return data;
}
function applyRemote(data) {
  if(!data.controlled){if(remote){remote=false;state.mode="manual";reset();}return;}
  if(!remote)++state.request;
  remote=true;state.mode="mcp";state.main=data.main;state.branch=data.branch;
  state.phase=data.phase;state.x=data.x;state.locked=data.locked;state.divert=data.action==="divert";
  state.decision={label:`Agente MCP · ${data.agent||"esperando"}`,reason:data.reason};
  $("rule-code").textContent=data.reason?`accion = "${data.action}"\norigen = "agente MCP"`:"esperando_decision_del_agente";
  $("reason-text").textContent=data.reason||"El agente debe consultar el escenario y elegir una acción.";
  $("agent-status").textContent=data.reason?`${data.agent}: ${data.reason}`:"Escenario preparado. Esperando una decisión del agente.";
  if(data.phase==="finished"&&!seenRemoteRuns.has(data.run_id)){seenRemoteRuns.add(data.run_id);finish();}
  refresh();
}
let syncBusy=false;
async function syncScene() {
  if(syncBusy)return;syncBusy=true;
  try{
    const data=await sceneRequest("/api/scene/sync",{main:state.main,branch:state.branch,phase:state.phase,action:state.divert?"divert":"keep",x:Math.min(814,state.x)});
    applyRemote(data);
    $("agent-status").dataset.connected="true";
  }catch(error){if(remote){$("agent-status").textContent="Conexión interrumpida. El estado se recuperará al reconectar.";state.phase="paused";refresh();}}
  finally{syncBusy=false;}
}
async function releaseAgent() {
  try{applyRemote(await sceneRequest("/api/scene/release",{}));}catch(error){showError(error);}
}
$("release-agent").addEventListener("click",releaseAgent);
setInterval(syncScene,300);
function frame(now){const dt=Math.min((now-last)/1000,.05);last=now;if(state.phase==="running"){state.x+=dt*76*(remote?1:Number($("speed").value));if(!state.locked&&state.x>=425){state.locked=true;refresh();}if(state.x>=814){state.x=814;if(!remote)finish();}}draw();requestAnimationFrame(frame);}
resize();refresh();requestAnimationFrame(frame);
