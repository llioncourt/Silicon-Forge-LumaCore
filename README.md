# Silicon Forge LumaCore

Experimental volumetric optical exposure modulation for MSLA resin printing, focused on the Anycubic Photon Mono M7 Pro and translucent blue Standard Resin. The goal is to investigate selective UV grayscale exposure as a way to control internal scattering without altering the statue's external silhouette.

> **Experimental / not production validated.** Photon Workshop displayed the grayscale test coupon at layer 40 (2.03 mm), but neither actual LCD grayscale response nor cure safety nor optical improvement has been verified.

## Verified equipment profile

- Printer: Anycubic Photon Mono M7 Pro
- Resin profile: Anycubic Standard Resin; physical material: translucent blue
- Release film: ACF; print mode: Normal Print
- Layer thickness: 0.050 mm; normal exposure: 1.800 s
- Test coupon PWSZ: 80 layers, 5 bottom layers, 25 s bottom exposure (from uploaded PWSZ)
- Optical finish planned: Unipega high-gloss coating, not Tekbond

## Experiment

Three grayscale digital levels: 15/15 (control), 14/15 and 13/15, with preserved binary silhouette; original 80-layer coupon, 48 modified layers and 32 unchanged. The user opened the modified PWSZ in Photon Workshop and visually confirmed three tonal zones at layer 40. Printing is in progress; *results are pending*.

## Engineering principles

- Original sculpture geometry must remain intact; no slicer repair, through-holes, hidden liquid-resin pockets or floating islands.
- Differentiate geometric watertightness from full mesh validity and printer compatibility.
- Never claim physical optical improvement from software mask inspection alone.
- Treat resin dose-response, post-cure, and Unipega optics as uncalibrated until experimentally measured.
- Work directly on `main`; no new branches without explicit permission.

## Repository status

Archival in progress. Source documents, code and experimental outputs are being recovered from the development session. Large binaries require separate transfer support; do not treat this README as proof they are uploaded.

## Scientific foundation (2026-11-21)

- [Literature review, original MATLAB code inspection and implications for M7 Pro](research/REVISAO_CIENTIFICA_GRIN_GMSLA_2026-11-21.md)

- [Anycubic M7 Pro & maker community: UVtools v7 gamma, PWSZ, LUTs, RERF, and physical grayscale measurements](research/ANYCUBIC_M7PRO_COMUNIDADE_GRAYSCALE_2026-11-21.md)
- [Validation gates and experimental roadmap](https://github.com/llioncourt/Silicon-Forge-LumaCore/issues/2)

The grayscale PWSZ coupon is **not yet GRIN-validated**. Demonstrated in Photon Workshop and physical printing; effect on n(lambda), absorption/scattering and optical beam steering after post-curing remains unmeasured. Research papers use different resins, exposure hardware and calibration and must not be copied as machine settings.
