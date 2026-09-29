# Lecture Companion 2.4 — User guide

[Deutsch](USER_GUIDE.de.md) · [English](USER_GUIDE.en.md) · [Русский](USER_GUIDE.ru.md)

## 1. First launch

- Save the complete ZIP. In File Explorer, right-click → **Extract All…**.

- Choose a writable folder on an **internal SSD**, such as Documents/LC2.4. Do not run from inside the ZIP, Program Files or a slow USB drive.

- Check that `LectureCompanion.exe`, `_internal`, `Laufzeit`, `Modelle` and `portable.json` are together.

- Double-click **LectureCompanion.exe**. This full package needs no setup, terminal commands, API key or model download.

- Wait for the robot. The loading screen shows the current stage and elapsed time. First preparation can take several minutes. Do not start extra copies. Escape cancels startup.

## 2. Computer requirements and device selection

**Windows 11 x64, preferably 32 GB RAM, internal SSD.** Keep extra disk space for model caches. A 16 GB PC may run short of memory with Teams and the models. This package does not support Windows ARM, macOS or Linux.

A compatible Intel NPU is preferred. If absent or unable to load the model, compatible OpenVINO CPU/GPU devices are benchmarked sequentially on the same short task. The fastest successful result is saved. Hardware, driver or model changes invalidate it. CPU may be slower; GPU compatibility depends on the driver.

Drivers are OS components that cannot simply run from this ZIP. No drivers or packages are installed automatically. On managed PCs, ask IT about restrictions; do not bypass security policy.

## 3. Prepare Teams

- Open the **desktop Teams app** and the meeting.

- Enable **live captions**. The assistant reads caption text directly; it does not record your microphone.

- Slide analysis requires a real screen/window share. A chat image is not a slide.

- Right-click the robot and enable summaries if paused. New speech is checked about once a minute; no new content means no unnecessary AI request.

Capture handles moving/covering the window. Minimization, protected content or Teams updates may prevent capture. Missing slides should produce an error, not content guessed from speech. Use this only with the required organizational permission. The assistant never posts to Teams chat.

## 4. Controls

- **Click:** a short explanation of new speech. A slide is included only if you explicitly enable the click-to-analyze option.

- **Hover:** open the question box below the robot. The placeholder is on the left. Long text grows downward, up to eight visible lines.

- **Rocket / Ctrl+Enter:** send; Enter adds a line. Maximum 2000 characters.

- **Image icon:** capture and analyze the current shared slide, not a stored image.

- **Drag:** move robot and cards together. Dragging a card header also moves the group.

- **Arrows / wheel:** browse up to ten answers. The front card is opaque; three older cards are translucent grey. “Latest” returns to the newest.

- **Right-click:** language, pause, sound and quit. The menu stays above the companion’s other windows.

## 5. Language, speed and sounds

**German is the default.** Choose DE, EN or RU in the robot menu. New answers use the lecture-caption language first and the interface language second. Matching languages produce one section, not duplicate text. DE/EN/RU are recognized locally; uncertain language without prior context falls back to the interface language only. Questions and slides follow the same rule, without an extra translation request. Existing answers stay as written. A question already accepted keeps its original language.

The settings icon offers **Fast** (short, no extra reasoning), **Balanced** and **Deep** (extra reasoning for explicit text questions only). Automatic summaries stay short. Changing modes does not interrupt work in progress.

The note opens volume controls. Crossed-out means mute; the three note sizes select 33, 67 or 100%. Clicking a note or releasing the slider plays a preview. The same volume controls startup, answers, dragging and the soft opening sound.

Blue binary digits sweep across the visor with pauses while processing. Occasional blinking is for idle mode. Processing phase, queue and timing appear below answers.

## 6. Files and privacy

- `Daten`: settings, ten answers, position, device test and logs; created on first launch.

- `Modelle`: both models and later device-specific caches.

- `Laufzeit`: Python, Node.js, Ollama and libraries.

- `_internal`: UI libraries and artwork.

- `Anleitungen`: three-language help.

The clean ZIP contains no real lecture history or private settings. Trimming a larger old development history creates one private `history-before-10.json` backup. Do not share it.

Assistant AI requests stay local. Teams and Windows may use the internet. Windows/third-party components can create ordinary system/user caches outside this folder. Portable means no separate installation, not an isolated Windows sandbox.

## 7. Troubleshooting

#### Nothing appears / Windows blocks the file

Extract everything, keep all folders beside the EXE and use a writable internal SSD location. Verify the source and supplied checksum; do not disable protection. The EXE is unsigned and a managed PC may require IT approval.

#### Loading takes a long time

First startup and device tests take longer. Watch the stage and time, close memory-heavy apps and do not start extra copies. Check `Daten/npu.log`, `Daten/server.log` and `Daten/device-benchmark.json`.

#### No summary or screenshot

Correct meeting open? Live captions enabled? New speech since the last answer? Actual screen share active? A manual question waits for the current generation, then takes priority over the next automatic summary.

#### Teams becomes slow

Pause summaries and let the active request finish. Choose Fast. Background vision has a three-minute cooldown and unloads afterwards. There is no hard “95% GPU” cap. When text uses the GPU, text and vision are serialized.

#### Wrong/incomplete answer

Check important facts against the original. Ask a shorter or clearer question. Deep reasoning is not a guarantee of correctness. A reasoning limit never triggers a paid cloud retry.

#### Repeat CPU/GPU benchmark

Quit. Rename `Daten/device-benchmark.json` to `device-benchmark.old.json`. The next startup without a usable NPU retests. Do not delete models.

## 8. Moving, updates and sharing

Quit through the robot menu and move the **entire folder**. Another PC still needs compatible Windows, memory and drivers, but no separate Python or model installation.

Extract updates into a new folder and keep the old version as fallback. For personal use, copy `Daten` only while both apps are closed. Share the **clean original ZIP**, not a used folder containing lectures and logs.

A completely clean second-PC Windows installation has not yet been tested. Passing local checks is not a promise for every computer.

## 9. Double-click demo, no Teams or commands

`LectureCompanion.exe` is the normal app. Double-click `LectureCompanionDemo.exe` for fictional examples without starting Teams or model services. Keep both EXEs next to their folders. See [Portfolio and 4-minute demo](docs/PORTFOLIO.en.md).
