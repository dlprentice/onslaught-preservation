# Onslaught preservation

Status: active — the repository's front page
Last updated: 2026-11-11 (headers described as present on every document; the check command named on the front page; the findings rule stated)
Summary: what this repository documents about *Battle Engine Aquila*, where to start in each section, how to read a
finding, the licence, related projects and how to contribute.

This repository documents how *Battle Engine Aquila* (Lost Toys, 2003) works: its file formats, career saves and
options, gameplay mechanics, levels and mission scripts, engine systems, and the PC, demo and console builds. The
findings are measured from the retail game, from Stuart Gillam's published GPL source and from controlled runtime
evidence.

The one rule for findings: documentation of behaviour, formats and mechanics lives here; a function's identity, naming
and matching go to [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp).

It is Markdown, TSV and JSON tables, plus one small check script ([`tools/check_docs.py`](tools/check_docs.py)). It contains no game executables, no copies of the game's data files and no
decompiler output. Short quoted strings appear where a finding needs them, for example in the comparison tables under
[`platforms/demo/`](platforms/demo/README.md). A patch document may also give the few original and patched bytes of its
patch site, as [CONTRIBUTING.md](CONTRIBUTING.md) allows.

## Start here

- [`INDEX.md`](INDEX.md) is the front door: what each store covers and the evidence rules every claim has to meet.
- [`QUICK-REFERENCE.md`](QUICK-REFERENCE.md) collects the lookup tables (save structures, tags, MSL commands,
  command-line options, source layout).
- [`DECOMP-BOUND.md`](DECOMP-BOUND.md) lists the per-function notes that were removed from this repository; their subject
  matter belongs to the decompilation's function notes, which are not yet published.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) says [where each kind of work belongs](CONTRIBUTING.md#where-to-contribute) across the
  project's public repositories, and what to check before a pull request.

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

- Each document opens with `Status:`, `Last updated:` (or `Date:`) and `Summary:` lines; some carry a
  `Verdict:` in place of the `Summary:`. A dated note's counts and names are those of its date; read it as history.
- A finding's `Evidence:` line starts with one of four labels. `MEASURED`: read from the shipped game, by a controlled
  runtime capture, a byte comparison, a table read out of shipped data, or a test that asserts a recovered law.
  `SOURCE`: backed by the pinned Onslaught source, with file and line; it shows shape, ownership and intent, and does not
  by itself show that the Steam build agrees. `INFERRED`: reasoned from something else. `UNKNOWN`: not settled, and the
  line says what would settle it. A document that mixes labels is graded by its weakest load-bearing claim.
- A *per-function contract* (for example under `saves/by-function/` or `mechanics/battleengine/contracts/`) is a
  bounded, static description published here. The decompilation's *per-function notes* are a different set and are not
  published.
- Every behaviour claim cites its evidence: a controlled runtime capture, a byte comparison against a named retail
  file, a focused test, or a pinned source file and line. Static evidence establishes identities and structures; only
  controlled runtime evidence establishes causality and values. Unknowns are written as open questions.
- Retail addresses refer to the specimen named in the document, normally the pristine Steam `BEA.exe`
  (SHA-256 `74154bfa…`; see the [retail specimen baseline](platforms/pc/retail-specimen-baseline.md)). To check your own
  copy, run `sha256sum BEA.exe`; a copy that does not match the specimen's hash is a different file, and a measurement
  made on it needs its own specimen line. `BEA.exe.original.backup`, the name some documents give the specimen, is the
  maintainer's untouched copy; you do not need a file of that name.
- Function names such as `CCareer__Save` are the names of the matching decompilation,
  [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), which is the naming authority. Its per-function notes are not
  published; a document that cites one says "(in the decompilation notes, not yet published)", and the reconstructed
  source itself is in onslaught-decomp.
- This repository has no `references/` folder. `references/Onslaught/<file>` cites Stuart's published source at the pinned commit
  [`c3d8ac4`](https://github.com/dlprentice/Onslaught/tree/c3d8ac464259942b83fa8aa7f867c856e77b734d) of the
  public reference fork of [stuart73/Onslaught](https://github.com/stuart73/Onslaught); for example,
  `references/Onslaught/Career.cpp` is
  [`Career.cpp` at that commit](https://github.com/dlprentice/Onslaught/blob/c3d8ac464259942b83fa8aa7f867c856e77b734d/Career.cpp).
  Some documents cite the fork's earlier commit [`5352a81`](https://github.com/dlprentice/Onslaught/tree/5352a81cdb838b145a57f7febc5d9fc4b0129ebb), which the source synthesis names as its pinned commit; `c3d8ac4` adds new files and changes none of the files present at `5352a81`, so a citation to one of those files gives the same lines at either commit.
  `references/AYAResourceExtractor/<file>` cites his
  [AYAResourceExtractor](https://github.com/stuart73/AYAResourceExtractor) at the pinned commit
  [`53b10b0`](https://github.com/dlprentice/AYAResourceExtractor/tree/53b10b083b59cfd7e72849c15bec8b608eaf8a23).
- `<maintainer evidence>/…` names a receipt (capture, probe output, readback) kept privately by the maintainer
  because it holds retail bytes or machine detail. Its hash, where given, identifies it.
- The *mirror index* cited by the format documents (`<maintainer evidence>/bea-asset-mirror/INDEX.jsonl`, schema `onslaught.asset-mirror-index.v1`) is the maintainer's private manifest of the installed retail files: one row per file, with its SHA-256 and format classification. [`formats/README.md`](formats/README.md) describes it, and the format documents cite its row counts and hashes.
- A path cited "in Onslaught-Career-Editor", such as `tools/…`, `rebuild/…`, `companion/…`, `tests_shared/…` or
  `VALIDATION.md`, names the file at commit [`51129bab`](https://github.com/dlprentice/Onslaught-Career-Editor/tree/51129bab45489e5e45ee1c047cbcd8072bf4cc50) of
  [Onslaught-Career-Editor](https://github.com/dlprentice/Onslaught-Career-Editor), where the tools, the rebuild and the companion were developed when the finding
  was written. The rebuild (`rebuild/…`) has since moved to [onslaught-godot](https://github.com/dlprentice/onslaught-godot). The retired
  AppCore editor and its patch catalogue (`OnslaughtCareerEditor.AppCore/…`, `patches/…`) are cited at
  [`4ac3c9ae`](https://github.com/dlprentice/Onslaught-Career-Editor/tree/4ac3c9ae32d97c1293858c49bf9cc485eb814f28), the last commit that has them.
  A document that cites a tool added later, such as the animation census in `formats/lvlr-archive.md`, names its own
  commit, for example [`843c86e`](https://github.com/dlprentice/Onslaught-Career-Editor/tree/843c86e06810c8fce953226ccebd41bf2cf74473).
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
- [onslaught-godot](https://github.com/dlprentice/onslaught-godot): a proof-of-concept C# rebuild of the game on Godot,
  not yet a playable release. Its simulation is compared Present by Present with selected recorded runs of Onslaught CE
  and the original game; its [parity record](https://github.com/dlprentice/onslaught-godot/blob/main/rebuild/PARITY.md)
  describes the measured routes and their limits.
- [Onslaught-Career-Editor](https://github.com/dlprentice/Onslaught-Career-Editor) (also called the Toolkit): Onslaught
  Companion, the app for careers, saves, settings and backups, with the game's lore and lore book, and the project's
  goal and plan (to be renamed onslaught-companion). Its player capabilities are to move into Onslaught CE, and the separate app is to be phased out after verified replacement; it has no published release yet.
- [stuart73/Onslaught](https://github.com/stuart73/Onslaught): Stuart Gillam's published Onslaught source, which
  many findings here cite.

## Contributing

Corrections and new findings are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) first: it says
[where each kind of work belongs](CONTRIBUTING.md#where-to-contribute), contributions come in under the same licence,
every claim needs evidence, and game files, decompiler output and disassembly listings with raw bytes are never
accepted. Before a pull request, run `python3 tools/check_docs.py --changed` (Python 3, standard library only); it checks
links, anchors, headers and machine paths. Security problems and leaked private material go through
[`SECURITY.md`](SECURITY.md).
