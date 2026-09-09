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
    grid.appendChild(field('Kitchen size','<select id="kitchenSize"><option value="small">Small / Kitchenette</option><option value="standard" selected>Standard Kitchen</option><option value="large">Large Kitchen</option></select>'));
  }

  function setupWindowService(){
    const windows=$('windows');
    const normalField=windows?.closest('.field');
    if(!normalField) return;

    const label=normalField.querySelector('label');
    if(label) label.textContent='Standard windows';

    if(!$('windowService')){
      normalField.insertAdjacentElement('beforebegin',field(
        'Window cleaning service',
        '<select id="windowService"><option value="interior">Interior Only</option><option value="complete">Complete — Interior + Exterior</option></select>'
      ));
    }

    if(!$('hardWindows')){
      normalField.insertAdjacentElement('afterend',field(
        'High / hard-to-reach windows',
        '<input id="hardWindows" type="number" min="0" value="0">'
      ));
    }else{
      const hardLabel=$('hardWindows')?.closest('.field')?.querySelector('label');
      if(hardLabel) hardLabel.textContent='High / hard-to-reach windows';
    }

    if(!$('hardWaterWindows')){
      $('hardWindows')?.closest('.field')?.insertAdjacentElement('afterend',field(
        'Windows with hard-water removal',
        '<input id="hardWaterWindows" type="number" min="0" value="0">'
      ));
    }

    if(!$('windowServiceNote')){
      const note=document.createElement('div');
      note.id='windowServiceNote';
      note.className='notice';
      note.style.gridColumn='1 / -1';
      note.innerHTML='<strong>Window service:</strong> Interior Only includes interior glass + accessible interior sill. Complete includes interior/exterior glass + accessible sills + screen cleaning when present and accessible. Hard-water removal is optional.';
      $('hardWaterWindows')?.closest('.grid')?.appendChild(note);
    }
  }

  function renameMetrics(){
    const labor=$('labor')?.closest('.metric')?.querySelector('span');
    const duration=$('duration')?.closest('.metric')?.querySelector('span');
    if(labor) labor.textContent='Total labor hours';
    if(duration) duration.textContent='Estimated on-site time';
  }

  function patchSavedTemplate(){
    try{
      const all=JSON.parse(localStorage.getItem('cwsTurnoverTemplates')||'[]');
      if(!all.length) return;
      const last=all[all.length-1];
      last.data=last.data||{};
      last.data.kitchenSize=$('kitchenSize')?.value||'standard';
      last.data.windowService=$('windowService')?.value||'interior';
      last.data.hardWindows=$('hardWindows')?.value||'0';
      last.data.hardWaterWindows=$('hardWaterWindows')?.value||'0';
      localStorage.setItem('cwsTurnoverTemplates',JSON.stringify(all));
    }catch(e){console.warn('Could not extend turnover template',e);}
  }

  function init(){
    addKitchenSize();
    setupWindowService();
    renameMetrics();
    document.addEventListener('click',e=>{
      if(e.target?.id==='cwsSaveTemplate') setTimeout(patchSavedTemplate,25);
    });
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();