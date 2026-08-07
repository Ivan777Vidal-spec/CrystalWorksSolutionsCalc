(()=>{
  const $=id=>document.getElementById(id);
  const money=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(Number.isFinite(n)?n:0);
  const parseMoney=s=>Number(String(s||'').replace(/[^0-9.-]/g,''))||0;
  const text=id=>$(id)?.value||'';
  const num=id=>parseFloat($(id)?.value)||0;
  const yes=id=>num(id)>0;

  const style=document.createElement('style');
  style.textContent=`
    .cws-breakdown{display:grid;gap:7px;margin-top:8px}.cws-price-row{display:flex;justify-content:space-between;gap:12px;font-size:13px;padding:6px 0;border-bottom:1px solid var(--line,#d8e4ef)}.cws-price-row:last-child{border-bottom:0}.cws-price-total{font-size:16px;font-weight:900;color:var(--navy,#062b4d);padding-top:8px;border-top:2px solid var(--navy,#062b4d)}
    .cws-summary-sections{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px}.cws-summary-section{border:1px solid var(--line,#d8e4ef);border-radius:14px;padding:14px}.cws-summary-section h3{margin:0 0 9px;color:var(--navy,#062b4d)}.cws-check{margin:5px 0;font-size:13px}.cws-check:before{content:'✓';color:#1f6fb2;font-weight:900;margin-right:8px}.cws-banner{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 18px}.cws-pill{padding:7px 10px;border-radius:999px;background:var(--soft,#edf5fb);font-size:12px;font-weight:800;color:var(--navy,#062b4d)}.cws-template-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.cws-template-row select{min-width:210px;padding:9px;border:1px solid var(--line,#d8e4ef);border-radius:10px;background:white}.cws-doc-note{font-size:12px;color:var(--muted,#64778c);line-height:1.45}.cws-summary-total{font-size:13px;color:var(--muted,#64778c);margin-top:8px}
    @media(max-width:700px){.cws-summary-sections{grid-template-columns:1fr}}
    @media print{#customerSummaryView .doc{max-width:none}#customerSummaryView .cws-summary-sections{grid-template-columns:1fr 1fr}}
  `;
  document.head.appendChild(style);

  function serviceLabel(){return $('service')?.selectedOptions?.[0]?.textContent||'Property Turnover';}
  function conditionLabel(){return $('condition')?.selectedOptions?.[0]?.textContent||'Normal';}

  function addonItems(){
    const items=[];
    const fridge=num('fridge'); if(fridge>0) items.push({name:fridge===.5?'Inside refrigerator — only if needed':'Inside refrigerator',price:fridge===.5?25:50});
    if(yes('oven')) items.push({name:'Inside oven',price:60});
    const windows=num('windows'); if(windows) items.push({name:`Interior windows (${windows})`,price:windows*3});
    const blinds=num('blinds'); if(blinds) items.push({name:`Wet-wipe blinds (${blinds})`,price:blinds*10});
    if(yes('garage')) items.push({name:'Garage cleaning',price:45});
    const carpet=num('carpetSqft'); if(carpet) items.push({name:`Carpet cleaning (${carpet.toLocaleString()} sqft)`,price:carpet*.37});
    const pressure=num('pressureSqft'); if(pressure) items.push({name:`Pressure washing (${pressure.toLocaleString()} sqft)`,price:pressure*.40});
    if(yes('trash')) items.push({name:'Trash removal',price:20});
    return items;
  }

  function scopeSections(){
    const level=$('service')?.value||'turnover';
    const general=['Dust reachable surfaces','Remove cobwebs','Vacuum floors','Mop hard floors','Clean doors and handles as included','Clean window sills'];
    const kitchen=['Clean countertops and sink','Clean backsplash','Clean appliance exteriors','Wipe cabinet fronts'];
    const bath=['Clean and sanitize toilet','Clean sink and vanity','Clean mirrors and fixtures','Clean shower / tub','Vacuum and mop floor'];
    const living=['Dust reachable surfaces','Clean closets and shelving as included','Vacuum and mop floors'];
    if(level==='turnover'||level==='restoration'){
      general.push('Detail baseboards','Clean door frames','Clean reachable vent covers');
      kitchen.push('Clean inside cabinets','Clean inside drawers');
      living.push('Detail baseboards and trim');
    }
    if(level==='restoration'){
      general.push('Extra detail for buildup and neglected areas');
      kitchen.push('Heavy grease and buildup treatment as needed');
      bath.push('Extra soap scum / hard-water buildup treatment as needed');
    }
    return {General:general,Kitchen:kitchen,Bathrooms:bath,'Bedrooms & Living Areas':living};
  }

  function ensureBreakdown(){
    if($('cwsPriceBreakdown')) return;
    const profit=$('profitBox'); if(!profit) return;
    const title=document.createElement('div'); title.className='section-title'; title.textContent='Square entry breakdown';
    const box=document.createElement('div'); box.id='cwsPriceBreakdown'; box.className='notice';
    profit.insertAdjacentElement('afterend',box); box.insertAdjacentElement('beforebegin',title);
    const hint=document.createElement('div'); hint.className='cws-summary-total'; hint.textContent='Owner only — use these line items when creating the official Square invoice.';
    box.insertAdjacentElement('afterend',hint);
  }

  function renderBreakdown(){
    ensureBreakdown(); const box=$('cwsPriceBreakdown'); if(!box) return;
    const total=parseMoney($('quote')?.textContent), displayedAddons=parseMoney($('addons')?.textContent);
    const base=Math.max(0,total-displayedAddons); const items=addonItems();
    let known=items.reduce((s,x)=>s+x.price,0); let reconcile=displayedAddons-known;
    let rows=`<div class="cws-breakdown"><div class="cws-price-row"><span>${serviceLabel()} — ${conditionLabel()}</span><strong>${money(base)}</strong></div>`;
    items.forEach(i=>rows+=`<div class="cws-price-row"><span>${i.name}</span><strong>${money(i.price)}</strong></div>`);
    if(Math.abs(reconcile)>=1) rows+=`<div class="cws-price-row"><span>Additional estimator adjustment</span><strong>${money(reconcile)}</strong></div>`;
    rows+=`<div class="cws-price-row cws-price-total"><span>Recommended total</span><strong>${money(total)}</strong></div></div>`;
    box.innerHTML=rows;
  }

  function ensureCustomerButton(){
    if($('customerSummaryBtn')) return;
    const p=$('proposalBtn'); if(!p) return;
    const b=document.createElement('button'); b.id='customerSummaryBtn'; b.className='btn secondary'; b.textContent='Customer Summary'; b.onclick=openCustomerSummary;
    p.insertAdjacentElement('afterend',b);
  }

  function ensureCustomerView(){
    if($('customerSummaryView')) return;
    const view=document.createElement('div'); view.id='customerSummaryView'; view.className='view';
    view.innerHTML=`<div class="no-print actions" style="max-width:960px;margin:0 auto 12px"><button class="btn secondary" id="summaryBackBtn">← Back</button><button class="btn primary" id="summaryPrintBtn">Print / Save PDF</button></div><section class="doc"><div class="doc-head"><div style="display:flex;gap:16px;align-items:center"><img class="doc-logo" src="/static/cws-logo.svg" alt="Crystal Works Solutions"><div><h1 style="margin:0">Property Turnover Summary</h1><div class="muted">Professional service. Consistent results.</div></div></div><div><strong id="csDate"></strong></div></div><div class="cws-banner" id="csBanner"></div><div class="proposal-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div class="doc-box"><h3>Prepared for</h3><div id="csClient"></div><div id="csAddress"></div><div id="csUnit"></div></div><div class="doc-box"><h3>Service</h3><div id="csService"></div><div id="csProperty"></div><div id="csCondition"></div></div></div><h2 style="margin-top:22px">What’s included</h2><div class="cws-summary-sections" id="csScope"></div><div id="csAddonWrap"><h2 style="margin-top:22px">Additional services</h2><div class="cws-summary-sections" id="csAddons"></div></div><div id="csNotesWrap"><h2 style="margin-top:22px">Special notes</h2><div class="doc-box" id="csNotes"></div></div><div class="doc-box" style="margin-top:20px"><strong>Scope note</strong><div class="cws-doc-note" style="margin-top:6px">Final scope is based on the visible property condition and selected services. Unseen or excessive restoration conditions may require additional approval before extra work is performed.</div></div></section>`;
    document.querySelector('main.page')?.appendChild(view);
    $('summaryBackBtn').onclick=()=>showEstimator();
    $('summaryPrintBtn').onclick=()=>printSummary();
  }

  function showEstimator(){document.querySelectorAll('.view').forEach(v=>v.classList.remove('active','print-active')); $('estimatorView')?.classList.add('active'); window.scrollTo(0,0);}
  function printSummary(){const v=$('customerSummaryView'); if(!v)return; document.querySelectorAll('.view').forEach(x=>x.classList.remove('print-active'));v.classList.add('print-active');window.print();setTimeout(()=>v.classList.remove('print-active'),500);}

  function openCustomerSummary(){
    ensureCustomerView();
    $('csDate').textContent=new Date().toLocaleDateString();
    $('csClient').textContent=text('client')||'Client';
    $('csAddress').textContent=text('address')||'';
    $('csUnit').textContent=text('unit')?`Unit / Property ID: ${text('unit')}`:'';
    $('csService').innerHTML=`<strong>${serviceLabel()}</strong>`;
    $('csProperty').textContent=`${$('propertyType')?.value||'Property'} • ${num('beds')} bd / ${num('baths')} ba${num('halfBaths')?` + ${num('halfBaths')} half`:''} • ${num('sqft').toLocaleString()} sqft`;
    $('csCondition').textContent=`Condition: ${conditionLabel()}`;
    $('csBanner').innerHTML=`<span class="cws-pill">${serviceLabel()}</span><span class="cws-pill">${$('propertyType')?.value||'Property'}</span><span class="cws-pill">${conditionLabel()} condition</span>`;
    const sections=scopeSections(); $('csScope').innerHTML=Object.entries(sections).map(([h,arr])=>`<div class="cws-summary-section"><h3>${h}</h3>${arr.map(x=>`<div class="cws-check">${x}</div>`).join('')}</div>`).join('');
    const adds=addonItems(); $('csAddonWrap').style.display=adds.length?'block':'none'; $('csAddons').innerHTML=adds.length?`<div class="cws-summary-section" style="grid-column:1/-1">${adds.map(x=>`<div class="cws-check">${x.name}</div>`).join('')}</div>`:'';
    const notes=text('specialNotes'); $('csNotesWrap').style.display=notes?'block':'none'; $('csNotes').textContent=notes;
    document.querySelectorAll('.view').forEach(v=>v.classList.remove('active')); $('customerSummaryView').classList.add('active'); window.scrollTo(0,0);
  }

  function templateFields(){return ['customerType','propertyType','beds','baths','halfBaths','sqft','service','condition','targetShift','fridge','oven','windows','blinds','garage','carpetSqft','pressureSqft','trash','extraMinutes','manualAdjust'];}
  function getTemplates(){try{return JSON.parse(localStorage.getItem('cwsTurnoverTemplates')||'[]')}catch(e){return[]}}
  function saveTemplates(v){localStorage.setItem('cwsTurnoverTemplates',JSON.stringify(v));}
  function ensureTemplates(){
    if($('cwsTemplateBox'))return;
    const firstCard=document.querySelector('#estimatorView .workspace .card'); if(!firstCard)return;
    const body=firstCard.querySelector('.body'); const box=document.createElement('div'); box.id='cwsTemplateBox'; box.className='notice'; box.style.marginTop='12px';
    box.innerHTML=`<strong>Property templates</strong><div class="cws-template-row"><select id="cwsTemplateSelect"><option value="">Load a saved template…</option></select><button class="btn secondary" id="cwsLoadTemplate">Load</button><button class="btn secondary" id="cwsSaveTemplate">Save Current as Template</button><button class="btn danger" id="cwsDeleteTemplate">Delete</button></div>`;
    body.appendChild(box); $('cwsSaveTemplate').onclick=saveTemplate; $('cwsLoadTemplate').onclick=loadTemplate; $('cwsDeleteTemplate').onclick=deleteTemplate; refreshTemplateSelect();
  }
  function refreshTemplateSelect(){const s=$('cwsTemplateSelect');if(!s)return;const prev=s.value;s.innerHTML='<option value="">Load a saved template…</option>'+getTemplates().map((t,i)=>`<option value="${i}">${t.name}</option>`).join('');if(prev&&s.options[+prev+1])s.value=prev;}
  function saveTemplate(){const suggested=`${$('propertyType')?.value||'Property'} ${num('beds')}bd/${num('baths')}ba — ${serviceLabel()}`;const name=prompt('Template name:',suggested);if(!name)return;const data={};templateFields().forEach(id=>{const e=$(id);if(e)data[id]=e.value});const all=getTemplates();all.push({name,data});saveTemplates(all);refreshTemplateSelect();alert('Template saved. Client, address, and unit were not saved so the template can be reused.');}
  function loadTemplate(){const i=parseInt($('cwsTemplateSelect')?.value,10);if(!Number.isInteger(i))return;const t=getTemplates()[i];if(!t)return;Object.entries(t.data).forEach(([id,v])=>{if($(id)){$(id).value=v;$(id).dispatchEvent(new Event('input',{bubbles:true}));$(id).dispatchEvent(new Event('change',{bubbles:true}));}});setTimeout(renderBreakdown,50);}
  function deleteTemplate(){const i=parseInt($('cwsTemplateSelect')?.value,10);if(!Number.isInteger(i))return;const all=getTemplates();if(confirm(`Delete template “${all[i]?.name||''}”?`)){all.splice(i,1);saveTemplates(all);refreshTemplateSelect();}}

  function refresh(){renderBreakdown();}
  function init(){ensureBreakdown();ensureCustomerButton();ensureCustomerView();ensureTemplates();refresh();document.addEventListener('input',()=>setTimeout(refresh,0));document.addEventListener('change',()=>setTimeout(refresh,0));const q=$('quote');if(q)new MutationObserver(refresh).observe(q,{childList:true,subtree:true,characterData:true});const a=$('addons');if(a)new MutationObserver(refresh).observe(a,{childList:true,subtree:true,characterData:true});}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();