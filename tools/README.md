# Werkzeuge für den Lernpfad Lager

## Lösungsblätter (PDF) und Web-Version bauen

```
python3 tools/pdfs.py --baukasten <Ordner des Lernpfad-Baukastens>
```

Das Skript baut die Web-Version, öffnet jede Modulseite im Browser, füllt alle Übungen mit der Musterlösung aus,
klappt alle Hilfen auf und speichert die Seite als `lernpfad-lager/material/pdf/<modul>-loesungen.pdf`.
Danach baut es die Web-Version noch einmal, damit die PDFs in `ausgabe/web/material/pdf` liegen.

In der Web-Version erscheint der Download-Link zum Lösungsblatt erst, wenn die Schüler:innen das Modul
unten als „erledigt“ markiert haben (Baustein `:::nacherledigt` in den Modulen).

Voraussetzungen: `pip install playwright pyyaml markdown-it-py mdit-py-plugins` und ein installierter Chrome/Chromium
(bei Bedarf Pfad mit `--chrome` oder der Umgebungsvariable `CHROME_PFAD` angeben).

Nach jeder inhaltlichen Änderung an einem Modul das Skript erneut ausführen und `lernpfad-lager/ausgabe/web` sowie
`lernpfad-lager/material/pdf` einchecken.
