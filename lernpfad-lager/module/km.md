---
titel: "Meilenstein 3: Kennzahlen-Auswertung in OnlyOffice"
minuten: 55
meilenstein: true
review: freigegeben
abgabe:
  titel: Kennzahlen-Tabelle abgeben
  text: Lade deine Tabelle als .xlsx hoch. Die Beurteilung schreibst du in dasselbe Tabellenblatt oder in ein zweites Blatt.
  dateitypen: .xlsx,.ods
  dateien: 1
raster:
  - {kriterium: Daten und Aufbau, erreicht: "Daten übernommen, Tabelle übersichtlich mit Beschriftung und Einheiten", besonders_gut: "klare Struktur, Eingabewerte und Ergebnisse optisch getrennt"}
  - {kriterium: Formeln, erreicht: "alle Kennzahlen mit Formeln berechnet, Zellbezüge statt Zahlen", besonders_gut: "Formeln so gebaut, dass sich die Ergebnisse bei geänderten Daten anpassen"}
  - {kriterium: Richtige Ergebnisse, erreicht: "alle Kennzahlen für beide Jahre richtig", besonders_gut: "zusätzlich Kapitalfreisetzung oder Zinsersparnis berechnet"}
  - {kriterium: Beurteilung, erreicht: "Zeitvergleich in mindestens vier Sätzen richtig gedeutet", besonders_gut: "Ursachen oder Maßnahmen begründet vorgeschlagen"}
---
## Auftrag

Die BüroComfort GmbH möchte wissen, ob sich das Lager für den **Bürostuhl ErgoMax** im letzten Jahr verbessert hat. Du berechnest die Kennzahlen **in OnlyOffice** und beurteilst den Vergleich mit dem Vorjahr.

:::material material/ergomax-lagerdaten.xlsx Übungsdatei: ErgoMax-Lagerdaten
Enthält die Monatsendbestände, den Jahresverbrauch, den Einstandspreis, den Marktzins und die Vorjahreswerte.
:::

Dein Auftrag:

1. **Öffne die Datei** im OnlyOffice-Tabelleneditor. Lege neben den Daten eine Tabelle mit den Spalten **Kennzahl – Aktuelles Jahr – Vorjahr** an.
2. **Berechne mit Formeln** für das **aktuelle Jahr**: durchschnittlicher Lagerbestand (Monatsinventur), Umschlagshäufigkeit, durchschnittliche Lagerdauer, Lagerzinssatz, DLB-Wert in € und Lagerzinsen.
3. **Berechne dieselben Kennzahlen für das Vorjahr.** Der DLB und der Jahresverbrauch des Vorjahrs stehen in der Datei.
4. **Beurteile in mindestens vier Sätzen:** Hat sich das Lager verbessert? Begründe mit den Kennzahlen. Nenne eine Maßnahme, wie die BüroComfort GmbH die Umschlagshäufigkeit weiter erhöhen könnte.

:::tipp Formeln in OnlyOffice
- Jede Formel beginnt mit einem **Gleichheitszeichen**, zum Beispiel `=B4+B5`.
- Statt Zahlen schreibst du **Zellbezüge** (zum Beispiel `E4`). Ändert sich ein Wert, rechnet die Tabelle neu.
- Den Mittelwert mehrerer Zellen berechnet die Funktion **MITTELWERT**, zum Beispiel `=MITTELWERT(B4:B16)`. Überlege, warum das hier dasselbe ist wie „(Anfangsbestand + 12 Monatsendbestände) : 13“.
- Runden: `=RUNDEN(Zelle;2)` rundet auf zwei Nachkommastellen.
:::

:::tipp Ein Blick auf den Rechenweg
Wenn du bei einer Kennzahl nicht weiterkommst, schau in [Modul 2](modul:k2), [Modul 3](modul:k3) und [Modul 4](modul:k4). Dort steht jede Formel mit Beispiel.
:::

:::checkliste Checkliste vor der Abgabe
- Die Kennzahlen für beide Jahre sind mit Formeln berechnet (keine abgetippten Ergebnisse).
- Die Tabelle hat Überschriften, Einheiten (Stück, Tage, %, €) und ist gut lesbar.
- Ich habe mindestens vier Sätze Beurteilung geschrieben.
- Ich habe eine Maßnahme zur Erhöhung der Umschlagshäufigkeit genannt.
:::

:::raster
:::

:::abgabe
:::
