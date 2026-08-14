(()=>{
  const $=id=>document.getElementById(id);

  const style=document.createElement('style');
  style.textContent=`
    @media print{
      @page{size:auto;margin:0.32in}
      body{font-size:9.5px!important;line-height:1.22!important}
      .doc{font-size:9.5px!important;line-height:1.22!important;max-width:none!important;padding:0!important;margin:0!important}
      .doc h1{font-size:18px!important;line-height:1.05!important;margin:0 0 3px!important}
      .doc h2{font-size:12px!important;margin:9px 0 5px!important}
      .doc h3{font-size:10.5px!important;margin:0 0 4px!important}
      .doc p,.doc div,.doc span,.doc strong,.doc td,.doc th{line-height:1.22!important}
      .doc-head{padding-bottom:7px!important;margin-bottom:8px!important;gap:8px!important}
      .doc-logo{width:58px!important;height:56px!important}
      .doc-box{padding:7px!important;margin-top:6px!important;border-radius:8px!important}
      .doc table{font-size:9px!important}
      .doc th,.doc td{padding:4px 5px!important;font-size:9px!important}
      .cws-banner{gap:4px!important;margin:5px 0 8px!important}
      .cws-pill{padding:3px 6px!important;font-size:8.5px!important}
      .cws-summary-sections{gap:6px!important;margin-top:6px!important}
      .cws-summary-section{padding:7px!important;border-radius:8px!important}
      .cws-check{font-size:9px!important;margin:2px 0!important}
      .cws-doc-note{font-size:8.5px!important;line-height:1.2!important}
      #customerSummaryView h2{margin-top:9px!important}
      #customerSummaryView .proposal-grid{gap:6px!important}
      #proposalView .doc,#summaryView .doc,#workOrderView .doc,#customerSummaryView .doc{zoom:.92}
    }
  `;
  document.head.appendChild(style);

  function scopeSections(){
    const level=$('service')?.value||'turnover';
    const refresh=level==='refresh';
    const restoration=level==='restoration';

    const general=[
      'Dust reachable surfaces and remove cobwebs',
      'Dust reachable light fixtures and ceiling fans',
      'Dust doors and door frames',
      'Clean window sills',
      'Vacuum / sweep floors and mop hard floors'
    ];
    const kitchen=[
      'Clean countertops, sink and backsplash',
      'Clean appliance exteriors',
      'Clean stovetop based on visible condition',
      'Wipe cabinet fronts / exteriors'
    ];
    const bathrooms=[
      'Clean and sanitize toilet',
      'Clean sink, vanity, mirrors and fixtures',
      'Clean shower / tub',
      'Vacuum / sweep and mop floor'
    ];
    const living=[
      'Dust reachable surfaces',
      'Clean closets, shelving and closet floors',
      'Clean laundry area',
      'Vacuum / sweep floors and mop hard floors'
    ];

    if(!refresh){
      general.splice(1,1,'Wipe down reachable light fixtures and ceiling fans');
      general.splice(2,1,'Wipe down doors and door frames');
      general.push('Detail baseboards','Clean reachable vent covers','Spot clean minor wall marks as appropriate');
      kitchen.push('Clean inside cabinets','Clean inside drawers');
      living.push('Detail baseboards and trim');
    }
    if(restoration){
      general.push('Additional passes for heavy grime and neglected buildup');
      kitchen.push('Heavy grease and buildup treatment as needed');
      bathrooms.push('Extra soap scum / hard-water buildup treatment as needed');
    }
    return {General:general,Kitchen:kitchen,Bathrooms:bathrooms,'Bedrooms, Closets & Living Areas':living};
  }

  function refreshCustomerScope(){
    const target=$('csScope');
    if(!target)return;
    const sections=scopeSections();
    target.innerHTML=Object.entries(sections).map(([heading,items])=>`<div class="cws-summary-section"><h3>${heading}</h3>${items.map(item=>`<div class="cws-check">${item}</div>`).join('')}</div>`).join('');
  }

  function packageDescription(){
    const level=$('service')?.value||'turnover';
    if(level==='refresh') return 'Light vacant-property refresh: dusting, closets and laundry area, normal kitchen/bathroom cleaning, stovetop as condition allows, and complete floor cleaning. Cabinet interiors, wall spot cleaning and detailed wipe-down work are not included unless added.';
    if(level==='restoration') return 'Everything in Vacant Turnover, with additional labor and treatment for heavy grease, soap scum, hard-water buildup, grime and neglected areas. Specialty floor restoration remains a separate service.';
    return 'Full vacant turnover: light fixtures/fans and doors/frames wiped down, closets and laundry area, inside cabinets and drawers, baseboards, reachable vents, minor wall spot cleaning, detailed kitchen/bathroom cleaning, and complete floor cleaning.';
  }

  function refreshDescription(){
    const d=$('serviceDescription'); if(d)d.textContent=packageDescription();
    const q=$('scopeText'); if(q)q.textContent=packageDescription();
    setTimeout(refreshCustomerScope,0);
  }

  function init(){
    refreshDescription();
    $('service')?.addEventListener('change',refreshDescription);
    document.addEventListener('click',e=>{
      if(e.target?.id==='customerSummaryBtn')setTimeout(refreshCustomerScope,0);
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();