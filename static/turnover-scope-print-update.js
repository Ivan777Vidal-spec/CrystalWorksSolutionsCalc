(()=>{
  const $=id=>document.getElementById(id);
  const style=document.createElement('style');
  style.textContent=`@media print{
    @page{size:auto;margin:0.42in}
    body{font-size:11.5px!important;line-height:1.3!important}
    .doc{font-size:11.5px!important;line-height:1.3!important;max-width:none!important;padding:0!important;margin:0!important}
    .doc h1{font-size:23px!important;line-height:1.08!important;margin:0 0 5px!important}
    .doc h2{font-size:15px!important;margin:13px 0 7px!important}
    .doc h3{font-size:12.5px!important;margin:0 0 6px!important}
    .doc p,.doc div,.doc span,.doc strong,.doc td,.doc th{line-height:1.3!important}
    .doc-head{padding-bottom:10px!important;margin-bottom:12px!important;gap:12px!important}
    .doc-logo{width:76px!important;height:74px!important}
    .doc-box{padding:10px!important;margin-top:8px!important;border-radius:10px!important}
    .doc table{font-size:10.5px!important}.doc th,.doc td{padding:6px 7px!important;font-size:10.5px!important}
    .cws-banner{gap:6px!important;margin:8px 0 12px!important}.cws-pill{padding:5px 8px!important;font-size:10px!important}
    .cws-summary-sections{gap:9px!important;margin-top:9px!important}.cws-summary-section{padding:10px!important;border-radius:10px!important}
    .cws-check{font-size:10.5px!important;margin:3px 0!important}.cws-doc-note{font-size:10px!important;line-height:1.28!important}
    #customerSummaryView h2{margin-top:13px!important}#customerSummaryView .proposal-grid{gap:9px!important}
    #proposalView .doc,#summaryView .doc,#workOrderView .doc,#customerSummaryView .doc{zoom:1!important}
  }`;
  document.head.appendChild(style);

  function packageDescription(){const level=$('service')?.value||'turnover';if(level==='refresh')return 'Light vacant-property refresh: dusting, closets and laundry area, normal kitchen/bathroom cleaning, stovetop as condition allows, and complete floor cleaning. Cabinet interiors, wall spot cleaning and detailed wipe-down work are not included unless added.';if(level==='restoration')return 'Everything in Vacant Turnover, with additional labor and treatment for heavy grease, soap scum, hard-water buildup, grime and neglected areas. Specialty floor restoration remains a separate service.';return 'Full vacant turnover: light fixtures/fans and doors/frames wiped down, closets and laundry area, inside cabinets and drawers, baseboards, reachable vents, minor wall spot cleaning, detailed kitchen/bathroom cleaning, and complete floor cleaning.';}
  function refreshDescription(){const d=$('serviceDescription');if(d)d.textContent=packageDescription();const q=$('scopeText');if(q)q.textContent=packageDescription();}
  function init(){refreshDescription();$('service')?.addEventListener('change',refreshDescription);}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();