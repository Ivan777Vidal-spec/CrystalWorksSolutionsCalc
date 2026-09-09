(()=>{
  const $=id=>document.getElementById(id);
  const num=id=>parseFloat($(id)?.value)||0;
  const selected=id=>$(id)?.selectedOptions?.[0]?.textContent||'';

  function details(){
    const standard=num('windows');
    const high=num('hardWindows');
    const hardWater=Math.min(num('hardWaterWindows'),standard+high);
    const mode=$('windowService')?.value||'interior';
    return {standard,high,hardWater,mode,total:standard+high};
  }

  function kitchenLabel(){return selected('kitchenSize')||'Standard Kitchen';}

  function windowScopeText(d){
    if(d.mode==='complete') return 'Interior + exterior glass, accessible interior/exterior sills, and screen cleaning when present and accessible.';
    return 'Interior glass and accessible interior window sills.';
  }

  function windowCountText(d){
    const parts=[];
    if(d.standard) parts.push(`${d.standard} standard window${d.standard===1?'':'s'}`);
    if(d.high) parts.push(`${d.high} high / hard-to-reach window${d.high===1?'':'s'}`);
    return parts.join(' + ');
  }

  function patchCustomerSummary(){
    if($('csProperty') && $('kitchenSize')){
      const base=$('csProperty').textContent.replace(/ • Kitchen:.*$/,'');
      $('csProperty').textContent=`${base} • Kitchen: ${kitchenLabel()}`;
    }

    const d=details();
    const box=$('csAddons');
    if(!box) return;
    box.querySelectorAll('.cws-check').forEach(row=>{
      const t=row.textContent.toLowerCase();
      if(t.includes('interior window')||t.includes('hard-to-reach interior window')||row.dataset.windowServiceRow) row.remove();
    });

    if(!d.total) return;
    const section=box.querySelector('.cws-summary-section')||box;
    const modeLabel=d.mode==='complete'?'Complete Window Cleaning — Interior + Exterior':'Window Cleaning — Interior Only';
    const rows=[
      `${modeLabel}: ${windowCountText(d)}`,
      windowScopeText(d)
    ];
    if(d.hardWater) rows.push(`Hard-water removal on ${d.hardWater} affected window${d.hardWater===1?'':'s'}`);
    rows.forEach(text=>{
      const row=document.createElement('div');
      row.className='cws-check';
      row.dataset.windowServiceRow='1';
      row.textContent=text;
      section.appendChild(row);
    });
    if($('csAddonWrap')) $('csAddonWrap').style.display='block';
  }

  function addCrewRow(tbody,name,target){
    const row=document.createElement('tr');
    row.className='addon';
    row.dataset.windowServiceRow='1';
    row.innerHTML=`<td class="order">+</td><td>${name}</td><td class="target">${target}</td><td class="assign"></td><td class="done"><span class="crew-check-square"></span></td>`;
    tbody.appendChild(row);
  }

  function patchCrewWorkOrder(){
    if($('cwService') && $('kitchenSize')){
      const base=$('cwService').textContent.replace(/ • Kitchen:.*$/,'');
      $('cwService').textContent=`${base} • Kitchen: ${kitchenLabel()}`;
    }
    const laborParent=$('cwLabor')?.parentElement;
    if(laborParent) laborParent.innerHTML=`<strong>Total Labor Hours:</strong> <span id="cwLabor">${$('labor')?.textContent||'—'}</span>`;

    const tbody=$('cwTasks');
    if(!tbody) return;
    tbody.querySelectorAll('tr').forEach(row=>{
      const t=row.textContent.toLowerCase();
      if(row.dataset.windowServiceRow||((row.classList.contains('addon'))&&(t.includes('interior window')||t.includes('hard-to-reach interior window')))) row.remove();
    });

    const d=details();
    if(!d.total) return;
    const hasAddonGroup=[...tbody.querySelectorAll('tr.group')].some(r=>r.textContent.trim()==='Selected Add-ons');
    if(!hasAddonGroup){
      const group=document.createElement('tr');
      group.className='group';
      group.dataset.windowServiceRow='1';
      group.innerHTML='<td colspan="5">Selected Add-ons</td>';
      tbody.appendChild(group);
    }

    const minutes=(d.standard*(d.mode==='complete'?8:5))+(d.high*(d.mode==='complete'?14:10));
    const taskName=d.mode==='complete'
      ? `Window cleaning — ${windowCountText(d)}: clean interior + exterior glass, accessible sills, and screens when present and accessible`
      : `Window cleaning — ${windowCountText(d)}: clean interior glass and accessible interior sills`;
    addCrewRow(tbody,taskName,`${Math.max(5,Math.round(minutes))} min est.`);
    if(d.hardWater) addCrewRow(tbody,`Hard-water removal — ${d.hardWater} affected window${d.hardWater===1?'':'s'}; treat mineral buildup with approved method and document permanent etching/damage`,'10 min/window est.');
  }

  function patchProposal(){
    const box=$('pAddons');
    if(!box) return;
    const d=details();
    let text=box.textContent||'';
    text=text.replace(/\d+(?:\.\d+)? interior windows,?\s*/gi,'').replace(/,\s*,/g,', ').replace(/^,\s*|,\s*$/g,'').trim();
    if(!d.total){box.textContent=text||'No additional services selected.';return;}
    const label=d.mode==='complete'?'Complete window cleaning':'Interior-only window cleaning';
    const parts=[];
    if(text && text!=='No additional services selected.') parts.push(text);
    parts.push(`${label}: ${windowCountText(d)} — ${windowScopeText(d)}`);
    if(d.hardWater) parts.push(`Hard-water removal: ${d.hardWater} window${d.hardWater===1?'':'s'}`);
    box.textContent=parts.join(' • ');
  }

  function clampHardWater(){
    const el=$('hardWaterWindows');
    if(!el) return;
    const total=num('windows')+num('hardWindows');
    el.max=String(total);
    if(num('hardWaterWindows')>total) el.value=String(total);
  }

  function init(){
    clampHardWater();
    document.addEventListener('input',e=>{
      if(['windows','hardWindows'].includes(e.target?.id)) clampHardWater();
    });
    document.addEventListener('click',e=>{
      const id=e.target?.id;
      if(id==='customerSummaryBtn') setTimeout(patchCustomerSummary,30);
      if(id==='workOrderBtn') setTimeout(patchCrewWorkOrder,30);
      if(id==='proposalBtn') setTimeout(patchProposal,30);
    });
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();