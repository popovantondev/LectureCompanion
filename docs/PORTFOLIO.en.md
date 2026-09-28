# Portfolio review and 4-minute demo — 2.4

The supplied portfolio-audit criteria are applied to this project only. No other projects were audited or published. Scores are 0–3, not certification.

| Criterion | Score | Evidence / limit |
| --- | --- | --- |
| Clear user problem | 3 | README: explain new lesson speech and fresh slides. |
| Original application logic | 3 | LiveSource.delta/commit, server.runLocal/question priority, lecture-language language pairs. |
| Readability / architecture | 2 | UI, source, inference, language and build modules are separated; pet_ui.py is still large. |
| Data / errors | 2 | History migration backup, input limits, device fallback and missing-file regression test. Not every disk/driver failure tested. |
| Git / version / build / tests | 2 | Version, allowlist, builders, tests and CI configuration exist. Source export prepared; no Git history/remote created. |
| German 3–5 minute demo | 3 | LectureCompanionDemo.exe; synthetic data without models or real meetings. |
| Platform path | 1 | Working Windows integration. A macOS UI/capture adapter is future work, not an existing port. |

Total: 16/21. Suitable for an explainable Windows portfolio demo, not evidence of universal compatibility.

## Double-click demo; no terminal

Extract the entire ZIP and double-click LectureCompanionDemo.exe. Keep the adjacent folders. It starts synthetic examples without Teams or model services. For real use open LectureCompanion.exe instead. Choose DE in the context menu if needed.

- 0:00–0:40: describe the user problem and separation of new speech from context.
- 0:40–1:40: drag the robot, browse cards, reveal the input, show volume/language. Explicitly state that the examples are fictional and inference is disabled.
- 1:40–2:40: explain local text/vision and lecture-language + interface-language sections. Matching languages are not duplicated.
- 2:40–3:30: open README and the verification report; explain freshness, queue and missing-file tests.
- 3:30–4:00: state Windows/AI limitations. The client explicitly excluded a clean second-PC test and a long lecture test from this completion; neither is reported passed.

## Release boundary and future work

The root-address crash is removed and covered by a regression test. Public-repository approval (source license decision, signing if required, actual Git history) remains separate. A realistic macOS path starts with a replaceable LiveSource adapter, then native window/caption capture tested with the same synthetic cases. This EXE does not run on macOS.
