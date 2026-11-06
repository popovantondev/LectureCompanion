<div align="center">
  <img src="presentation-icon.png" width="128" alt="Lecture Companion icon">
</div>

# Lecture Companion

[Русский](README.ru.md) · [Deutsch](README.md) · **English**

<!-- public-release:start -->
Follow Teams lectures with local caption summaries and explanations of a selected slide.

**Windows 11 · x64 · Preview 2.4**

**[Download](https://github.com/popovantondev/LectureCompanion/releases/tag/v2.4)** · **[User guide](https://popovantondev.github.io/LectureCompanion/Guide-en.html)** · **[Report a problem](https://github.com/popovantondev/LectureCompanion/issues/new/choose)**

**Requirements and limitations:** Teams Desktop and compatible drivers; recommended: 32 GB RAM, internal SSD and 25 GB free for the parts, ZIP and extraction. EXE is unsigned; a second clean-PC check is pending.

**First steps:** Download all four parts and JoinPortable.cmd into one folder (about 5.8 GB). Run JoinPortable.cmd to verify and combine them, extract the entire ZIP and open LectureCompanion.exe.

**Application files:**

- [`JoinPortable.cmd`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/JoinPortable.cmd)
- [`LectureCompanion-2.4-Final-Portable.zip.part01`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/LectureCompanion-2.4-Final-Portable.zip.part01)
- [`LectureCompanion-2.4-Final-Portable.zip.part02`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/LectureCompanion-2.4-Final-Portable.zip.part02)
- [`LectureCompanion-2.4-Final-Portable.zip.part03`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/LectureCompanion-2.4-Final-Portable.zip.part03)
- [`LectureCompanion-2.4-Final-Portable.zip.part04`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/LectureCompanion-2.4-Final-Portable.zip.part04)

**Checksums:** [`SHA256SUMS`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/SHA256SUMS)
<!-- public-release:end -->

**[Website](https://popovantondev.github.io/LectureCompanion/index-en.html)** · **[Try in the browser](https://popovantondev.github.io/LectureCompanion/index-en.html)**

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

## Legal notes: only with the consent of everyone involved

Lecture Companion reads live captions from the Teams desktop app and, on request, analyzes a part of the shared screen. Before every meeting, obtain the consent of everyone involved (lecturers and participants) and follow the rules of your organization. If someone declines or withdraws consent, pause the summaries or close the app.

Even though the app does not record audio: secretly recording the non-publicly spoken word can be a criminal offence under [§ 201 of the German Criminal Code (StGB)](https://www.gesetze-im-internet.de/stgb/__201.html), and captions and slide images from a meeting can contain personal data under the [GDPR (DSGVO)](https://www.edpb.europa.eu/sme/be-compliant/process-personal-data-lawfully_en). Clarify purpose, scope and storage location and secure a legal basis in advance, usually consent.

The app processes captions and slide images locally and stores the last ten answers in the “Daten” folder; it writes nothing to the Teams chat. Do not share real captions, screenshots or logs in public issues. This project does not establish lawfulness and does not guarantee data-protection compliance.

## Download and start

Release 2.4 is publicly available as a pre-release. Download all four ZIP parts and `JoinPortable.cmd` from the [v2.4 release page](https://github.com/popovantondev/LectureCompanion/releases/tag/v2.4) and save them in the same folder. Double-click `JoinPortable.cmd`; it checks the part sizes and SHA-256 without installing anything. Extract the resulting ZIP fully to an internal SSD, then run `LectureCompanion.exe`. The [English step-by-step guide](https://popovantondev.github.io/LectureCompanion/Guide-en.html) explains how to use the app.

- [English step-by-step guide](docs/USER_GUIDE.en.md)
- Windows 11 x64; 32 GB RAM recommended. Compatible drivers and the Teams desktop app must already be installed.
- First startup and model initialization may take a while. The package is several GiB.

## Privacy and limitations

Captions and requested slide images are processed locally. The app has no cloud fallback and does not automatically upload them. Meeting content can contain personal data; see “Legal notes” above.

Answers can be wrong. Protected or minimized Teams windows and Teams updates may prevent caption or slide access. Performance and compatibility depend on the PC and its drivers. The EXE is unsigned, and a clean second-Windows-PC test is still outstanding.

## Documentation and development

[User guide](docs/USER_GUIDE.en.md) · [Architecture and build](docs/DEVELOPMENT.en.md) · [Verification report](VERIFICATION.en.md) · [Release checklist](PUBLIC-REPOSITORY.md)

Run model-free source checks with `python verify.py --node PATH_TO_NODE`; add `--ui` for native Windows UI checks. The synthetic demo starts without Teams or model requests: double-click `LectureCompanionDemo.exe`.

## Usage rights

The source code and robot artwork are public for viewing only and are not licensed for reuse. You may download and run the unmodified official EXE for personal, non-commercial use; modification or redistribution is not permitted. Third-party components keep their own licenses and notices (`LICENSE`, `THIRD_PARTY.md`). GitHub may permit viewing and forking public repositories; this is not technical copy protection.
