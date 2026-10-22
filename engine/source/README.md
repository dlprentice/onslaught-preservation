# Reference Source Analysis

Status: active — folder index
Last updated: 2026-10-22 (research-campaign records removed)
Summary: how the notes on Stuart's pinned source are organised, and what the reference submodules are used for.

The pinned [`references/Onslaught`](https://github.com/stuart73/Onslaught) and
[`references/AYAResourceExtractor`](https://github.com/stuart73/AYAResourceExtractor)
submodules are actively used reference evidence. Their current build, format,
test, provenance, and license posture is recorded in the
reference-submodule audit (archived research record, not published).

Stuart Gillam's source represents an internal PC development lineage. The Steam
retail executable and save layout differ. Source names and architecture are
useful hypotheses; they are not proof of retail identity or behavior.

[`stuart-source-synthesis.md`](stuart-source-synthesis.md) is the dated narrative
synthesis of that exact pinned source corpus. The source files themselves remain
the line-level authority.

## System maps

- Core ([index](core/README.md)): [thing](core/thing-system.md), [actor](core/actor-system.md),
  [engine](core/engine-system.md), [platform](core/platform-system.md)
- Gameplay ([index](gameplay/README.md)): [career](gameplay/career-system.md),
  [battle](gameplay/battle-system.md), [game loop](gameplay/game-system.md)
- Frontend ([index](frontend/README.md)): [menus](frontend/fep-systems.md),
  [controllers](frontend/controller-system.md)
- I/O ([index](io/README.md)): [storage](io/storage-system.md), [chunker](io/chunker-system.md),
  [events](io/event-system.md)

The February parse and manifests remain provenance snapshots, not completeness
or semantic-correctness claims. Current retail relationships belong in the
smallest owning binary-analysis note rather than a generated crosswalk mirror.

The GPL rebuild is RE-informed original code, not a mechanical translation of
these references. Follow `rebuild/PROVENANCE.md` in Onslaught-Career-Editor
for its license and implementation boundary.
