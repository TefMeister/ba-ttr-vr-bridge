# 2026-11-14: DLSS off at 150% changes nothing: the far skyline still swims and the picture is still soft

Developer PC, /ms, Opus, Tefa in the headset (Quest 3 through Virtual Desktop, 72 Hz). Tefa's question: do the
smudging and the swimming far skyline go away with DLSS off and about 1.5x supersampling?

## The test

- Our test mod `Bridge - picture test DLSS off 150` (`bridge-mods/`): its own `TTWVR.ini` at TTWVR's path with
  `Resolution=150%`, `Upscaler=Off`, every other line as TTWVR's (165%, DLSS, Quality, Sharpness 65%). On in
  `rung-05 interface` only, on the top line of `modlist.txt` (= highest priority, above `TTWVR 1.0.0`); backup
  `modlist.txt.bak-2026-11-14-picture-test`. TTWVR's own file untouched.
- Run 17:05-17:08, Save 4, rung 5. Logs kept: `runs/2026-11-14 1705 rung-05 interface headset picture test DLSS off 150/`
  (with Virtual Desktop's `OpenXR.log`). An 11.6 s main-loop stop during the load (TTWVR's hang watcher, dump written,
  then turning again); no crash.
- Switched off again afterwards (Tefa did not ask to keep it); `ladder.py check` clean.

## What Tefa saw

*"still the same in fallout, game is low resolution"* `[reported, n=1]`: the far skyline still swims with the head
sway, the near grass and shrubs the same, the picture still low resolution.

## The sizes `[measured 2026-11-14]`

- Virtual Desktop's own log, this run: `Application: NVVR (FalloutNV.exe)`, `Recommended resolution: 2688x2880 (1.000
  supersampling, 1.000 upscaling)`. TTWVR's log: `Meta Quest 3 (swapchains up to 16384x16384)`.
- **The 4096-per-eye cap is the OpenXR Simulator's** (`swapchains up to 4096x4096` in its runs), not the headset's: on
  the Quest nothing is capped at 165% or at 150%.
- TTWVR's percentage is per side (simulator: 2944 wide at 100%, 4864 at 165%) `[measured 2026-11-12]`. So on the Quest:
  now (165% + DLSS Quality) about 4435x4752 out, drawn at about 2957x3168; the test (150%, no upscaler) drawn at
  4032x4320, about 1.9 times the pixels `[inferred-static]`.
- TTWVR's log never prints the eye size it chose, nor which settings file won; the test file's win is
  `[inferred-static]` (MO2 priority). Tefa was asked whether the VR menu showed 150% / Off.
- The 2026-11-11 note "Upscaler=Off froze the picture" was a simulator-only finding: in the headset the picture with the
  upscaler off was live `[verified-live 2026-11-14, n=1]`.

## What it means

- **The swimming far skyline is not DLSS** `[verified-live 2026-11-14, n=1]`. It stays with the board's suspect, TTWVR's
  far (LOD) pass in stereo (`MODEL: FABLE`).
- **The softness is not the size the game draws at**: about twice the pixels without any upscaler looked the same
  `[reported, n=1]`. Downstream suspects `[hypothesis]`: Virtual Desktop's stream (codec H.264+ on this PC; bitrate and
  quality are set on the headset), or the way TTWVR hands the eye picture over. The cheap decider: does another VR game
  look sharp through Virtual Desktop on the same settings? (asked of Tefa).
- Frame rate at 150% without DLSS: not yet reported.

## Then: the same rung with the test mod off (17:52, Tefa)

Rung 5 again with TTWVR's own settings (165%, DLSS Quality, Sharpness 65%), logs in
`runs/2026-11-14 1752 rung-05 interface headset short run/`. Tefa: *"picture was clear now, but the far away thing and
bushes still smudge"* `[reported, n=1]`. The two runs differ only by the test mod, so DLSS Quality at 165% looks
clearer than no upscaler at 150% (DLSS also anti-aliases and sharpens) `[inferred]`; it stays. The soft look Tefa
remembered from rung 3 (2026-11-13) was most likely DLSS Performance, set then `[hypothesis]`. The smudging of far
things and bushes is there with and without DLSS, so it is not the upscaler `[reported, n=2 runs]`.
