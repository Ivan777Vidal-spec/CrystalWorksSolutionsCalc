(()=>{
  const $=id=>document.getElementById(id);

  function safeName(value){
    return String(value||'property').trim().replace(/[^a-z0-9 _-]+/gi,'').replace(/\s+/g,'-').slice(0,60)||'property';
  }

  function documentHtml(viewId,title){
    const view=$(viewId);
    const doc=view?.querySelector('.doc');
    if(!doc) return '';
    const clone=doc.cloneNode(true);
    clone.querySelectorAll('input,select,textarea,button').forEach(el=>el.remove());
    clone.querySelectorAll('img').forEach(img=>{
      const src=img.getAttribute('src')||'';
      if(src.startsWith('/')) img.setAttribute('src',window.location.origin+src);
    });
    const css=`
      @page{size:letter;margin:.45in}
      body{font-family:Arial,Helvetica,sans-serif;color:#17324a;font-size:10pt;line-height:1.25;margin:0}
      h1{font-size:18pt;margin:0 0 6pt} h2{font-size:13pt;margin:12pt 0 6pt} h3{font-size:10.5pt;margin:0 0 5pt}
      table{width:100%;border-collapse:collapse} th,td{border:1px solid #9db2c5;padding:4pt;vertical-align:top}
      th{background:#e8f1f7}.doc-head{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #9db2c5;padding-bottom:8pt;margin-bottom:8pt}
      .doc-logo{width:54pt;height:auto}.proposal-grid,.cws-summary-sections,.crew-footer-grid,.crew-sign{display:grid;grid-template-columns:1fr 1fr;gap:8pt}
      .doc-box,.cws-summary-section,.crew-box{border:1px solid #9db2c5;padding:7pt}.cws-banner{margin:6pt 0}.cws-pill{display:inline-block;border:1px solid #9db2c5;padding:3pt 6pt;margin-right:4pt}
      .cws-check{margin:3pt 0}.cws-check:before{content:'✓ ';font-weight:bold}.crew-banner{border:1px solid #9db2c5;padding:5pt;text-align:center;font-weight:bold;margin-bottom:6pt}
      .crew-table .group td{font-weight:bold;background:#e8f1f7}.crew-check-square{display:inline-block;width:9pt;height:9pt;border:1px solid #17324a}
      .muted,.cws-doc-note{color:#5f7180}.no-print{display:none!important}
    `;
    return `<!doctype html><html><head><meta charset="utf-8"><title>${title}</title><style>${css}</style></head><body>${clone.outerHTML}</body></html>`;
  }

  function downloadEditable(viewId,label){
    const html=documentHtml(viewId,label);
    if(!html){alert('Open the document first, then try again.');return;}
    const property=safeName($('unit')?.value||$('address')?.value||'property');
    const filename=`CWS-${safeName(label)}-${property}.doc`;
    const blob=new Blob(['\ufeff',html],{type:'application/msword'});
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a');
    a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }

  function addButton(viewId,label){
    const view=$(viewId);
    const actions=view?.querySelector('.no-print.actions');
    if(!actions||actions.querySelector('[data-google-doc-export]')) return;
    const btn=document.createElement('button');
    btn.type='button';
    btn.className='btn secondary';
    btn.dataset.googleDocExport='1';
    btn.textContent='Download for Google Docs';
    btn.title='Downloads an editable document you can upload to Google Drive and open with Google Docs.';
    btn.addEventListener('click',()=>downloadEditable(viewId,label));
    actions.appendChild(btn);
  }

  function install(){
    addButton('proposalView','Proposal');
    addButton('customerSummaryView','Customer-Summary');
    addButton('crewChecklistView','Crew-Work-Order');
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>setTimeout(install,30));
  else setTimeout(install,30);
  document.addEventListener('click',()=>setTimeout(install,20));
})();