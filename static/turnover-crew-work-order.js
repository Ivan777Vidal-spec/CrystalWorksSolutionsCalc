(()=>{
  const $=id=>document.getElementById(id);
  const num=id=>parseFloat($(id)?.value)||0;
  const text=id=>$(id)?.value||'';
  const selected=id=>$(id)?.selectedOptions?.[0]?.textContent||'';

  const style=document.createElement('style');
  style.textContent=`
    .crew-doc{font-size:12px;line-height:1.25}.crew-doc .doc-head{margin-bottom:10px;padding-bottom:10px}.crew-doc .doc-logo{width:72px;height:70px}.crew-title{text-align:center;flex:1}.crew-title h1{font-size:20px;margin:0;color:var(--navy,#062b4d)}.crew-title div{font-size:11px;color:var(--muted,#64778c)}
    .crew-meta{width:100%;border-collapse:collapse;margin:7px 0 10px}.crew-meta td{border:1px solid #9db2c5;padding:5px 7px;font-size:11px;vertical-align:top}.crew-meta strong{color:var(--navy,#062b4d)}
    .crew-banner{border:1px solid #9db2c5;background:#edf5fb;padding:6px;text-align:center;font-weight:800;color:var(--navy,#062b4d);margin-bottom:8px}
    .crew-table{width:100%;border-collapse:collapse;table-layout:fixed}.crew-table th,.crew-table td{border:1px solid #8fa7ba;padding:5px 6px;font-size:10.5px;vertical-align:middle}.crew-table th{background:#dcebf6;color:#173a5c;font-weight:900;text-align:left}.crew-table .order{width:42px;text-align:center}.crew-table .target{width:78px;text-align:center}.crew-table .assign{width:84px}.crew-table .done{width:48px;text-align:center;font-size:17px}.crew-table tr.group td{background:#edf5fb;color:#0b4a78;font-weight:900;text-transform:uppercase;letter-spacing:.04em}.crew-table tr.addon td{background:#fff9e8}.crew-table tr.restoration td{background:#fff1eb}
    .crew-footer-grid{display:grid;grid-template-columns:1.4fr 1fr;gap:10px;margin-top:10px}.crew-box{border:1px solid #9db2c5;min-height:78px;padding:7px}.crew-box h3{margin:0 0 6px;font-size:11px;color:var(--navy,#062b4d);text-transform:uppercase}.crew-lines{line-height:1.75}.crew-sign{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}.crew-sign div{border-top:1px solid #6f8498;padding-top:4px;font-size:10px;color:#53687c}.crew-check-square{display:inline-block;width:14px;height:14px;border:1.5px solid #2f4f69;vertical-align:middle}
    @media print{#crewChecklistView .doc{max-width:none!important;padding:0!important}.crew-doc{font-size:10.5px}.crew-table th,.crew-table td{padding:4px 5px;font-size:9.5px}.crew-doc h2,.crew-doc h3{break-after:avoid}.crew-table tr{break-inside:avoid}.crew-footer-grid{break-inside:avoid}}
  `;
  document.head.appendChild(style);

  function task(name,target,group,cls=''){
    return {name,target,group,cls};
  }

  function buildTasks(){
    const service=$('service')?.value||'turnover';
    const sqft=num('sqft');
    const beds=num('beds');
    const baths=num('baths')+num('halfBaths')*.5;
    const large=sqft>=1800;
    const tasks=[
      task('Initial walkthrough; verify scope, access, utilities and visible condition','5–10 min','Arrival / Setup'),
      task('Take before photos of property condition and any pre-existing damage','5 min','Arrival / Setup'),
      task('Stage equipment and supplies; start high-to-low dusting','5–10 min','Arrival / Setup'),
      task('Remove cobwebs; dust reachable vents, ledges, fans and high surfaces',large?'20–30 min':'10–20 min','High Dust / Dry Work'),
      task('Dust window sills, shelves, doors and reachable surfaces',large?'20–30 min':'10–20 min','High Dust / Dry Work'),
      task('Pre-spray shower/tub and allow chemical dwell time','5 min','Bathrooms'),
      task(`Clean ${baths||1} bathroom(s): mirrors, sink/vanity, fixtures and counters`,baths>2?'30–45 min':'15–30 min','Bathrooms'),
      task('Scrub shower/tub, remove normal soap film and rinse','15–30 min','Bathrooms'),
      task('Clean and sanitize toilet including base and surrounding area','10–15 min','Bathrooms'),
      task('Clean kitchen counters, sink, backsplash and appliance exteriors','20–30 min','Kitchen'),
      task('Wipe cabinet fronts, handles and visible kitchen surfaces','15–25 min','Kitchen'),
      task(`Clean ${beds||1} bedroom(s), closets and living areas`,beds>3?'40–60 min':'25–45 min','Bedrooms / Living Areas'),
      task('Vacuum entire property, edges and accessible closet floors',large?'25–40 min':'15–25 min','Floors'),
      task('Mop all hard floors; leave floors streak-free','15–30 min','Floors'),
      task('Remove trash, collect equipment and perform final detail pass','10–15 min','Final Walkthrough'),
      task('Take after photos; verify doors/windows, lights, keys and property security','5–10 min','Final Walkthrough')
    ];

    if(service==='turnover'||service==='restoration'){
      tasks.splice(10,0,
        task('Clean inside kitchen cabinets and drawers','20–40 min','Vacant Turnover Detail'),
        task('Detail baseboards, door frames and reachable vent covers',large?'30–45 min':'20–30 min','Vacant Turnover Detail')
      );
    }
    if(service==='restoration'){
      tasks.splice(tasks.length-4,0,
        task('Treat heavy grease / buildup areas; repeat agitation and dwell as needed','As needed','Restoration Work','restoration'),
        task('Treat heavy soap scum / mineral buildup where included','As needed','Restoration Work','restoration'),
        task('Document restoration areas that cannot be safely corrected within scope','As needed','Restoration Work','restoration')
      );
    }

    const addons=[];
    const fridge=num('fridge');
    if(fridge>0) addons.push(task(fridge===.5?'Clean inside refrigerator only if condition requires it':'Clean inside refrigerator','20–35 min','Selected Add-ons','addon'));
    if(num('oven')>0) addons.push(task('Clean inside oven','30–60 min','Selected Add-ons','addon'));
    const windows=num('windows'); if(windows) addons.push(task(`Clean ${windows} interior window${windows===1?'':'s'}`,`${Math.max(5,Math.round(windows*5))} min est.`,'Selected Add-ons','addon'));
    const blinds=num('blinds'); if(blinds) addons.push(task(`Wet-wipe ${blinds} blind${blinds===1?'':'s'}`,`${Math.max(10,Math.round(blinds*7))} min est.`,'Selected Add-ons','addon'));
    if(num('garage')>0) addons.push(task('Complete selected garage cleaning','30–60 min','Selected Add-ons','addon'));
    const carpet=num('carpetSqft'); if(carpet) addons.push(task(`Carpet cleaning — ${carpet.toLocaleString()} sqft: vacuum, pretreat, extract and final check`,'Per area','Selected Add-ons','addon'));
    const pressure=num('pressureSqft'); if(pressure) addons.push(task(`Pressure washing — ${pressure.toLocaleString()} sqft: pretreat as needed, wash and final rinse`,'Per area','Selected Add-ons','addon'));
    if(num('trash')>0) addons.push(task('Complete selected trash removal','As needed','Selected Add-ons','addon'));
    return tasks.concat(addons);
  }

  function taskRows(tasks){
    let html='', lastGroup='', order=0;
    tasks.forEach(t=>{
      if(t.group!==lastGroup){html+=`<tr class="group"><td colspan="5">${t.group}</td></tr>`;lastGroup=t.group;}
      order++;
      html+=`<tr class="${t.cls||''}"><td class="order">${order}</td><td>${t.name}</td><td class="target">${t.target}</td><td class="assign"></td><td class="done"><span class="crew-check-square"></span></td></tr>`;
    });
    return html;
  }

  function ensureCrewView(){
    if($('crewChecklistView')) return;
    const view=document.createElement('div');
    view.id='crewChecklistView';
    view.className='view';
    view.innerHTML=`
      <div class="no-print actions" style="max-width:960px;margin:0 auto 12px"><button class="btn secondary" id="crewBackBtn">← Back</button><button class="btn primary" id="crewPrintBtn">Print / Save PDF</button></div>
      <section class="doc crew-doc">
        <div class="doc-head"><img class="doc-logo" src="/static/cws-logo.svg" alt="Crystal Works Solutions"><div class="crew-title"><h1>PROPERTY TURNOVER CREW WORK ORDER</h1><div>Internal field checklist • Complete from top to bottom unless crew leader reassigns sequence</div></div><div id="cwDate"></div></div>
        <table class="crew-meta"><tr><td><strong>Property:</strong> <span id="cwAddress"></span></td><td><strong>Unit / ID:</strong> <span id="cwUnit"></span></td><td><strong>Service:</strong> <span id="cwService"></span></td></tr><tr><td><strong>Crew Leader:</strong> ____________________</td><td><strong>Crew Members:</strong> ____________________</td><td><strong>Condition:</strong> <span id="cwCondition"></span></td></tr><tr><td><strong>Estimated Labor:</strong> <span id="cwLabor"></span></td><td><strong>Recommended Crew:</strong> <span id="cwCrew"></span></td><td><strong>Completion Date:</strong> <span id="cwCompletion"></span></td></tr></table>
        <div class="crew-banner">Consistency Standard: complete the assigned scope, report exceptions, and perform a final walkthrough before leaving.</div>
        <table class="crew-table"><thead><tr><th class="order">#</th><th>Area / Task</th><th class="target">Target</th><th class="assign">Assigned To</th><th class="done">Done</th></tr></thead><tbody id="cwTasks"></tbody></table>
        <div class="crew-footer-grid"><div class="crew-box"><h3>Crew Notes / Property Issues</h3><div id="cwSpecialNotes"></div><div class="crew-lines">____________________________________________________________________<br>____________________________________________________________________<br>____________________________________________________________________</div></div><div class="crew-box"><h3>Completion</h3><div>Start time: __________ &nbsp; Finish time: __________</div><div style="margin-top:6px">Touch-up required: □ Yes &nbsp; □ No</div><div style="margin-top:6px">After photos completed: □ Yes</div><div class="crew-sign"><div>Crew Leader</div><div>Supervisor / QC</div></div></div></div>
      </section>`;
    document.querySelector('main.page')?.appendChild(view);
    $('crewBackBtn').onclick=()=>showEstimator();
    $('crewPrintBtn').onclick=()=>window.printCurrent?window.printCurrent('crewChecklistView'):window.print();
  }

  function showEstimator(){
    document.querySelectorAll('.view').forEach(v=>v.classList.remove('active','print-active'));
    $('estimatorView')?.classList.add('active');
    window.scrollTo(0,0);
  }

  function openCrewWorkOrder(){
    ensureCrewView();
    $('cwDate').textContent=new Date().toLocaleDateString();
    $('cwAddress').textContent=text('address')||'—';
    $('cwUnit').textContent=text('unit')||'—';
    $('cwService').textContent=selected('service')||'Property Turnover';
    $('cwCondition').textContent=selected('condition')||'Normal';
    $('cwLabor').textContent=$('labor')?.textContent||'—';
    $('cwCrew').textContent=$('crew')?.textContent||'—';
    $('cwCompletion').textContent=text('completionDate')||'____________';
    $('cwTasks').innerHTML=taskRows(buildTasks());
    const notes=text('specialNotes');
    $('cwSpecialNotes').innerHTML=notes?`<strong>Estimator notes:</strong> ${notes}`:'';
    document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));
    $('crewChecklistView').classList.add('active');
    window.scrollTo(0,0);
  }

  function init(){
    ensureCrewView();
    const btn=$('workOrderBtn');
    if(btn){btn.textContent='Crew Work Order';btn.onclick=openCrewWorkOrder;}
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>setTimeout(init,1));
  else setTimeout(init,1);
})();
