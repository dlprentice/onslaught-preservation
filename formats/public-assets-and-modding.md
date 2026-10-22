# Public assets and modding overview

Status: public-safe overview
Last updated: 2026-10-22 (retired AppCore/WinUI tools in the past tense)
Summary: what public changes may contain, and two controlled copied-game findings (one localization entry, one
compiled mission command) that show which modified retail inputs the engine consumes.

The companion's source tree and portable app do not include retail game assets or converted copies. Resource
analysis, copied-game runs and the rebuild read a user's lawfully obtained installation as local input.

## Public Boundary

- Retail executable patching and local analysis still require a legally
  obtained installation or verified copied specimen.
- Public changes may add exact extraction/conversion recipes and bounded
  provenance, not retail asset payloads. Do not add bulk exports, saves,
  screenshots, copied executables, converted assets, or raw proof bundles.
- Patches must target copied executables, not the installed Steam folder.
- Patch descriptions should say only what is byte-verified or runtime-proven.

## Proven Copied-Content Slice

These are historical findings. They were made with the copied-game ("safe-copy") feature of the retired AppCore
editor (Onslaught-Career-Editor
[`4ac3c9ae`](https://github.com/dlprentice/Onslaught-Career-Editor/tree/4ac3c9ae32d97c1293858c49bf9cc485eb814f28),
the last commit that has it); no maintained tool offers either change now.

A controlled run of a copied game showed that the engine displays a replaced fixed-size English localization entry:
Level 100 `TUTORIAL_01`, text ID `4422830`, in
`data/language/english.dat`. The editor verified the supported Steam table hash
and original UTF-16 bytes, kept the table and file length unchanged, wrote a
backup, and recorded before/after hashes in the copied-profile manifest. The
copied game rendered the unique replacement in Level 100.

A second controlled run showed that the engine consumes a rebuilt
`data/resources/100_res_PC.aya` with one exact compiled mission-command change:
Level 100's initial `DisableFlightMode` call becomes `EnableFlightMode`.
The editor verified the original archive and decompressed payload hashes, changed
one byte in the `LevelScript` instruction stream, wrote an original backup,
round-tripped the four size-prefixed zlib members, and validated the exact
original/modified payload pair before launch. In controlled retail runs, the
same transform input reached the original rejection return with the clean
archive and the walker-to-jet state write with the changed archive. A copy made
by the retired WinUI app reproduced the accepted path with the runtime flight flag
set.

The implementation anchors are `LevelScript` instruction 33 (`CALL`,
opcode `24`) and its command byte at decompressed payload offset `3658889`:
descriptor `101` is `DisableFlightMode` and descriptor `100` is
`EnableFlightMode`. Retail observation distinguished the walker-to-jet state
write at `BEA.exe+0xA753` from the disabled-flight return at
`BEA.exe+0xA87D`. Stuart's `BattleEngine.cpp` supports the interpretation—the
walker morph returns while flight mode is disabled—but the copied Steam runtime
establishes the released behavior.

These slices establish that the retail engine consumes the copied language
table and this one rebuilt compiled mission archive. They do not establish
arbitrary string growth, other languages, loose `.msl` loading, a general
mission compiler/editor, texture replacement, general AYA repacking, or a mod
package format. The early-flight change deliberately bypassed Level 100's
training progression; it is not a claim about intended campaign behavior.

## Useful References

- [AYA Tags](aya-tags.md)
- [AYA Resource Chunks](aya-resource-chunks.md)
- [Command-Line Parameters](../platforms/command-line/cli-parameters.md)
- [MSL Scripting Overview](../levels/scripting/msl-scripting.md)
