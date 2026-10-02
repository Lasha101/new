/* ============================================================
   ScanID — guide photo
   Le message de l'agence (lien personnalisé), la bonne photo
   en direct, les erreurs illustrées, le message à envoyer
   ============================================================ */
var MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
function frDate(iso){ var p = String(iso || "").split("-"); if (p.length < 3 || !+p[1]) return ""; return (+p[2]) + " " + MOIS[+p[1] - 1]; }

/* ---------- Page reçue par un voyageur : le message de son agence ---------- */
(function(){
  var box = $("#agency-note"); if (!box) return;
  var q; try { q = new URLSearchParams(location.search); } catch(e) { return; }
  var ag = (q.get("agence") || "").trim().slice(0, 80), v = (q.get("voyage") || "").trim().slice(0, 80), when = frDate(q.get("avant"));
  if (!ag) return;
  $("#an-t").textContent = ag + " vous demande une photo de votre passeport";
  $("#an-p").textContent = (v ? "Pour « " + v + " », envoyez-la à votre agence" : "Envoyez-la à votre agence") + (when ? " avant le " + when : "") + ", par le canal habituel. Voici comment la réussir.";
  box.hidden = false;
  $$("[data-agency-only]").forEach(function(el){ el.hidden = true; });
})();

/* ---------- La bonne photo, en direct ---------- */
(function(){
  var cam = $("#cam"); if (!cam) return;
  $("#cam-doc").innerHTML = LIB.passport({ mini: true });
  var st = { blur: 0, glare: 0, cut: 0, tilt: 0 }, W = { blur: 3, glare: 1, cut: 3, tilt: 1 };
  var HINT = { cut: "Un coin dépasse du cadre", blur: "Image floue : ne bougez pas", glare: "Reflet : inclinez un peu le document", tilt: "Posez le document bien à plat" };
  var RES = {
    ok: ["Lecture fiable", "Toutes les conditions sont réunies."],
    check: ["Ligne à relire", "La lecture passe, mais le score de confiance baisse : un coup d’œil suffira."],
    redo: ["Photo à reprendre", "Trop d’informations illisibles : mieux vaut refaire la photo avant de l’envoyer."]
  };
  function render(){
    var sev = 0, first = "";
    ["cut", "blur", "glare", "tilt"].forEach(function(k){ cam.classList.toggle(k, !!st[k]); if (st[k]){ sev += W[k]; if (!first) first = k; } });
    var q = sev === 0 ? "ok" : sev < 3 ? "check" : "redo";
    cam.setAttribute("data-q", q);
    $("#cam-hint").textContent = first ? HINT[first] : "Parfait, ne bougez plus";
    var res = $("#ph-res"); res.setAttribute("data-q", q); res.innerHTML = "<b>" + RES[q][0] + "</b><span>" + RES[q][1] + "</span>";
    $$("#ph-rules li[data-r]").forEach(function(li){ li.classList.toggle("bad", !!st[li.getAttribute("data-r")]); });
  }
  ["blur", "glare", "cut", "tilt"].forEach(function(k){ segToggle("#ph-" + k, function(v){ st[k] = +v; render(); }); });
  render();
})();

/* ---------- Les erreurs à éviter ---------- */
(function(){
  $$(".errs .vis").forEach(function(v, i){ v.insertAdjacentHTML("afterbegin", LIB.passport({ mini: true, seed: 1.2 + i * .7 })); });
})();

/* ---------- Le message à envoyer aux voyageurs ---------- */
(function(){
  var ag = $("#gen-ag"); if (!ag) return;
  var dest = $("#gen-dest"), dt = $("#gen-date");
  try { var t = new Date(); t.setDate(t.getDate() + 14); dt.value = t.toISOString().slice(0, 10); } catch(e) {}
  function link(a, v, iso){
    var q = "agence=" + encodeURIComponent(a).replace(/%20/g, "+");
    if (v) q += "&voyage=" + encodeURIComponent(v).replace(/%20/g, "+");
    if (iso) q += "&avant=" + iso;
    return "https://scanid.fr/guide-photo.html?" + q;
  }
  function render(){
    var a = ag.value.trim() || "Votre agence", v = dest.value.trim(), iso = dt.value, when = frDate(iso);
    $("#gen-t").textContent = a + " vous demande une photo de votre passeport";
    $("#gen-when").textContent = (v ? "Pour « " + v + " », envoyez-la à votre agence" : "Envoyez-la à votre agence") + (when ? " avant le " + when : "") + ".";
    var msg = "Bonjour,\n" + (v ? "Pour votre voyage « " + v + " », merci" : "Merci") + " de nous envoyer une photo de la page d’identité de votre passeport" + (when ? " avant le " + when : "") + ".\nVoici comment la réussir : " + link(ag.value.trim() || a, v, iso) + "\n" + a;
    $("#gen-msg").textContent = msg.replace(/« /g, "« ").replace(/ »/g, " »").replace(/ :/g, " :");
  }
  [ag, dest, dt].forEach(function(i){ i.addEventListener("input", render); });
  $("#gen-copy").addEventListener("click", function(){ copyText($("#gen-msg").textContent, "Message copié : collez-le dans votre e-mail ou votre messagerie."); });
  render();
})();
