/* ============================================================
   ScanID — page Tarifs
   Le bon pack en un geste : le volume annuel donne la formule
   la moins chère (packs combinés et documents à la carte)
   ============================================================ */
(function(){
  var rg = $("#finder-range"); if (!rg) return;
  var MIN = 10, MAX = 12000, LN = Math.log(MAX) - Math.log(MIN);
  var PACKS = [{ k: "p4", size: 5000, price: 2950, n: "Pack 5 000" }, { k: "p3", size: 3000, price: 1890, n: "Pack 3 000" }, { k: "p2", size: 1000, price: 690, n: "Pack 1 000" }, { k: "p1", size: 100, price: 99, n: "Pack 100" }];
  var UNIT = 1.5;
  function posOf(n){ return 1000 * (Math.log(n) - Math.log(MIN)) / LN; }
  function vol(pos){
    var n = Math.exp(Math.log(MIN) + pos / 1000 * LN);
    if (n < 100) return Math.max(MIN, Math.round(n / 5) * 5);
    if (n < 1000) return Math.round(n / 10) * 10;
    return Math.round(n / 50) * 50;
  }
  function best(n){
    var b = null;
    for (var a = 0; a <= 2; a++) for (var t = 0; t <= 3; t++) for (var o = 0; o <= 9; o++) for (var h = 0; h <= 9; h++){
      var cred = a * 5000 + t * 3000 + o * 1000 + h * 100, rest = Math.max(0, n - cred);
      var cost = a * 2950 + t * 1890 + o * 690 + h * 99 + rest * UNIT, items = a + t + o + h + (rest ? 1 : 0);
      if (!b || cost < b.cost - .001 || (Math.abs(cost - b.cost) < .001 && items < b.items)) b = { cost: cost, q: [a, t, o, h], rest: rest, items: items, cred: cred };
    }
    return b;
  }
  /* repères sous le curseur */
  var ticks = $("#finder-ticks");
  if (ticks) ticks.innerHTML = [10, 100, 1000, 10000].map(function(v){ return '<span style="left:' + (posOf(v) / 10).toFixed(2) + '%">' + FMT.format(v) + "</span>"; }).join("");
  var cards = $$(".offers .pk[data-k]");
  function render(){
    var n = vol(+rg.value), on = {};
    rg.style.setProperty("--p", (+rg.value / 10) + "%");
    $("#finder-n").textContent = FMT.format(n);
    $("#finder-m").textContent = "soit environ " + FMT.format(Math.max(1, Math.round(n / 12))) + " par mois";
    rg.setAttribute("aria-valuetext", FMT.format(n) + " documents par an");
    if (n >= 10000){
      $("#finder-best").textContent = "Un volume sur mesure";
      $("#finder-detail").textContent = "Au-delà de 10 000 documents par an, le prix se fixe ensemble, dès 0,49 € HT le document.";
      $("#finder-price").innerHTML = "<b>Sur devis</b><span>dès 0,49 € HT le document</span>";
      on.p5 = 1;
    } else {
      var b = best(n), parts = [];
      PACKS.forEach(function(p, i){ var q = b.q[i]; if (q){ parts.push(q + " " + (q > 1 ? p.n.replace("Pack", "Packs") : p.n)); on[p.k] = 1; } });
      if (b.rest){ parts.push(FMT.format(b.rest) + " document" + (b.rest > 1 ? "s" : "") + " à la carte"); on.c = 1; }
      $("#finder-best").textContent = nb(parts.join(" + "));
      var credits = b.cred + b.rest;
      $("#finder-detail").textContent = credits > n ? FMT.format(credits) + " crédits pour " + FMT.format(n) + " documents : le surplus reste utilisable pendant 12 mois." : FMT.format(n) + " crédits pour " + FMT.format(n) + " documents.";
      $("#finder-price").innerHTML = "<b>" + euros(b.cost) + " HT</b><span>soit " + euros(b.cost / n, true) + " HT le document</span>";
    }
    cards.forEach(function(c){ c.classList.toggle("on", !!on[c.getAttribute("data-k")]); });
  }
  rg.addEventListener("input", render);
  $$(".finder [data-step]").forEach(function(btn){
    btn.addEventListener("click", function(){
      var n = vol(+rg.value), dir = +btn.getAttribute("data-step"), stepN = n < 100 ? 10 : n < 1000 ? 50 : 500;
      var target = clamp(n + dir * stepN, MIN, MAX);
      var p = Math.round(posOf(target));
      if (vol(p) === n) p = clamp(+rg.value + dir, 0, 1000);
      rg.value = p; render();
    });
  });
  rg.value = Math.round(posOf(1200));
  render();
})();
