# Prüfbericht — 2.4

Prüfdatum: 2026-09-09. Lokaler Host: Windows 11 x64, Intel Core Ultra 7 255U, 32 GB RAM.

## Bereits geprüft

- Native UI: vier verbundene Karten, zehn Antworten, Navigation, kein Remap/Restack bei unveränderten Statusdaten, Menü über anderen App-Fenstern, linke Eingabehilfe, mehrzeiliges Feld, drei Sprachen, Binärlauf und Pause, gedrosselter Bewegungston. Synthetische Bilder visuell geprüft.
- JavaScript: neue Rede vs. 20 Minuten alter Kontext, Fragepriorität, Generierungsgrenzen, Sprachwechsel während einer angenommenen Frage, sprachabhängiger Bildcache, keine doppelte Bildgenerierung.
- Geräteauswahl: simuliert ohne NPU, CPU-only, GPU schneller, Cache, Hardwarewechsel, NPU-Treiberfehler, vollständiger Testfehler.
- Echte CPU-Inferenz mit eigenständigem kopiertem Python/OpenVINO: Modellladen 13,197 s; erste kurze Generierung 24,102 s; warme Wiederholung 4,967 s. Identischer kurzer Eingabetext, höchstens 48 Tokens. Keine allgemeine Geschwindigkeitsgarantie.
- Portable Python importiert OpenVINO/GenAI ausschließlich aus seiner eigenen Verzeichnisstruktur. Auf diesem Gerät wurden CPU, GPU und NPU erkannt.

## Release-Integration

EXE 2.4 und vollständige Portable-Version bestanden den Start in DE/EN/RU (vier Karten, zehn Antworten; frischer normaler Start auf Deutsch). Das Paket wurde vor dem normalen Start verschoben; Python, Node und Ollama liefen aus dem neuen Ordner mit beiden mitgelieferten Modellen. NPU-Rechentest: 9,40 s ohne und 53,83 s mit zusätzlichem Denken, beide korrekt. Synthetische Erklärungen DE/EN/RU: 12,90 / 11,20 / 13,52 s. Künstliche LAN/WAN-Folie korrekt erkannt, 33,99 s inklusive Modellvorbereitung; Ollama meldete Intel Graphics/Vulkan. Normales Schließen beendete alle drei eigenen Dienste, gab die Ports frei und erlaubte erneutes Verschieben. Alle drei HTML-Anleitungen wurden geöffnet und visuell geprüft. ZIPs enthalten keinen Datenordner, Unterrichtsverlauf oder Geräte-Cache; SHA-256-Prüfsummen liegen daneben. Kleine Tests sind keine allgemeine Geschwindigkeitsgarantie.

## Grenzen

Saubere zweite Windows-Installation noch nicht geprüft. Kein vollständiger Test aller Teams-Layouts, DPI-/Mehrschirmkombinationen oder Treiber. NPU/GPU-Auslastung ist kein garantierter Prozentdeckel. Modelle können falsche Antworten geben. EXE nicht signiert. Der Quellcode-Export und der Portable-Inhalt werden vor Übergabe auf private Daten geprüft.

## Abschluss der aktuellen Version

Der fehlende index.html kann die lokale Startadresse nicht mehr zum Absturz bringen: / und /health liefern eine dateiunabhängige Diagnoseantwort. Ein neuer Regressionstest wurde zunächst gegen die alte Version rot und danach gegen die Korrektur grün ausgeführt. Die schnelle Testsuite enthält ihn dauerhaft.

Unterrichtssprache plus Oberflächensprache werden in einem Modellaufruf ausgegeben, ohne doppelte Ausgabe bei gleicher Sprache. Tests prüfen Erkennung, unklare Fragmente, bereits angenommene Fragen, Tokenlimits und Bildcache je Sprachpaar. Echte synthetische DE+RU-Prüfung: Text auf NPU 19,62 s; LAN/WAN-Bild 24,87 s. Beide enthielten tatsächliche Sätze in beiden Sprachen. Einzelmessungen, keine allgemeine Leistungszusage.


Zweit-PC- und längerer Unterrichtstest wurden vom Auftraggeber aus dem Abschlussumfang dieser Version genommen; nicht als bestanden gewertet.

Die abschließende EXE wurde neu gebaut. LectureCompanionDemo.exe startete allein anhand ihres Dateinamens als Demo; danach waren alle drei Modell-/Serverports frei. Der normale Start verwendete NPU. Drei echte Aufrufpaare von / und /health blieben erfolgreich. Alle 1066 App-Dateien im aktualisierten Ordner stimmten per SHA-256 mit dem frischen Build überein. Die gespeicherte Benutzersprache wurde beibehalten; neue Profile bleiben Deutsch.
