/* ============================================================
   ScanID — page Essai
   L'essai en trois questions : envoi à l'application
   (/api/trial-requests), repli sur Formspree si besoin.
   Le passeport spécimen à télécharger.
   ============================================================ */
(function(){
  var form = $("#trial"); if (!form) return;
  form.setAttribute("novalidate", "");
  var step = 1, LAST = 3, volume = "";
  var sets = $$("fieldset[data-step]", form), tabs = $$(".trial__steps li", form);
  var back = $("#tr-back"), next = $("#tr-next"), big = $("#tr-big");
  /* Réglage « trial » de l'application : création automatique du compte après validation */
  var trialAuto = PREVIEW ? true : null;
  if (!PREVIEW) fetch("/api/config", { cache: "no-store" }).then(function(r){ return r.ok ? r.json() : {}; }).then(function(c){ trialAuto = !!(c && c.trial); }).catch(function(){ trialAuto = false; });
  function show(focus){
    sets.forEach(function(s){ s.hidden = +s.getAttribute("data-step") !== step; });
    tabs.forEach(function(t, i){ t.classList.toggle("on", i + 1 === step); t.classList.toggle("done", i + 1 < step); if (i + 1 === step) t.setAttribute("aria-current", "step"); else t.removeAttribute("aria-current"); });
    back.hidden = step === 1;
    next.innerHTML = step === LAST ? "Ouvrir mon espace d’essai" : "Continuer <span class=\"ar\" aria-hidden=\"true\">→</span>";
    if (focus){ var f = $("fieldset[data-step='" + step + "'] input, fieldset[data-step='" + step + "'] button", form); if (f) f.focus(); }
  }
  function check(el){
    var v = el.type === "checkbox" ? el.checked : el.value.trim(), ok = !!v;
    if (ok && el.type === "email") ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(el.value.trim());
    el.setAttribute("aria-invalid", String(!ok));
    var fld = el.closest(".fld, .consent"), msg = fld ? $(".err", fld) : null;
    if (msg) msg.hidden = ok;
    return ok;
  }
  function validStep(){
    var bad = null;
    $$("fieldset[data-step='" + step + "'] [required]", form).forEach(function(el){ if (!check(el) && !bad) bad = el; });
    if (step === 2 && !volume){ $("#tr-vol-err").hidden = false; if (!bad) bad = $("#tr-vol button"); }
    if (bad){ bad.focus(); return false; }
    return true;
  }
  $$("[required]", form).forEach(function(el){ el.addEventListener("blur", function(){ if (el.getAttribute("aria-invalid") === "true") check(el); }); });
  $("#tr-vol").addEventListener("click", function(e){
    var b = e.target.closest("button"); if (!b) return;
    $$("#tr-vol button").forEach(function(x){ x.setAttribute("aria-pressed", String(x === b)); });
    volume = b.getAttribute("data-v"); $("#tr-vol-err").hidden = true;
    big.hidden = b.getAttribute("data-big") !== "1";
  });
  back.addEventListener("click", function(){ step = Math.max(1, step - 1); show(true); });

  function payload(){
    return { nom: $("#tr-nom").value.trim(), societe: $("#tr-agence").value.trim(), email: $("#tr-email").value.trim(), telephone: $("#tr-tel").value.trim(),
             volume: volume, message: "", siret: "", tva: "", consentement: $("#tr-ok").checked };
  }
  function done(data, viaApi){
    var mail = "<b>" + esc(data.email) + "</b>";
    $("#tr-done-p").innerHTML = (viaApi && trialAuto === true)
      ? "Dès sa validation, vous recevez à " + mail + " le lien pour choisir votre mot de passe, avec vos 20 documents offerts, sous un jour ouvré."
      : "Merci. Votre demande est bien enregistrée : vous recevez vos accès par e-mail à " + mail + ", sous un jour ouvré.";
    form.hidden = true;
    var ok = $("#trial-done"); ok.hidden = false; ok.setAttribute("tabindex", "-1"); ok.focus();
    try { w.scrollTo({ top: ok.getBoundingClientRect().top + w.scrollY - 110, behavior: reduce ? "auto" : "smooth" }); } catch(e) {}
  }
  function fail(){
    next.disabled = false; show(false);
    toast("L’envoi n’a pas abouti. Écrivez-nous à contact@scanid.fr : nous ouvrons votre essai sous un jour ouvré.");
  }
  function send(data){
    if (PREVIEW) return new Promise(function(ok){ setTimeout(function(){ ok(true); }, 700); });
    return fetch("/api/trial-requests", { method: "POST", headers: { "Content-Type": "application/json", "Accept": "application/json" }, body: JSON.stringify(data) })
      .then(function(r){ if (!r.ok) throw new Error(String(r.status)); return true; })
      .catch(function(){ return sendFormspree(Object.assign({}, data), "Demande d’essai · 20 documents offerts").then(function(){ return false; }); });
  }
  form.addEventListener("submit", function(e){
    e.preventDefault();
    if ($(".hp input", form).value) return;
    if (!validStep()) return;
    if (step < LAST){ step++; show(true); return; }
    var data = payload();
    next.disabled = true; next.textContent = "Envoi en cours…";
    send(data).then(function(viaApi){ done(data, viaApi); }, fail);
  });
  show(false);
})();

/* ---------- Le spécimen ---------- */
(function(){
  var box = $("#spec-pp"); if (!box) return;
  box.innerHTML = LIB.passport({});
})();
