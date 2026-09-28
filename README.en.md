# Lecture Companion

**Windows 11 · Portable · Version 2.4 · Local processing · Unsigned release preview**

[Deutsch](README.md) · [Русский](README.ru.md) · [English](README.en.md)

![Lecture Companion — English interface with synthetic examples](docs/screenshots/app-en.png)

*Synthetic demo. No real meeting, captions, or participant data.*

Lecture Companion helps you follow IT classes in Microsoft Teams. It briefly summarizes new live captions and can explain the currently shared slide on request. Processing stays on your PC — no API key or cloud fallback.

## What it does

- Separates new captions from earlier context.
- Captures a fresh view of the shared screen when requested — not the meeting chat.
- Answers first in the lecture language and then in the interface language; matching languages are not repeated.
- Keeps up to ten answers in navigable cards, with quick access to questions and slide analysis.
- Prefers a compatible Intel NPU and otherwise uses a local CPU/GPU fallback.
- Supports German, English, and Russian for the interface and new answers.

## Download and start

The complete Portable download is provided on the [GitHub Releases page](https://github.com/popovantondev/LectureCompanion/releases). Because of GitHub's per-file release-asset limit, the ZIP is split into four parts. Download all four parts and `JoinPortable.cmd` into one folder, then double-click the CMD file. It checks the part sizes and ZIP checksum, uses built-in Windows tools, and installs nothing. Extract the resulting ZIP fully to an internal SSD and double-click `LectureCompanion.exe` — no separate Python setup or command line is needed.

- [English step-by-step guide](Anleitungen/English.html)
- Windows 11 x64; 32 GB RAM recommended. Compatible drivers and the Teams desktop app must already be installed.
- First startup and model initialization may take a while. The package is several GiB.

## Privacy and limitations

Captions and requested slide images are processed locally. The app has no cloud fallback and does not automatically upload them. Meeting content may contain personal data: follow your organization’s rules and do not share real captions or screenshots.

Answers can be wrong. Protected or minimized Teams windows and Teams updates may prevent caption or slide access. Performance and compatibility depend on the PC and its drivers. The EXE is unsigned, and a clean second-Windows-PC test is still outstanding.

## Documentation and development

[User guide](Anleitungen/English.html) · [Architecture and build](docs/DEVELOPMENT.en.md) · [Verification report](VERIFICATION.en.md) · [Release checklist](PUBLIC-REPOSITORY.md)

Run model-free source checks with `python verify.py --node PATH_TO_NODE`; add `--ui` for native Windows UI checks. The synthetic demo starts without Teams or model requests: double-click `LectureCompanionDemo.exe`.

## Usage rights

The source code and robot artwork are public for viewing only and are not licensed for reuse. You may download and run the unmodified official EXE for personal, non-commercial use; modification or redistribution is not permitted. Third-party components keep their own licenses and notices (`LICENSE`, `THIRD_PARTY.md`). GitHub may permit viewing and forking public repositories; this is not technical copy protection.
