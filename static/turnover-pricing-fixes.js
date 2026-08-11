(()=>{
  const local$=id=>document.getElementById(id);
  const val=id=>parseFloat(local$(id)?.value)||0;
  const fmt=v=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(v||0);
  const readMoney=s=>Number(String(s||'').replace(/[^0-9.-]/g,''))||0;

  const style=document.createElement('style');
  style.textContent=`
    @media print{
      .crew-doc{font-size:9.5px!important;line-height:1.12!important}
      .crew-doc .doc-head{margin-bottom:6px!important;padding-bottom:6px!important}
      .crew-doc .doc-logo{width:58px!important;height:56px!important}
      .crew-title h1{font-size:16px!important}
      .crew-title div{font-size:8.5px!important}
      .crew-meta{margin:4px 0 6px!important}
      .crew-meta td{padding:3px 5px!important;font-size:8.5px!important}
      .crew-banner{padding:4px!important;margin-bottom:5px!important;font-size:8.5px!important}
      .crew-table th,.crew-table td{padding:2.5px 4px!important;font-size:8px!important;line-height:1.08!important}
      .crew-table .done{font-size:13px!important}
      .crew-footer-grid{gap:6px!important;margin-top:6px!important}
      .crew-box{min-height:58px!important;padding:5px!important}
      .crew-box h3{font-size:9px!important;margin-bottom:3px!important}
      .crew-lines{line-height:1.35!important}
      .crew-sign{margin-top:5px!important}
    }
  `;
  document.head.appendChild(style);

  function correctedCalc(){
    const s=Math.max(n('sqft'),100);
    let base=interp(s,'h');
    const expectedBeds=interp(s,'b');
    const expectedBathEq=interp(s,'ba');
    const actualBathEq=n('baths')+n('halfBaths')*.5;

    // Continuous bedroom/bath adjustment. The old Math.floor() logic could make
    // a 400-sq-ft 2bd/1ba quote higher than the same 900-sq-ft layout.
    const roomAdj=(n('beds')-expectedBeds)*.22+(actualBathEq-expectedBathEq)*.42;
    base=Math.max(1,base+roomAdj);

    const serviceMult=settings[$('service').value+'Mult']||1;
    const conditionMult=settings[$('condition').value+'Mult']||1;
    const add=addonCalc();
    const extra=(settings.pricingMode==='advanced'?n('extraMinutes')/60:0);

    const baseLabor=Math.max(.5,(base+extra)*serviceMult*conditionMult);
    const labor=baseLabor+add.labor;
    const manual=(settings.pricingMode==='advanced'?n('manualAdjust'):0);

    // Flat-rate add-ons are charged exactly once. Their labor still increases
    // estimated labor, crew duration and direct cost for profitability tracking.
    const quote=Math.max(settings.minJob,baseLabor*settings.hourlyRate)+add.price+manual;

    const crew=Math.max(1,Math.ceil(labor/Math.max(n('targetShift'),.5)));
    const duration=labor/crew;
    const cost=labor*settings.cleanerWage*(1+settings.burden/100)+settings.supplies;
    const profit=quote-cost;
    const margin=quote?profit/quote*100:0;

    last={labor,quote,crew,duration,addons:add.price,cost,profit,margin};
    $('summaryTitle').textContent=$('service').selectedOptions[0].text;
    $('quote').textContent=money(quote);
    $('labor').textContent=labor.toFixed(2)+' hr';
    $('crew').textContent=crew;
    $('duration').textContent=duration.toFixed(2)+' hr';
    $('addons').textContent=money(add.price);
    $('profitBox').innerHTML=`Estimated direct cost: <b>${money(cost)}</b><br>Estimated gross profit: <b>${money(profit)}</b> (${margin.toFixed(1)}%)`;
    $('scopeText').textContent=scope[$('service').value];
    $('serviceDescription').textContent=scope[$('service').value];
    renderUnits();

    // Enhancement script watches these values, so refresh our accurate Square
    // line-item breakdown after it has had a chance to react.
    setTimeout(renderCorrectBreakdown,0);
  }

  function addonLineItems(){
    const items=[];
    const fridge=val('fridge'); if(fridge>0) items.push([fridge===.5?'Inside refrigerator — only if needed':'Inside refrigerator',fridge*50]);
    if(val('oven')) items.push(['Inside oven',60]);
    const windows=val('windows'); if(windows) items.push([`Interior windows (${windows})`,windows*10]);
    const blinds=val('blinds'); if(blinds) items.push([`Wet-wipe blinds (${blinds})`,blinds*10]);
    if(val('garage')) items.push(['Garage cleaning',75]);
    const carpet=val('carpetSqft'); if(carpet) items.push([`Carpet cleaning (${carpet.toLocaleString()} sqft)`,carpet*.37]);
    const pressure=val('pressureSqft'); if(pressure) items.push([`Pressure washing (${pressure.toLocaleString()} sqft)`,pressure*.40]);
    if(val('trash')) items.push(['Trash removal',50]);
    return items;
  }

  function renderCorrectBreakdown(){
    const box=local$('cwsPriceBreakdown');
    if(!box) return;
    const total=readMoney(local$('quote')?.textContent);
    const addonTotal=readMoney(local$('addons')?.textContent);
    const base=Math.max(0,total-addonTotal);
    const service=local$('service')?.selectedOptions?.[0]?.textContent||'Property Turnover';
    const condition=local$('condition')?.selectedOptions?.[0]?.textContent||'Normal';
    let html=`<div class="cws-breakdown"><div class="cws-price-row"><span>${service} — ${condition}</span><strong>${fmt(base)}</strong></div>`;
    addonLineItems().forEach(([name,price])=>{html+=`<div class="cws-price-row"><span>${name}</span><strong>${fmt(price)}</strong></div>`;});
    html+=`<div class="cws-price-row cws-price-total"><span>Recommended total</span><strong>${fmt(total)}</strong></div></div>`;
    box.innerHTML=html;
  }

  calc=correctedCalc;

  function rerun(){
    try{correctedCalc();renderCorrectBreakdown();}catch(e){console.error('Turnover pricing recalculation failed',e);}
  }

  document.addEventListener('input',()=>setTimeout(renderCorrectBreakdown,1));
  document.addEventListener('change',()=>setTimeout(renderCorrectBreakdown,1));
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>setTimeout(rerun,0));
  else setTimeout(rerun,0);
})();
