#!/usr/bin/env python3
"""Baut die Lösungsblätter und Arbeitsblätter (PDF) für den Lernpfad und danach die Web-Version neu.

Ablauf:
  1. Web-Version bauen (die PDFs dürfen dabei noch leer sein, sie werden nur verlinkt).
  2. Jede Modulseite im Browser öffnen, alle Übungen mit der Musterlösung ausfüllen,
     alle Hilfen aufklappen und die Seite als PDF speichern (material/pdf/<modul>-loesungen.pdf).
  3. Arbeitsblatt zum Ausdrucken (ohne Lösungen, mit Schreibzeilen): material/pdf/<modul>-arbeitsblatt.pdf
  4. Web-Version noch einmal bauen, damit die fertigen PDFs in ausgabe/web/material/pdf liegen.

Aufruf:  python3 tools/pdfs.py [--baukasten <Ordner des Lernpfad-Baukastens>]
Voraussetzung: pip install playwright (und ein Chrome/Chromium).
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
PFAD = WURZEL / "lernpfad-lager"
PDF = PFAD / "material" / "pdf"

# Muster-Antworten eintragen und prüfen (läuft im Browser)
LOESEN = r"""
() => {
  const plain = h => { const d = document.createElement("div"); d.innerHTML = h;
    d.querySelectorAll("img").forEach(i => i.replaceWith(document.createTextNode(i.alt || "Bild")));
    return (d.textContent || "").trim(); };
  const norm = h => { const d = document.createElement("div"); d.innerHTML = h; return d.innerHTML; };
  const knopf = (box, t) => Array.from(box.querySelectorAll("button")).find(b => b.textContent.trim() === t);
  const tipp = (el, v) => { el.value = v; el.dispatchEvent(new Event("input", { bubbles: true })); el.dispatchEvent(new Event("change", { bubbles: true })); };
  document.querySelectorAll("[data-uebung]").forEach(box => {
    const d = JSON.parse(box.getAttribute("data-uebung"));
    if (d.typ === "rechnen") {
      box.querySelectorAll("input").forEach((inp, k) => tipp(inp, d.ergebnisse[k].text));
      knopf(box, "Prüfen").click();
    } else if (d.typ === "zuordnen") {
      box.querySelectorAll("select").forEach((s, k) => {
        const ziel = plain(d.paare[k][1]);
        const o = Array.from(s.options).find(o => o.textContent.trim() === ziel);
        tipp(s, o.value);
      });
      knopf(box, "Prüfen").click();
    } else if (d.typ === "luecken") {
      let i = 0, s = 0;
      const felder = box.querySelectorAll("input.ue-luecke, select.ue-luecke");
      d.teile.forEach(t => {
        if (t.t != null) return;
        const f = felder[i++];
        tipp(f, t.wahl ? t.wahl[0] : t.antworten[0]);
      });
      knopf(box, "Prüfen").click();
    } else if (d.typ === "reihenfolge") {
      const soll = d.schritte.map(plain);
      for (let n = 0; n < 80; n++) {
        const lis = Array.from(box.querySelectorAll(".ue-reihe li"));
        const ist = lis.map(li => li.querySelector(".ue-schritt").textContent.trim());
        const pos = soll.findIndex((w, q) => ist[q] !== w);
        if (pos < 0) break;
        const von = ist.indexOf(soll[pos]);
        lis[von].querySelector("button[aria-label='Nach oben']").click();
      }
      knopf(box, "Prüfen").click();
    } else if (d.typ === "auswahl") {
      const richtig = d.optionen.filter(o => o.richtig);
      const btns = Array.from(box.querySelectorAll(".ue-opt"));
      richtig.forEach(o => { const b = btns.find(b => norm(b.innerHTML) === norm(o.text)); if (b) b.click(); });
      if (richtig.length > 1) knopf(box, "Prüfen").click();
    }
  });
  document.querySelectorAll("details").forEach(d => { d.classList.remove("gesperrt"); d.open = true;
    const s = d.querySelector("summary"); if (s) s.innerHTML = s.innerHTML.replace(/^🔒\s*/, ""); });
}
"""


# Arbeitsblatt: nur Aufgaben (ohne Hilfen und Lösungen), Übungen zum Ausfüllen auf Papier
ARBEITSBLATT = r"""
(titel) => {
  const plain = h => { const d = document.createElement("div"); d.innerHTML = h;
    d.querySelectorAll("img").forEach(i => i.replaceWith(document.createTextNode(i.alt || "Bild")));
    return (d.textContent || "").trim(); };
  const drehen = a => a.length > 1 ? a.slice(2).concat(a.slice(0, 2)) : a;     // feste, „gemischte“ Reihenfolge
  const frageText = f => (f || "").replace(/\s*(Wähle|Klicke)[^.]*klicke auf „Prüfen“\./i, "").replace(/ Wähle alle richtigen Antworten und klicke auf „Prüfen“\./, " Mehrere Antworten sind richtig.");
  const leer = (k) => '<span class="ab-leer ' + (k || "") + '"></span>';
  function druck(d) {
    let h = d.titel ? '<div class="ab-ut">' + d.titel + "</div>" : "";
    if (d.frage) h += '<p class="ab-frage">' + frageText(d.frage) + "</p>";
    if (d.typ === "rechnen") {
      h += d.ergebnisse.map(e => '<div class="ab-zeile"><span class="ab-lab">' + e.label + "</span> " + leer("mittel") + " " + (e.einheit || "") + "</div>").join("");
    } else if (d.typ === "zuordnen") {
      const r = []; d.paare.forEach(p => { if (r.indexOf(p[1]) < 0) r.push(p[1]); }); (d.ablenker || []).forEach(a => { if (r.indexOf(a) < 0) r.push(a); });
      h += '<table class="ab-tab"><tbody>' + d.paare.map(p => "<tr><td>" + p[0] + "</td><td>" + leer("breit") + "</td></tr>").join("") + "</tbody></table>";
      h += '<p class="ab-wahl"><b>Zur Auswahl:</b> ' + drehen(r).map(x => "„" + x + "“").join(" · ") + "</p>";
    } else if (d.typ === "luecken") {
      h += '<p class="ab-text">' + d.teile.map(t => t.t != null ? t.t : t.wahl
        ? '<i>(' + drehen(t.wahl).join(" / ") + ")</i> " + leer("kurz") : leer("mittel")).join("") + "</p>";
    } else if (d.typ === "reihenfolge") {
      h += d.schritte.length ? d.schritte.map((x, i) => i).length && "" : "";
      h += '<p class="ab-wahl">Trage die Zahlen 1 bis ' + d.schritte.length + " in die Kästchen ein.</p>";
      h += drehen(drehen(d.schritte)).map(x => '<div class="ab-zeile"><span class="ab-kasten"></span> ' + x + "</div>").join("");
    } else if (d.typ === "auswahl") {
      const n = d.optionen.filter(o => o.richtig).length;
      if (n > 1 && !/Mehrere Antworten/.test(h)) h += '<p class="ab-wahl">Mehrere Antworten sind richtig.</p>';
      h += '<div class="ab-optionen">' + drehen(d.optionen).map(o => '<div class="ab-opt"><span class="ab-kasten"></span> ' + o.text + "</div>").join("") + "</div>";
    }
    return h;
  }
  const main = document.querySelector("main");
  const ersteAufgabe = main.querySelector(".task");
  const teile = Array.from(main.querySelectorAll(".box.note, .task")).filter(e =>
    e.classList.contains("task") || (ersteAufgabe && (e.compareDocumentPosition(ersteAufgabe) & Node.DOCUMENT_POSITION_FOLLOWING)));
  const out = document.createElement("div"); out.id = "ab";
  out.innerHTML = "<h1>" + titel + '</h1><p class="ab-kopf">Name: <span class="ab-leer breit"></span> &nbsp; Datum: <span class="ab-leer mittel"></span> &nbsp; Klasse: <span class="ab-leer kurz"></span></p>';
  teile.forEach(e => {
    const c = e.cloneNode(true);
    c.querySelectorAll("details, .ue-fb, .ue-knoepfe").forEach(x => x.remove());
    let hatUebung = false;
    c.querySelectorAll("[data-uebung]").forEach(u => { hatUebung = true; u.innerHTML = druck(JSON.parse(u.getAttribute("data-uebung"))); u.classList.add("ab-uebung"); });
    c.querySelectorAll("input[type=checkbox]").forEach(i => { i.removeAttribute("checked"); i.checked = false; });
    if (c.classList.contains("task") && (!hatUebung || c.querySelector(".checkliste")))
      c.insertAdjacentHTML("beforeend", '<div class="ab-zeilen"><span></span><span></span><span></span><span></span></div>');
    out.appendChild(c);
  });
  main.innerHTML = ""; main.appendChild(out);
}
"""

AB_CSS = """
#topbar, #sidebar, .pager, .done-wrap, .note-box, .quiz, .nach-wrap, [data-lp], footer.site, .app-switch, .download { display: none !important; }
.layout { display: block !important; }
main { max-width: none !important; padding: 0 !important; }
body { background: #fff !important; }
.task, .box { break-inside: avoid; box-shadow: none !important; }
#ab h1 { margin: 0 0 .3rem; }
.ab-kopf { margin: 0 0 1rem; }
.ab-leer { display: inline-block; border-bottom: 1px solid #333; height: 1.1em; vertical-align: baseline; }
.ab-leer.kurz { width: 5rem; } .ab-leer.mittel { width: 9rem; } .ab-leer.breit { width: 17rem; }
.ab-ut { font-weight: 700; margin-bottom: .2rem; }
.ab-frage { font-weight: 600; margin: .3rem 0 .6rem; }
.ab-zeile { margin: .5rem 0; display: flex; gap: .5rem; align-items: baseline; }
.ab-lab { min-width: 13rem; font-weight: 600; }
.ab-tab { width: 100%; border-collapse: collapse; }
.ab-tab td { border: 1px solid #bbb; padding: .55rem .6rem; vertical-align: middle; }
.ab-tab td:first-child { width: 55%; }
.ab-wahl { font-size: .92rem; margin: .5rem 0; }
.ab-text { line-height: 2.4; }
.ab-kasten { display: inline-block; width: 1.3rem; height: 1.3rem; border: 1.5px solid #333; border-radius: 3px; flex: none; }
.ab-opt { margin: .4rem 0; display: flex; gap: .6rem; align-items: center; }
.ab-opt img { max-height: 90px; }
.ab-zeilen span { display: block; border-bottom: 1px solid #999; height: 2rem; }
.uebung { border-left-color: #888 !important; }
"""

DRUCK_CSS = """
#topbar, #sidebar, .pager, .done-wrap, .note-box, .quiz, .nach-wrap, [data-lp], footer.site,
.ue-knoepfe, .app-switch { display: none !important; }
.layout { display: block !important; }
main { max-width: none !important; padding: 0 !important; }
.box, details, figure, .table-wrap, .uebung { break-inside: avoid; }
body { background: #fff !important; }
"""


def baukasten_finden(arg):
    for p in (arg, os.environ.get("LERNPFAD_BAUKASTEN"), Path.home() / ".claude/skills/lernpfad-baukasten",
              WURZEL.parent / "Lernpfad-baukasten"):
        if p and (Path(p) / "skripte" / "bauen.py").is_file():
            return Path(p)
    sys.exit("Lernpfad-Baukasten nicht gefunden. Mit --baukasten <Ordner> angeben.")


def bauen(baukasten):
    r = subprocess.run([sys.executable, str(baukasten / "skripte" / "bauen.py"), str(PFAD)], capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[0] if r.stdout.strip() else r.stderr)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baukasten")
    ap.add_argument("--chrome", default=os.environ.get("CHROME_PFAD", "/opt/pw-browsers/chromium"))
    a = ap.parse_args()
    baukasten = baukasten_finden(a.baukasten)
    from playwright.sync_api import sync_playwright

    module = sorted(m.name for m in (PFAD / "module").glob("*.md"))
    ids = []
    for m in module:
        t = (PFAD / "module" / m).read_text(encoding="utf-8")
        if ":::nacherledigt" in t and re.search(r"material/pdf/([\w-]+)-loesungen\.pdf", t):
            ids.append(m[:-3])
    PDF.mkdir(parents=True, exist_ok=True)
    for i in ids:
        for art in ("loesungen", "arbeitsblatt"):
            (PDF / f"{i}-{art}.pdf").touch(exist_ok=True)
    bauen(baukasten)

    web = PFAD / "ausgabe" / "web"
    kurs = re.search(r"^titel: (.+)$", (PFAD / "kurs.yaml").read_text(encoding="utf-8"), re.M).group(1).strip('"')
    with sync_playwright() as p:
        launch = {"executable_path": a.chrome} if os.path.exists(a.chrome) else {}
        b = p.chromium.launch(**launch)
        pg = b.new_page(viewport={"width": 1000, "height": 1400})
        for i in ids:
            datei = next(web.glob(f"{i}-*.html"))
            kopf = html.escape(kurs)
            rand = {"top": "16mm", "bottom": "18mm", "left": "14mm", "right": "14mm"}

            def fuss(art):
                return (f'<div style="font-size:8px;width:100%;text-align:center;color:#666">{kopf} · {art} · '
                        'Seite <span class="pageNumber"></span> von <span class="totalPages"></span></div>')

            # Lösungsblatt
            pg.goto(datei.as_uri())
            pg.wait_for_timeout(400)
            pg.evaluate(LOESEN)
            pg.add_style_tag(content=DRUCK_CSS)
            pg.emulate_media(media="print")
            ziel = PDF / f"{i}-loesungen.pdf"
            pg.pdf(path=str(ziel), format="A4", print_background=True, margin=rand, display_header_footer=True,
                   header_template="<span></span>", footer_template=fuss("Lösungsblatt"))
            print("PDF:", ziel.name, ziel.stat().st_size // 1024, "KB")

            # Arbeitsblatt (frische Seite, ohne Lösungen)
            pg.goto(datei.as_uri())
            pg.wait_for_timeout(400)
            titel = pg.evaluate("document.querySelector('main h1') ? document.querySelector('main h1').textContent : document.title")
            pg.evaluate(ARBEITSBLATT, "Arbeitsblatt: " + titel)
            pg.add_style_tag(content=AB_CSS)
            pg.emulate_media(media="print")
            ziel = PDF / f"{i}-arbeitsblatt.pdf"
            pg.pdf(path=str(ziel), format="A4", print_background=True, margin=rand, display_header_footer=True,
                   header_template="<span></span>", footer_template=fuss("Arbeitsblatt"))
            print("PDF:", ziel.name, ziel.stat().st_size // 1024, "KB")
        b.close()
    bauen(baukasten)


if __name__ == "__main__":
    main()
