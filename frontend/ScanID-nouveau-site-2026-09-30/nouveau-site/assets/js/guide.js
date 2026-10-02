/* ============================================================
   ScanID — guide d'utilisation : tableau d'exemple, traitement
   ============================================================ */
(function(){
  var t = $("#g-table");
  var keep = ["nom", "prenom", "sexe", "naissance", "expiration", "num", "type", "score"];
  if (t) t.innerHTML = LIB.tableHTML(LIB.GROUPE.slice(4, 9), { cols: LIB.COLS.filter(function(c){ return keep.indexOf(c.k) >= 0; }) });
  var job = $("#g-job");
  if (job && !reduce) onceVisible(job, function(){ job.classList.add("play"); }, .5);
})();
