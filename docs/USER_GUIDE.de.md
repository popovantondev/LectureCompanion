# Lecture Companion 2.4 — Benutzerhandbuch

[Deutsch](USER_GUIDE.de.md) · [English](USER_GUIDE.en.md) · [Русский](USER_GUIDE.ru.md)

## 1. In fünf Schritten starten

- Speichere das ganze ZIP auf dem PC. Rechtsklick im Explorer → **Alle extrahieren…**.

- Entpacke es auf eine **interne SSD**, in einen Ordner mit Schreibrechten, z. B. Dokumente/LC2.4. Nicht direkt im ZIP, unter „Programme“ oder auf einem langsamen USB-Stick starten.

- Öffne den entpackten Ordner. Neben `LectureCompanion.exe` müssen `_internal`, `Laufzeit`, `Modelle` und `portable.json` liegen.

- Doppelklicke **LectureCompanion.exe**. Kein Setup, kein Terminal, kein API-Schlüssel und kein Modelldownload sind für dieses vollständige Paket nötig.

- Warte auf den Roboter. Startphase und Zeit stehen unter ihm. Der erste Start kann mehrere Minuten dauern. Starte nicht mehrere Kopien. Escape bricht den Start ab.

## 2. Voraussetzungen und Gerätetest

**Windows 11 x64; möglichst 32 GB RAM; interne SSD.** Zusätzlich zum entpackten Paket wird Platz für Modell-Caches benötigt. Auf 16 GB können Teams und die Modelle zusammen zu viel Speicher brauchen. Diese Ausgabe unterstützt weder macOS/Linux noch Windows ARM.

Ein kompatibler Intel NPU wird bevorzugt. Fehlt er oder schlägt das Laden fehl, werden kompatible OpenVINO-CPU/GPU-Geräte nacheinander mit derselben kurzen Aufgabe getestet. Der schnellste erfolgreiche Test gewinnt. Das Ergebnis wird gespeichert; Hardware-, Treiber- oder Modelländerungen lösen eine neue Prüfung aus. CPU ist oft langsamer. GPU-Unterstützung hängt vom Treiber ab.

Treiber gehören zu Windows und können nicht einfach im ZIP mitlaufen. Der Assistent installiert nichts automatisch. Auf gesperrten Schul-/Firmen-PCs muss gegebenenfalls die IT zustimmen. Sicherheitsregeln nicht umgehen.

## 3. Teams vorbereiten

- Öffne die **Desktop-App** von Teams und die Besprechung.

- Schalte im Besprechungsmenü die **Liveuntertitel** ein. Der Assistent liest den Text direkt; er zeichnet kein Mikrofon auf.

- Für Folien muss eine echte Bildschirm-/Fensterfreigabe laufen. Chat-Bilder sind keine Folien.

- Rechtsklick auf den Roboter → **Zusammenfassungen starten**, falls pausiert. Etwa einmal pro Minute wird neue Rede geprüft. Ohne neue Inhalte wird keine unnötige KI-Anfrage erzeugt.

Aufnahmen berücksichtigen Fensterbewegung und Überdeckung. Minimierung, geschützte Inhalte und Teams-Updates können die Aufnahme verhindern. Dann soll eine klare Fehlermeldung erscheinen, kein aus dem Gespräch erfundener Folieninhalt.

Nutze diese Funktion nur mit der erforderlichen Erlaubnis deiner Organisation. Der Begleiter schreibt nichts in den Teams-Chat.

## 4. Bedienelemente

- **Roboter anklicken:** neue Aussagen kurz erklären. Eine Folie wird nur mitanalysiert, wenn „Folie auch per Klick analysieren“ aktiviert wurde.

- **Darüberfahren:** Fragefeld unter dem Roboter öffnen. Der Hinweis steht links; langer Text lässt das Feld nach unten wachsen, bis acht sichtbare Zeilen.

- **Rakete / Strg+Enter:** Frage senden. Enter fügt eine neue Zeile ein. Maximal 2000 Zeichen.

- **Bildsymbol:** die aktuelle freigegebene Folie frisch aufnehmen und auswerten — nicht ein altes Archivbild.

- **Ziehen:** Roboter und Karten gemeinsam verschieben. Auch die Karten-Kopfzeile bewegt die Gruppe.

- **Pfeile / Mausrad:** bis zu zehn Antworten durchblättern. Eine deckende aktuelle Karte, drei ältere grau-transparent dahinter. „Zur neuesten“ springt zurück.

- **Rechtsklick:** Menü mit Sprache, Pause, Ton und Beenden. Es liegt über den anderen Fenstern des Begleiters.

## 5. Sprache, Tempo und Klang

**Deutsch ist Standard.** Im Roboter-Menü wählst du DE, EN oder RU. Neue Antworten enthalten zuerst die Sprache der Unterrichtsuntertitel und danach die Sprache der Oberfläche. Sind beide gleich, gibt es nur einen Abschnitt. DE/EN/RU werden lokal erkannt; bei unklarer Sprache ohne bisherigen Kontext wird nur die Oberflächensprache verwendet. Fragen und Folien verwenden dieselbe Regel; pro Antwort erfolgt kein zusätzlicher Übersetzungsaufruf. Alte Antworten bleiben unverändert. Eine bereits angenommene Frage wird in ihrer ursprünglichen Sprache fertig beantwortet.

Die Regler-Schaltfläche bietet **Schnell** (kurz, ohne zusätzliches Denken), **Normal** und **Gründlich** (zusätzliches Denken nur bei eigenen Textfragen). Automatische Zusammenfassungen bleiben kurz. Ein Wechsel unterbricht keine laufende Anfrage.

Die Note öffnet die Lautstärke. Durchgestrichen = stumm; die drei Notengrößen wählen 33, 67 und 100 %. Klicken oder Loslassen des Reglers spielt eine Probe. Die Einstellung gilt auch für Start, Antwort, Ziehen und das sanfte Öffnungsgeräusch.

Während der Verarbeitung laufen blaue Nullen und Einsen mit Pausen über das Visier. Seltenes Blinzeln gehört zum Ruhezustand. Unter den Antworten stehen aktuelle Phase, Warteschlange und Bearbeitungszeit.

## 6. Was liegt in welchem Ordner?

- `Daten`: Einstellungen, zehn Antworten, Fensterposition, Testresultate und Protokolle. Entsteht beim ersten Start.

- `Modelle`: fertige KI-Modelle und später Geräte-Caches.

- `Laufzeit`: Python, Node.js, Ollama und Bibliotheken.

- `_internal`: Grafik und Bibliotheken der Oberfläche.

- `Anleitungen`: Hilfe auf Deutsch, Englisch und Russisch.

Das frische ZIP enthält keine Unterrichtsverläufe oder privaten Einstellungen. Beim Kürzen eines alten Entwicklungsverlaufs wird einmal `history-before-10.json` gesichert. Diese private Sicherung niemals weitergeben.

Die KI-Anfragen bleiben lokal. Teams und Windows selbst nutzen gegebenenfalls das Internet. Windows und Drittkomponenten können gewöhnliche System-/Benutzer-Caches außerhalb der App anlegen. Portable bedeutet keine separate Installation, nicht eine vollständig isolierte Sandbox.

## 7. Wenn etwas nicht klappt

#### Nichts erscheint / Windows blockiert die Datei

Alles entpackt? Alle Unterordner neben der EXE? Nutze eine beschreibbare interne SSD. Prüfe die Herkunft und die mitgelieferte Prüfsumme. Schutzfunktionen nicht abschalten. Die EXE ist nicht digital signiert; auf verwalteten PCs kann IT-Freigabe nötig sein.

#### Start dauert sehr lange

Erststart und Gerätetest brauchen Zeit. Achte auf Phase und Dauer. Schließe speicherintensive Programme; starte keine zweite Kopie. Details stehen unter `Daten/npu.log`, `Daten/server.log` und `Daten/device-benchmark.json`.

#### Keine Zusammenfassung / kein Screenshot

Ist die richtige Besprechung geöffnet? Sind Liveuntertitel aktiv? Gibt es neue Rede seit der letzten Antwort? Läuft eine echte Bildschirmfreigabe? Eine eigene Frage wartet auf die laufende Antwort, bekommt dann aber Vorrang vor der nächsten automatischen Zusammenfassung.

#### Teams ruckelt

Zusammenfassungen pausieren und die laufende Anfrage beenden lassen. „Schnell“ wählen. Hintergrund-Bildanalyse hat mindestens drei Minuten Abstand und entlädt das Bildmodell danach. Es gibt keinen harten „95%-GPU“-Limiter. Nutzt Text dieselbe GPU, wird Bild-/Textgenerierung serialisiert.

#### KI antwortet falsch oder unvollständig

Wichtige Aussagen am Original prüfen. Eine kürzere, klarere Frage stellen. „Gründlich“ garantiert keine richtige Antwort. Ein erreichtes Denklimit löst keinen kostenpflichtigen Cloud-Versuch aus.

#### CPU/GPU-Test wiederholen

Programm schließen. `Daten/device-benchmark.json` in `device-benchmark.alt.json` umbenennen. Beim nächsten Start ohne nutzbaren NPU wird neu getestet. Modelle nicht löschen.

## 8. Verschieben, aktualisieren, weitergeben

Über das Roboter-Menü beenden und immer den **ganzen Ordner** verschieben. Auf einem anderen PC bleiben Windows-, RAM- und Treibervoraussetzungen bestehen; Python oder Modelle müssen nicht nachinstalliert werden.

Updates in einen neuen Ordner entpacken, die alte Version als Rückfall behalten. Für die eigene Nutzung kann `Daten` bei beendeten Programmen übernommen werden. Anderen Personen nur das **saubere Original-ZIP** geben, nicht den benutzten Ordner mit Unterricht und Protokollen.

Ein Test auf einer wirklich sauberen zweiten Windows-Installation steht noch aus. Lokale Prüfungen sind keine Garantie für jeden PC.

## 9. Demo ohne Teams und ohne Befehle

`LectureCompanion.exe` ist das normale Programm. `LectureCompanionDemo.exe` öffnet durch Doppelklick eine Demonstration mit erfundenen Beispielen, ohne Teams oder KI-Modelle zu starten. Beide EXEs bleiben neben ihren Unterordnern.
