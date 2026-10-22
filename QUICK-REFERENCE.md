# Quick reference

Status: active — compact lookup tables
Last updated: 2026-10-22 (research-campaign counts removed)
Summary: dense lookup tables (AYA tags, save structures, MSL commands, command-line options, source layout) and where each one is documented in full.

These are compact lookup tables. When a table is corrected, update the detailed document it summarises as well.

For format facts use [formats/aya-tags.md](formats/aya-tags.md) and [formats/aya-resource-chunks.md](formats/aya-resource-chunks.md); for static anchors use [formats/game-assets-index.md](formats/game-assets-index.md) and [engine/mapped-systems.md](engine/mapped-systems.md).

## AYA / Resources

| File | Use |
| --- | --- |
| [formats/aya-tags.md](formats/aya-tags.md) | AYA file tag IDs, mesh/texture marker tags, and format markers |
| [formats/aya-resource-chunks.md](formats/aya-resource-chunks.md) | Resource archive chunk IDs, top-level chunk table, and hex IDs |

## Save / Career

| File | Use |
| --- | --- |
| [saves/save-structs.md](saves/save-structs.md) | BES/CCareer struct layout quick reference |
| [saves/save-ranks.md](saves/save-ranks.md) | Rank floats and raw bit patterns |
| [saves/save-goodies.md](saves/save-goodies.md) | Goodie/unlockable IDs and state handling |
| [saves/save-kills.md](saves/save-kills.md) | Kill counter categories, offsets, and packed metadata |

## Engine / Source

| File | Use |
| --- | --- |
| [mechanics/battleengine/battleengine-config-values.md](mechanics/battleengine/battleengine-config-values.md) | BattleEngine default config values and combat/movement constants |
| [engine/source/engine-singletons.md](engine/source/engine-singletons.md) | Engine singleton globals and subsystem ownership |
| [engine/source/source-files.md](engine/source/source-files.md) | Stuart source file organization |
| [engine/source/source-key-functions.md](engine/source/source-key-functions.md) | Important source function signatures |
| [engine/source/source-hierarchy.md](engine/source/source-hierarchy.md) | Class hierarchy and thing-type flags |

## Controls / Mission Scripts

| File | Use |
| --- | --- |
| [platforms/command-line/cli-parameters.md](platforms/command-line/cli-parameters.md) | Retail/source command-line parameter quick reference |
| [levels/scripting/msl-commands.md](levels/scripting/msl-commands.md) | MSL command reference and mission scripting verbs |

## Canonical Detailed Docs

Use these quick tables for lookup speed, then verify or expand findings in the detailed docs:

- [INDEX.md](INDEX.md)
- [Mapped systems](engine/mapped-systems.md) - Current static system owners and claim boundaries
- [formats/game-assets-index.md](formats/game-assets-index.md)
- [saves/save-format.md](saves/save-format.md)
- `struct-layouts.md` (archived research record, not published)
- [formats/aya-asset-format.md](formats/aya-asset-format.md)
- [levels/scripting/msl-scripting.md](levels/scripting/msl-scripting.md)
- [engine/source/README.md](engine/source/README.md)
