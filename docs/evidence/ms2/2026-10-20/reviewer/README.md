# Isolated reviewer setup — checkpoint 32

Executed on 2026-10-20, native Apple M1 / Linux ARM64. The exact clean source
revision was `a25ed2a8aa19a59f7262942a4864ffa59ec7cb53`.

A fresh GitHub clone was fast-forwarded to that local implementation commit
before final publication. No restored data or host node_modules were carried
over from the original checkout. The existing checksum-verified archive was
restored into the new checkout, yielding 187 files. Docker could reuse build
layers; this was not a fresh Docker installation or a second machine.

## Actual execution

`make ms2-demo` exited **0** in project `lungcancer-ms2-review`, using separate
image tags, mounts and port **18080**. It verified the prepared inventory, ran
the real 16-tile preprocessing smoke, performed the real HTTP upload/poll and
computed `non_tumor` from the existing 512-vector cache. Reference difference:
**6.938893903907228e-18**, below 1e-8. No encoder, training or new test-metric
calculation ran.

All **ten** browser/API scenarios passed: known/renamed bytes, filename and
case invariance, fixture isolation, modified/unknown inputs, empty/oversized
uploads, and actual isolated-API outage/recovery. Zero page errors; no request
interception supplied predictions. The existing host browser test client and
Chromium installation were reused; the served app/backend came from the new
checkout's containers.

Stop/resume passed; only reviewer containers/networks were removed afterward.
The original app at 127.0.0.1:8080 retained its container IDs, image tags,
complete private input inventory and ready health. Reviewer raw inputs and
bulk outputs remain ignored locally.

## Inspect the evidence

- [Reproduction summary, access scope and preservation checks](reproduction.json).
- [Actual bounded workflow and image identities](demo.json), [HTTP prediction](prediction.json).
- [187-file restore log](restore.txt), [complete build/start/preprocessing/HTTP log](demo.txt).
- [Real preprocessing result](real_preprocessing.json), [inventory/runtime report](verification_preprocess.json).
- [Browser report](browser-report.json), [browser command log](browser.txt).
- [Unmodified real successful browser screenshot](known-result.png), [unmodified unsupported-input screenshot](unknown-error.png).
- [Actual 512-coordinate overlay](analyzed_tiles_overlay.jpg).
- [Stop](app-stop.txt), [resume](app-resume.txt), [cleanup](app-down.txt), [live runtime inspection before cleanup](runtime.json).
- [Source/published artifact hashes and substitutions](manifest.json), [SHA256SUMS](SHA256SUMS).

Text copies replace absolute checkout paths with `<REVIEW_CHECKOUT>` or
`<REPO_ROOT>`; the manifest records both source and published hashes.
The published demo log also strips trailing whitespace; its original hash and
normalization are recorded in the manifest. Screenshots/JPEGs are unmodified.
Input binaries, permission email addresses,
credentials, weights and signed download URLs are excluded.

Drive metadata established owner and one existing collaborator's permissions
on the protected archive. No sharing change or another person's login/run is
claimed. The original scientific GDC/UNI2/training stages remain Colab work;
this result does not establish fresh-UNI2 container inference. See
[pipeline scope](../../../../PIPELINE_SCOPE.md) and
[reviewer instructions](../../../../REVIEWER_SETUP.md).
