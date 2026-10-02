/* ============================================================
   ScanID — page Présentation
   Le film de l'application, le fichier colonne par colonne,
   le traitement par lot
   ============================================================ */

/* ---------- L'application en film ---------- */
(function(){
  var film = $("#film"); if (!film) return;
  var view = $("#film-view"), stage = $("#film-stage"), app = $("#app"), cursor = $("#film-cursor"), file = $("#film-file"), xl = $("#film-xl");
  var dest = $("#app-dest"), destV = $(".val", dest), drop = $("#app-drop"), dropT = $("#app-drop-t"), dropS = $("#app-drop-s"), go = $("#app-go");
  var proc = $("#app-proc"), cred = $("#app-cred"), credPill = $("#app-cred-pill"), pages = $("#app-pages"), rowsEl = $("#app-rows"), seg = $("#app-seg"), xlsx = $("#app-xlsx");
  var steps = $$("#film-steps li"), playBtn = $("#film-play");
  var k = 1, run = 0, paused = false, visible = false, started = false, userPaused = false;
  var GR = LIB.GROUPE, START = 20, N = GR.length;
  $("#film-xl-t").innerHTML = LIB.tableHTML(GR);
  function fit(){ k = view.clientWidth / 1100; stage.style.transform = "scale(" + k + ")"; view.style.height = (700 * k) + "px"; }
  fit(); w.addEventListener("resize", fit);
  function at(el){ var r = el.getBoundingClientRect(), s = stage.getBoundingClientRect(); return { x: (r.left - s.left + r.width / 2) / k, y: (r.top - s.top + r.height / 2) / k }; }
  function sleep(ms, tk){
    return new Promise(function(res, rej){
      var left = ms, last = performance.now();
      function step(){ if (tk !== run){ rej(0); return; } var now = performance.now(); if (!paused) left -= now - last; last = now; if (left <= 0) res(); else setTimeout(step, 40); }
      setTimeout(step, 40);
    });
  }
  function move(p, dur, tk){ cursor.style.transitionDuration = dur + "ms"; cursor.style.transform = "translate(" + p.x + "px," + p.y + "px)"; return sleep(dur + 60, tk); }
  function click(el){ cursor.classList.remove("click"); void cursor.offsetWidth; cursor.classList.add("click"); if (el){ el.classList.add("press"); setTimeout(function(){ el.classList.remove("press"); }, 160); } }
  function setStep(i){ steps.forEach(function(s, j){ s.classList.toggle("on", j === i); s.classList.toggle("done", j < i); }); }
  function filter(t){
    $$("span", seg).forEach(function(s){ s.classList.toggle("on", s.getAttribute("data-t") === t); });
    $$("tr[data-type]", rowsEl).forEach(function(tr){ tr.classList.toggle("hide", !!t && tr.getAttribute("data-type") !== t); });
  }
  function fillRows(anim){
    rowsEl.innerHTML = GR.map(function(r){
      return '<tr data-type="' + r.type + '"' + (anim ? ' class="in"' : "") + '><td><span class="cb"></span></td><td>' + esc(r.nom) + "</td><td>" + esc(r.prenom) + "</td><td>" + r.sexe + "</td><td>" + r.naissance + "</td><td>" + r.expiration + "</td><td>" + esc(r.nat) + "</td><td>" + r.num + "</td><td>" + r.type + "</td></tr>";
    }).join("");
    if (anim) $$("tr", rowsEl).forEach(function(tr, i){ $$("td", tr).forEach(function(td){ td.style.animationDelay = (i * 80) + "ms"; }); });
  }
  function reset(){
    app.style.transition = "none"; app.style.transform = "translateY(0)"; void app.offsetWidth; app.style.transition = "";
    destV.textContent = ""; dest.classList.remove("focus");
    drop.classList.remove("hot"); dropT.textContent = "Cliquez ou glissez vos fichiers ici"; dropS.textContent = "PNG, JPG, HEIC ou PDF jusqu’à 10 Mo";
    go.classList.remove("ready"); proc.innerHTML = "<span>Aucun document récent.</span>";
    cred.textContent = String(START); pages.textContent = "0";
    rowsEl.innerHTML = '<tr class="empty"><td colspan="9">Aucune donnée trouvée.</td></tr>';
    filter(""); xl.classList.remove("on");
    file.style.transition = "none"; file.style.opacity = "0"; file.style.transform = "translate(1120px,380px)"; void file.offsetWidth; file.style.transition = "";
    cursor.style.transitionDuration = "0ms"; cursor.style.transform = "translate(900px,640px)"; cursor.style.opacity = "";
    setStep(-1);
  }
  function finalState(){
    reset(); destV.textContent = "Séminaire Lisbonne"; cred.textContent = String(START - N); pages.textContent = String(N);
    proc.innerHTML = '<div class="app__job"><span>dossier-lisbonne.pdf</span><span class="bar"><i style="width:100%"></i></span><span class="st">' + N + " / " + N + " · terminé</span></div>";
    app.style.transform = "translateY(-470px)"; fillRows(false); cursor.style.opacity = "0";
    steps.forEach(function(s){ s.classList.add("done"); });
  }
  async function play(tk){
    try {
      reset(); await sleep(500, tk);
      setStep(0);
      await move(at(dest), 800, tk); click(dest); dest.classList.add("focus");
      var txt = "Séminaire Lisbonne";
      for (var i = 1; i <= txt.length; i++){ destV.textContent = txt.slice(0, i); await sleep(55, tk); }
      await sleep(350, tk); dest.classList.remove("focus");
      setStep(1);
      file.style.opacity = "1";
      await move({ x: 1040, y: 392 }, 750, tk);
      var dp = at(drop); drop.classList.add("hot");
      file.style.transform = "translate(" + (dp.x - 90) + "px," + (dp.y - 20) + "px)";
      await move({ x: dp.x + 10, y: dp.y }, 820, tk);
      file.style.opacity = "0"; drop.classList.remove("hot");
      dropT.textContent = "Fichier prêt : dossier-lisbonne.pdf"; dropS.textContent = "PDF · " + N + " pages"; go.classList.add("ready");
      await sleep(450, tk);
      setStep(2);
      await move(at(go), 700, tk); click(go);
      proc.innerHTML = '<div class="app__job"><span>dossier-lisbonne.pdf</span><span class="bar"><i></i></span><span class="st">0 / ' + N + "</span></div>";
      var bar = $(".bar i", proc), st = $(".st", proc);
      for (var n = 1; n <= N; n++){
        await sleep(190, tk);
        bar.style.width = (n / N * 100) + "%"; st.textContent = n + " / " + N; cred.textContent = String(START - n); pages.textContent = String(n);
        credPill.classList.add("tick"); setTimeout(function(){ credPill.classList.remove("tick"); }, 120);
      }
      st.textContent = N + " / " + N + " · terminé";
      dropT.textContent = "Cliquez ou glissez vos fichiers ici"; dropS.textContent = "PNG, JPG, HEIC ou PDF jusqu’à 10 Mo"; go.classList.remove("ready");
      await sleep(400, tk);
      app.style.transform = "translateY(-470px)";
      await move({ x: 980, y: 620 }, 900, tk);
      fillRows(true);
      await sleep(1500, tk);
      setStep(3);
      var pi = $('span[data-t="PI"]', seg);
      await move(at(pi), 800, tk); click(pi); filter("PI");
      await sleep(1600, tk);
      var all = $('span[data-t=""]', seg);
      await move(at(all), 600, tk); click(all); filter("");
      await sleep(800, tk);
      setStep(4);
      await move(at(xlsx), 850, tk); click(xlsx);
      await sleep(250, tk); xl.classList.add("on");
      await move({ x: 1020, y: 250 }, 900, tk);
      await sleep(3600, tk);
      if (tk === run) play(tk);
    } catch(e) { /* nouvelle lecture ou arrêt */ }
  }
  function start(){ run++; started = true; paused = userPaused || !visible; play(run); }
  playBtn.addEventListener("click", function(){
    if (!started){ userPaused = false; playBtn.textContent = "Pause"; start(); return; }
    userPaused = !userPaused; paused = userPaused || !visible; playBtn.textContent = userPaused ? "Lecture" : "Pause";
  });
  $("#film-replay").addEventListener("click", function(){ userPaused = false; playBtn.textContent = "Pause"; start(); });
  if (reduce){ finalState(); playBtn.textContent = "Lecture"; return; }
  reset();
  watchVisible(film, function(v){ visible = v; if (v && !started) start(); paused = userPaused || !visible; }, "-10% 0px");
})();

/* ---------- Le fichier, colonne par colonne ---------- */
(function(){
  var tw = $("#sheet-tw"); if (!tw) return;
  var INFO = {
    nom: ["A", "Nom de famille", "Tel qu’imprimé sur le document, en capitales."],
    prenom: ["B", "Prénom", "Les prénoms, en capitales."],
    sexe: ["C", "Sexe", "F ou M, tel qu’indiqué sur le document."],
    naissance: ["D", "Date de naissance", "Au format JJ/MM/AAAA, prêt à coller dans vos formulaires et vos listes de passagers."],
    expiration: ["E", "Date d’expiration", "Même format. Pratique pour repérer, d’un coup d’œil, un document qui expire avant le retour."],
    nat: ["F", "Nationalité", "En toutes lettres."],
    num: ["G", "Numéro du document", "Le numéro du passeport ou de la carte d’identité."],
    type: ["H", "Type", "PP pour un passeport, PI pour une carte d’identité. Dans l’application, un filtre n’affiche qu’un type de document."],
    dest: ["I", "Destination", "Le nom du dossier saisi à l’import. Il sert à trier vos groupes et à n’exporter que l’un d’eux."],
    score: ["J", "Score de confiance", "Entre 0 et 1. Proche de 1, la lecture est sûre ; plus bas, relisez la ligne : la photo était peut-être floue ou abîmée. Ici, la ligne de Manon Simon est à relire."]
  };
  var COLS = LIB.COLS, GR = LIB.GROUPE, type = "";
  var h = '<table class="xl xl--sheet"><caption class="sr">Exemple de fichier ScanID : douze voyageurs fictifs, une ligne par document</caption><thead><tr class="lt"><th class="xl__n" aria-hidden="true"></th>' + COLS.map(function(c){ return '<th aria-hidden="true">' + INFO[c.k][0] + "</th>"; }).join("") + '</tr><tr><th class="xl__n" aria-hidden="true">1</th>' +
    COLS.map(function(c){ return '<th scope="col" data-col="' + c.k + '"><button type="button" data-col="' + c.k + '" aria-pressed="false">' + esc(c.t) + "</button></th>"; }).join("") + "</tr></thead><tbody>";
  GR.forEach(function(r, i){
    h += '<tr data-type="' + r.type + '"><td class="xl__n" aria-hidden="true">' + (i + 2) + "</td>" + COLS.map(function(c){
      var v = r[c.k];
      if (c.k === "score"){ var s = parseFloat(String(v).replace(",", ".")); return '<td data-col="score" class="' + (s < .9 ? "low" : "") + '"><span class="sc"><i style="--s:' + s + '"></i>' + v + "</span></td>"; }
      return '<td data-col="' + c.k + '">' + esc(v) + "</td>";
    }).join("") + "</tr>";
  });
  tw.innerHTML = h + "</tbody></table>";
  function show(col){
    var I = INFO[col];
    $$("td[data-col], th[data-col]", tw).forEach(function(el){ el.classList.toggle("hi", el.getAttribute("data-col") === col); });
    $$("button[data-col]", tw).forEach(function(b){ b.setAttribute("aria-pressed", String(b.getAttribute("data-col") === col)); });
    var ex = GR[col === "score" ? 7 : 0][col];
    $("#sheet-side").innerHTML = '<p class="label">Colonne ' + I[0] + '</p><p class="h4">' + esc(I[1]) + '</p><p class="small">' + esc(I[2]) + '</p><span class="ex">' + esc(ex) + "</span>";
  }
  tw.addEventListener("click", function(e){ var b = e.target.closest("button[data-col]"); if (b) show(b.getAttribute("data-col")); });
  segToggle("#sheet-seg", function(v){ type = v; $$("tbody tr", tw).forEach(function(tr){ tr.classList.toggle("hide", !!v && tr.getAttribute("data-type") !== v); }); });
  var dl = $("#sheet-dl");
  if (dl) dl.addEventListener("click", function(){
    var rows = GR.filter(function(r){ return !type || r.type === type; });
    download("scanid-exemple-seminaire-lisbonne.csv", LIB.csv(rows));
  });
  show("score");
})();

/* ---------- Un PDF, tout un dossier ---------- */
(function(){
  var b = $("#batch"); if (!b) return;
  var pagesEl = $("#batch-pages"), listEl = $("#batch-list"), sum = $("#batch-sum"), GR = LIB.GROUPE, timers = [];
  pagesEl.innerHTML = GR.map(function(r, i){ return '<span class="pg' + (r.type === "PI" ? " pi" : "") + '" style="transition-delay:' + (i * 55) + 'ms"><i></i><b></b><em></em></span>'; }).join("");
  listEl.innerHTML = GR.map(function(r, i){ return "<div><span>" + pad(i + 1) + "</span><span>" + esc(r.nom) + " " + esc(r.prenom) + "</span><span>" + r.type + "</span></div>"; }).join("");
  var pgs = $$(".pg", pagesEl), lines = $$("div", listEl);
  function clear(){ timers.forEach(clearTimeout); timers = []; b.classList.remove("fan"); pgs.forEach(function(p){ p.classList.remove("scan", "ok"); }); lines.forEach(function(l){ l.classList.remove("in"); }); sum.classList.remove("in"); }
  function T(fn, ms){ timers.push(setTimeout(fn, ms)); }
  function play(){
    clear();
    if (reduce){ b.classList.add("fan"); pgs.forEach(function(p){ p.classList.add("ok"); }); lines.forEach(function(l){ l.classList.add("in"); }); sum.classList.add("in"); return; }
    T(function(){ b.classList.add("fan"); }, 250);
    pgs.forEach(function(p, i){
      T(function(){ p.classList.add("scan"); }, 1400 + i * 280);
      T(function(){ p.classList.add("ok"); lines[i].classList.add("in"); }, 1400 + i * 280 + 420);
    });
    T(function(){ sum.classList.add("in"); }, 1400 + pgs.length * 280 + 600);
  }
  onceVisible(b, play, .35);
  var rp = $("#batch-replay"); if (rp) rp.addEventListener("click", play);
})();
