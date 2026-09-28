# Veröffentlichung / Publishing / Публикация

## Vorgeschlagene GitHub-Metadaten

- Repository: `LectureCompanion` (public; Veröffentlichung vom Eigentümer freigegeben am 2026-09-28)
- Kurzbeschreibung: `Local processing companion for Microsoft Teams lectures · Windows · Deutsch / English / Русский`
- Topics: `windows`, `microsoft-teams`, `lecture-assistant`, `portable-app`, `python`, `nodejs`
- README entry: German default, with separate Russian and English pages and one matching-language synthetic screenshot per page.

## Deutsch

Der Quellcode wird mit `export-source.py` anhand von `release-manifest.json` zusammengestellt — nicht aus einem benutzten Portable-Ordner. Keine Modelle, Unterrichtsdaten, Zugangsdaten, Profile, Logs, Caches oder Backups. `.gitignore` ist nur eine zusätzliche Sicherung: bereits getrackte Dateien werden dadurch nicht entfernt.

Der Quellcode und die Roboterillustration werden öffentlich nur zur Ansicht bereitgestellt; eine Wiederverwendung ist nicht lizenziert. Die unveränderte offizielle Programmdatei darf privat und nicht kommerziell heruntergeladen und gestartet werden; Ändern oder Weiterverteilen ist nicht erlaubt. Siehe `LICENSE`. GitHub kann Nutzern im Rahmen seiner Bedingungen das Anzeigen und Forken öffentlicher Repositories erlauben; das lässt sich nicht als Kopierschutz behandeln. Der Eigentümer hat bestätigt, dass die Roboterillustration im Repository und in Screenshots gezeigt werden darf.

Portable-Paket und EXE werden als GitHub-Release-Assets veröffentlicht, nicht ins Git-Repository eingecheckt. Das ZIP überschreitet das Release-Asset-Limit pro Datei und wird daher in vier Teile unter 2 GiB geteilt; `JoinPortable.cmd` fügt sie lokal ohne Installation zusammen. Vor Veröffentlichung jedes Assets dessen Herkunft, Inhalt, Modelllizenzen und Datenschutz prüfen. EXE-Signierung und Zweit-PC-Test sind noch offene Einschränkungen.

## English

Use export-source.py and its explicit manifest, not an archive of a used Portable folder. Never include classroom data, credentials, profiles, logs, caches or backups. Source code and mascot are public for viewing only; the unmodified official EXE may be downloaded and run for personal, non-commercial use. Modification or redistribution is not permitted (`LICENSE`). GitHub may allow viewing and forking public repositories under its Terms; this is not technical copy protection. Publish the Portable ZIP only as split release assets, plus `JoinPortable.cmd`; preserve third-party notices and model licenses. Signing and clean second-PC testing remain open limitations.

## Русский

Исходники собираются `export-source.py` по явному манифесту, не из использованной Portable-папки. Не включать лекции, доступы, профили, логи, кэши и резервные копии. Код и робот доступны для просмотра; неизменённую официальную EXE можно скачать и запускать лично, некоммерчески. Изменять или распространять нельзя (`LICENSE`). GitHub может разрешать просмотр и форк публичного репозитория — это не техническая защита от копирования. Portable ZIP публикуется только разрезанным на части файлом релиза вместе с `JoinPortable.cmd`; сохранить уведомления сторонних компонентов и лицензии моделей. Подпись и проверка на чистом втором ПК остаются ограничениями.
