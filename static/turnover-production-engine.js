(()=>{
'use strict';
const by=id=>document.getElementById(id), num=id=>Math.max(0,parseFloat(by(id)?.value)||0);
const LEVELS=['refresh','turnover','restoration'], LABEL={refresh:'Refresh',turnover:'Vacant Turnover',restoration:'Restoration'};
const AREAS=[
{id:'bed',name:'Bedrooms',source:'beds',times:[12,25,45]},
{id:'bath',name:'Full bathrooms',source:'baths',times:[20,55,110]},
{id:'half',name:'Half bathrooms',source:'halfBaths',times:[12,25,50]},
{id:'kitchen',name:'Kitchens',times:[35,105,210]},
{id:'living',name:'Living areas',times:[15,35,65]},
{id:'hall',name:'Hallways / stairs',times:[10,25,45]},
{id:'floor',name:'Floor cleaning (per 100 sqft)',times:[1.2,2.2,3.5]}
];
const DEFAULT={times:Object.fromEntries(AREAS.map(a=>[a.id,a.times])),kitchenSize:{small:.7,standard:1,large:1.45},oven:{light:{minutes:25,price:40},normal:{minutes:45,price:60},heavy:{minutes:90,price:90}},setup:30};
let config=readConfig(),groups={},ovenGroups=[{qty:0,condition:'normal'}],windowGroups=[{qty:0,service:'interior',access:'standard',hardWater:false}];
let previousPackage=by('service').value, updating=false;
function readConfig(){try{const v=JSON.parse(localStorage.getItem('cwsProductionTimesV1'));return {...structuredDefault(),...v,times:{...structuredDefault().times,...(v?.times||{})},oven:{...structuredDefault().oven,...(v?.oven||{})}}}catch(e){return structuredDefault()}}
function structuredDefault(){return JSON.parse(JSON.stringify(DEFAULT))}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function initialGroups(){AREAS.forEach(a=>{if(a.id==='floor')return;groups[a.id]=[{qty:a.source?num(a.source):1,level:previousPackage,size:'standard'}]});groups.living[0].qty=1;groups.hall[0].qty=1}
initialGroups();
const style=document.createElement('style');style.textContent='.cws-production{margin-top:14px}.cws-production .group{padding:12px;border:1px solid #d8e4ef;border-radius:10px;margin:9px 0;background:white}.cws-production .group-grid{display:grid;grid-template-columns:90px 1fr 1fr auto;gap:8px;align-items:end}.cws-production label{display:block;font-size:12px;margin-bottom:4px}.cws-production input,.cws-production select{width:100%;padding:9px;border:1px solid #cbd5e1;border-radius:7px}.cws-production button{cursor:pointer}.cws-production .muted{color:#64778c;font-size:12px}.cws-production .group-head{display:flex;justify-content:space-between;align-items:center;margin:12px 0 4px}.cws-production .group-head button{padding:6px 9px}.cws-production .group-grid .remove{padding:8px}.cws-production .settings-grid{display:grid;grid-template-columns:1fr repeat(3,90px);gap:8px;align-items:center;margin:8px 0}@media(max-width:620px){.cws-production .group-grid{grid-template-columns:70px 1fr;}.cws-production .settings-grid{grid-template-columns:1fr repeat(3,60px)}}';document.head.appendChild(style);
const section=document.createElement('section');section.className='card cws-production';section.innerHTML='<div class="head"><span class="chip">Cleaning Areas</span><h2>Customize room cleaning levels</h2></div><div class="body"><div class="notice">Every room starts at your selected package level. Add groups to clean different rooms at different levels. Changing the package resets room levels to that package.</div><div id="cwsRoomGroups"></div><div id="cwsOvenGroups"></div><div id="cwsWindowGroups"></div></div>';
const serviceCard=by('service').closest('section.card');serviceCard.after(section);
const oldOven=by('oven').closest('.field');oldOven.style.display='none';by('oven').value='0';
const oldWindow=by('windows').closest('.field');oldWindow.style.display='none';by('windows').value='0';
const oldHard=by('hardWindows')?.closest('.field');if(oldHard)oldHard.style.display='none';
const oldWater=by('hardWaterWindows')?.closest('.field');if(oldWater)oldWater.style.display='none';
const oldWindowService=by('windowService')?.closest('.field');if(oldWindowService)oldWindowService.style.display='none';
const settingsBlock=document.createElement('section');settingsBlock.className='cws-production';settingsBlock.innerHTML='<h2>Production Time Settings</h2><p class="muted">Worker-minutes per room and package. These replace the old square-footage anchor estimates.</p><div id="cwsTimeSettings"></div><h3>Kitchen size multipliers</h3><div id="cwsKitchenSettings"></div><h3>Oven time and price</h3><div id="cwsOvenSettings"></div><label>Setup / cleanup worker-minutes <input type="number" min="0" id="cwsSetup" style="max-width:110px"></label><div class="actions" style="margin-top:12px"><button type="button" class="btn secondary" id="cwsResetTimes">Restore Production Defaults</button></div><p class="muted">Use the existing Save Settings button to save production times too. Values are saved in this browser.</p>';
by('saveSettings').closest('.actions').before(settingsBlock);
function optLevel(level){return LEVELS.map(x=>'<option value="'+x+'" '+(x===level?'selected':'')+'>'+LABEL[x]+'</option>').join('')}
function drawGroups(){const host=by('cwsRoomGroups');host.innerHTML=AREAS.filter(a=>a.id!=='floor').map(a=>'<div class="group-head"><strong>'+a.name+'</strong><button type="button" class="btn secondary" data-add="'+a.id+'">+ Add Group</button></div>'+groups[a.id].map((g,i)=>'<div class="group"><div class="group-grid"><label>Amount<input type="number" min="0" data-area="'+a.id+'" data-index="'+i+'" data-key="qty" value="'+g.qty+'"></label><label>Cleaning level<select data-area="'+a.id+'" data-index="'+i+'" data-key="level">'+optLevel(g.level)+'</select></label>'+(a.id==='kitchen'?'<label>Kitchen size<select data-area="'+a.id+'" data-index="'+i+'" data-key="size">'+['small','standard','large'].map(x=>'<option '+(g.size===x?'selected':'')+'>'+x+'</option>').join('')+'</select></label>':'<span></span>')+'<button type="button" class="btn secondary remove" data-remove="'+a.id+'" data-index="'+i+'" '+(groups[a.id].length===1?'disabled':'')+'>×</button></div><div class="muted" data-group-time="'+a.id+'-'+i+'"></div></div>').join('')).join('');
host.querySelectorAll('[data-add]').forEach(b=>b.onclick=()=>{groups[b.dataset.add].push({qty:1,level:by('service').value,size:'standard'});drawGroups();calculate()});
host.querySelectorAll('[data-remove]').forEach(b=>b.onclick=()=>{groups[b.dataset.remove].splice(+b.dataset.index,1);drawGroups();calculate()});
host.querySelectorAll('[data-area]').forEach(el=>{el.oninput=()=>{const g=groups[el.dataset.area][+el.dataset.index];g[el.dataset.key]=el.dataset.key==='qty'?Math.max(0,+el.value||0):el.value;syncCounts();calculate()};el.onchange=el.oninput});
drawOvens();drawWindows();calculate()}
function drawOvens(){by('cwsOvenGroups').innerHTML='<div class="group-head"><strong>Ovens (separate add-on)</strong><button type="button" class="btn secondary" id="cwsAddOven">+ Add Oven Group</button></div>'+ovenGroups.map((g,i)=>'<div class="group group-grid"><label>Amount<input type="number" min="0" data-oven="'+i+'" data-key="qty" value="'+g.qty+'"></label><label>Condition<select data-oven="'+i+'" data-key="condition">'+['light','normal','heavy'].map(x=>'<option '+(g.condition===x?'selected':'')+'>'+x+'</option>').join('')+'</select></label><span></span><button type="button" class="btn secondary" data-remove-oven="'+i+'" '+(ovenGroups.length===1?'disabled':'')+'>×</button></div>').join('');
by('cwsAddOven').onclick=()=>{ovenGroups.push({qty:1,condition:'normal'});drawOvens();calculate()};
by('cwsOvenGroups').querySelectorAll('[data-oven]').forEach(el=>el.oninput=el.onchange=()=>{ovenGroups[+el.dataset.oven][el.dataset.key]=el.dataset.key==='qty'?Math.max(0,+el.value||0):el.value;calculate()});
by('cwsOvenGroups').querySelectorAll('[data-remove-oven]').forEach(el=>el.onclick=()=>{ovenGroups.splice(+el.dataset.removeOven,1);drawOvens();calculate()})}
function drawWindows(){by('cwsWindowGroups').innerHTML='<div class="group-head"><strong>Windows (separate add-on)</strong><button type="button" class="btn secondary" id="cwsAddWindow">+ Add Window Group</button></div>'+windowGroups.map((g,i)=>'<div class="group"><div class="group-grid"><label>Amount<input type="number" min="0" data-window="'+i+'" data-key="qty" value="'+g.qty+'"></label><label>Service<select data-window="'+i+'" data-key="service">'+[['interior','Interior only'],['exterior','Exterior only'],['complete','Both sides']].map(([v,t])=>'<option value="'+v+'" '+(g.service===v?'selected':'')+'>'+t+'</option>').join('')+'</select></label><label>Access<select data-window="'+i+'" data-key="access">'+['standard','high'].map(x=>'<option '+(g.access===x?'selected':'')+'>'+x+'</option>').join('')+'</select></label><button type="button" class="btn secondary" data-remove-window="'+i+'" '+(windowGroups.length===1?'disabled':'')+'>×</button></div><label class="muted"><input type="checkbox" style="width:auto" data-window="'+i+'" data-key="hardWater" '+(g.hardWater?'checked':'')+'> Hard-water removal</label></div>').join('');
by('cwsAddWindow').onclick=()=>{windowGroups.push({qty:1,service:'interior',access:'standard',hardWater:false});drawWindows();calculate()};
by('cwsWindowGroups').querySelectorAll('[data-window]').forEach(el=>el.oninput=el.onchange=()=>{windowGroups[+el.dataset.window][el.dataset.key]=el.type==='checkbox'?el.checked:el.dataset.key==='qty'?Math.max(0,+el.value||0):el.value;calculate()});
by('cwsWindowGroups').querySelectorAll('[data-remove-window]').forEach(el=>el.onclick=()=>{windowGroups.splice(+el.dataset.removeWindow,1);drawWindows();calculate()})}
function syncCounts(){AREAS.filter(a=>a.source).forEach(a=>{const el=by(a.source);if(el)el.value=groups[a.id].reduce((s,g)=>s+g.qty,0)})}
function drawSettings(){by('cwsTimeSettings').innerHTML='<div class="settings-grid"><strong>Area</strong><strong>Refresh</strong><strong>Turnover</strong><strong>Restoration</strong></div>'+AREAS.map(a=>'<div class="settings-grid"><span>'+a.name+'</span>'+LEVELS.map((l,i)=>'<input aria-label="'+a.name+' '+l+'" type="number" min="0" step="1" data-time="'+a.id+'" data-i="'+i+'" value="'+config.times[a.id][i]+'">').join('')+'</div>').join('');
by('cwsKitchenSettings').innerHTML=['small','standard','large'].map(x=>'<label>'+x+' <input type="number" min=".1" step=".05" data-kitchen-size="'+x+'" value="'+config.kitchenSize[x]+'"></label>').join(' ');
by('cwsOvenSettings').innerHTML=['light','normal','heavy'].map(x=>'<div class="settings-grid"><strong>'+x+'</strong><label>Minutes<input type="number" min="0" data-oven-setting="'+x+'" data-key="minutes" value="'+config.oven[x].minutes+'"></label><label>Price $<input type="number" min="0" data-oven-setting="'+x+'" data-key="price" value="'+config.oven[x].price+'"></label></div>').join('');
by('cwsSetup').value=config.setup;
settingsBlock.querySelectorAll('[data-time]').forEach(el=>el.oninput=()=>{config.times[el.dataset.time][+el.dataset.i]=Math.max(0,+el.value||0);calculate()});
settingsBlock.querySelectorAll('[data-kitchen-size]').forEach(el=>el.oninput=()=>{config.kitchenSize[el.dataset.kitchenSize]=Math.max(.1,+el.value||.1);calculate()});
settingsBlock.querySelectorAll('[data-oven-setting]').forEach(el=>el.oninput=()=>{config.oven[el.dataset.ovenSetting][el.dataset.key]=Math.max(0,+el.value||0);calculate()});
by('cwsSetup').oninput=()=>{config.setup=Math.max(0,+by('cwsSetup').value||0);calculate()}}
drawSettings();by('cwsResetTimes').onclick=()=>{if(confirm('Restore default production times? Save Settings to keep them.')){config=structuredDefault();drawSettings();calculate()}};
by('saveSettings').addEventListener('click',()=>localStorage.setItem('cwsProductionTimesV1',JSON.stringify(config)));
by('restoreSettings').addEventListener('click',()=>{config=structuredDefault();drawSettings();calculate()});
by('service').addEventListener('change',()=>{previousPackage=by('service').value;Object.values(groups).forEach(arr=>arr.forEach(g=>g.level=previousPackage));drawGroups()});
AREAS.filter(a=>a.source).forEach(a=>by(a.source).addEventListener('change',()=>{const diff=num(a.source)-groups[a.id].reduce((s,g)=>s+g.qty,0);if(diff)groups[a.id][0].qty=Math.max(0,groups[a.id][0].qty+diff);drawGroups()}));
function windowDetails(){let minutes=0,price=0;windowGroups.forEach(g=>{const high=g.access==='high',both=g.service==='complete',m=high?(both?14:10):(both?8:5),p=high?(both?20:15):(both?15:10);minutes+=g.qty*(m+(g.hardWater?10:0));price+=g.qty*(p+(g.hardWater?15:0))});return{minutes,price}}
function areaDetails(){let minutes=0,lines=[];AREAS.filter(a=>a.id!=='floor').forEach(a=>groups[a.id].forEach(g=>{if(!g.qty)return;const m=g.qty*config.times[a.id][LEVELS.indexOf(g.level)]*(a.id==='kitchen'?config.kitchenSize[g.size]:1);minutes+=m;lines.push(g.qty+' × '+a.name+(a.id==='kitchen'?' ('+g.size+')':'')+' — '+LABEL[g.level]);}));const floor=num('sqft')/100*config.times.floor[LEVELS.indexOf(by('service').value)];minutes+=floor;lines.push('Floors — '+by('service').selectedOptions[0].text+' ('+num('sqft')+' sqft)');return{minutes,lines}}
let model={};
function calculate(){if(updating)return;updating=true;try{
const area=areaDetails(),windows=windowDetails(),ovens=ovenGroups.reduce((s,g)=>({minutes:s.minutes+g.qty*config.oven[g.condition].minutes,price:s.price+g.qty*config.oven[g.condition].price}),{minutes:0,price:0});
const cond=settings[by('condition').value+'Mult']||1,extra=settings.pricingMode==='advanced'?num('extraMinutes'):0;
const routine=area.minutes*cond+config.setup+extra;
const otherMinutes=num('fridge')*.35*60+num('blinds')*.12*60+num('garage')*.75*60+num('trash')*.5*60+num('carpetSqft')*.06+num('pressureSqft')*.08;
const otherPrice=num('fridge')*50+num('blinds')*10+num('garage')*75+num('trash')*50+num('carpetSqft')*.37+num('pressureSqft')*.4;
const labor=(routine+ovens.minutes+windows.minutes+otherMinutes)/60,addonPrice=ovens.price+windows.price+otherPrice;
const manual=settings.pricingMode==='advanced'?(parseFloat(by('manualAdjust').value)||0):0;
const quote=Math.round((Math.max(settings.minJob,routine/60*settings.hourlyRate)+ovens.price+windows.price+otherPrice+otherMinutes/60*settings.hourlyRate+manual)/5)*5;
const crew=Math.min(8,Math.max(1,Math.ceil(labor/Math.max(num('targetShift'),.5))));
const duration=labor/crew;const cost=labor*settings.cleanerWage*(1+settings.burden/100)+settings.supplies;const profit=quote-cost,margin=quote?100*profit/quote:0;
model={labor,quote,crew,duration,addons:addonPrice,cost,profit,margin,lines:area.lines,ovens,windows,ovenGroups:ovenGroups.filter(g=>g.qty).map(g=>({...g})),windowGroups:windowGroups.filter(g=>g.qty).map(g=>({...g}))};
last={labor,quote,crew,duration,addons:addonPrice,cost,profit,margin};
by('summaryTitle').textContent=by('service').selectedOptions[0].text;by('quote').textContent=money(quote);by('labor').textContent=labor.toFixed(2)+' hr';by('crew').textContent=crew;by('duration').textContent=duration.toFixed(2)+' hr';by('addons').textContent=money(addonPrice);
by('profitBox').innerHTML='Estimated direct cost: <b>'+money(cost)+'</b><br>Estimated gross profit: <b>'+money(profit)+'</b> ('+margin.toFixed(1)+'%)';
by('scopeText').textContent=scope[by('service').value]+' Customized room levels: '+area.lines.join('; ');
by('serviceDescription').textContent=scope[by('service').value];
groups && AREAS.filter(a=>a.id!=='floor').forEach(a=>groups[a.id].forEach((g,i)=>{const el=document.querySelector('[data-group-time="'+a.id+'-'+i+'"]');if(el)el.textContent=(g.qty*config.times[a.id][LEVELS.indexOf(g.level)]*(a.id==='kitchen'?config.kitchenSize[g.size]:1)).toFixed(0)+' worker-minutes'}));
renderUnits();
}finally{updating=false}}
calc=calculate;
function documentDetails(){return model.lines.concat(model.ovenGroups.map(g=>g.qty+' × '+g.condition+' oven cleaning'),model.windowGroups.map(g=>g.qty+' × '+g.service+' windows ('+g.access+(g.hardWater?', hard-water':'')+')'))}
function updateDocuments(){const details=documentDetails();const scopeText=scope[by('service').value]+'\nCustomized area instructions:\n'+details.join('\n');if(by('wScope'))by('wScope').textContent=scopeText;if(by('pScope'))by('pScope').textContent=scopeText;if(by('wLabor'))by('wLabor').textContent='Estimated labor: '+model.labor.toFixed(2)+' worker-hours';if(by('wCrew'))by('wCrew').textContent='Recommended crew: '+model.crew;if(by('pPrice'))by('pPrice').textContent=money(model.quote);if(by('pAddons'))by('pAddons').textContent=documentDetails().filter(x=>/oven|windows/.test(x)).join('; ')||'No specialty window or oven services.'}
by('proposalBtn').addEventListener('click',()=>setTimeout(updateDocuments,30));
by('workOrderBtn').addEventListener('click',()=>setTimeout(updateDocuments,30));
document.addEventListener('input',e=>{if(e.target.closest('.cws-production'))return;setTimeout(calculate,5)});
document.addEventListener('change',e=>{if(e.target.closest('.cws-production'))return;setTimeout(calculate,5)});
drawGroups();
})();