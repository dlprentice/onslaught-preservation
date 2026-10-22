# Binary Analysis

Status: living index of the static and byte-level findings
Last updated: 2026-10-22 (research-campaign records and decompiler-style code removed)
Summary: front door to the static and byte-level findings about the Steam `BEA.exe`: specimen baseline, dated
analyses, per-system contracts and per-function notes. Makes no claim of its own — every claim below belongs to the
document it links.

The byte-matching decompilation (not yet published) is the naming and behaviour authority. The earlier research
process records that used to head this index are kept privately and are not published. Function counts and
names quoted in the documents below are dated snapshots.

## Dated analyses and provenance

- [Retail Specimen Baseline](../platforms/pc/retail-specimen-baseline.md)
- Retail capture provenance — what the reference screenshots actually show (archived research record, not published)
- The 34 newly admitted MissionScript functions now have bounded static contracts (in the decompilation notes, not yet published)
- MissionScript 34-handler semantic refinement (in the decompilation notes, not yet published)
- D3DX9 section-contribution provenance (in the decompilation notes, not yet published)
- Collision-component implementation-identity correction (archived research record, not published)
- [PC demo versus PC retail](../platforms/demo/demo-vs-retail.md)
- `pc-demo-retail-virtual-target-map-2026-08-11.tsv` (in the decompilation notes, not yet published)
- `CUnit` primary virtual interface: demo/retail semantic crosswalk (in the decompilation notes, not yet published)
- `cunit-primary-vtable-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- `CBattleEngine` virtual-interface semantic crosswalk (in the decompilation notes, not yet published)
- `cbattleengine-vtable-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- `CThing` base-interface semantic crosswalk (in the decompilation notes, not yet published)
- `cthing-vtable-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- `CComplexThing` virtual-interface semantic crosswalk (in the decompilation notes, not yet published)
- `ccomplexthing-vtable-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- `CThing` / `CComplexThing` retail object layout (in the decompilation notes, not yet published)
- `CActor` virtual-interface semantic crosswalk (in the decompilation notes, not yet published)
- `cactor-vtable-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- `CPCController` platform-interface semantic crosswalk (in the decompilation notes, not yet published)
- `cpccontroller-vtable-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- [`CController` shared mapping and dispatch semantic recovery](../mechanics/controller-shared-semantics.md)
- `controller-shared-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- Controller-to-player/game event spine (in the decompilation notes, not yet published)
- `controller-player-game-event-spine-2026-08-11.tsv` (in the decompilation notes, not yet published)
- `CPCMusic` platform-interface semantic crosswalk (in the decompilation notes, not yet published)
- `cpcmusic-vtable-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- [`CMusic` shared music-policy semantic recovery](audio/cmusic-shared-semantics.md)
- `cmusic-shared-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- [`CSoundManager` shared audio-policy semantic recovery](audio/csoundmanager-shared-semantics.md)
- `csoundmanager-shared-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- [`CPCSoundManager` DirectSound backend semantic recovery](audio/cpcsoundmanager-backend-semantics.md)
- `cpcsoundmanager-backend-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- [PC memory-buffer and allocation-service semantic recovery](io/pc-memory-io-semantics.md)
- `pc-memory-io-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- [Frontend save/load and PC persistence semantics](../saves/frontend-save-load-semantics.md)
- `frontend-save-load-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- [`CPCMemoryCard` released PC save-backend semantics](../saves/cpcmemorycard-pc-save-backend-semantics.md)
- `cpcmemorycard-pc-save-backend-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- [`CCareer` released PC save-format semantics](../saves/career-save-format-semantics.md)
- `career-save-format-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- [`CTokenArchive` particle grammar and reference semantics](../formats/tokenarchive-semantics.md)
- `tokenarchive-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- `PCLTShell` virtual-interface semantic crosswalk (in the decompilation notes, not yet published)
- `pcltshell-vtable-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- [`CGame` level-lifecycle semantic recovery](cgame-level-lifecycle-semantics.md)
- `cgame-level-lifecycle-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- [Event-manager scheduler semantic recovery](world/event-manager-scheduler-semantics.md)
- `event-manager-scheduler-semantics-2026-08-11.tsv` (in the decompilation notes, not yet published)
- CTentacle factory-name chain — evidence and rehearsal (archived research record, not published)
- [Reverse-Engineering Index](../INDEX.md)
- Runtime-witness corpus merge — DeepSeek Extended findings relocated and queued (archived research record, not published)

## Product and format contracts

- [Executable analysis](../platforms/pc/executable-analysis.md)
- [Windowed mode](../platforms/display/windowed-mode-analysis.md)
- [Widescreen patch](../platforms/patches/widescreen-patch-analysis.md)
- [Career progression bridge](../saves/career-progression-static-bridge-contract.md)
- [Mission script contract](../levels/scripting/missionscript-iscript-static-contract.md)
- [Physics script contract](../formats/physics-script-static-contract.md)
- [Texture resource decoding](../formats/texture-resource-decode-static-contract.md)
- [Terrain shade plane origin and axis order](render/terrain/terrain-shade-plane-origin.md)
- Terrain shade bilinear interpolation decode (to be published here after review)
- [Terrain draw texture-stage flags](render/terrain/terrain-draw-stage-flags.md)
- [Terrain per-node colour light absent from the PC path](render/terrain/terrain-per-node-colour-absent.md)
- Retail's implied macro cache inverted from rendered pixels (archived research record, not published)
- Sun colour route to the terrain draw — all ten references, negative (to be published here after review)
- Terrain material record and the `LANDSCAPE_LIGHTING` gate (to be published here after review)
- Terrain ambient-light term implemented and measured (archived research record, not published)
- Cockpit lighting law — located, decoded, already implemented (to be published here after review)
- [The default render-state block `0x004EB1E0` — re-derived from bytes](render/d3d-default-render-state-block.md)
- Half-pixel pixel-centre offset corrected in the projection (archived research record, not published)
- [CMSH `CPOS`/`CORI` identity](../formats/cmsh-cpos-cori-identity.md)
- [`CRound::Hit`, `CExplosion::Hit`, and their separate damage paths](../mechanics/cround-hit-damage-path.md)
- `CRound` event-2000 two-position runtime addendum (archived research record, not published)
  — bounds two exact receiver-matched `CALL_ENTRY` paths, explicitly retaining
  the 167/10/2 selection limit and leaving allocator return/effects open
- [`CWorldPhysicsManager::CreateExplosion` caller family](../mechanics/cexplosion-factory-callers.md)
- [Local multiplayer evidence boundary](../platforms/local-multiplayer-static-runtime-contract.md)

Focused patch notes remain beside the binary evidence they depend on. Applied
wave scripts and readiness reports are retained in Git history, not as active
tools or navigation.

## Function notes

`functions` (in the decompilation notes, not yet published) contains retained per-function evidence.
These notes are not decompiler source and do not authorize copying proprietary
code into the rebuild.

For controlled debugger work, use the CDB runbook (archived research record, not published).
Full databases, backups, raw logs, and captures stay outside Git.
