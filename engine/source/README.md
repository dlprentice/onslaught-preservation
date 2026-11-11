# Reference source analysis

Status: active — folder index
Last updated: 2026-11-11 (quick-reference pages linked)
Summary: how the notes on Stuart's pinned external source are organised and where to find the current rebuild's
implementation and licence boundary.

These notes use Stuart Gillam's published Onslaught source at commit
[`c3d8ac4`](https://github.com/dlprentice/Onslaught/tree/c3d8ac464259942b83fa8aa7f867c856e77b734d), taken from the public
reference fork of [stuart73/Onslaught](https://github.com/stuart73/Onslaught), and
[AYAResourceExtractor at `53b10b0`](https://github.com/dlprentice/AYAResourceExtractor/tree/53b10b083b59cfd7e72849c15bec8b608eaf8a23)
as external reference evidence. The labels `references/Onslaught` and
`references/AYAResourceExtractor` are historical citation paths; this repository
contains neither submodule. A finding that names an earlier commit, such as `5352a81` (the last of the six upload commits in the synthesis's pin and upload history, which older notes cite as their source pin), describes that dated source snapshot. The current pin is `c3d8ac4`, a later reference-fork commit that merges Stuart's mesh source additions. The earlier reference-submodule audit is an archived
research record, not published.

Stuart Gillam's source represents an internal PC development lineage. The Steam
retail executable and save layout differ. Source names and architecture are
useful hypotheses; they are not proof of retail identity or behavior.

[`stuart-source-synthesis.md`](stuart-source-synthesis.md) is the dated narrative
synthesis of Stuart's source at commit `5352a81` (committed 2025-12-12), the snapshot named in its header.
The `references/Onslaught` citations in these notes use the README pin `c3d8ac4` instead. Every file tracked at
`5352a81` has the same Git blob ID at `c3d8ac4`; `c3d8ac4` adds 23 files (21 C/C++ mesh files and two repository guide
files), so the cited files are identical at both commits. The source files themselves remain the
line-level authority for that source lineage.

## Fetching the pinned source

This repository holds neither the Stuart fork nor its files. The `references/Onslaught/<file>` citations name the fork at commit `c3d8ac464259942b83fa8aa7f867c856e77b734d`, so to check one, clone the fork outside this repository and check out that commit:

```sh
git clone https://github.com/dlprentice/Onslaught ../onslaught-src
git -C ../onslaught-src checkout c3d8ac464259942b83fa8aa7f867c856e77b734d
```

Then read `references/Onslaught/<file>` as `../onslaught-src/<file>`; the fork keeps its sources at its root. Keep that checkout outside this repository. It holds Stuart's GPL-3.0-only source, which these notes quote only as [CONTRIBUTING.md](../../CONTRIBUTING.md) allows.

## System maps

- Core ([index](core/README.md)): [thing](core/thing-system.md), [actor](core/actor-system.md),
  [engine](core/engine-system.md), [platform](core/platform-system.md)
- Gameplay ([index](gameplay/README.md)): [career](gameplay/career-system.md),
  [battle](gameplay/battle-system.md), [game loop](gameplay/game-system.md)
- Frontend ([index](frontend/README.md)): [menus](frontend/fep-systems.md),
  [controllers](frontend/controller-system.md)
- I/O ([index](io/README.md)): [storage](io/storage-system.md), [chunker](io/chunker-system.md),
  [events](io/event-system.md)

Quick-reference pages for the source as a whole:
[singletons and subsystem ownership](engine-singletons.md), [file organisation](source-files.md),
[class hierarchy and thing types](source-hierarchy.md) and [key function signatures](source-key-functions.md).

The physical-file byte and line manifest and the parser census in
[`stuart-source-synthesis.md`](stuart-source-synthesis.md), both counted at commit `5352a81`,
remain provenance snapshots, not completeness or semantic-correctness claims. Current retail relationships belong in the
smallest owning binary-analysis note rather than a generated crosswalk mirror.

The GPL rebuild is RE-informed original code, not a mechanical translation of
these references. Follow [onslaught-godot's provenance record](https://github.com/dlprentice/onslaught-godot/blob/main/rebuild/PROVENANCE.md)
for its current license and implementation boundary.
