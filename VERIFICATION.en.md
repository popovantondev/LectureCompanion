# Verification — 2.4

2026-09-09, Windows 11 x64, Intel Core Ultra 7 255U, 32 GB RAM.

Passed local checks: native linked cards, ten-answer cap, navigation, no remap/restack on unchanged state, popup above other app windows, left placeholder, multiline input, three languages, binary sweep/pause and throttled drag sound; synthetic visuals inspected. Backend checks cover fresh-vs-old speech, question priority, token limits, in-flight language preservation, per-language image caching and serialization.

Simulated device tests cover no NPU, CPU-only, faster GPU, cache/hardware changes, NPU driver failure and total failure. Real CPU generation using the isolated copied Python: model load 13.197 s; first short generation 24.102 s; warm repeat 4.967 s, up to 48 tokens. This is not a general speed guarantee. Imports resolve inside the portable runtime; CPU/GPU/NPU are detected here.

Release integration passed: frozen EXE 2.4 starts in DE/EN/RU (four cards, ten answers); fresh normal start selects German. After moving the package, Python, Node and Ollama ran from the new folder with both included models. NPU arithmetic: 9.40 s without and 53.83 s with extra thinking, both correct. Synthetic DE/EN/RU explanations: 12.90 / 11.20 / 13.52 s. Synthetic LAN/WAN slide correctly described in 33.99 s including preparation; Ollama reported Intel Graphics/Vulkan. Normal EXE close ended the three owned services, freed their ports and allowed another folder move. All three HTML guides were visually checked. ZIPs exclude private data, lecture history and device caches; SHA-256 sidecars accompany them. These small tests are not general speed guarantees. A clean second PC, all Teams/DPI/multi-monitor configurations and all drivers remain untested. EXE unsigned. AI may be wrong. Final source and portable artifacts are checked for private data.

## Current-version completion

The root route no longer depends on missing index.html: / and /health return file-independent diagnostics. The new regression test failed against the old handler and passed after correction; it is part of the default suite.

Answers use lecture + interface languages in one model call, with no duplicate section for matching languages. Tests cover detection, uncertain fragments, accepted questions, token limits and language-pair image caching. Real synthetic DE+RU test: NPU text 19.62 s; LAN/WAN image 24.87 s. Both contained actual sentences in both languages. Single measurements, not general performance claims.

LectureCompanionDemo.exe provides a double-click synthetic demo. See docs/PORTFOLIO.en.md for the evidence-based criteria review and demonstration plan.

The client excluded a clean second-PC test and a long lecture test from this version’s completion; neither is reported passed.

The final EXE was rebuilt. LectureCompanionDemo.exe entered demo mode through its filename alone, leaving all three service ports unused. Normal launch used NPU; three real root/health request pairs survived. All 1066 updated app files matched the fresh build by SHA-256. The saved user language was preserved; new profiles remain German.
