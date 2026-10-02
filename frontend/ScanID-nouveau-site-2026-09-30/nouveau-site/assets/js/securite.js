/* ============================================================
   ScanID — page Sécurité
   Le trajet du document, qui fait quoi
   ============================================================ */

/* ---------- Le document ne fait que passer ---------- */
(function(){
  var flow = $("#flow"); if (!flow) return;
  var card = $("#flow-card"), beam = $("#flow-beam"), row = $("#flow-row"), gone = $("#flow-gone"), cv = $("#flow-cv"), ctx = cv.getContext("2d");
  var slots = $$(".flow__slot", flow), stack = $$("#flow-stack i"), timers = [], visible = false, running = false, loopN = 0, parts = [], raf = 0;
  card.innerHTML = LIB.passport({ mini: true });
  function rel(el){ var r = el.getBoundingClientRect(), f = flow.getBoundingClientRect(); return { x: r.left - f.left, y: r.top - f.top, w: r.width, h: r.height }; }
  function center(i){ var s = rel(slots[i]); return { x: s.x + s.w / 2, y: s.y + s.h / 2 }; }
  function place(el, x, y, dur){ el.style.transition = dur ? "transform " + dur + "ms cubic-bezier(.65,0,.35,1), opacity .4s" : "none"; el.style.transform = "translate(" + x.toFixed(1) + "px," + y.toFixed(1) + "px)"; }
  function sizeCv(){ var f = flow.getBoundingClientRect(), dpr = Math.min(2, w.devicePixelRatio || 1); cv.width = f.width * dpr; cv.height = f.height * dpr; cv.style.width = f.width + "px"; cv.style.height = f.height + "px"; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
  function T(fn, ms){ timers.push(setTimeout(fn, ms)); }
  function dust(x, y, wd, ht){
    var cols = ["#6B2033", "#18212F", "#17B2DA", "#9AA3B0", "#E8EEF1"];
    for (var i = 0; i < 190; i++) parts.push({ x: x + Math.random() * wd, y: y + Math.random() * ht, vx: -.3 + Math.random() * 1.6, vy: -1.4 + Math.random() * 1.1, r: 1 + Math.random() * 2.2, life: 0, max: 50 + Math.random() * 45, c: cols[i % cols.length] });
    if (!raf) raf = requestAnimationFrame(tickDust);
  }
  function tickDust(){
    var f = flow.getBoundingClientRect(); ctx.clearRect(0, 0, f.width, f.height);
    parts = parts.filter(function(p){ return p.life < p.max; });
    parts.forEach(function(p){ p.life++; p.x += p.vx; p.y += p.vy; p.vy -= .01; ctx.globalAlpha = Math.max(0, 1 - p.life / p.max); ctx.fillStyle = p.c; ctx.fillRect(p.x, p.y, p.r, p.r); });
    ctx.globalAlpha = 1;
    raf = parts.length ? requestAnimationFrame(tickDust) : 0;
  }
  function cycle(){
    if (!visible){ running = false; return; }
    running = true;
    var cw = card.offsetWidth, ch = card.offsetHeight, c0 = center(0), c1 = center(1);
    gone.classList.remove("on");
    card.style.opacity = "0"; place(card, c0.x - cw / 2, c0.y - ch / 2, 0);
    row.style.opacity = "0";
    if (loopN % 4 === 0) stack.forEach(function(s){ s.classList.remove("new"); });
    T(function(){ card.style.opacity = "1"; }, 60);
    T(function(){ place(card, c1.x - cw / 2, c1.y - ch / 2, 950); }, 700);
    T(function(){
      beam.style.width = (cw + 20) + "px"; beam.style.transition = "none";
      beam.style.transform = "translate(" + (c1.x - cw / 2 - 10) + "px," + (c1.y - ch / 2) + "px)"; beam.style.opacity = "1";
      requestAnimationFrame(function(){ beam.style.transition = "transform .8s cubic-bezier(.65,0,.35,1)"; beam.style.transform = "translate(" + (c1.x - cw / 2 - 10) + "px," + (c1.y + ch / 2) + "px)"; });
    }, 1750);
    T(function(){
      beam.style.opacity = "0";
      var rw = row.offsetWidth, rh = row.offsetHeight;
      place(row, c1.x - rw / 2, c1.y - rh / 2, 0); row.style.opacity = "1";
      var r = rel(card); card.style.opacity = "0"; dust(r.x, r.y, r.w, r.h);
      gone.classList.add("on");
      var target = stack[loopN % 4], tr = rel(target);
      T(function(){ place(row, tr.x + tr.w / 2 - rw / 2, tr.y + tr.h / 2 - rh / 2, 950); }, 80);
      T(function(){ row.style.opacity = "0"; target.classList.add("new"); }, 1100);
    }, 2650);
    T(function(){ loopN++; cycle(); }, 5600);
  }
  sizeCv();
  w.addEventListener("resize", sizeCv);
  if (reduce){ stack.forEach(function(s){ s.classList.add("new"); }); gone.classList.add("on"); return; }
  watchVisible(flow, function(v){
    visible = v;
    if (v && !running){ timers.forEach(clearTimeout); timers = []; cycle(); }
    if (!v){ timers.forEach(clearTimeout); timers = []; running = false; }
  }, "-10% 0px");
})();

/* ---------- Qui fait quoi ---------- */
(function(){
  var map = $("#roles-map"); if (!map) return;
  var INFO = {
    voy: ["Vos voyageurs", "Personnes concernées", ["Leurs documents sont traités pour le compte de votre agence.", "Ils exercent leurs droits auprès de votre agence ; ScanID vous assiste.", "Ils peuvent saisir la CNIL."]],
    agence: ["Votre agence", "Responsable de traitement", ["Vous décidez pourquoi et comment les données de vos voyageurs sont utilisées.", "Un accord de sous-traitance (DPA) vous est fourni.", "Vous gardez la main sur vos fichiers de résultats : vous les supprimez quand vous voulez."]],
    scanid: ["ScanID", "Sous-traitant, article 28 du RGPD", ["Traite les documents pour votre compte, sur vos seules instructions.", "Ne conserve jamais les pièces d’identité : lues en mémoire, puis détruites.", "Aucune revente, aucun usage caché, aucun entraînement d’IA."]],
    google: ["Google Cloud, API Vision", "Lecture optique · région UE", ["Lit les images en mémoire, sans stockage.", "Traitement en région Union européenne.", "S’engage à ne pas utiliser les contenus soumis pour entraîner ses modèles."]],
    ionos: ["IONOS", "Hébergement · UE", ["Héberge le site, l’application et les fichiers de résultats.", "Traitement dans l’Union européenne ou l’Espace économique européen.", "Les fichiers de résultats sont chiffrés au repos."]],
    stripe: ["Stripe", "Paiement", ["Encaisse le paiement des packs.", "ScanID n’a jamais accès à vos données bancaires complètes.", "Aucune donnée de passeport."]],
    forms: ["Formspree", "Formulaires du site · États-Unis", ["Reçoit seulement ce que vous tapez dans les formulaires du site (essai, contact).", "Transfert encadré par les clauses contractuelles types de la Commission européenne.", "Aucune donnée de passeport."]]
  };
  var EDGES = [["voy", "agence", 1], ["agence", "scanid", 1], ["scanid", "google", 1], ["scanid", "ionos", 1], ["scanid", "stripe", 0], ["agence", "forms", 0]];
  var svg = $("#roles-lines"), nodes = {};
  $$(".node", map).forEach(function(n){ nodes[n.getAttribute("data-n")] = n; });
  function box(n){ var r = n.getBoundingClientRect(), m = map.getBoundingClientRect(); return { x: r.left - m.left, y: r.top - m.top, w: r.width, h: r.height }; }
  function draw(){
    var m = map.getBoundingClientRect(); svg.setAttribute("viewBox", "0 0 " + m.width + " " + m.height); svg.setAttribute("width", m.width); svg.setAttribute("height", m.height);
    svg.innerHTML = EDGES.map(function(e){
      var a = box(nodes[e[0]]), b = box(nodes[e[1]]), dx = (b.x + b.w / 2) - (a.x + a.w / 2), dy = (b.y + b.h / 2) - (a.y + a.h / 2), p;
      if (Math.abs(dx) > Math.abs(dy)){
        var x1 = dx > 0 ? a.x + a.w : a.x, x2 = dx > 0 ? b.x : b.x + b.w, y1 = a.y + a.h / 2, y2 = b.y + b.h / 2, mx = (x1 + x2) / 2;
        p = "M" + x1 + " " + y1 + "C" + mx + " " + y1 + " " + mx + " " + y2 + " " + x2 + " " + y2;
      } else {
        var X1 = a.x + a.w / 2, X2 = b.x + b.w / 2, Y1 = dy > 0 ? a.y + a.h : a.y, Y2 = dy > 0 ? b.y : b.y + b.h, my = (Y1 + Y2) / 2;
        p = "M" + X1 + " " + Y1 + "C" + X1 + " " + my + " " + X2 + " " + my + " " + X2 + " " + Y2;
      }
      return '<path class="' + (e[2] ? "pp-data" : "no-data") + '" d="' + p + '"/>';
    }).join("");
  }
  function show(k){
    var I = INFO[k];
    $$(".node", map).forEach(function(n){ n.setAttribute("aria-pressed", String(n.getAttribute("data-n") === k)); });
    $("#roles-side").innerHTML = '<p class="label">' + esc(I[1]) + '</p><p class="h4">' + esc(I[0]) + "</p><ul>" + I[2].map(function(s){ return "<li>" + esc(s) + "</li>"; }).join("") + "</ul>";
  }
  map.addEventListener("click", function(e){ var n = e.target.closest(".node"); if (n) show(n.getAttribute("data-n")); });
  draw(); show("scanid");
  w.addEventListener("resize", function(){ clearTimeout(draw._t); draw._t = setTimeout(draw, 100); });
  onceVisible(map, draw, .1);
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(draw);
})();
