# Lecture Companion

**Windows 11 · Portable · Version 2.4 · Lokale KI · Release-Preview, nicht signiert**

[Deutsch](README.md) · [Русский](README.ru.md) · [English](README.en.md)

![Lecture Companion — deutsche Oberfläche mit synthetischen Beispielen](docs/screenshots/app-de.png)

*Synthetische Demo. Kein echtes Meeting, keine echten Untertitel und keine Teilnehmerdaten.*

Lecture Companion hilft dir, einer IT-Vorlesung in Microsoft Teams zu folgen. Die App fasst neue Liveuntertitel kurz zusammen und erklärt auf Wunsch die aktuell geteilte Folie. Die Verarbeitung erfolgt lokal auf dem PC — ohne ChatGPT-Konto, API-Schlüssel oder Cloud-Fallback.

## Was die App kann

- Erkennt neue Untertitel getrennt vom bisherigen Kontext.
- Nimmt auf Knopfdruck einen frischen Ausschnitt der Bildschirmfreigabe auf — nicht das Besprechungschatfenster.
- Antwortet zuerst in der Sprache der Vorlesung und danach in der Oberflächensprache; gleiche Sprachen werden nicht doppelt ausgegeben.
- Zeigt bis zu zehn Antworten als navigierbare Kartenstapel; Fragen und Folienanalyse sind direkt erreichbar.
- Verwendet bevorzugt einen kompatiblen Intel NPU, sonst einen lokalen CPU-/GPU-Fallback.
- Unterstützt Deutsch, Englisch und Russisch für Oberfläche und neue Antworten.

## Download und Start

Der vollständige Portable-Download wird im [GitHub-Releases-Bereich](https://github.com/popovantondev/LectureCompanion/releases) bereitgestellt. Wegen der Dateigrößenbegrenzung von GitHub Releases wird das ZIP in vier Teile aufgeteilt. Lade alle vier Teile und `JoinPortable.cmd` in denselben Ordner herunter und doppelklicke auf `JoinPortable.cmd`. Das Skript prüft die Dateigrößen und die ZIP-Prüfsumme, verwendet nur Windows-Bordmittel und installiert nichts. Danach das erzeugte ZIP vollständig auf eine interne SSD entpacken und `LectureCompanion.exe` starten — keine separate Python-Installation oder Kommandozeile nötig.

- [Deutsche Schritt-für-Schritt-Anleitung](Anleitungen/Deutsch.html)
- Windows 11 x64; 32 GB RAM empfohlen. Kompatible Treiber und die Teams-Desktop-App müssen bereits installiert sein.
- Erster Start und Modellinitialisierung können dauern. Das Paket ist mehrere GiB groß.

## Datenschutz und Grenzen

Untertitel und angeforderte Folienbilder werden lokal verarbeitet. Die App bietet keinen Cloud-Fallback und lädt sie nicht automatisch hoch. Meeting-Inhalte können personenbezogene Daten enthalten: beachte die Regeln deiner Organisation und teile keine echten Untertitel oder Screenshots.

KI-Antworten können Fehler enthalten. Geschützte oder minimierte Teams-Fenster sowie Änderungen an Teams können den Zugriff auf Untertitel oder Folien verhindern. Gerätegeschwindigkeit und Kompatibilität hängen von PC und Treibern ab. Die EXE ist nicht signiert; ein Test auf einem sauberen zweiten Windows-PC steht noch aus.

## Dokumentation und Entwicklung

[Handbuch](Anleitungen/Deutsch.html) · [Architektur und Build](docs/ENTWICKLUNG.de.md) · [Prüfbericht](VERIFICATION.md) · [Release-Checkliste](PUBLIC-REPOSITORY.md)

Für Quellcode-Prüfungen: `python verify.py --node PATH_TO_NODE`; native Windows-UI-Prüfungen: `--ui`. Die synthetische Demo startet ohne Teams oder Modellabfragen: `LectureCompanionDemo.exe` per Doppelklick.

## Nutzungsrechte

Der Quellcode und das Roboterbild sind öffentlich nur zur Ansicht verfügbar und nicht zur Wiederverwendung lizenziert. Die offizielle, unveränderte EXE darf privat und nicht kommerziell heruntergeladen und gestartet werden; Ändern oder Weiterverteilen ist nicht erlaubt. Drittanbieterkomponenten behalten ihre eigenen Lizenzen und Hinweise (`LICENSE`, `THIRD_PARTY.md`). GitHub kann Anzeigen und Forken öffentlicher Repositories erlauben; das ist keine technische Kopiersperre.
