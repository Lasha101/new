/* ============================================================
   ScanID — le décodeur de bande MRZ (passeport spécimen, TD3)
   ============================================================ */
(function(){
  var box = $("#mrzd-lines"); if (!box) return;
  var M = LIB.SPEC.mrz, L = [M.l1, M.l2];
  var SEG = [
    [0, 0, 1, "Type de document", "P pour passeport. Une carte d’identité commence par I."],
    [0, 1, 1, "Sous-type", "Un chevron : pas de sous-type pour ce passeport."],
    [0, 2, 3, "Pays émetteur", "FRA : la France, en code à trois lettres."],
    [0, 5, 8, "Nom", "SPECIMEN. Les accents disparaissent ; espaces et tirets deviennent des chevrons."],
    [0, 13, 2, "Séparateur", "Deux chevrons séparent le nom des prénoms."],
    [0, 15, 7, "Prénoms", "CAMILLE. Plusieurs prénoms sont séparés par un seul chevron."],
    [0, 22, 22, "Remplissage", "Des chevrons complètent la ligne jusqu’à 44 caractères. Un nom trop long est tronqué."],
    [1, 0, 9, "Numéro du document", "23AF41907 : neuf caractères, lettres et chiffres.", "num"],
    [1, 9, 1, "Clé du numéro", "Un chiffre calculé à partir du numéro : une faute de lecture se voit aussitôt.", "num"],
    [1, 10, 3, "Nationalité", "FRA : nationalité française."],
    [1, 13, 6, "Date de naissance", "860514, au format année, mois, jour : le 14 mai 1986.", "dob"],
    [1, 19, 1, "Clé de la date de naissance", "Calculée à partir des six chiffres de la date.", "dob"],
    [1, 20, 1, "Sexe", "F, M, ou un chevron si le sexe n’est pas précisé."],
    [1, 21, 6, "Date d’expiration", "330922 : le 22 septembre 2033.", "exp"],
    [1, 27, 1, "Clé de la date d’expiration", "Calculée à partir des six chiffres de la date.", "exp"],
    [1, 28, 14, "Données facultatives", "Vides sur ce spécimen : quatorze chevrons.", "opt"],
    [1, 42, 1, "Clé des données facultatives", "0, puisque la zone est vide.", "opt"],
    [1, 43, 1, "Clé globale", "Elle contrôle ensemble le numéro, les deux dates et les données facultatives, avec leurs clés.", "all"]
  ];
  var FIELD = { num: [0, 9, 9], dob: [13, 6, 19], exp: [21, 6, 27], opt: [28, 14, 42] };
  function val(c){ return c >= "0" && c <= "9" ? +c : c === "<" ? 0 : c.charCodeAt(0) - 55; }
  function calc(key){
    var l2 = L[1], s, keyPos;
    if (key === "all"){ s = l2.substr(0, 10) + l2.substr(13, 7) + l2.substr(21, 22); keyPos = 43; }
    else { var f = FIELD[key]; s = l2.substr(f[0], f[1]); keyPos = f[2]; }
    var wts = [7, 3, 1], tot = 0, prods = [];
    for (var i = 0; i < s.length; i++){ var p = val(s.charAt(i)) * wts[i % 3]; tot += p; prods.push(p); }
    var k = tot % 10, printed = l2.charAt(keyPos);
    var head = key === "all" ? "Les 39 caractères contrôlés, pondérés 7, 3, 1, 7, 3, 1…\n" :
      "Caractères    " + s.split("").join("  ") + "\nValeurs       " + s.split("").map(function(c){ return String(val(c)); }).join(" ") + "\nPoids         " + s.split("").map(function(_, i){ return "×" + wts[i % 3]; }).join(" ") + "\n";
    return esc(head + (key === "all" ? "" : "Produits      " + prods.join(" + ") + "\n")) + "Somme         <b>" + tot + "</b>\n" + tot + " modulo 10  =  <b>" + k + "</b>   clé imprimée : <b>" + esc(printed) + "</b>" + (String(k) === printed ? "   ✓" : "");
  }
  function segOf(li, ci){ for (var i = 0; i < SEG.length; i++){ var s = SEG[i]; if (s[0] === li && ci >= s[1] && ci < s[1] + s[2]) return i; } return 0; }
  box.innerHTML = L.map(function(line, li){
    return '<div class="mrzd__line">' + line.split("").map(function(c, ci){
      var sg = SEG[segOf(li, ci)];
      return '<span class="mrzd__c' + (c === "<" ? " g" : "") + (/^Clé/.test(sg[3]) ? " key" : "") + '" data-l="' + li + '" data-c="' + ci + '">' + esc(c) + "</span>";
    }).join("") + "</div>";
  }).join("");
  var cells = $$(".mrzd__c", box), sel = 7;
  function mark(i, cls){ var sg = SEG[i]; cells.forEach(function(c){ var li = +c.getAttribute("data-l"), ci = +c.getAttribute("data-c"); c.classList.toggle(cls, li === sg[0] && ci >= sg[1] && ci < sg[1] + sg[2]); }); }
  function info(i){
    var sg = SEG[i];
    $("#mrzd-where").textContent = "Ligne " + (sg[0] + 1) + " · caractère" + (sg[2] > 1 ? "s " + (sg[1] + 1) + " à " + (sg[1] + sg[2]) : " " + (sg[1] + 1)) + " · zone " + (i + 1) + " sur " + SEG.length;
    $("#mrzd-t").textContent = sg[3];
    $("#mrzd-p").textContent = sg[4];
    $("#mrzd-calc").innerHTML = sg[5] ? calc(sg[5]) : "Aucune clé de contrôle pour cette zone.\nLa ligne 1 se vérifie par sa structure :\ntype, pays, nom, prénoms.";
  }
  function pick(i){ sel = (i + SEG.length) % SEG.length; cells.forEach(function(c){ c.classList.remove("hov"); }); mark(sel, "sel"); info(sel); }
  box.addEventListener("mouseover", function(e){ var c = e.target.closest(".mrzd__c"); if (!c) return; var i = segOf(+c.getAttribute("data-l"), +c.getAttribute("data-c")); mark(i, "hov"); info(i); });
  box.addEventListener("mouseleave", function(){ cells.forEach(function(c){ c.classList.remove("hov"); }); info(sel); });
  box.addEventListener("click", function(e){ var c = e.target.closest(".mrzd__c"); if (c) pick(segOf(+c.getAttribute("data-l"), +c.getAttribute("data-c"))); });
  $("#mrzd-prev").addEventListener("click", function(){ pick(sel - 1); });
  $("#mrzd-next").addEventListener("click", function(){ pick(sel + 1); });
  pick(7);
})();
