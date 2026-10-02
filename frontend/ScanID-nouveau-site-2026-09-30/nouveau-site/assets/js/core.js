/* ============================================================
   ScanID — noyau du site
   Outils, apparitions, défilement, barre, grand menu,
   barre mobile, guilloches, formulaires, boutons d'achat
   ============================================================ */
var d = document, w = window;
d.documentElement.classList.add("js");
function $(s, c){ return (c || d).querySelector(s); }
function $$(s, c){ return Array.prototype.slice.call((c || d).querySelectorAll(s)); }
function clamp(v, a, b){ return Math.max(a, Math.min(b, v)); }
function lerp(a, b, t){ return a + (b - a) * t; }
function seg01(p, a, b){ return clamp((p - a) / (b - a), 0, 1); }
function easeOut(t){ return 1 - Math.pow(1 - t, 3); }
function easeIO(t){ return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
function pad(n){ return (n < 10 ? "0" : "") + n; }
var FMT = (function(){ try { return new Intl.NumberFormat("fr-FR"); } catch(e) { return { format: function(n){ return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, "\u00a0"); } }; } })();
function nb(s){ return String(s).replace(/(\d) (\d{3})\b/g, "$1\u00a0$2"); }
function euros(n, dec){ var s = dec ? n.toFixed(2).replace(".", ",") : FMT.format(Math.round(n)); return s + "\u00a0€"; }
var esc = LIB.esc;
var reduce = w.matchMedia("(prefers-reduced-motion: reduce)").matches;
var finePointer = w.matchMedia("(hover: hover) and (pointer: fine)").matches;
var hasIO = "IntersectionObserver" in w;
var PREVIEW = !!w.SCANID_PREVIEW;
function store(k, v){ try { if (v === undefined) return w.sessionStorage.getItem(k); if (v === null) w.sessionStorage.removeItem(k); else w.sessionStorage.setItem(k, v); } catch(e) { return null; } }

/* ---------- Message éphémère ---------- */
var toastEl = null, toastT = 0;
function toast(msg){
  if (!toastEl){ toastEl = d.createElement("div"); toastEl.className = "toast"; toastEl.setAttribute("role", "status"); toastEl.setAttribute("aria-live", "polite"); d.body.appendChild(toastEl); }
  toastEl.textContent = msg; toastEl.classList.add("on");
  clearTimeout(toastT); toastT = setTimeout(function(){ toastEl.classList.remove("on"); }, 4200);
}
function copyText(text, okMsg){
  function fallback(){
    var ta = d.createElement("textarea"); ta.value = text; ta.setAttribute("readonly", "");
    ta.style.position = "fixed"; ta.style.top = "0"; ta.style.left = "0"; ta.style.opacity = "0";
    d.body.appendChild(ta); ta.select(); var ok = false;
    try { ok = d.execCommand("copy"); } catch(e) {}
    d.body.removeChild(ta);
    toast(ok ? okMsg : "Copie impossible ici : sélectionnez le texte à la main.");
  }
  try {
    if (navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(text).then(function(){ toast(okMsg); }, fallback); return; }
  } catch(e) {}
  fallback();
}
function download(filename, data, mime){
  if (PREVIEW){ toast("Dans l’aperçu, le téléchargement est désactivé. Sur scanid.fr, le fichier s’enregistre directement."); return; }
  try {
    var blob = data instanceof Blob ? data : new Blob([data], { type: mime || "text/csv;charset=utf-8" });
    var url = URL.createObjectURL(blob), a = d.createElement("a");
    a.href = url; a.download = filename; d.body.appendChild(a); a.click();
    setTimeout(function(){ URL.revokeObjectURL(url); a.remove(); }, 800);
  } catch(e) { toast("Le téléchargement n’a pas pu démarrer. Réessayez depuis un autre navigateur."); }
}
function onceVisible(el, fn, thr){
  if (!el) return;
  if (!hasIO){ fn(); return; }
  var o = new IntersectionObserver(function(es){ es.forEach(function(en){ if (en.isIntersecting){ o.disconnect(); fn(); } }); }, { threshold: thr || .3 });
  o.observe(el);
}
function watchVisible(el, cb, margin){
  if (!el) return;
  if (!hasIO){ cb(true); return; }
  var o = new IntersectionObserver(function(es){ es.forEach(function(en){ cb(en.isIntersecting); }); }, { rootMargin: margin || "0px" });
  o.observe(el);
}
function segToggle(seg, fn){
  if (typeof seg === "string") seg = $(seg);
  if (!seg) return;
  seg.addEventListener("click", function(e){
    var b = e.target.closest("button"); if (!b || !seg.contains(b)) return;
    $$("button", seg).forEach(function(x){ x.setAttribute("aria-pressed", String(x === b)); });
    fn(b.getAttribute("data-v"), b);
  });
}
function setSeg(seg, v){
  if (typeof seg === "string") seg = $(seg);
  if (!seg) return;
  $$("button", seg).forEach(function(x){ x.setAttribute("aria-pressed", String(x.getAttribute("data-v") === v)); });
}

/* ---------- Apparitions : seul ce qui est encore sous l'écran s'anime ---------- */
(function(){
  var els = $$("[data-rise]");
  if (reduce || !hasIO){ els.forEach(function(el){ el.classList.add("in"); }); return; }
  var vh = w.innerHeight;
  var io = new IntersectionObserver(function(es){
    es.forEach(function(en){ if (en.isIntersecting){ en.target.classList.add("in"); io.unobserve(en.target); } });
  }, { rootMargin: "0px 0px -6% 0px", threshold: .05 });
  els.forEach(function(el){ if (el.getBoundingClientRect().top < vh * .96) el.classList.add("in"); else io.observe(el); });
  setTimeout(function(){ els.forEach(function(el){ if (el.getBoundingClientRect().top < w.innerHeight) el.classList.add("in"); }); }, 2600);
})();

/* ---------- Moteur de défilement ---------- */
var scrollers = [], ticking = false, onScrollFns = [];
function addScroller(el, fn){
  if (!el) return null;
  var s = { el: el, fn: fn, active: !hasIO, off: false };
  scrollers.push(s);
  if (hasIO){
    var o = new IntersectionObserver(function(es){ es.forEach(function(en){ s.active = en.isIntersecting; }); tick(); }, { rootMargin: "160px 0px" });
    o.observe(el);
  }
  tick();
  return s;
}
function tick(){ if (!ticking){ ticking = true; requestAnimationFrame(run); } }
function run(){
  ticking = false;
  var vh = w.innerHeight;
  for (var i = 0; i < scrollers.length; i++){
    var s = scrollers[i]; if (!s.active || s.off) continue;
    var r = s.el.getBoundingClientRect(), total = r.height - vh;
    var p = total > 0 ? clamp(-r.top / total, 0, 1) : clamp((vh - r.top) / (vh + r.height), 0, 1);
    s.fn(p, r, vh);
  }
  for (var j = 0; j < onScrollFns.length; j++) onScrollFns[j]();
}
w.addEventListener("scroll", tick, { passive: true });
w.addEventListener("resize", tick);

/* ---------- Barre du site : claire ou nuit selon ce qu'elle survole ---------- */
(function(){
  var bar = $(".site-bar"); if (!bar) return;
  var zones = [];
  function refresh(){ zones = $$(".intro, .dark, .site-footer, [data-bar='dark']"); }
  function update(){
    var y = w.scrollY || w.pageYOffset || 0, mid = bar.offsetHeight * .6, onDark = false;
    for (var i = 0; i < zones.length; i++){ var r = zones[i].getBoundingClientRect(); if (r.top <= mid && r.bottom >= mid){ onDark = true; break; } }
    bar.classList.toggle("on-dark", onDark);
    bar.classList.toggle("scrolled", y > 8);
  }
  refresh(); update();
  onScrollFns.push(update);
  w.addEventListener("resize", function(){ refresh(); update(); });
})();

/* ---------- Guilloches : dessinées au moment où elles deviennent visibles ---------- */
function drawRosettes(root){
  $$("canvas[data-rosette]", root).forEach(function(c){
    if (c.dataset.done) return;
    onceVisible(c, function(){ if (c.dataset.done) return; c.dataset.done = "1"; LIB.rosette(c, LIB.ROSETTES[c.getAttribute("data-rosette")] || LIB.ROSETTES.band, { size: +(c.getAttribute("data-size") || 1100) }); }, .01);
  });
}
drawRosettes(d);

/* ---------- Grand menu ---------- */
(function(){
  var panel = $("#menu-panel"), openers = $$("[data-menu-open]"); if (!panel || !openers.length) return;
  var closer = $("[data-menu-close]", panel), last = null;
  function focusables(){ return $$("a[href], button:not([disabled])", panel).filter(function(el){ return el.offsetParent !== null; }); }
  function open(from){
    last = from || d.activeElement;
    panel.hidden = false; void panel.offsetWidth;
    panel.classList.add("on"); d.documentElement.classList.add("menu-open");
    openers.forEach(function(b){ b.setAttribute("aria-expanded", "true"); });
    var c = $(".menu-panel__guil canvas", panel); if (c && !c.dataset.done){ c.dataset.done = "1"; LIB.rosette(c, LIB.ROSETTES.menu, { size: 900 }); }
    setTimeout(function(){ (closer || focusables()[0]).focus(); }, 60);
  }
  function close(){
    panel.classList.remove("on"); d.documentElement.classList.remove("menu-open");
    openers.forEach(function(b){ b.setAttribute("aria-expanded", "false"); });
    setTimeout(function(){ if (!panel.classList.contains("on")) panel.hidden = true; }, 520);
    if (last && last.focus) last.focus();
  }
  openers.forEach(function(b){ b.addEventListener("click", function(){ open(b); }); });
  if (closer) closer.addEventListener("click", close);
  panel.addEventListener("click", function(e){ var a = e.target.closest("a[href]"); if (a && a.getAttribute("href").charAt(0) === "#") close(); });
  d.addEventListener("keydown", function(e){
    if (!panel.classList.contains("on")) return;
    if (e.key === "Escape"){ e.preventDefault(); close(); return; }
    if (e.key === "Tab"){
      var f = focusables(); if (!f.length) return;
      var first = f[0], lastEl = f[f.length - 1];
      if (e.shiftKey && d.activeElement === first){ e.preventDefault(); lastEl.focus(); }
      else if (!e.shiftKey && d.activeElement === lastEl){ e.preventDefault(); first.focus(); }
    }
  });
})();

/* ---------- Barre mobile : l'essai sous le pouce ---------- */
(function(){
  var pb = $(".phone-bar"); if (!pb) return;
  var foot = $(".site-footer"), hideAt = $("[data-phonebar-hide]");
  function update(){
    var y = w.scrollY || 0, vh = w.innerHeight, show = y > vh * .75;
    if (foot && foot.getBoundingClientRect().top < vh) show = false;
    if (hideAt){ var r = hideAt.getBoundingClientRect(); if (r.top < vh && r.bottom > 0) show = false; }
    pb.classList.toggle("on", show);
    pb.setAttribute("aria-hidden", String(!show));
    $$("a", pb).forEach(function(a){ a.tabIndex = show ? 0 : -1; });
  }
  update(); onScrollFns.push(update);
})();

/* ---------- Pictogrammes : le trait se dessine ---------- */
(function(){
  var grids = $$(".pic[data-draw]"); if (!grids.length) return;
  grids.forEach(function(grid){
    $$("svg .s, svg .l", grid).forEach(function(p){ try { var L = Math.ceil(p.getTotalLength ? p.getTotalLength() : 120); p.style.setProperty("--len", L); } catch(e) {} });
    if (reduce) return;
    onceVisible(grid, function(){ $$(".pic__it", grid).forEach(function(it, i){ setTimeout(function(){ it.classList.add("draw"); }, i * 110); }); }, .3);
  });
})();

/* ---------- Aperçu privé : les téléchargements directs sont bloqués ---------- */
if (PREVIEW){
  d.addEventListener("click", function(e){
    var a = e.target.closest && e.target.closest("a[download]");
    if (a){ e.preventDefault(); toast("Dans l’aperçu, le téléchargement est désactivé. Sur scanid.fr, le fichier s’enregistre directement."); }
  });
}

/* ---------- Envoi des formulaires simples (contact, rappel, checklist) ---------- */
var FORMSPREE = "https://formspree.io/f/xqeowdvk";
function formData(form){
  var o = {};
  $$("input, select, textarea", form).forEach(function(el){
    if (!el.name || el.name.charAt(0) === "_") return;
    if (el.type === "checkbox"){ o[el.name] = el.checked; return; }
    if (el.type === "radio"){ if (el.checked) o[el.name] = el.value; return; }
    o[el.name] = el.value.trim();
  });
  return o;
}
function validate(form){
  var bad = null;
  $$("[required]", form).forEach(function(el){
    var ok = el.type === "checkbox" ? el.checked : !!el.value.trim();
    if (ok && el.type === "email") ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(el.value.trim());
    el.setAttribute("aria-invalid", String(!ok));
    var fld = el.closest(".fld"), msg = fld ? $(".err", fld) : null;
    if (msg) msg.hidden = ok;
    if (!ok && !bad) bad = el;
  });
  if (bad){ bad.focus(); return false; }
  return true;
}
function sendFormspree(payload, subject){
  if (PREVIEW) return new Promise(function(ok){ setTimeout(function(){ ok({ preview: true }); }, 600); });
  payload._subject = subject;
  return fetch(FORMSPREE, { method: "POST", headers: { "Content-Type": "application/json", "Accept": "application/json" }, body: JSON.stringify(payload) })
    .then(function(r){ if (!r.ok) throw new Error(String(r.status)); return r.json().catch(function(){ return {}; }); });
}
$$("form[data-form]").forEach(function(form){
  var kind = form.getAttribute("data-form");
  if (kind === "trial") return; /* page Essai : géré par essai.js */
  form.setAttribute("novalidate", "");
  form.addEventListener("submit", function(e){
    e.preventDefault();
    if ($(".hp input", form) && $(".hp input", form).value) return;
    if (!validate(form)) return;
    var btn = $("button[type=submit]", form), label = btn ? btn.innerHTML : "";
    if (btn){ btn.disabled = true; btn.textContent = "Envoi en cours…"; }
    var subj = form.getAttribute("data-subject") || "Message depuis scanid.fr";
    sendFormspree(formData(form), subj).then(function(){
      var ok = $(".form-msg--ok", form.parentNode) || $("[data-ok]", form.parentNode);
      form.hidden = true;
      if (ok){ ok.hidden = false; ok.setAttribute("tabindex", "-1"); ok.focus(); }
    }).catch(function(){
      if (btn){ btn.disabled = false; btn.innerHTML = label; }
      toast("L’envoi n’a pas abouti. Écrivez-nous à contact@scanid.fr, nous répondons sous un jour ouvré.");
    });
  });
});

/* ---------- Boutons d'achat : compte créé avant le paiement dès que l'application le permet ---------- */
(function(){
  var btns = $$("a.js-buy"); if (!btns.length || PREVIEW) return;
  var ready = null;
  fetch("/api/config", { cache: "no-store" }).then(function(r){ return r.ok ? r.json() : {}; }).then(function(c){ ready = !!(c && c.signup); }).catch(function(){ ready = false; });
  btns.forEach(function(a){
    a.addEventListener("click", function(ev){ if (ready === true){ ev.preventDefault(); location.href = "/app/inscription?pack=" + a.getAttribute("data-pack"); } });
  });
})();
