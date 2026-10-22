# Index

Status: active — the front door to this repository's findings
Last updated: 2026-10-22 (rewritten as this repository's own index)
Summary: where each kind of finding about *Battle Engine Aquila* lives in this repository, the evidence rules
every claim meets, and the patch analyses, per-subsystem contracts and machine-readable tables.

This repository documents *Battle Engine Aquila* as prose and tables: file formats, save and options layouts,
mechanics, levels and mission scripts, engine systems, the PC, demo and console builds, documented executable
patches, and notes on Stuart Gillam's published source (GitHub `stuart73/Onslaught`). Function names follow the
byte-matching decompilation of the retail executable, which is the naming authority; its function notes are not
yet published. A document that cites one says "(in the decompilation notes, not yet published)", and a citation
of the project's private research history says "(archived research record, not published)". Dated notes quote the
counts and names of their own time; read them as history.

## Evidence rules

- Static names, types, strings and call relationships prove only the structures they directly show.
- Stuart's source release (`references/Onslaught`) and his AYA extractor are references, not proof of how the
  Steam executable is implemented or of complete format support.
- A controlled runtime observation establishes only the measured behaviour on the measured specimen.
- Agreement with a rebuild does not re-prove retail behaviour.
- This repository holds no executables, game data, converted game data, saves, debugger logs or decompiler output.
  Retail inputs stay with whoever owns the game.

## Start here

| Area | Entry point |
| --- | --- |
| File and asset formats | [Formats](formats/README.md) and the [game-assets index](formats/game-assets-index.md) |
| Saves and options | [Save-file index](saves/README.md) |
| Measured mechanics | [Game-mechanics index](mechanics/README.md) |
| Levels and mission scripts | [Levels](levels/README.md) and [mission scripting](levels/scripting/README.md) |
| Engine architecture | [Engine](engine/README.md) and the [mapped-systems routing table](engine/mapped-systems.md) |
| Retail binary findings | [Static findings index](engine/static-findings-index.md) and the [retail specimen baseline](platforms/pc/retail-specimen-baseline.md) |
| PC demo versus retail | [Build comparison](platforms/demo/demo-vs-retail.md) |
| Stuart's source | [Source-code index](engine/source/README.md) and the [source synthesis](engine/source/stuart-source-synthesis.md) |
| Development history and credits | [History](history/README.md) and the [development source index](history/development-sources.md) |
| Compact lookups | [Quick reference](QUICK-REFERENCE.md) |

## Patch analyses — not write authorisation

These documents record where a byte lives, which function owns it, what the clean bytes are, and what was observed
when a copied executable carried the change. An observation covers only the copy it was made on. Applying a patch
to an installed game is the player's own choice and needs a verified backup first; the pristine
`BEA.exe.original.backup` is never a target. The patch catalogue that the companion app applies lives in
Onslaught-Career-Editor (`patches/CATALOG_CONTRACT.md` and `patches/README.md` there); where a note here and that
catalogue disagree, the catalogue wins.

**Two documents carry a withdrawn claim.** The 2026-07-28 guard-byte correction struck a hex-edit recipe out of both
the windowed-mode and the widescreen analyses. Both keep the withdrawn text visible and struck through. Read the
correction before acting on either.

### The widescreen patch

| Document | What it settles |
| --- | --- |
| [Widescreen patch analysis](platforms/patches/widescreen-patch-analysis.md) | The `BEA_Widescreen.exe` diff: **191 changed bytes across 28 regions**, file length unchanged, code-cave-plus-trampoline technique, both SHA-256s recorded. A historical analysis of an external patch; its guard-byte normalisation section is **withdrawn (2026-07-28)**. |
| [28-region diff table](platforms/patches/widescreen-diff-regions-28.tsv) | File offsets, addresses, before/after bytes, owning function, evidence and behaviour class for each region. All 28 regions are accounted for: 14 functional and 14 supporting. |

### Per-feature patch notes

| Document | Anchor, and how far the claim reaches |
| --- | --- |
| [CLI defaults and complete parser](platforms/command-line/CLIParams__ParseCommandLine.md) | Initializer ownership (CLIParams, not Unit AI); four defaulting controls, 47 isolated original-parser cases and the 25-option static map. Actual startup and downstream acceptance remain open. |
| [Windowed mode](platforms/display/windowed-mode-analysis.md) | **Partially superseded 2026-07-28.** `-forcewindowed` is real and reachable, but its parser gate `0x00662f3e` is BSS, zero at load, and is set only by `-testeur` earlier on the same command line. There is no file byte to edit. The two-gate model and the startup-flow patch at file offset `0x12A644` stand. |
| [Extra-graphics feature gate](platforms/patches/extra-graphics-feature-gate-patch.md) | `GEFORCE_FX_POWER` registers with default `0`; `0x004CDD40`, `6A 00` → `6A 01`, with the companion row that ignores `cardid.txt` vendor/device matching. |
| [Version overlay](platforms/patches/version-overlay-patch.md) | The opt-in `V1.00 - PATCHED` marker as a pair: a visible pointer row and a hidden cave-string row. One copied-game title/menu run confirmed the marker. |
| [Frontend clear-screen colour](platforms/patches/frontend-clear-screen-color-patch.md) | Three mutually exclusive immediates at `0x00540F88` in `CDXFrontEnd__RenderStart`; source anchor `references/Onslaught/DXFrontend.cpp`. |
| [Goodies gallery display unlock](platforms/patches/goodies-gallery-display-unlock-patch.md) | Forces the existing display flag inside `CFEPGoodies__Process` (`0x0045D7F4`). **Display only — it does not alter save progression.** |
| [Free-camera Aurore-gate bypass](platforms/patches/free-camera-aurore-gate-bypass-patch.md) | NOPs the `IsCheatActive(4)` gate on `BUTTON_TOGGLE_FREE_CAMERA` in `CGame__ReceiveButtonAction`, plus eight keyboard cave variants. **Experimental.** |
| [Pause-key default row](platforms/patches/pause-key-default-row-patch.md) | One immediate in `OptionsEntries__InitDefaultSingleBindingsTable` (`0x005144CD`, `01` → `18`). **Experimental.** |

## Static contracts by subsystem

Bounded static maps, one subsystem each. They establish addresses, call relationships, constants and structures in
the analysed specimen, not runtime behaviour, exact layouts or source-body identity.
[Mapped systems](engine/mapped-systems.md) names the current owner document for each system.

| Subsystem | Contract |
| --- | --- |
| MissionScript / IScript | [missionscript-iscript-static-contract.md](levels/scripting/missionscript-iscript-static-contract.md) |
| PhysicsScript | [physics-script-static-contract.md](formats/physics-script-static-contract.md) |
| Meshes and resources | [mesh-resource-render-static-contract.md](engine/render/mesh-resource-render-static-contract.md) |
| Render/resource bridge | [render-resource-bridge-static-contract.md](engine/render/render-resource-bridge-static-contract.md) |
| Texture decode | [texture-resource-decode-static-contract.md](formats/texture-resource-decode-static-contract.md) |
| HUD and frontend overlay | [hud-frontend-overlay-static-contract.md](engine/frontend/hud-frontend-overlay-static-contract.md) |
| Destroyable segments | [destroyable-segments-static-contract.md](mechanics/destroyable-segments-static-contract.md) |
| Units, movement, weapons | [unit-battleengine-gameplay-static-contract.md](mechanics/unit-battleengine-gameplay-static-contract.md) |
| Local multiplayer | [local-multiplayer-static-runtime-contract.md](platforms/local-multiplayer-static-runtime-contract.md) |
| Career progression bridge | [career-progression-static-bridge-contract.md](saves/career-progression-static-bridge-contract.md) |
| Level 100 final wave: turrets, Missile Pod locks, crosshair refresh, seeking rounds and RNG-drawing owners | [level100-final-drone-wave.md](levels/level100-final-drone-wave.md) |
| Battle Engine weapon stores, charge law and firing state | [battle-engine-weapon-stores.md](mechanics/battleengine/battle-engine-weapon-stores.md) |
| Battle Engine auto-aim, launch position and cockpit Gun emitters | [battle-engine-aiming.md](mechanics/battleengine/battle-engine-aiming.md) |
| Level 100 construction order: shared draws, queued events and the first event flush | [level100-construction-order.md](levels/level100-construction-order.md) |
| World 110 construction order, the Level 100 to World 110 transition, first flush and player start | [world-110-construction-order.md](levels/world-110-construction-order.md) |
| Named waypoint paths: loading, start node, following and the Level 100 and World 110 routes | [waypoint-paths.md](mechanics/waypoint-paths.md) |
| Dropship flight: per-tick move, guide steering, turning and move orders | [dropship-flight.md](mechanics/dropship-flight.md) |
| Dropship landing: landing states, `Land()`, unloading, withdrawal, turret and AI schedule | [dropship-landing.md](mechanics/dropship-landing.md) |
| Walker dash: the retail timing window, its float32 frame table and the strafe roll | [walker-dash.md](mechanics/battleengine/walker-dash.md) |
| CMSH `CPOS`/`CORI` identity | [cmsh-cpos-cori-identity.md](formats/cmsh-cpos-cori-identity.md) |

Per-function contracts sit beside their subsystem: [Battle Engine](mechanics/battleengine/contracts/README.md),
[world](engine/world/contracts/README.md), [unit AI](mechanics/ai/README.md), [career](mechanics/career/README.md)
and [save functions](saves/by-function/README.md). Function-level notes that were mostly records of the research
process have moved to the decompilation notes; [DECOMP-BOUND.md](DECOMP-BOUND.md) lists them.

Machine-readable tables:

- [MissionScript VM datatype/opcode schema](levels/scripting/missionscript-vm-datatype-opcode-schema.v1.json)
- [Mission script-command registry](levels/scripting/mission-script-command-registry.tsv)
- [Battle Engine target-acquisition contract](mechanics/battleengine/battleengine-target-acquisition-static-contract-v1.json)
- [Walker transform/morph timing](mechanics/battleengine/walker-transform-morph-timing-v1.json)

## Reference and routing

| Document | Use it for |
| --- | --- |
| [Mapped systems](engine/mapped-systems.md) | From a system to its current smallest evidence owner. Start here when you know the subsystem but not the document. |
| [High-impact call chains](engine/high-impact-call-chain-appendix.md) | Static chains with their consequence spelled out, for example that loading a retail save can rewrite the boot-time options snapshot, and that resume or exit can persist both the career and `defaultoptions.bea`. |
| [Executable analysis](platforms/pc/executable-analysis.md) | PE identity, hashes, size, DLL imports, the D3D9 confirmation, and the Lost Toys/Encore branding. |
| [Controlled runtime observations](engine/controlled-runtime-observations.md) | What controlled runs of copied retail builds have measured, and their limits. |

## Product-facing summaries

- [Save/options boundary](saves/public-save-options.md)
- [Assets and modding boundary](formats/public-assets-and-modding.md)

The companion app that edits careers, saves and settings, and applies the patch catalogue, is
[Onslaught-Career-Editor](https://github.com/dlprentice/Onslaught-Career-Editor).
