(()=>{
  const style=document.createElement('style');
  style.textContent=`
    @media print{
      /* Crew work order: slightly more compact so normal jobs stay on one page. */
      #crewChecklistView .doc{font-size:9.8px!important;line-height:1.18!important}
      #crewChecklistView .doc-head{padding-bottom:6px!important;margin-bottom:7px!important;gap:7px!important}
      #crewChecklistView .doc-logo{width:54px!important;height:52px!important}
      #crewChecklistView .crew-title h1{font-size:17px!important}
      #crewChecklistView .crew-title div{font-size:8.5px!important}
      #crewChecklistView .crew-meta{margin:4px 0 6px!important}
      #crewChecklistView .crew-meta td{padding:3px 5px!important;font-size:8.8px!important}
      #crewChecklistView .crew-banner{padding:4px!important;margin-bottom:5px!important;font-size:8.8px!important}
      #crewChecklistView .crew-table th,#crewChecklistView .crew-table td{padding:3px 4px!important;font-size:8.6px!important;line-height:1.14!important}
      #crewChecklistView .crew-table .done{font-size:13px!important}
      #crewChecklistView .crew-check-square{width:11px!important;height:11px!important}
      #crewChecklistView .crew-footer-grid{gap:6px!important;margin-top:6px!important}
      #crewChecklistView .crew-box{min-height:56px!important;padding:5px!important}
      #crewChecklistView .crew-box h3{font-size:9px!important;margin-bottom:3px!important}
      #crewChecklistView .crew-lines{line-height:1.4!important}
      #crewChecklistView .crew-sign{gap:5px!important;margin-top:5px!important}

      /* Customer summary: use more of the page without making it oversized. */
      #customerSummaryView .doc{font-size:12.2px!important;line-height:1.34!important}
      #customerSummaryView .doc h1{font-size:25px!important}
      #customerSummaryView .doc h2{font-size:16px!important;margin:15px 0 8px!important}
      #customerSummaryView .doc h3{font-size:13.5px!important;margin-bottom:7px!important}
      #customerSummaryView .doc-logo{width:84px!important;height:82px!important}
      #customerSummaryView .doc-head{padding-bottom:12px!important;margin-bottom:14px!important;gap:14px!important}
      #customerSummaryView .doc-box{padding:12px!important;margin-top:10px!important}
      #customerSummaryView .cws-banner{gap:8px!important;margin:10px 0 14px!important}
      #customerSummaryView .cws-pill{padding:6px 9px!important;font-size:10.8px!important}
      #customerSummaryView .cws-summary-sections{gap:11px!important;margin-top:11px!important}
      #customerSummaryView .cws-summary-section{padding:12px!important}
      #customerSummaryView .cws-check{font-size:11.3px!important;margin:4px 0!important}
      #customerSummaryView .cws-doc-note{font-size:10.8px!important;line-height:1.3!important}
    }
  `;
  document.head.appendChild(style);
})();