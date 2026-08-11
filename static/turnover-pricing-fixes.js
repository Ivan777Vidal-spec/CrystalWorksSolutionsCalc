(()=>{
  function correctedCalc(){
    const s=Math.max(n('sqft'),100);
    let base=interp(s,'h');
    const expectedBeds=interp(s,'b');
    const expectedBathEq=interp(s,'ba');
    const actualBathEq=n('baths')+n('halfBaths')*.5;

    // Continuous bedroom/bath adjustment prevents smaller homes from jumping
    // above larger homes because expected bathrooms were previously floored.
    const roomAdj=(n('beds')-expectedBeds)*.22+(actualBathEq-expectedBathEq)*.42;
    base=Math.max(1,base+roomAdj);

    const serviceMult=settings[$('service').value+'Mult']||1;
    const conditionMult=settings[$('condition').value+'Mult']||1;
    const add=addonCalc();
    const extra=(settings.pricingMode==='advanced'?n('extraMinutes')/60:0);

    const baseLabor=Math.max(.5,(base+extra)*serviceMult*conditionMult);
    const labor=baseLabor+add.labor;
    const manual=(settings.pricingMode==='advanced'?n('manualAdjust'):0);

    // Add-ons are flat-rate line items. Their labor still affects scheduling and
    // direct cost, but is not billed a second time through the hourly base.
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
  }

  calc=correctedCalc;

  function rerun(){
    try{correctedCalc();}catch(e){console.error('Turnover pricing recalculation failed',e);}
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>setTimeout(rerun,0));
  else setTimeout(rerun,0);
})();
