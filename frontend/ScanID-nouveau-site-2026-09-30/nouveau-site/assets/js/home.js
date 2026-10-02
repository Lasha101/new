/* ============================================================
   Accueil : le passeport qui se lit, la loupe, le dépôt
   ============================================================ */

/* ---------- Le passeport qui se lit (une fois par visite) ---------- */
(function(){
  var root = $("#intro"); if (!root) return;
  var scene = $(".intro__scene", root), docEl = $(".intro__doc", root), beam = $(".intro__beam", root), sheet = $(".intro__sheet", root);
  var steps = $$(".intro__step", root), navs = $$(".intro__nav > div", root), countEl = $("#intro-count"), hint = $(".intro__hint", root);
  var S = LIB.SPEC, GR = LIB.GROUPE;
  docEl.innerHTML = LIB.passport({});
  var svg = $("svg", docEl);
  var NS = "http://www.w3.org/2000/svg", lits = [];
  $$(".pp-v, .pp-mrz", svg).forEach(function(t){
    var bb; try { bb = t.getBBox(); } catch(e) { return; }
    if (!bb || !bb.width) return;
    var g = d.createElementNS(NS, "g"), pad = 8;
    var r = d.createElementNS(NS, "rect");
    r.setAttribute("x", bb.x - pad); r.setAttribute("y", bb.y - pad / 2); r.setAttribute("width", bb.width + pad * 2); r.setAttribute("height", bb.height + pad); r.setAttribute("rx", 5); r.setAttribute("class", "pp-hl");
    var c = d.createElementNS(NS, "path"), x1 = bb.x - pad, y1 = bb.y - pad / 2, x2 = bb.x + bb.width + pad, y2 = bb.y + bb.height + pad / 2, k = 12;
    c.setAttribute("d", "M" + x1 + " " + (y1 + k) + "V" + y1 + "H" + (x1 + k) + "M" + (x2 - k) + " " + y1 + "H" + x2 + "V" + (y1 + k) + "M" + x2 + " " + (y2 - k) + "V" + y2 + "H" + (x2 - k) + "M" + (x1 + k) + " " + y2 + "H" + x1 + "V" + (y2 - k));
    c.setAttribute("class", "pp-cn");
    g.appendChild(r); g.appendChild(c);
    t.parentNode.insertBefore(g, t);
    lits.push({ t: t, g: g, y: bb.y + bb.height / 2, k: t.getAttribute("data-k"), bb: bb });
  });
  /* le tableau, dans l'ordre des colonnes du fichier */
  var COLS = [["nom", "Nom de famille"], ["prenom", "Prénom"], ["sexe", "Sexe"], ["naissance", "Né(e) le"], ["expiration", "Expire le"], ["nat", "Nationalité"], ["num", "N° du document"], ["type", "Type"], ["score", "Score"]];
  var html = '<div class="sh-top"><b>DOSSIER · SÉMINAIRE LISBONNE</b><span class="sh-dl">Télécharger Excel</span></div><div class="sh-body"><table class="xl"><thead><tr>' +
    COLS.map(function(c){ return '<th scope="col">' + c[1] + "</th>"; }).join("") + "</tr></thead><tbody>";
  GR.forEach(function(r, i){
    html += '<tr data-i="' + i + '">' + COLS.map(function(c){
      var v = r[c[0]];
      if (c[0] === "score"){ var s = parseFloat(v.replace(",", ".")); return '<td class="' + (s < .9 ? "low" : "") + '"><span class="v sc"><i style="--s:' + s + '"></i>' + v + "</span></td>"; }
      return '<td><span class="v">' + esc(v) + "</span></td>";
    }).join("") + "</tr>";
  });
  sheet.innerHTML = html + "</tbody></table></div>";
  var rows = $$("tbody tr", sheet), row1 = $$("td", rows[0]), dlEl = $(".sh-dl", sheet), sheetBody = $(".sh-body", sheet);
  /* les valeurs lues volent vers la première ligne */
  var FLY = [["nom", 0], ["prenom", 1], ["sexe", 2], ["naissance", 3], ["expiration", 4], ["nat", 5], ["num", 6]];
  var ghosts = FLY.map(function(f){
    var gEl = d.createElement("span"); gEl.className = "intro__ghost"; gEl.setAttribute("aria-hidden", "true"); gEl.textContent = S[f[0]]; scene.appendChild(gEl);
    var src = null; lits.forEach(function(l){ if (l.k === f[0]) src = l; });
    return { el: gEl, src: src, cell: row1[f[1]] };
  });
  var pile = $(".intro__pile", root), cards = [];
  for (var i = 1; i < GR.length; i++){ var cd = d.createElement("i"); pile.appendChild(cd); cards.push(cd); }

  var G = {}, W = 0, H = 0, docW = 0, cellPos = [];
  function measure(){
    var r = scene.getBoundingClientRect(); W = r.width; H = r.height;
    var mobile = W / H < 1;
    G = mobile ? { d0: { x: .02, y: .01, w: .96 }, d2: { x: 0, y: 0, w: .46 }, pile: { x: .54, y: .015, w: .28, dx: .012, dy: .008 } }
               : { d0: { x: .1, y: .02, w: .8 }, d2: { x: 0, y: 0, w: .33 }, pile: { x: .38, y: .02, w: .145, dx: .011, dy: .011 } };
    docW = G.d0.w * W;
    docEl.style.width = docW + "px";
    $$("i", pile).forEach(function(c){ c.style.width = (G.pile.w * W) + "px"; });
    var sr = sheet.getBoundingClientRect();
    cellPos = ghosts.map(function(g){ var cr = g.cell.getBoundingClientRect(); return { x: sheet.offsetLeft + (cr.left - sr.left) + cr.width / 2, y: sheet.offsetTop + (cr.top - sr.top) + cr.height / 2 }; });
  }
  var rowOn = [], litOn = [];
  function render(p){
    var s2 = G.d2.w / G.d0.w;
    var enter = easeOut(seg01(p, 0, .06)), straighten = easeIO(seg01(p, .09, .15)), shrink = easeIO(seg01(p, .3, .37));
    if (p <= 0) enter = 1;
    var sc = lerp(1, s2, shrink);
    var x = lerp(G.d0.x * W, G.d2.x * W, shrink), y = lerp(G.d0.y * H, G.d2.y * H, shrink);
    var rot = lerp(-4, 0, straighten);
    var dim = 1 - .35 * seg01(p, .82, .9);
    docEl.style.opacity = (enter * dim).toFixed(3);
    docEl.style.transform = "translate(" + x.toFixed(1) + "px," + y.toFixed(1) + "px) rotate(" + rot.toFixed(2) + "deg) scale(" + sc.toFixed(4) + ")";
    var bt = seg01(p, .13, .29), bOn = p > .125 && p < .3;
    var docH = docW * .704 * sc;
    beam.style.opacity = bOn ? (Math.min(1, bt * 8, (1 - bt) * 8)).toFixed(2) : "0";
    beam.style.transform = "translate(" + x.toFixed(1) + "px," + (y + bt * docH).toFixed(1) + "px)";
    beam.style.width = (docW * sc) + "px";
    var by = bt * 880;
    lits.forEach(function(l, i){
      var on = p >= .13 && (by >= l.y || p >= .29);
      if (on !== !!litOn[i]){ litOn[i] = on; l.g.classList.toggle("lit", on); l.t.classList.toggle("lit", on); }
    });
    var sh = easeOut(seg01(p, .3, .37));
    sheet.style.opacity = sh.toFixed(3);
    sheet.style.transform = "translateY(" + ((1 - sh) * 26).toFixed(1) + "px)";
    ghosts.forEach(function(g, i){
      var t = seg01(p, .37 + i * .014, .43 + i * .014), te = easeIO(t);
      if (!g.src || !cellPos[i] || !g.cell.offsetWidth){ g.el.style.opacity = "0"; g.cell.classList.toggle("on", t >= 1); return; }
      var sx = x + (g.src.bb.x / 1250) * docW * sc, sy = y + (g.src.bb.y / 880) * docW * .704 * sc;
      var tx = cellPos[i].x - g.el.offsetWidth / 2, ty = cellPos[i].y - g.el.offsetHeight / 2;
      var arc = Math.sin(te * Math.PI) * -28;
      g.el.style.transform = "translate(" + lerp(sx, tx, te).toFixed(1) + "px," + (lerp(sy, ty, te) + arc).toFixed(1) + "px)";
      g.el.style.opacity = (t <= 0 ? 0 : t >= 1 ? 0 : Math.min(1, t * 6)).toFixed(2);
      g.cell.classList.toggle("on", t >= 1);
    });
    var r1 = p >= .49;
    row1.forEach(function(td, k){ if (k >= 7) td.classList.toggle("on", r1); });
    var n = 1;
    for (var j = 1; j < rows.length; j++){
      var pj = .52 + (j - 1) * (.25 / (rows.length - 1)), on = p >= pj;
      if (on) n++;
      if (on !== !!rowOn[j]){
        rowOn[j] = on;
        $$("td", rows[j]).forEach(function(td){ td.classList.toggle("on", on); });
        if (on && !reduce && p < .99){ rows[j].classList.remove("flash"); void rows[j].offsetWidth; rows[j].classList.add("flash"); }
      }
      var c = cards[j - 1], ct = easeOut(seg01(p, pj - .02, pj + .01));
      var cx = (G.pile.x + (j - 1) * G.pile.dx) * W, cy = (G.pile.y + (j - 1) * G.pile.dy) * H;
      c.style.opacity = (ct * dim).toFixed(2);
      c.style.transform = "translate(" + (cx + (1 - ct) * W * .25).toFixed(1) + "px," + cy.toFixed(1) + "px) rotate(" + ((j % 2 ? 2.5 : -2.5) * ct).toFixed(1) + "deg)";
    }
    if (p < .49) n = p >= .43 ? 1 : 0;
    var last = rows[Math.max(0, n - 1)];
    if (sheetBody && last){ var over = last.offsetTop + last.offsetHeight - sheetBody.clientHeight; sheetBody.scrollTop = over > 0 ? over : 0; }
    if (countEl) countEl.textContent = n + " / " + GR.length + " documents lus";
    dlEl.classList.toggle("on", p >= .84);
    if (hint) hint.style.opacity = p > .02 ? "0" : "1";
    var st = root.classList.contains("static") ? 0 : (p < .1 ? 0 : p < .3 ? 1 : p < .51 ? 2 : p < .8 ? 3 : 4);
    steps.forEach(function(s, k){ s.classList.toggle("on", k === st); if (k) s.setAttribute("aria-hidden", String(k !== st)); });
    var B = [0, .1, .3, .51, .8, 1];
    navs.forEach(function(nv, k){ $("i", nv).style.transform = "scaleX(" + seg01(p, B[k], B[k + 1]).toFixed(3) + ")"; nv.classList.toggle("on", k === st); });
  }
  var lastP = 0, scroller = null;
  function onResize(){ measure(); render(root.classList.contains("static") ? 1 : lastP); }
  function toStatic(revisit){ root.classList.add("static"); root.classList.toggle("revisit", !!revisit); if (scroller) scroller.off = true; measure(); render(1); }
  function toScroll(){
    root.classList.remove("static", "revisit"); measure(); render(0);
    if (!scroller) scroller = addScroller(root, function(p){ lastP = p; render(p); }); else scroller.off = false;
  }
  w.addEventListener("resize", function(){ clearTimeout(onResize._t); onResize._t = setTimeout(onResize, 120); });
  var replay = $(".intro__replay", root);
  if (replay) replay.addEventListener("click", function(){ toScroll(); w.scrollTo(0, 0); });
  if (reduce){ toStatic(false); return; }
  if (store("scanid-intro-vue")){ toStatic(true); return; }
  store("scanid-intro-vue", "1");
  toScroll();
})();

/* ---------- La loupe : ce que ScanID voit ---------- */
var FIELDS = [
  ["ptype", 400, 176, "Type", "P", 1], ["pays", 560, 176, "Pays émetteur", "FRA", 0], ["num", 820, 176, "N° du document", "23AF41907", 1],
  ["nom", 400, 268, "Nom de famille", "SPECIMEN", 1], ["prenom", 400, 360, "Prénom", "CAMILLE", 1],
  ["nat", 400, 452, "Nationalité", "FRANÇAISE", 1], ["sexe", 820, 452, "Sexe", "F", 1],
  ["naissance", 400, 544, "Date de naissance", "14/05/1986", 1],
  ["expiration", 820, 544, "Date d’expiration", "22/09/2033", 1]
];
function fieldBox(f){ var wd = Math.max(3, f[4].length) * 21.6 + 28; return { x: f[1] - 14, y: f[2] + 8, w: wd, h: 48 }; }
function dataLayerSVG(){
  var m = LIB.SPEC.mrz, CW = 1130 / 44, g = "";
  LIB.wavePaths(1250, 880, 16, 1.7).forEach(function(dd, i){ g += '<path d="' + dd + '" stroke="#17B2DA" stroke-opacity="' + (i % 2 ? .07 : .04) + '"/>'; });
  var boxes = FIELDS.map(function(f){
    var b = fieldBox(f), on = f[5];
    return '<rect x="' + b.x + '" y="' + b.y + '" width="' + b.w.toFixed(0) + '" height="' + b.h + '" rx="6" class="ld-box"' + (on ? "" : ' stroke="#5C6675" stroke-dasharray="7 6" fill="none"') + "/>" +
      '<text x="' + f[1] + '" y="' + (f[2] + 1) + '" class="ld-l"' + (on ? "" : ' fill="#7C8696"') + ">" + esc(f[3].toUpperCase()) + (on ? "" : " · NON EXPORTÉ") + "</text>" +
      '<text x="' + f[1] + '" y="' + (f[2] + 42) + '" class="ld-v"' + (on ? "" : ' fill="#8D97A6"') + ">" + esc(f[4]) + "</text>";
  }).join("");
  function spans(line, map){ var out = "", i = 0; map.forEach(function(sg){ out += '<tspan fill="' + sg[1] + '">' + esc(line.substr(i, sg[0])) + "</tspan>"; i += sg[0]; }); return out; }
  var C = "#17B2DA", Wt = "#F3F6F8", Gr = "#5C6675", K = "#E7A2B4";
  var l1 = spans(m.l1, [[2, Gr], [3, Wt], [8, C], [2, Gr], [7, C], [22, Gr]]);
  var l2 = spans(m.l2, [[9, C], [1, K], [3, Wt], [6, C], [1, K], [1, C], [6, C], [1, K], [14, Gr], [1, K], [1, K]]);
  function mark(a, n, label, y){ var x1 = 60 + a * CW, x2 = 60 + (a + n) * CW; return '<path d="M' + (x1 + 3).toFixed(1) + " " + y + "v8H" + (x2 - 3).toFixed(1) + "v-8" + '" fill="none" stroke="#17B2DA" stroke-width="1.6" opacity=".7"/><text x="' + ((x1 + x2) / 2).toFixed(1) + '" y="' + (y + 28) + '" text-anchor="middle" class="ld-l" style="font-size:14px">' + label + "</text>"; }
  return '<svg viewBox="0 0 1250 880" aria-hidden="true">' +
    '<rect width="1250" height="880" fill="#0B1522"/><g fill="none" stroke-width="1.2">' + g + "</g>" +
    '<text x="60" y="104" class="ld-l" style="font-size:22px;letter-spacing:5px">CE QUE SCANID LIT</text>' +
    '<text x="1190" y="104" text-anchor="end" class="ld-note">EN MÉMOIRE · RIEN N’EST CONSERVÉ</text>' +
    '<rect x="60" y="160" width="300" height="420" rx="12" fill="none" stroke="#5C6675" stroke-width="2" stroke-dasharray="9 7"/>' +
    '<text x="210" y="360" text-anchor="middle" class="ld-note">PHOTO</text><text x="210" y="392" text-anchor="middle" class="ld-note" style="font-size:16px">NI EXTRAITE,</text><text x="210" y="416" text-anchor="middle" class="ld-note" style="font-size:16px">NI CONSERVÉE</text>' +
    boxes +
    '<rect x="0" y="668" width="1250" height="212" fill="#0E1C2E"/>' +
    '<text x="60" y="728" class="ld-mrz" textLength="1130" lengthAdjust="spacingAndGlyphs">' + l1 + "</text>" +
    '<text x="60" y="806" class="ld-mrz" textLength="1130" lengthAdjust="spacingAndGlyphs">' + l2 + "</text>" +
    mark(0, 9, "N°", 818) + mark(10, 3, "PAYS", 818) + mark(13, 6, "NAISSANCE", 818) + mark(20, 1, "S", 818) + mark(21, 6, "EXPIRATION", 818) +
    "</svg>";
}
(function(){
  var lp = $("#loupe"); if (!lp) return;
  $(".loupe__doc", lp).innerHTML = LIB.passport({});
  $(".loupe__data", lp).innerHTML = dataLayerSVG();
  var cap = $("#loupe-cap"), auto = true, idleT = 0, raf = 0, t0 = 0, vis = false, MRZ_Y = 668;
  function describe(vx, vy){
    if (vy >= MRZ_Y) return "<b>Bande MRZ</b> · les deux lignes que les machines savent lire, avec leurs clés de contrôle";
    if (vx >= 60 && vx <= 360 && vy >= 160 && vy <= 580) return "<b>Photo</b> · ni extraite, ni conservée";
    for (var i = 0; i < FIELDS.length; i++){
      var f = FIELDS[i], b = fieldBox(f);
      if (vx >= b.x - 10 && vx <= b.x + b.w + 10 && vy >= f[2] - 26 && vy <= b.y + b.h + 8)
        return "<b>" + esc(f[3]) + "</b> · " + esc(f[4]) + (f[5] ? " · colonne du fichier" : " · lu, mais pas exporté aujourd’hui");
    }
    return "Promenez la loupe sur le passeport";
  }
  function place(px, py){
    var r = lp.getBoundingClientRect();
    px = clamp(px, 0, r.width); py = clamp(py, 0, r.height);
    lp.style.setProperty("--x", px + "px"); lp.style.setProperty("--y", py + "px");
    cap.innerHTML = describe(px / r.width * 1250, py / r.height * 880);
  }
  var PATH = [[520, 298], [470, 390], [520, 482], [900, 482], [520, 574], [900, 574], [900, 206], [640, 206], [520, 740], [900, 800], [210, 370]];
  function loop(t){
    if (!auto || !vis){ raf = 0; return; }
    if (!t0) t0 = t;
    var k = (t - t0) / 2300, i = Math.floor(k) % PATH.length, f = easeIO(k - Math.floor(k));
    var a = PATH[i], b = PATH[(i + 1) % PATH.length], r = lp.getBoundingClientRect();
    var hold = Math.min(1, f * 1.6);
    place(lerp(a[0], b[0], hold) / 1250 * r.width, lerp(a[1], b[1], hold) / 880 * r.height);
    raf = requestAnimationFrame(loop);
  }
  function startAuto(){ auto = true; if (!raf && vis && !reduce){ t0 = 0; raf = requestAnimationFrame(loop); } }
  function user(e){
    auto = false; clearTimeout(idleT); idleT = setTimeout(startAuto, 4000);
    var r = lp.getBoundingClientRect(); place(e.clientX - r.left, e.clientY - r.top);
  }
  lp.addEventListener("pointermove", function(e){ if (e.pointerType === "mouse" || e.buttons) user(e); });
  lp.addEventListener("pointerdown", function(e){ user(e); });
  lp.addEventListener("pointerleave", function(e){ if (e.pointerType === "mouse"){ clearTimeout(idleT); idleT = setTimeout(startAuto, 1200); } });
  watchVisible(lp, function(v){ vis = v; if (v && auto) startAuto(); });
  var r0 = lp.getBoundingClientRect(); place(r0.width * .42, r0.height * .33);
})();

/* ---------- Déposez, c'est lu ---------- */
(function(){
  var zone = $("#drop-zone"); if (!zone) return;
  var card = $("#drop-card"), bar = $("#drop-bar"), busy = false;
  card.innerHTML = LIB.passport({ mini: true });
  $("#drop-thumb").innerHTML = LIB.passport({ mini: true }) + "<i></i>";
  function setState(s){ zone.setAttribute("data-state", s); }
  function read(){
    if (busy) return; busy = true;
    card.classList.add("gone"); setState("reading");
    var t = 0, total = reduce ? 300 : 1900;
    var iv = setInterval(function(){
      t += 60; bar.style.width = Math.min(100, t / total * 100) + "%";
      if (t >= total){ clearInterval(iv); done(); }
    }, 60);
  }
  function done(){
    var cols = [{ k: "nom", t: "Nom de famille" }, { k: "prenom", t: "Prénom" }, { k: "sexe", t: "Sexe" }, { k: "naissance", t: "Date de naissance" }, { k: "expiration", t: "Date d’expiration" }, { k: "nat", t: "Nationalité" }, { k: "num", t: "N° du document" }, { k: "type", t: "Type" }, { k: "score", t: "Score" }];
    $("#drop-table").innerHTML = LIB.tableHTML([LIB.SPEC], { cols: cols });
    $$("#drop-table td").forEach(function(td, i){ td.style.animationDelay = (i * 70) + "ms"; });
    setState("done"); busy = false;
    var h = $("#drop-done-t"); if (h){ h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
  }
  function reset(){ card.classList.remove("gone"); bar.style.width = "0"; setState("idle"); }
  $("#drop-use").addEventListener("click", read);
  $("#drop-again").addEventListener("click", reset);
  $("#drop-dl").addEventListener("click", function(){ download("scanid-exemple-specimen.csv", LIB.csv([LIB.SPEC])); });
  var ghost = null, sx = 0, sy = 0, moved = false;
  card.addEventListener("pointerdown", function(e){
    if (busy || card.classList.contains("gone")) return;
    e.preventDefault(); sx = e.clientX; sy = e.clientY; moved = false;
    try { card.setPointerCapture(e.pointerId); } catch(_) {}
    ghost = d.createElement("div"); ghost.className = "drop__ghost"; ghost.innerHTML = LIB.passport({ mini: true });
    ghost.style.left = (e.clientX - 100) + "px"; ghost.style.top = (e.clientY - 70) + "px"; ghost.style.display = "none";
    d.body.appendChild(ghost);
  });
  card.addEventListener("pointermove", function(e){
    if (!ghost) return;
    if (!moved && Math.abs(e.clientX - sx) + Math.abs(e.clientY - sy) > 6){ moved = true; ghost.style.display = "block"; card.style.opacity = ".35"; }
    ghost.style.left = (e.clientX - 100) + "px"; ghost.style.top = (e.clientY - 70) + "px";
    var r = zone.getBoundingClientRect();
    zone.classList.toggle("over", e.clientX > r.left && e.clientX < r.right && e.clientY > r.top && e.clientY < r.bottom);
  });
  function end(e){
    if (!ghost) return;
    var r = zone.getBoundingClientRect(), inside = e && e.clientX > r.left && e.clientX < r.right && e.clientY > r.top && e.clientY < r.bottom;
    ghost.remove(); ghost = null; card.style.opacity = ""; zone.classList.remove("over");
    if (inside || !moved) read();
  }
  card.addEventListener("pointerup", end);
  card.addEventListener("pointercancel", function(){ if (ghost){ ghost.remove(); ghost = null; card.style.opacity = ""; zone.classList.remove("over"); } });
  card.addEventListener("keydown", function(e){ if (e.key === "Enter" || e.key === " "){ e.preventDefault(); read(); } });
  zone.addEventListener("dragover", function(e){ e.preventDefault(); zone.classList.add("over"); });
  zone.addEventListener("dragleave", function(){ zone.classList.remove("over"); });
  zone.addEventListener("drop", function(e){ e.preventDefault(); zone.classList.remove("over"); toast("Ici, seul le spécimen est lu : votre fichier n’a pas quitté votre ordinateur. Pour vos vrais documents, demandez votre essai gratuit."); });
})();

/* ---------- L'origine : une pile de passeports ---------- */
(function(){
  var st = $("#origin-stack"); if (!st) return;
  var G = LIB.GROUPE;
  st.innerHTML = [G[3], G[5], G[0]].map(function(p){ return LIB.passport({ mini: true, data: p.mrz ? p : Object.assign({}, p, { mrz: LIB.td3(Object.assign({ dobMrz: p.naissance.split("/").reverse().join("").slice(2), expMrz: p.expiration.split("/").reverse().join("").slice(2) }, p)) }) }); }).join("");
})();
