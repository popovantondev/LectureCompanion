# Portfolio-Prüfung und 4-Minuten-Demo — 2.4

Grundlage: die bereitgestellte Portfolio-Audit-Anleitung, angewendet auf dieses eine Projekt. Kein Audit fremder Projekte, keine Veröffentlichung. Bewertung 0–3; kein Zertifikat.

## Bewertung mit Belegen

| Kriterium | Punkte | Beleg / Grenze |
| --- | --- | --- |
| Klare Benutzeraufgabe | 3 | README.md: neue Unterrichtsaussagen und aktuelle Folie verständlich erklären. |
| Eigene Anwendungslogik | 3 | live-source.js: delta/commit; server.js: runLocal und Vorrang eigener Fragen; lecture-language.js: Sprachpaar. |
| Lesbarkeit / Architektur | 2 | Getrennte UI-, Quellen-, Modell-, Sprach- und Buildmodule; docs/ENTWICKLUNG.de.md. pet_ui.py ist noch groß, weitere Zerlegung wäre sinnvoll. |
| Daten / Fehlerbehandlung | 2 | Zehn Antworten mit Migrationssicherung; lokale APIs, Eingabegrenzen, Geräte-Fallback; test-server-routes.js prüft fehlende Webdatei. Nicht jede Speicher-/Treiberstörung getestet. |
| Git / Version / Build / Tests | 2 | Versionsdatei, Manifest, Buildwerkzeuge, Tests und CI-Datei vorhanden. Sauberer Source-Export; keine Git-Historie oder Remote-Veröffentlichung erzeugt. |
| Deutsche Demo in 3–5 Minuten | 3 | LectureCompanionDemo.exe und Ablauf unten; synthetische Daten, keine echten Meetings. |
| Plattformweg | 1 | Fertiger Windows-Adapter; Node-Kern kann als Grundlage dienen. Win32-Fenster und Teams-Erfassung brauchen für macOS eigene Adapter; kein fertiger Mac-Port. |

Summe: 16/21. Für eine erklärbare Windows-Portfolio-Demo geeignet; kein Nachweis universeller Kompatibilität.

## Ohne Terminal zeigen

1. Die vollständige ZIP-Datei entpacken. LectureCompanionDemo.exe doppelklicken; die Unterordner daneben lassen. Kein Modellstart und keine Teams-Verbindung. Für echte Nutzung stattdessen LectureCompanion.exe öffnen.
2. Im Rechtsklick-Menü DE wählen, falls eine frühere Einstellung eine andere Sprache vorgibt.
3. 0:00–0:40: „Der Begleiter hilft mir, neue Aussagen im IT-Unterricht zu verstehen. Er trennt neue Informationen vom alten Kontext.“
4. 0:40–1:40: Roboter ziehen, Karten vor/zurück blättern, Fragefeld durch Darüberfahren öffnen, Lautstärke und Sprache zeigen. „Diese Demo verwendet erfundene Beispiele. Modellaufrufe sind abgeschaltet.“
5. 1:40–2:40: „Text und Bild werden lokal verarbeitet. Bei verschiedener Unterrichts- und Oberflächensprache gibt es zwei kurze Abschnitte; sonst einen. Eine Folienfrage nimmt ein frisches Bild auf.“
6. 2:40–3:30: README-Projektaufbau und Prüfbericht öffnen. „Die Tests sichern unter anderem neue versus alte Aussagen, Warteschlange und fehlende Dateien ab.“
7. 3:30–4:00: „Diese Ausgabe ist für Windows. Ein zweiter-PC-Test und ein langer Unterrichtstest wurden für diesen Abschluss vom Auftraggeber zurückgestellt. KI-Antworten bleiben prüfpflichtig.“

## Abschlussrahmen

Der Defekt der lokalen Startadresse wird durch eine dateiunabhängige Diagnoseantwort behoben und durch einen Regressionstest abgesichert. Zweit-PC- und Langzeittest sind ausdrücklich aus dem aktuellen Abschlussumfang genommen, nicht als bestanden markiert. Die öffentliche Repository-Freigabe (Lizenzentscheidung, Signierung nach Bedarf, echte Git-Historie) ist ein gesonderter Schritt.

## Realistischer nächster Plattformschritt

Den Quelladapter hinter der LiveSource-Schnittstelle austauschbar machen; danach eine eigenständige macOS-Fenster-/Untertitelquelle mit denselben synthetischen Tests entwickeln. Keine Behauptung, der jetzige EXE-Build laufe bereits auf macOS.
