(()=>{
  const $=id=>document.getElementById(id);
  let activePrintView=null;

  const style=document.createElement('style');
  style.textContent=`
    .cws-monthly-toggle{margin-top:12px;width:100%}
    .cws-monthly-details{margin-top:12px}
    .cws-monthly-details.hidden{display:none!important}
    @media print{
      html,body{background:#fff!important;min-height:0!important;height:auto!important;overflow:visible!important}
      body.cws-printing main.page{padding:0!important;max-width:none!important}
      body.cws-printing .view.print-active{display:block!important;visibility:visible!important;position:static!important;opacity:1!important}
      body.cws-printing .view.print-active .doc{display:block!important;visibility:visible!important;opacity:1!important;position:static!important;min-height:1px!important}
      body.cws-printing .view:not(.print-active){display:none!important}
    }
  `;
  document.head.appendChild(style);

  function preparePrint(id){
    const view=$(id);
    if(!view) return false;
    activePrintView=view;
    document.querySelectorAll('.view').forEach(v=>v.classList.remove('print-active'));
    view.classList.add('print-active');
    document.body.classList.add('cws-printing');
    // Force layout before Safari creates its print snapshot.
    void view.offsetHeight;
    return true;
  }

  function cleanupPrint(){
    document.body.classList.remove('cws-printing');
    if(activePrintView) activePrintView.classList.remove('print-active');
    activePrintView=null;
  }

  function printView(id){
    if(!preparePrint(id)) return;
    window.print();
    // Do not use a short timeout here. iOS Safari may build the preview after
    // window.print() returns, which was causing the page to turn blank.
  }

  function installPrintFix(){
    window.printCurrent=printView;
    window.addEventListener('beforeprint',()=>{
      if(activePrintView){
        document.body.classList.add('cws-printing');
        activePrintView.classList.add('print-active');
      }
    });
    window.addEventListener('afterprint',cleanupPrint);

    const summaryBtn=$('summaryPrintBtn');
    if(summaryBtn) summaryBtn.onclick=()=>printView('customerSummaryView');
  }

  function installMonthlyBillingToggle(){
    const completion=$('completionDate');
    const billing=$('billingPeriod');
    const override=$('unitOverride');
    const add=$('addUnit');
    const open=$('openSummary');
    const list=$('unitList');
    if(!completion||!billing||!override||!add||!open||!list) return;

    const card=completion.closest('.card');
    if(!card||$('cwsMonthlyToggle')) return;

    const headTitle=card.querySelector('.head h2');
    if(headTitle) headTitle.textContent='Completion date & optional monthly billing';
    const chip=card.querySelector('.chip');
    if(chip) chip.textContent='5. Completion / Account Billing';

    const body=completion.closest('.body');
    const grid=completion.closest('.grid');
    if(!body||!grid) return;

    // Completion date remains available for every job.
    const billingField=billing.closest('.field');
    const overrideField=override.closest('.field');
    const completionField=completion.closest('.field');
    if(completionField){
      const simpleGrid=document.createElement('div');
      simpleGrid.className='grid';
      grid.parentNode.insertBefore(simpleGrid,grid);
      simpleGrid.appendChild(completionField);
    }

    const details=document.createElement('div');
    details.id='cwsMonthlyDetails';
    details.className='cws-monthly-details hidden';
    details.innerHTML='<div class="notice" style="margin-bottom:10px">Use this only when you are grouping multiple apartment units or realtor properties into one monthly service summary for the Square invoice.</div>';
    const detailsGrid=document.createElement('div');
    detailsGrid.className='grid';
    if(billingField) detailsGrid.appendChild(billingField);
    if(overrideField) detailsGrid.appendChild(overrideField);
    details.appendChild(detailsGrid);

    const actions=add.closest('.actions');
    if(actions) details.appendChild(actions);
    details.appendChild(list);

    grid.remove();

    const toggle=document.createElement('button');
    toggle.id='cwsMonthlyToggle';
    toggle.type='button';
    toggle.className='btn secondary cws-monthly-toggle';
    toggle.textContent='Open Monthly Billing / Multi-Unit';
    toggle.setAttribute('aria-expanded','false');
    toggle.onclick=()=>{
      const opening=details.classList.contains('hidden');
      details.classList.toggle('hidden',!opening);
      toggle.setAttribute('aria-expanded',String(opening));
      toggle.textContent=opening?'Hide Monthly Billing':'Open Monthly Billing / Multi-Unit';
    };
    body.appendChild(toggle);
    body.appendChild(details);
  }

  function init(){
    // The enhancement script also initializes on DOMContentLoaded; run one tick
    // later so its dynamically-created customer summary exists before patching.
    setTimeout(()=>{
      installPrintFix();
      installMonthlyBillingToggle();
    },0);
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
  else init();
})();
