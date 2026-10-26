#!/usr/bin/env python3
"""Baut die Lösungsblätter (PDF) für den Lernpfad und danach die Web-Version neu.

Ablauf:
  1. Web-Version bauen (die PDFs dürfen dabei noch leer sein, sie werden nur verlinkt).
  2. Jede Modulseite im Browser öffnen, alle Übungen mit der Musterlösung ausfüllen,
     alle Hilfen aufklappen und die Seite als PDF speichern (material/pdf/<modul>-loesungen.pdf).
  3. Web-Version noch einmal bauen, damit die fertigen PDFs in ausgabe/web/material/pdf liegen.

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
        (PDF / f"{i}-loesungen.pdf").touch(exist_ok=True)
    bauen(baukasten)

    web = PFAD / "ausgabe" / "web"
    kurs = re.search(r"^titel: (.+)$", (PFAD / "kurs.yaml").read_text(encoding="utf-8"), re.M).group(1).strip('"')
    with sync_playwright() as p:
        launch = {"executable_path": a.chrome} if os.path.exists(a.chrome) else {}
        b = p.chromium.launch(**launch)
        pg = b.new_page(viewport={"width": 1000, "height": 1400})
        for i in ids:
            datei = next(web.glob(f"{i}-*.html"))
            pg.goto(datei.as_uri())
            pg.wait_for_timeout(400)
            pg.evaluate(LOESEN)
            pg.add_style_tag(content=DRUCK_CSS)
            pg.emulate_media(media="print")
            ziel = PDF / f"{i}-loesungen.pdf"
            kopf = html.escape(kurs)
            pg.pdf(path=str(ziel), format="A4", print_background=True,
                   margin={"top": "16mm", "bottom": "18mm", "left": "14mm", "right": "14mm"},
                   display_header_footer=True,
                   header_template="<span></span>",
                   footer_template=f'<div style="font-size:8px;width:100%;text-align:center;color:#666">{kopf} · Lösungsblatt · Seite <span class="pageNumber"></span> von <span class="totalPages"></span></div>')
            print("PDF:", ziel.name, ziel.stat().st_size // 1024, "KB")
        b.close()
    bauen(baukasten)


if __name__ == "__main__":
    main()
