# Onslaught preservation

Status: active — the repository's front page
Last updated: 2026-10-29 (onslaught-godot described as its own README describes it; earlier: related projects linked; Onslaught-Career-Editor citations pinned to one commit)
Summary: what this repository documents about *Battle Engine Aquila*, where to start in each section, how to read a
finding, the licence, related projects and how to contribute.

This repository documents how *Battle Engine Aquila* (Lost Toys, 2003) works: its file formats, career saves and
options, gameplay mechanics, levels and mission scripts, engine systems, and the PC, demo and console builds. The
findings are measured from the retail game, from Stuart Gillam's published GPL source and from controlled runtime
evidence.

It is Markdown and tables only. It contains no game executables, no game data or converted copies of game data,
and no decompiler output.

## Start here

- [`INDEX.md`](INDEX.md) is the front door: what each store covers and the evidence rules every claim has to meet.
- [`QUICK-REFERENCE.md`](QUICK-REFERENCE.md) collects the lookup tables (save structures, tags, MSL commands,
  command-line options, source layout).
- [`DECOMP-BOUND.md`](DECOMP-BOUND.md) lists the function-level notes that moved to the decompilation notes.

| Section | What it covers | Start with |
| --- | --- | --- |
| [`formats/`](formats/README.md) | File and asset formats: AYA containers, CMSH meshes, DDS and TGA textures, LVLR archives, XAP sample banks, Ogg and Bink media, particle and physics scripts, token archives | [AYA container](formats/aya-container.md), [CMSH mesh](formats/cmsh-mesh.md), [formats summary](formats/formats-summary.tsv) |
| [`saves/`](saves/README.md) | The `.bes` career save, the options file, control bindings and the save and load flow; [`saves/by-function/`](saves/by-function/README.md) holds function-level save contracts | [Save format](saves/save-format.md), [career save semantics](saves/career-save-format-semantics.md), [save structures](saves/save-structs.md) |
| [`mechanics/`](mechanics/README.md) | How play works: the [Battle Engine](mechanics/battleengine/README.md) (with its [contracts](mechanics/battleengine/contracts/README.md)), [unit AI](mechanics/ai/README.md), [career rules](mechanics/career/README.md), [cheats](mechanics/cheats/README.md) and [weapons](mechanics/weapons/README.md) | [Battle Engine aiming](mechanics/battleengine/battle-engine-aiming.md), [grade system](saves/grade-system.md), [god mode](mechanics/cheats/god-mode.md) |
| [`levels/`](levels/README.md) | The level inventory, how level 100 and world 110 are built, and [mission scripting](levels/scripting/README.md) | [Level inventory](levels/level-inventory.md), [MSL scripting](levels/scripting/msl-scripting.md) |
| [`engine/`](engine/README.md) | Engine architecture: [world](engine/world/README.md) and its [contracts](engine/world/contracts/README.md), [rendering](engine/render/README.md) (with [terrain](engine/render/terrain/README.md)), [front end](engine/frontend/README.md), [audio](engine/audio/README.md), [I/O](engine/io/README.md), and a guide to [Stuart's source](engine/source/README.md) | [Engine architecture](engine/README.md), [static findings index](engine/static-findings-index.md) |
| [`platforms/`](platforms/README.md) | The [retail PC executable](platforms/pc/README.md), the [PC demo](platforms/demo/README.md), [console versions](platforms/console/README.md), [display](platforms/display/README.md) and [command-line](platforms/command-line/README.md) options, and documented [executable patches](platforms/patches/README.md) | [Retail specimen baseline](platforms/pc/retail-specimen-baseline.md), [command-line parameters](platforms/command-line/cli-parameters.md) |
| [`history/`](history/README.md) | Development sources, attribution, community resources and lore errata | [Attribution](history/attribution.md), [development sources](history/development-sources.md) |

## How to read a finding

- Each document opens with `Status:`, `Last updated:` (or `Date:`) and `Summary:` lines. Older documents that predate
  the convention have no header yet; their dates are in the text.
- Every behaviour claim cites its evidence: a controlled runtime capture, a byte comparison against a named retail
  file, a focused test, or a pinned source file and line. Static evidence establishes identities and structures; only
  controlled runtime evidence establishes causality and values. Unknowns are written as open questions.
- Retail addresses refer to the specimen named in the document, normally the pristine Steam `BEA.exe`
  (SHA-256 `74154bfa…`; see the [retail specimen baseline](platforms/pc/retail-specimen-baseline.md)).
- Function names such as `CCareer__Save` are the names of the matching decompilation,
  [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), which is the naming authority. Its per-function notes are not
  published; a document that cites one says "(in the decompilation notes, not yet published)", and the decompiled
  source itself is in onslaught-decomp.
- `references/Onslaught/<file>` cites Stuart's published source at the pinned commit
  [`c3d8ac4`](https://github.com/dlprentice/Onslaught/tree/c3d8ac464259942b83fa8aa7f867c856e77b734d) of the
  public reference fork of [stuart73/Onslaught](https://github.com/stuart73/Onslaught).
  `references/AYAResourceExtractor/<file>` cites his
  [AYAResourceExtractor](https://github.com/stuart73/AYAResourceExtractor) at the pinned commit
  [`53b10b0`](https://github.com/dlprentice/AYAResourceExtractor/tree/53b10b083b59cfd7e72849c15bec8b608eaf8a23).
- `<maintainer evidence>/…` names a receipt (capture, probe output, readback) kept privately by the maintainer
  because it holds retail bytes or machine detail. Its hash, where given, identifies it.
- A path cited "in Onslaught-Career-Editor", such as `tools/…`, `rebuild/…`, `companion/…`, `tests_shared/…` or
  `VALIDATION.md`, names the file at commit [`51129bab`](https://github.com/dlprentice/Onslaught-Career-Editor/tree/51129bab45489e5e45ee1c047cbcd8072bf4cc50) of
  [Onslaught-Career-Editor](https://github.com/dlprentice/Onslaught-Career-Editor), where the tools, the rebuild and the companion were developed when the finding
  was written. The rebuild (`rebuild/…`) has since moved to [onslaught-godot](https://github.com/dlprentice/onslaught-godot). The retired
  AppCore editor and its patch catalogue (`OnslaughtCareerEditor.AppCore/…`, `patches/…`) are cited at
  [`4ac3c9ae`](https://github.com/dlprentice/Onslaught-Career-Editor/tree/4ac3c9ae32d97c1293858c49bf9cc485eb814f28), the last commit that has them.
- "(archived research record, not published)" marks a citation of the project's private research history: process
  records that are kept but not published.

## Licence

The documentation and tables are licensed under the Creative Commons Attribution-ShareAlike 4.0 International
licence ([`LICENSE`](LICENSE), also at [`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt)), with these
exceptions, recorded per path in [`REUSE.toml`](REUSE.toml):

- The notes in [`engine/source/`](engine/source/README.md) quote Stuart Gillam's published Onslaught source, which is
  GPL version 3 only. They are CC BY-SA 4.0 and GPL-3.0-only ([`LICENSES/GPL-3.0-only.txt`](LICENSES/GPL-3.0-only.txt)),
  crediting Stuart, and the quoted source keeps its own licence.
- The two AYAResourceExtractor notes in `formats/` (`aya-resource-extractor-*`) quote Stuart's separately published
  AYAResourceExtractor, whose licence is MIT. They are CC BY-SA 4.0 and MIT ([`LICENSES/MIT.txt`](LICENSES/MIT.txt)).
- Quotations of developers, interviews and articles stay with their authors, quoted for commentary and preservation.

The licences grant no rights in the game, its executable, assets, names or trademarks. *Battle Engine Aquila* belongs
to its rights holders; this is an unofficial community project and is not affiliated with or endorsed by them.
Credits are in [`history/attribution.md`](history/attribution.md).

## Related projects

- [onslaught-ce](https://github.com/dlprentice/onslaught-ce): Onslaught CE, a native Linux and Windows port of the game built from its
  source, to play it on current systems with your own copy of the game.
- [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp): the byte-matching decompilation of the retail executable, the naming
  authority for the function names used here.
- [onslaught-godot](https://github.com/dlprentice/onslaught-godot): a proof-of-concept C# rebuild of the game on Godot, not yet
  playable. Its simulation is compared frame by frame with recorded runs of Onslaught CE, and with recorded runs of the
  original game up to frame 10,000.
- [Onslaught-Career-Editor](https://github.com/dlprentice/Onslaught-Career-Editor): the companion app for careers, saves, settings and backups, with the game's
  lore and lore book (to be renamed onslaught-companion).
- [stuart73/Onslaught](https://github.com/stuart73/Onslaught): Stuart Gillam's published Onslaught source, which
  many findings here cite.

## Contributing

Corrections and new findings are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) first: contributions come in
under the same licence, every claim needs evidence, and game files, decompiler output and disassembly listings with
raw bytes are never accepted.
