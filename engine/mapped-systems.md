# Mapped systems

Status: active — routing table
Last updated: 2026-10-22 (retired AppCore/WinUI tools in the past tense)
Summary: the smallest current evidence owner for each system, and the code that consumes it.

This page routes implementation work to the smallest current static evidence
owner. It is not a function-completion ledger and does not promote static
analysis to runtime proof.

## Canonical system owners

| System | Evidence owner | Implementation consumer (Onslaught-Career-Editor `51129bab` unless named) |
| --- | --- | --- |
| Career save layout, grades, unlocks, kills | [`../saves/README.md`](../saves/README.md) | companion `CareerSave` (the retired AppCore `BesFilePatcher` before it) |
| Options and control bindings | [`../saves/save-options-startup-compatibility.md`](../saves/save-options-startup-compatibility.md) | companion `OptionsFile` (the retired AppCore `ConfigurationEditorService` before it) |
| Executable identity and patch regions | [`../platforms/pc/executable-analysis.md`](../platforms/pc/executable-analysis.md) and focused patch notes | none now; the retired AppCore patch catalogue and `BinaryPatchEngine` used it |
| BattleEngine movement, morph, weapons, units | [`../mechanics/unit-battleengine-gameplay-static-contract.md`](../mechanics/unit-battleengine-gameplay-static-contract.md) | rebuild Core policies and copied-target research |
| Target acquisition | [`../mechanics/battleengine/battleengine-target-acquisition-static-contract-v1.md`](../mechanics/battleengine/battleengine-target-acquisition-static-contract-v1.md) | deterministic rebuild targeting work |
| PhysicsScript | [`../formats/physics-script-static-contract.md`](../formats/physics-script-static-contract.md) | parser/schema and rebuild interface work |
| MissionScript / IScript | [`../levels/scripting/missionscript-iscript-static-contract.md`](../levels/scripting/missionscript-iscript-static-contract.md) | scripting format/schema work |
| Frontend, input, HUD | [`frontend/hud-frontend-overlay-static-contract.md`](frontend/hud-frontend-overlay-static-contract.md) | UI/rebuild interpretation only |
| Meshes, resources, render bridge | [`render/mesh-resource-render-static-contract.md`](render/mesh-resource-render-static-contract.md) and [`render/render-resource-bridge-static-contract.md`](render/render-resource-bridge-static-contract.md) | asset parsing and rebuild rendering adapters |
| Texture/resource decode | [`../formats/texture-resource-decode-static-contract.md`](../formats/texture-resource-decode-static-contract.md) | asset inspection/export tooling |
| Audio, media, cutscenes, camera | `audio-media-cutscene-static-review-2026-05-26.md` (archived research record, not published) | media browser and research |
| Assets, AYA chunks, mission text | [`../formats/game-assets-index.md`](../formats/game-assets-index.md) | guarded exporters (`tools/`) |
| Local multiplayer evidence | [`../platforms/local-multiplayer-static-runtime-contract.md`](../platforms/local-multiplayer-static-runtime-contract.md) | copied-profile split-screen preset only |
| Function-level identities | `_index.md` (in the decompilation notes, not yet published) | source/evidence lookup |

## Claim boundary

Static evidence can establish addresses, call relationships, constants,
formats, and bounded structures visible in the analyzed specimen. It does not
by itself establish runtime behavior, exact object layouts, source-body
identity, patch safety, visual parity, online play, or reconstruction parity.

Stuart's source and the pinned `references/Onslaught` submodule inform names and
hypotheses but are not retail Steam proof. Controlled runtime observations must
use a verified copied target and record specimen identity; proprietary payloads
and bulky captures remain outside Git.

When a finding changes product behavior, update the owning companion or rebuild
code and its consequential focused test in that project. Do not create a new progress ledger,
wave mirror, generated inventory, or readiness report merely to restate these
owners.
