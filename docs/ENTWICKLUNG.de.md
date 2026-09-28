# Entwicklung und Architektur — 2.4

[Deutsch](ENTWICKLUNG.de.md) · [English](DEVELOPMENT.en.md) · [Русский](РАЗРАБОТКА.ru.md)

## Datenfluss und Grenzen

Teams UI Automation → LiveSource → neue Rede + getrennte Kontextzeilen → lokaler Koordinator → OpenVINO-Textmodell → zehn Einträge → native Kartenoberfläche.
Manuelle Folienfrage → frische PrintWindow-Aufnahme der Freigabe → lokales Ollama-Bildmodell → Antwort. Die Bildbeschreibung wird nach Bildhash **und Sprache** gecacht. Capture-Zeit bleibt beim Cache-Treffer frisch.

Die APIs hören ausschließlich auf 127.0.0.1: 8765 Koordinator, 8766 Textmodell, 11435 Bildmodell. Schreibende Endpunkte prüfen den lokalen Origin und Eingabelängen. Transkripte und Bildtexte sind untrusted Daten, keine Anweisungen. Keine Übertragung an Cloud-Modelle. Keine Passwörter/API-Schlüssel.

Der Launcher besitzt die von ihm gestarteten Prozesse und beendet nur diese. Portable verweigert Start bei bereits belegten Dienstports, statt unbemerkt Dienste einer anderen Installation zu verwenden. Pro Windows-Benutzer nur eine normale GUI. Ein eigener Textauftrag bekommt Vorrang vor dem nächsten Auto-Update, unterbricht jedoch keine aktive Generierung.

## Portabilität

`portable.json` enthält relative Pfade. `Laufzeit/python` ist eine echte eigenständige Python-Distribution mit expliziten lokalen Importpfaden, keine kopierte venv. `runtime_boot.py` ergänzt nur das explizite App-Ressourcenverzeichnis. Python-Registry/User-Site/PYTHONPATH dürfen nicht als heimliche Abhängigkeiten dienen.

`Modelle` enthält genau die OpenVINO-Qwen3-8B-INT4-Ausgabe und die für qwen3-vl:2b-instruct benötigten Ollama-Blobs. Cache und Benutzerzustand werden nicht ausgeliefert. `Daten` entsteht am Ziel-PC. CPU/GPU-Auswahl wird anhand von Geräte-/Treiber-/Modell-Fingerprint gespeichert. Tests sind sequenziell und zeitbegrenzt, CPU auf höchstens vier Inferenz-Threads begrenzt. Der kurze Benchmark ist kein allgemeines Leistungsversprechen.

## Reproduzieren

Entwickler brauchen Python 3.12 und Node.js; Anwender des fertigen Komplettpakets nicht.

1. `python -m pip install -r requirements-ui.txt`
2. `python verify.py --node PATH_TO_NODE --ui`
3. `python build-exe.py --output PATH_TO_BUILD/dist`
4. Eigenständige Python-Basis und die Pakete aus `requirements-npu.txt` bereitstellen. `prepare-runtime.py --help` dokumentiert die expliziten lokalen Quellen. Das Werkzeug lädt nichts herunter. Das erzeugte Python wird mit isolierten Importpfaden überprüft; CPU/Vulkan-Ollama und Lizenztexte werden mitgenommen.
5. Modelle separat bereitstellen: [Textmodell](https://huggingface.co/OpenVINO/Qwen3-8B-int4-cw-ov), [Bildmodell](https://ollama.com/library/qwen3-vl:2b-instruct). Download ist ein bewusster Entwickler-/Paketierungsschritt, nicht Aufgabe des Endnutzers.
6. `python build-portable.py --app APP_FOLDER --runtime RUNTIME_FOLDER --models MODEL_ROOT --output NEW_NAME.zip`. MODEL_ROOT enthält `Qwen3-8B-int4-cw-ov` und `ollama/manifests/...`, `ollama/blobs/...`.
7. ZIP vollständig in einen anderen Ordner entpacken. Demo, normaler Start, Sprachwechsel, echte Fragen, Folienfehler und Prozessende prüfen. Dann auf einer sauberen zweiten Windows-Installation testen.
8. `python export-source.py --output NEW_SOURCE.zip` erzeugt einen separaten Git-tauglichen Quellcode-Export.

Python 3.12.14 / Node 24.19.0 / OpenVINO 2026.3.1, GenAI und Tokenizers 2026.3.1.0 / NumPy 2.5.3 / Ollama 0.33.3 wurden für diese Zusammenstellung verwendet. Keine unangekündigten Upgrades in einer Release-Runde. Modelle brauchen mehrere GiB; der Code gehört separat in Git.

## Tests / Änderungsregeln

`verify.py` prüft Syntax, Versionsgleichheit, Übersetzungen, Paket-Positivliste, neue-vs-alte Rede, Fragepriorität, Tokenlimits, Sprach-Caches und simulierte Geräteauswahl. `--ui` prüft tatsächliche Tk/Win32-Fenster, Stapel, Z-Reihenfolge, Fragefeld, Töne (Audioausgabe gemockt) und Animationen. Hardware-Integration ist separat: kein CI-Test soll unbemerkt Modelle laden oder echte Meetings lesen.

Bei Änderungen: reproduzierenden Regressionstest ergänzen, Auswirkungen auf Kontext/Freshness/Sprachen erklären, alle schnellen Tests ausführen, bei UI-Änderungen synthetisch rendern, erst dann EXE/ZIP neu bauen. Keine realen Unterrichtsinhalte als Fixtures verwenden. Versionsquelle: `version.json`. Alte Releases nicht überschreiben.

## Offene Freigabepunkte

EXE-Signierung, saubere Zweit-PC-Prüfung und Entscheidung über die Lizenz des eigenen Quellcodes sind separat. Drittanbieterhinweise stehen in `THIRD_PARTY.md`; Original-Lizenztexte bleiben im Paket. Keine allgemeine Rechts- oder Hardwarekompatibilitätsgarantie. Nicht als offizieller Filmcharakter vermarkten.

