/* ============================================================
   ScanID — bibliothèque graphique
   Passeport spécimen (données fictives), bande MRZ, guilloches
   ============================================================ */
var LIB = (function(){
  "use strict";

  /* ---------- MRZ (norme OACI 9303) ---------- */
  function mrzVal(c){ if (c >= "0" && c <= "9") return +c; if (c === "<") return 0; return c.charCodeAt(0) - 55; }
  function checkDigit(s){ var w = [7, 3, 1], t = 0; for (var i = 0; i < s.length; i++) t += mrzVal(s.charAt(i)) * w[i % 3]; return String(t % 10); }
  function deaccent(s){ return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toUpperCase(); }
  function mrzText(s, len){
    s = deaccent(s).replace(/[^A-Z0-9<]+/g, "<");
    while (s.length < len) s += "<";
    return s.slice(0, len);
  }
  function td3(p){
    var l1 = mrzText("P<" + p.pays + p.nom + "<<" + p.prenom.replace(/ /g, "<"), 44);
    var num = mrzText(p.num, 9), dob = p.dobMrz, exp = p.expMrz, opt = "<<<<<<<<<<<<<<";
    var c1 = checkDigit(num), c2 = checkDigit(dob), c3 = checkDigit(exp), c4 = "0";
    var comp = checkDigit(num + c1 + dob + c2 + exp + c3 + opt + c4);
    var l2 = num + c1 + p.pays + dob + c2 + p.sexe + exp + c3 + opt + c4 + comp;
    return { l1: l1, l2: l2, checks: { num: c1, dob: c2, exp: c3, opt: c4, comp: comp } };
  }

  /* ---------- Le spécimen et un groupe fictif ---------- */
  var SPEC = { nom: "SPECIMEN", prenom: "CAMILLE", pays: "FRA", nat: "FRANÇAISE", num: "23AF41907", sexe: "F",
    naissance: "14/05/1986", dobMrz: "860514", expiration: "22/09/2033", expMrz: "330922",
    type: "PP", dest: "SÉMINAIRE LISBONNE", score: "0,98" };
  SPEC.mrz = td3(SPEC);

  var GROUPE = [
    SPEC,
    { nom: "MARTIN", prenom: "CLAIRE", sexe: "F", naissance: "02/11/1979", expiration: "17/03/2031", nat: "FRANÇAISE", num: "19CK52874", type: "PP", score: "0,99" },
    { nom: "BERNARD", prenom: "JULIEN", sexe: "M", naissance: "28/06/1990", expiration: "04/02/2032", nat: "FRANÇAISE", num: "X4RT82J61", type: "PI", score: "0,97" },
    { nom: "PETIT", prenom: "SOPHIE", sexe: "F", naissance: "11/01/1984", expiration: "30/08/2029", nat: "FRANÇAISE", num: "21DE63095", type: "PP", score: "0,99" },
    { nom: "DUBOIS", prenom: "THOMAS", sexe: "M", naissance: "19/09/1976", expiration: "12/12/2026", nat: "FRANÇAISE", num: "16AB90412", type: "PP", score: "0,96" },
    { nom: "MOREAU", prenom: "LUCIE", sexe: "F", naissance: "07/04/1995", expiration: "21/05/2030", nat: "FRANÇAISE", num: "20HF47730", type: "PP", score: "0,98" },
    { nom: "LAURENT", prenom: "HUGO", sexe: "M", naissance: "25/12/1988", expiration: "09/10/2033", nat: "FRANÇAISE", num: "Y7PL31Q08", type: "PI", score: "0,95" },
    { nom: "SIMON", prenom: "MANON", sexe: "F", naissance: "30/03/1992", expiration: "15/07/2028", nat: "FRANÇAISE", num: "18GH20563", type: "PP", score: "0,82" },
    { nom: "MICHEL", prenom: "ANTOINE", sexe: "M", naissance: "13/08/1981", expiration: "03/01/2034", nat: "FRANÇAISE", num: "24JK71180", type: "PP", score: "0,99" },
    { nom: "LEFEBVRE", prenom: "CHLOÉ", sexe: "F", naissance: "22/02/1998", expiration: "26/11/2031", nat: "FRANÇAISE", num: "21LM09347", type: "PP", score: "0,97" },
    { nom: "GARCIA", prenom: "NICOLAS", sexe: "M", naissance: "05/10/1973", expiration: "18/06/2029", nat: "FRANÇAISE", num: "Z2WN58T43", type: "PI", score: "0,96" },
    { nom: "ROUX", prenom: "PAULINE", sexe: "F", naissance: "16/07/1986", expiration: "29/04/2032", nat: "FRANÇAISE", num: "22PQ86201", type: "PP", score: "0,98" }
  ];
  GROUPE.forEach(function(g){ g.dest = "SÉMINAIRE LISBONNE"; if (!g.pays) g.pays = "FRA"; });

  /* Colonnes du fichier exporté par l'application, dans le même ordre */
  var COLS = [
    { k: "nom", t: "Nom de famille" }, { k: "prenom", t: "Prénom" }, { k: "sexe", t: "Sexe" },
    { k: "naissance", t: "Date de naissance" }, { k: "expiration", t: "Date d’expiration" }, { k: "nat", t: "Nationalité" },
    { k: "num", t: "Numéro de document" }, { k: "type", t: "Type" }, { k: "dest", t: "Destination" }, { k: "score", t: "Score de confiance" }
  ];

  function esc(s){ return String(s == null ? "" : s).replace(/[&<>"]/g, function(c){ return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  /* ---------- Vagues guillochées (fond du passeport) ---------- */
  function wavePaths(w, h, n, seed){
    var out = [], s = seed || 1;
    for (var i = 0; i < n; i++){
      var d = "", y0 = (h / (n - 1)) * i;
      for (var x = -20; x <= w + 20; x += 18){
        var y = y0 + 16 * Math.sin(x / 96 + i * .55 + s) + 8 * Math.sin(x / 41 + i * 1.3 + s * 2);
        d += (x === -20 ? "M" : "L") + x.toFixed(0) + " " + y.toFixed(1);
      }
      out.push(d);
    }
    return out;
  }

  /* ---------- Portrait du spécimen : gravure, comme les billets ---------- */
  function portraitSVG(id, H){
    var X = 60, Y = 160, B = Y + H, ink = "#1D2635";
    var sil = '<ellipse cx="210" cy="318" rx="82" ry="104"/><path d="M181 396L239 396L244 ' + (B - 104) + 'L176 ' + (B - 104) + 'Z"/>' +
      '<path d="M64 ' + B + 'C72 ' + (B - 70) + ' 118 ' + (B - 100) + ' 178 ' + (B - 114) + 'L242 ' + (B - 114) + 'C302 ' + (B - 100) + ' 348 ' + (B - 70) + ' 356 ' + B + 'Z"/>';
    var box = '<rect x="' + X + '" y="' + Y + '" width="300" height="' + H + '" rx="12"';
    var lines = "", hatch = "";
    for (var i = 0; i < 66; i++){
      var y = Y + 4 + i * 6.4, dd = "";
      for (var x = X; x <= X + 300; x += 10){ dd += (x === X ? "M" : "L") + x + " " + (y + 1.5 * Math.sin(x / 17 + i * .45)).toFixed(1); }
      lines += '<path d="' + dd + '"/>';
    }
    for (var j = -20; j < 50; j++){ var x0 = 150 + j * 7; hatch += '<path d="M' + x0 + " " + Y + "L" + (x0 + 260) + " " + B + '"/>'; }
    return '<defs><clipPath id="' + id + 'pb">' + box + '/></clipPath><clipPath id="' + id + 'ps">' + sil + '</clipPath>' +
      '<clipPath id="' + id + 'pr"><rect x="236" y="' + Y + '" width="130" height="' + H + '"/></clipPath>' +
      '<linearGradient id="' + id + 'pm" x1="0" y1="0" x2="1" y2="0"><stop offset=".15" stop-color="#fff" stop-opacity=".5"/><stop offset=".75" stop-color="#fff" stop-opacity="1"/></linearGradient>' +
      '<mask id="' + id + 'pk"><rect x="' + X + '" y="' + Y + '" width="300" height="' + H + '" fill="url(#' + id + 'pm)"/></mask></defs>' +
      box + ' fill="#EDEFF3"/>' +
      '<g clip-path="url(#' + id + 'pb)" fill="none" stroke="#9EA7B5" stroke-width=".9" opacity=".6">' + lines + "</g>" +
      '<g clip-path="url(#' + id + 'ps)"><g mask="url(#' + id + 'pk)" fill="none" stroke="' + ink + '" stroke-width="2.5">' + lines + "</g>" +
        '<g clip-path="url(#' + id + 'pr)" fill="none" stroke="' + ink + '" stroke-width="1.1" opacity=".55">' + hatch + "</g></g>" +
      box + ' fill="none" stroke="#C3C9D4" stroke-width="2"/>';
  }

  /* ---------- Passeport spécimen (page de données, 125 × 88 mm) ---------- */
  var PP_UID = 0;
  function passport(o){
    o = o || {};
    var p = o.data || SPEC, id = "pp" + (++PP_UID), mini = o.mini;
    var brand = o.brand || "#6B2033", light = o.light || "#17B2DA";
    var waves = wavePaths(1250, 880, mini ? 10 : 16, o.seed || 1.7);
    var g = "";
    waves.forEach(function(d, i){ g += '<path d="' + d + '" stroke="' + (i % 2 ? light : brand) + '" stroke-opacity="' + (i % 2 ? .13 : .1) + '"/>'; });
    function field(x, y, label, val, k){
      return '<text x="' + x + '" y="' + y + '" class="pp-l">' + esc(label) + '</text>' +
             '<text x="' + x + '" y="' + (y + 42) + '" class="pp-v" data-k="' + k + '">' + esc(val) + '</text>';
    }
    var fields = mini ? (
        field(400, 196, "Nom / Surname", p.nom, "nom") +
        field(400, 296, "Prénoms / Given names", p.prenom, "prenom") +
        field(400, 396, "Date de naissance / Date of birth", p.naissance.replace(/\//g, " "), "naissance") +
        field(400, 496, "Date d’expiration / Date of expiry", p.expiration.replace(/\//g, " "), "expiration")
      ) : (
        field(400, 176, "Type / Type", "P", "ptype") +
        field(560, 176, "Code du pays / Code", "FRA", "pays") +
        field(820, 176, "Passeport n° / Passport No.", p.num, "num") +
        field(400, 268, "Nom / Surname", p.nom, "nom") +
        field(400, 360, "Prénoms / Given names", p.prenom, "prenom") +
        field(400, 452, "Nationalité / Nationality", p.nat, "nat") +
        field(820, 452, "Sexe / Sex", p.sexe || "F", "sexe") +
        field(400, 544, "Date de naissance / Date of birth", p.naissance.replace(/\//g, " "), "naissance") +
        field(820, 544, "Date d’expiration / Date of expiry", p.expiration.replace(/\//g, " "), "expiration")
      );
    var mrz = p.mrz || SPEC.mrz;
    var H = mini ? 400 : 420;
    var portrait = "<g>" + portraitSVG(id, H) + "</g>";
    var ghost = mini ? "" : '<g transform="translate(1080 196) scale(.34)" opacity=".42">' + portraitSVG(id + "x", 420) + "</g>";
    return '' +
      '<svg class="pp' + (mini ? " pp--mini" : "") + '" viewBox="0 0 1250 880" role="img" aria-label="Page de données d’un passeport spécimen : ' + esc(p.nom) + " " + esc(p.prenom) + ', données fictives">' +
      '<defs><clipPath id="' + id + 'c"><rect width="1250" height="880" rx="38"/></clipPath>' +
      '<linearGradient id="' + id + 'g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F7F3F4"/><stop offset=".55" stop-color="#F1F2F5"/><stop offset="1" stop-color="#ECF1F5"/></linearGradient></defs>' +
      '<g clip-path="url(#' + id + 'c)">' +
        '<rect width="1250" height="880" fill="url(#' + id + 'g)"/>' +
        '<g fill="none" stroke-width="1.3">' + g + "</g>" +
        '<text x="660" y="560" transform="rotate(-16 660 560)" text-anchor="middle" class="pp-wm" fill="' + brand + '">SPÉCIMEN</text>' +
        '<text x="60" y="104" class="pp-h" fill="' + brand + '">PASSEPORT</text>' +
        '<text x="60" y="134" class="pp-h2" fill="' + brand + '">PASSPORT · DONNÉES FICTIVES</text>' +
        '<text x="1190" y="104" text-anchor="end" class="pp-h2" fill="' + brand + '">SPÉCIMEN · SCANID</text>' +
        portrait + ghost + fields +
        '<rect x="0" y="' + (mini ? 640 : 668) + '" width="1250" height="240" fill="#FFFFFF" fill-opacity=".62"/>' +
        '<text x="60" y="' + (mini ? 736 : 752) + '" class="pp-mrz" textLength="1130" lengthAdjust="spacingAndGlyphs" data-k="mrz1">' + esc(mrz.l1) + "</text>" +
        '<text x="60" y="' + (mini ? 818 : 828) + '" class="pp-mrz" textLength="1130" lengthAdjust="spacingAndGlyphs" data-k="mrz2">' + esc(mrz.l2) + "</text>" +
      "</g>" +
      '<rect x="1" y="1" width="1248" height="878" rx="37" fill="none" stroke="#C9CDD6" stroke-width="2"/>' +
      "</svg>";
  }

  /* ---------- Guilloches (canvas) ---------- */
  function gcd(a, b){ return b ? gcd(b, a % b) : a; }
  function rosette(canvas, layers, opt){
    opt = opt || {};
    var size = opt.size || 1200, ctx = canvas.getContext("2d");
    canvas.width = size; canvas.height = size;
    ctx.clearRect(0, 0, size, size);
    var maxR = 0;
    layers.forEach(function(L){ var m = L.type === "epi" ? L.R + L.r + L.d : Math.abs(L.R - L.r) + L.d; if (m > maxR) maxR = m; });
    var k = (size / 2 * .97) / maxR, c = size / 2;
    layers.forEach(function(L){
      var R = L.R, r = L.r, d = L.d, turns = r / gcd(R, r), T = Math.PI * 2 * turns, step = L.step || .004;
      ctx.beginPath();
      for (var t = 0; t <= T + step; t += step){
        var x, y, a = L.rot || 0;
        if (L.type === "epi"){ x = (R + r) * Math.cos(t) - d * Math.cos((R + r) / r * t); y = (R + r) * Math.sin(t) - d * Math.sin((R + r) / r * t); }
        else { x = (R - r) * Math.cos(t) + d * Math.cos((R - r) / r * t); y = (R - r) * Math.sin(t) - d * Math.sin((R - r) / r * t); }
        var xr = x * Math.cos(a) - y * Math.sin(a), yr = x * Math.sin(a) + y * Math.cos(a);
        if (t === 0) ctx.moveTo(c + xr * k, c + yr * k); else ctx.lineTo(c + xr * k, c + yr * k);
      }
      ctx.strokeStyle = L.color; ctx.globalAlpha = L.alpha == null ? .5 : L.alpha; ctx.lineWidth = L.lw || 1;
      ctx.stroke();
    });
    ctx.globalAlpha = 1;
  }
  var ROSETTES = {
    hero: [
      { R: 210, r: 74, d: 122, color: "#17B2DA", alpha: .5, lw: 1.1 },
      { R: 210, r: 74, d: 100, color: "#17B2DA", alpha: .26, lw: 1, rot: .045 },
      { R: 182, r: 52, d: 132, color: "#B8506A", alpha: .55, lw: 1.1 },
      { type: "epi", R: 300, r: 20, d: 36, color: "#17B2DA", alpha: .3, lw: 1, step: .002 }
    ],
    band: [
      { R: 196, r: 44, d: 110, color: "#17B2DA", alpha: .42, lw: 1.1 },
      { R: 196, r: 44, d: 84, color: "#17B2DA", alpha: .22, lw: 1, rot: .06 },
      { R: 166, r: 54, d: 140, color: "#B8506A", alpha: .5, lw: 1.1 },
      { type: "epi", R: 286, r: 18, d: 26, color: "#E8EEF1", alpha: .14, lw: .9, step: .002 }
    ],
    menu: [
      { R: 220, r: 60, d: 118, color: "#17B2DA", alpha: .35, lw: 1 },
      { R: 188, r: 46, d: 128, color: "#B8506A", alpha: .4, lw: 1 },
      { type: "epi", R: 300, r: 22, d: 30, color: "#E8EEF1", alpha: .1, lw: .9, step: .002 }
    ]
  };

  /* ---------- Tableaux et fichiers d'exemple ---------- */
  function tableHTML(rows, opt){
    opt = opt || {};
    var cols = opt.cols || COLS;
    var h = '<table class="xl"><thead><tr>' + cols.map(function(c){ return '<th scope="col" data-col="' + c.k + '">' + esc(c.t) + "</th>"; }).join("") + "</tr></thead><tbody>";
    rows.forEach(function(r, i){
      h += '<tr data-i="' + i + '" data-type="' + esc(r.type) + '">' +
        cols.map(function(c){
          var v = r[c.k];
          if (c.k === "score"){ var s = parseFloat(String(v).replace(",", ".")); return '<td data-col="score" class="' + (s < .9 ? "low" : "") + '"><span class="sc"><i style="--s:' + s + '"></i>' + esc(v) + "</span></td>"; }
          return '<td data-col="' + c.k + '">' + esc(v) + "</td>";
        }).join("") + "</tr>";
    });
    return h + "</tbody></table>";
  }
  function csv(rows){
    var head = COLS.map(function(c){ return c.t.replace(/’/g, "'"); }).join(";");
    return "﻿" + head + "\r\n" + rows.map(function(r){ return COLS.map(function(c){ return String(r[c.k] == null ? "" : r[c.k]).replace(/;/g, ","); }).join(";"); }).join("\r\n") + "\r\n";
  }

  return { td3: td3, checkDigit: checkDigit, mrzText: mrzText, SPEC: SPEC, GROUPE: GROUPE, COLS: COLS, esc: esc,
           passport: passport, rosette: rosette, ROSETTES: ROSETTES, tableHTML: tableHTML, csv: csv, wavePaths: wavePaths };
})();
