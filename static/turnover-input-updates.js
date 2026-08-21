(()=>{
  const $=id=>document.getElementById(id);

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
    const wrap=field('Kitchen size','<select id="kitchenSize"><option value="small">Small / Kitchenette</option><option value="standard" selected>Standard Kitchen</option><option value="large">Large Kitchen</option></select>');
    grid.appendChild(wrap);
  }

  function addHardWindows(){
    if($('hardWindows')) return;
    const windows=$('windows');
    const normalField=windows?.closest('.field');
    if(!normalField) return;
    const label=normalField.querySelector('label');
    if(label) label.textContent='Standard interior windows';
    const wrap=field('Hard-to-reach interior windows','<input id="hardWindows" type="number" min="0" value="0">');
    normalField.insertAdjacentElement('afterend',wrap);
  }

  function renameMetrics(){
    const labor=$('labor')?.closest('.metric')?.querySelector('span');
    const duration=$('duration')?.closest('.metric')?.querySelector('span');
    if(labor) labor.textContent='Total labor hours';
    if(duration) duration.textContent='Estimated on-site time';
  }

  function init(){
    addKitchenSize();
    addHardWindows();
    renameMetrics();
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();