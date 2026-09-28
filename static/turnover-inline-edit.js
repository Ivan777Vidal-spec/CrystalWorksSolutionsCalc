(()=>{
  const EDITABLE_VIEWS=['proposalView','customerSummaryView','crewChecklistView'];
  const $=id=>document.getElementById(id);

  const style=document.createElement('style');
  style.textContent=`
    .doc-editing [contenteditable="true"]{outline:1px dashed #6f98b7;outline-offset:1px;cursor:text}
    .doc-editing [contenteditable="true"]:focus{outline:2px solid #2b6f9f;background:#f7fbff}
    .doc-edit-hint{font-size:12px;color:#53687c;align-self:center}
    @media print{.doc-editing [contenteditable="true"]{outline:none!important;background:transparent!important}}
  `;
  document.head.appendChild(style);

  function editableNodes(doc){
    if(!doc) return [];
    return [...doc.querySelectorAll('h1,h2,h3,p,li,td,th,.doc-box,.cws-check,.cws-doc-note,.crew-banner,.crew-box')].filter(el=>{
      if(el.closest('.no-print')) return false;
      if(el.querySelector('input,select,textarea,button')) return false;
      return el.children.length===0 || [...el.children].every(c=>['BR','STRONG','SPAN','B','I','EM'].includes(c.tagName));
    });
  }

  function setEditing(view,on){
    const doc=view?.querySelector('.doc');
    if(!doc) return;
    view.classList.toggle('doc-editing',on);
    editableNodes(doc).forEach(el=>{
      if(on){el.setAttribute('contenteditable','true');el.setAttribute('spellcheck','true');}
      else el.removeAttribute('contenteditable');
    });
    const btn=view.querySelector('[data-edit-document]');
    if(btn){btn.textContent=on?'Done Editing':'Edit Document';btn.dataset.editing=on?'1':'0';}
    const hint=view.querySelector('[data-edit-hint]');
    if(hint) hint.textContent=on?'Click any outlined text or table cell to edit it. Your edits will print.':'';
  }

  function addEditButton(viewId){
    const view=$(viewId);
    const actions=view?.querySelector('.no-print.actions');
    if(!actions||actions.querySelector('[data-edit-document]')) return;
    const btn=document.createElement('button');
    btn.type='button';btn.className='btn secondary';btn.dataset.editDocument='1';btn.textContent='Edit Document';
    btn.onclick=()=>setEditing(view,btn.dataset.editing!=='1');
    const printBtn=[...actions.querySelectorAll('button')].find(b=>/print/i.test(b.textContent||''));
    if(printBtn) actions.insertBefore(btn,printBtn); else actions.appendChild(btn);
    const hint=document.createElement('span');hint.dataset.editHint='1';hint.className='doc-edit-hint';actions.appendChild(hint);
  }

  function removeOldExport(viewId){
    const view=$(viewId);
    view?.querySelectorAll('[data-google-doc-export]').forEach(b=>b.remove());
  }

  function install(){
    EDITABLE_VIEWS.forEach(id=>{addEditButton(id);removeOldExport(id);});
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>setTimeout(install,40));
  else setTimeout(install,40);
  document.addEventListener('click',()=>setTimeout(install,20));
})();