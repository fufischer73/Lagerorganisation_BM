/* Interaktive Übungen: <div class="uebung" data-uebung='{"typ": …}'></div>
   Typen: auswahl, zuordnen, luecken, reihenfolge, rechnen. bausteine.py erzeugt die Daten aus :::uebung.
   Läuft rein im Browser (auch im Moodle-Lernpaket), nichts wird gespeichert oder gesendet. */
(function () {
  "use strict";

  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    if (attrs) for (var k in attrs) if (attrs.hasOwnProperty(k)) e.setAttribute(k, attrs[k]);
    if (html != null) e.innerHTML = html;
    return e;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function mischen(a) {
    var b = a.slice();
    for (var i = b.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = b[i]; b[i] = b[j]; b[j] = t; }
    return b;
  }
  function gleich(a, b) { return a.length === b.length && a.every(function (x, i) { return x === b[i]; }); }
  function text(html) {
    var d = document.createElement("div"); d.innerHTML = html;
    var bilder = d.querySelectorAll("img");
    for (var i = 0; i < bilder.length; i++) bilder[i].parentNode.replaceChild(document.createTextNode(bilder[i].alt || "Bild"), bilder[i]);
    return (d.textContent || "").trim();
  }
  function norm(s) { return String(s).toLowerCase().replace(/\s+/g, " ").trim(); }

  // „12,96“, „1.274“, „1 274 Stück“, „5 %“ → Zahl (NaN, wenn keine Zahl)
  function zahl(s) {
    var t = String(s).replace(/[\s ]/g, "").replace(/[^\d.,\-]+$/, "");
    if (/^-?\d{1,3}(\.\d{3})+(,\d+)?$/.test(t)) t = t.replace(/\./g, "");
    t = t.replace(",", ".");
    return /^-?\d+(\.\d+)?$/.test(t) ? parseFloat(t) : NaN;
  }

  var uid = 0;

  function geruest(d, box) {
    box.innerHTML = "";
    box.appendChild(el("div", { "class": "box-title" }, "🧩 Übung" + (d.titel ? ": " + d.titel : "")));
    if (d.frage) box.appendChild(el("p", { "class": "ue-frage" }, d.frage));
    var feld = el("div", { "class": "ue-feld" });
    var knoepfe = el("div", { "class": "ue-knoepfe" });
    var fb = el("div", { "class": "ue-fb", "role": "status", "aria-live": "polite" });
    box.appendChild(feld);
    box.appendChild(knoepfe);
    box.appendChild(fb);
    return { feld: feld, knoepfe: knoepfe, fb: fb };
  }
  function knopf(label, fn, cls) {
    var b = el("button", { type: "button", "class": "btn ue-btn" + (cls ? " " + cls : "") }, label);
    b.addEventListener("click", fn);
    return b;
  }
  function meldung(fb, ok, msg) {
    fb.className = "ue-fb " + (ok ? "ok" : "bad");
    fb.innerHTML = (ok ? "✅ " : "❌ ") + msg;
  }
  function erklaerung(d, fb) {
    if (d.erklaerung) fb.innerHTML += '<div class="ue-erkl">' + d.erklaerung + "</div>";
  }

  // ---------- auswahl ----------
  function auswahl(d, box) {
    var g = geruest(d, box), mehrere = d.optionen.filter(function (o) { return o.richtig; }).length > 1;
    var liste = el("div", { "class": "ue-optionen", role: mehrere ? "group" : "radiogroup" });
    var opts = mischen(d.optionen), gewaehlt = [], fertig = false;
    var bilder = opts.some(function (o) { return /<img/i.test(o.text); });
    if (bilder) liste.className += " bilder";
    var btns = opts.map(function (o, i) {
      var b = el("button", { type: "button", "class": "ue-opt", "aria-pressed": "false" }, o.text);
      b.addEventListener("click", function () {
        if (fertig) return;
        if (mehrere) {
          var pos = gewaehlt.indexOf(i);
          if (pos > -1) gewaehlt.splice(pos, 1); else gewaehlt.push(i);
          b.setAttribute("aria-pressed", pos > -1 ? "false" : "true");
          b.classList.toggle("sel", pos === -1);
        } else {
          pruefenAuswahl([i]);
        }
      });
      liste.appendChild(b);
      return b;
    });
    g.feld.appendChild(liste);
    function pruefenAuswahl(sel) {
      var richtig = sel.length > 0 && sel.every(function (i) { return opts[i].richtig; }) &&
        opts.filter(function (o) { return o.richtig; }).length === sel.length;
      btns.forEach(function (b, i) { b.classList.remove("right", "wrong"); });
      if (richtig) {
        fertig = true;
        sel.forEach(function (i) { btns[i].classList.add("right"); });
        meldung(g.fb, true, (sel.length === 1 && opts[sel[0]].feedback) || "Richtig!");
        erklaerung(d, g.fb);
      } else {
        sel.forEach(function (i) { btns[i].classList.add("wrong"); });
        meldung(g.fb, false, (sel.length === 1 && opts[sel[0]].feedback) || d.hinweis || "Noch nicht ganz. Versuche es noch einmal.");
      }
    }
    if (mehrere) {
      g.knoepfe.appendChild(el("span", { "class": "ue-info" }, "Mehrere Antworten sind richtig."));
      g.knoepfe.appendChild(knopf("Prüfen", function () { if (!fertig) pruefenAuswahl(gewaehlt.slice()); }));
    }
  }

  // ---------- zuordnen ----------
  function zuordnen(d, box) {
    var g = geruest(d, box), id = "ue" + (++uid);
    var rechts = [], i;
    d.paare.forEach(function (p) { if (rechts.indexOf(p[1]) < 0) rechts.push(p[1]); });
    (d.ablenker || []).forEach(function (a) { if (rechts.indexOf(a) < 0) rechts.push(a); });
    var optionen = mischen(rechts);
    var tabelle = el("div", { "class": "ue-zeilen" }), selects = [];
    d.paare.forEach(function (p, n) {
      var zeile = el("div", { "class": "ue-zeile" });
      zeile.appendChild(el("span", { "class": "ue-links", id: id + "-" + n }, p[0]));
      var s = el("select", { "aria-labelledby": id + "-" + n });
      s.appendChild(el("option", { value: "" }, "– wählen –"));
      optionen.forEach(function (o, k) { s.appendChild(el("option", { value: String(k) }, text(o))); });
      s.addEventListener("change", function () { s.className = ""; });
      zeile.appendChild(s);
      tabelle.appendChild(zeile);
      selects.push(s);
    });
    g.feld.appendChild(tabelle);
    var versuch = 0, loes = null;
    g.knoepfe.appendChild(knopf("Prüfen", function () {
      var richtig = 0, leer = 0;
      selects.forEach(function (s, n) {
        if (s.value === "") { leer++; s.className = ""; return; }
        var ok = optionen[+s.value] === d.paare[n][1];
        s.className = ok ? "right" : "wrong";
        if (ok) richtig++;
      });
      versuch++;
      if (leer) { meldung(g.fb, false, "Bitte ordne zuerst alle Zeilen zu (" + leer + " fehlen noch)."); return; }
      if (richtig === d.paare.length) { meldung(g.fb, true, "Alles richtig!"); erklaerung(d, g.fb); if (loes) loes.hidden = true; }
      else {
        meldung(g.fb, false, richtig + " von " + d.paare.length + " richtig. " + (d.hinweis || "Die rot markierten Zeilen noch einmal prüfen."));
        if (versuch >= 2 && !loes) {
          loes = knopf("Lösung zeigen", function () {
            selects.forEach(function (s, n) { s.value = String(optionen.indexOf(d.paare[n][1])); s.className = "right"; });
            meldung(g.fb, true, "So ist es richtig."); erklaerung(d, g.fb); loes.hidden = true;
          }, "ue-sek");
          g.knoepfe.appendChild(loes);
        }
      }
    }));
  }

  // ---------- luecken ----------
  function luecken(d, box) {
    var g = geruest(d, box), p = el("p", { "class": "ue-text" }), felder = [];
    d.teile.forEach(function (t) {
      if (t.t != null) { p.appendChild(el("span", null, t.t)); return; }
      var f;
      if (t.wahl) {
        f = el("select", { "class": "ue-luecke", "aria-label": "Lücke " + (felder.length + 1) });
        f.appendChild(el("option", { value: "" }, "– wählen –"));
        mischen(t.wahl).forEach(function (w) { f.appendChild(el("option", { value: w }, esc(w))); });
      } else {
        f = el("input", { type: "text", "class": "ue-luecke", autocomplete: "off", autocapitalize: "off", spellcheck: "false", "aria-label": "Lücke " + (felder.length + 1) });
        f.style.width = Math.max(7, Math.min(24, Math.max.apply(null, t.antworten.map(function (a) { return a.length; })) + 2)) + "ch";
      }
      f.addEventListener("input", function () { f.className = "ue-luecke"; });
      felder.push({ f: f, t: t });
      p.appendChild(f);
    });
    g.feld.appendChild(p);
    var versuch = 0, loes = null;
    function ok(x) {
      var w = x.f.value;
      if (x.t.wahl) return w === x.t.wahl[0];
      return x.t.antworten.some(function (a) {
        if (norm(a) === norm(w)) return true;
        var za = zahl(a), zw = zahl(w);
        return !isNaN(za) && !isNaN(zw) && Math.abs(za - zw) < 1e-9;
      });
    }
    g.knoepfe.appendChild(knopf("Prüfen", function () {
      var richtig = 0, leer = 0;
      felder.forEach(function (x) {
        if (!x.f.value) { leer++; x.f.className = "ue-luecke"; return; }
        var r = ok(x); x.f.className = "ue-luecke " + (r ? "right" : "wrong"); if (r) richtig++;
      });
      versuch++;
      if (leer) { meldung(g.fb, false, "Fülle zuerst alle Lücken aus (" + leer + " fehlen noch)."); return; }
      if (richtig === felder.length) { meldung(g.fb, true, "Alles richtig!"); erklaerung(d, g.fb); if (loes) loes.hidden = true; }
      else {
        meldung(g.fb, false, richtig + " von " + felder.length + " Lücken richtig. " + (d.hinweis || "Die rot markierten Lücken noch einmal prüfen."));
        if (versuch >= 2 && !loes) {
          loes = knopf("Lösung zeigen", function () {
            felder.forEach(function (x) { x.f.value = x.t.wahl ? x.t.wahl[0] : x.t.antworten[0]; x.f.className = "ue-luecke right"; });
            meldung(g.fb, true, "So ist es richtig."); erklaerung(d, g.fb); loes.hidden = true;
          }, "ue-sek");
          g.knoepfe.appendChild(loes);
        }
      }
    }));
  }

  // ---------- reihenfolge ----------
  function reihenfolge(d, box) {
    var g = geruest(d, box), n = d.schritte.length, fertig = false;
    var order = [], i;
    for (i = 0; i < n; i++) order.push(i);
    var tries = 0;
    do { order = mischen(order); tries++; } while (tries < 20 && order.every(function (v, k) { return v === k; }));
    var ol = el("ol", { "class": "ue-reihe" });
    g.feld.appendChild(ol);
    function zeichne(fokus) {
      ol.innerHTML = "";
      order.forEach(function (idx, pos) {
        var li = el("li");
        li.appendChild(el("span", { "class": "ue-schritt" }, d.schritte[idx]));
        var bb = el("span", { "class": "ue-pfeile" });
        var hoch = el("button", { type: "button", "class": "ue-pfeil", "aria-label": "Nach oben" }, "▲");
        var runter = el("button", { type: "button", "class": "ue-pfeil", "aria-label": "Nach unten" }, "▼");
        hoch.disabled = pos === 0 || fertig; runter.disabled = pos === n - 1 || fertig;
        hoch.addEventListener("click", function () { tausche(pos, pos - 1, "hoch"); });
        runter.addEventListener("click", function () { tausche(pos, pos + 1, "runter"); });
        bb.appendChild(hoch); bb.appendChild(runter); li.appendChild(bb);
        if (fokus && fokus.pos === pos) li.setAttribute("data-fokus", fokus.art);
        ol.appendChild(li);
      });
      var f = ol.querySelector("[data-fokus]");
      if (f) { var b = f.querySelectorAll("button")[f.getAttribute("data-fokus") === "hoch" ? 0 : 1]; if (b && !b.disabled) b.focus(); else { var alt = f.querySelector("button:not([disabled])"); if (alt) alt.focus(); } }
    }
    function tausche(a, b, art) {
      var t = order[a]; order[a] = order[b]; order[b] = t;
      g.fb.className = "ue-fb"; g.fb.innerHTML = "";
      zeichne({ pos: b, art: art });
    }
    zeichne();
    g.knoepfe.appendChild(knopf("Prüfen", function () {
      var richtig = 0;
      var lis = ol.children;
      order.forEach(function (idx, pos) {
        var ok = idx === pos; if (ok) richtig++;
        lis[pos].className = ok ? "right" : "wrong";
      });
      if (richtig === n) { fertig = true; meldung(g.fb, true, "Die Reihenfolge stimmt!"); erklaerung(d, g.fb); zeichne(); for (var k = 0; k < ol.children.length; k++) ol.children[k].className = "right"; }
      else meldung(g.fb, false, richtig + " von " + n + " Schritten stehen an der richtigen Stelle. " + (d.hinweis || "Verschiebe die rot markierten Schritte."));
    }));
  }

  // ---------- rechnen ----------
  function rechnen(d, box) {
    var g = geruest(d, box), felder = [], zeilen = el("div", { "class": "ue-rechnen" });
    d.ergebnisse.forEach(function (e, n) {
      var z = el("label", { "class": "ue-rzeile" });
      z.appendChild(el("span", { "class": "ue-rlabel" }, e.label));
      var inp = el("input", { type: "text", inputmode: "decimal", autocomplete: "off", "class": "ue-zahl", "aria-label": text(e.label) });
      inp.addEventListener("input", function () { inp.className = "ue-zahl"; });
      z.appendChild(inp);
      if (e.einheit) z.appendChild(el("span", { "class": "ue-einheit" }, esc(e.einheit)));
      zeilen.appendChild(z);
      felder.push(inp);
    });
    g.feld.appendChild(zeilen);
    var versuch = 0;
    function pruef() {
      var richtig = 0, leer = 0;
      felder.forEach(function (inp, n) {
        var e = d.ergebnisse[n];
        if (!inp.value.trim()) { leer++; inp.className = "ue-zahl"; return; }
        var v = zahl(inp.value), ok = !isNaN(v) && Math.abs(v - e.wert) <= (e.toleranz || 0) + 1e-9;
        inp.className = "ue-zahl " + (ok ? "right" : "wrong");
        if (ok) richtig++;
      });
      versuch++;
      if (leer) { meldung(g.fb, false, "Trage zuerst alle Ergebnisse ein."); return; }
      if (richtig === felder.length) { meldung(g.fb, true, "Richtig gerechnet!"); erklaerung(d, g.fb); return; }
      var extra = "";
      felder.forEach(function (inp) { if (inp.className.indexOf("wrong") > -1 && isNaN(zahl(inp.value))) extra = " Gib nur Zahlen ein, zum Beispiel 12,96."; });
      meldung(g.fb, false, richtig + " von " + felder.length + " Ergebnissen stimmen." + extra + " " + (d.hinweis || "Öffne den Tipp oder den Rechenweg."));
    }
    g.knoepfe.appendChild(knopf("Prüfen", pruef));
    felder.forEach(function (inp) { inp.addEventListener("keydown", function (ev) { if (ev.key === "Enter") { ev.preventDefault(); pruef(); } }); });
  }

  var TYPEN = { auswahl: auswahl, zuordnen: zuordnen, luecken: luecken, reihenfolge: reihenfolge, rechnen: rechnen };

  document.addEventListener("DOMContentLoaded", function () {
    var boxen = document.querySelectorAll("[data-uebung]");
    for (var i = 0; i < boxen.length; i++) {
      try {
        var d = JSON.parse(boxen[i].getAttribute("data-uebung"));
        if (TYPEN[d.typ]) TYPEN[d.typ](d, boxen[i]);
      } catch (e) {
        boxen[i].innerHTML = '<div class="box-title">Übung konnte nicht geladen werden</div>';
      }
    }
  });
})();
