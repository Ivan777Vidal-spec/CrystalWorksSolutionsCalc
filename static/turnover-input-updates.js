(()=>{
  const $=id=>document.getElementById(id);
  const num=id=>parseFloat($(id)?.value)||0;
  const selected=id=>$(id)?.selectedOptions?.[0]?.textContent||'';

  function field(label,html){
    const wrap=document.createElement('div');
    wrap.className='field';
    wrap.innerHTML=`<label>${label}</label>${html}`;
    return wrap;
  }

  function addKitchenSize(){
    if($('kitchenSize')) return;
    const sqft=$('sqft');
    const grid=sqft?.closest('.grid');
    if(!grid) return;
    grid.appendChild(field('Kitchen size','<select id="kitchenSize"><option value="small">Small / Kitchenette</option><option value="standard" selected>Standard Kitchen</option><option value="large">Large Kitchen</option></select>'));
  }

  function addHardWindows(){
    if($('hardWindows')) return;
    const windows=$('windows');
    const normalField=windows?.closest('.field');
    if(!normalField) return;
    const label=normalField.querySelector('label');
    if(label) label.textContent='Standard interior windows';
    normalField.insertAdjacentElement('afterend',field('Hard-to-reach interior windows','<input id="hardWindows" type="number" min="0" value="0">'));
  }

  function renameMetrics(){
    const labor=$('labor')?.closest('.metric')?.querySelector('span');
    const duration=$('duration')?.closest('.metric')?.querySelector('span');
    if(labor) labor.textContent='Total labor hours';
    if(duration) duration.textContent='Estimated on-site time';
  }

  function patchCustomerSummary(){
    if($('csProperty') && $('kitchenSize')){
      const current=$('csProperty').textContent.replace(/ • Kitchen:.*$/,'');
      $('csProperty').textContent=`${current} • Kitchen: ${selected('kitchenSize')}`;
    }
    const count=num('hardWindows');
    if(!count || !$('csAddons')) return;
    const section=$('csAddons').querySelector('.cws-summary-section')||$('csAddons');
    if(section.querySelector('[data-hard-window-summary]')) return;
    const row=document.createElement('div');
    row.className='cws-check';
    row.dataset.hardWindowSummary='1';
    row.textContent=`Hard-to-reach interior windows (${count})`;
    section.appendChild(row);
    if($('csAddonWrap')) $('csAddonWrap').style.display='block';
  }

  function patchCrewWorkOrder(){
    const count=num('hardWindows');
    if(count && $('cwTasks') && !$('cwTasks').querySelector('[data-hard-window-task]')){
      const group=document.createElement('tr');
      group.className='group';
      group.dataset.hardWindowTask='1';
      group.innerHTML='<td colspan="5">Selected Add-ons</td>';
      const row=document.createElement('tr');
      row.className='addon';
      row.dataset.hardWindowTask='1';
      row.innerHTML=`<td class="order">+</td><td>Clean ${count} hard-to-reach interior window${count===1?'':'s'}; use approved ladder/access method</td><td class="target">${Math.max(10,count*10)} min est.</td><td class="assign"></td><td class="done"><span class="crew-check-square"></span></td>`;
      $('cwTasks').append(group,row);
    }
    if($('cwService') && $('kitchenSize')){
      const base=$('cwService').textContent.replace(/ • Kitchen:.*$/,'');
      $('cwService').textContent=`${base} • Kitchen: ${selected('kitchenSize')}`;
    }
    const laborLabel=$('cwLabor')?.parentElement;
    if(laborLabel) laborLabel.innerHTML=`<strong>Total Labor Hours:</strong> <span id="cwLabor">${$('labor')?.textContent||'—'}</span>`;
  }

  function patchSavedTemplate(){
    try{
      const all=JSON.parse(localStorage.getItem('cwsTurnoverTemplates')||'[]');
      if(!all.length) return;
      const last=all[all.length-1];
      last.data=last.data||{};
      last.data.kitchenSize=$('kitchenSize')?.value||'standard';
      last.data.hardWindows=$('hardWindows')?.value||'0';
      localStorage.setItem('cwsTurnoverTemplates',JSON.stringify(all));
    }catch(e){console.warn('Could not extend turnover template',e);}
  }

  function init(){
    addKitchenSize();
    addHardWindows();
    renameMetrics();
    document.addEventListener('click',e=>{
      const id=e.target?.id;
      if(id==='customerSummaryBtn') setTimeout(patchCustomerSummary,25);
      if(id==='workOrderBtn') setTimeout(patchCrewWorkOrder,25);
      if(id==='cwsSaveTemplate') setTimeout(patchSavedTemplate,25);
    });
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();