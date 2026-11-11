# History and attribution

Status: active — folder index
Last updated: 2026-11-11 (known bugs added; earlier: 2026-11-06 (the community Discord history replaces the March 2026 extract; earlier: 2026-10-22 (method history added)))
Summary: attribution, development sources, community resources and lore errata.

## Overview

This folder holds the history around the game and this documentation rather than findings about the game itself: who contributed what, where development sources came from, community resources, and corrections to published lore.

## Documents

| Document | Description |
|----------|-------------|
| [attribution.md](attribution.md) | Public-safe attribution, contributor history, and preservation context |
| [community-resources.md](community-resources.md) | Speedrun resources, emulators, similar games |
| [development-sources.md](development-sources.md) | First-party development sources and what each is good for |
| [community-history.md](community-history.md) | Dated history of the community Discord, 2021 to 2026 (replaces the March 2026 extract) |
| [known-bugs.md](known-bugs.md) | Reported problems with the original game, the ranking mechanism, and the early save-patching mistakes that crashed careers |
| [lore-errata.md](lore-errata.md) | Corrections to published lore |

## How the findings were made

Most of the older static findings were first worked out in a Ghidra project of the retail executable, with
function names, signatures and comments refined over many passes. Since October 2026 the byte-matching
decompilation ([onslaught-decomp](https://github.com/dlprentice/onslaught-decomp)) is the naming and behaviour authority; the Ghidra project and the records of those passes are
kept privately as history and are not published, and nothing in this repository depends on them.

## Notable Contributors

| Name | Role | Repo Relevance |
|------|------|----------------|
| Stuart Gillam | Lead programmer | Internal-source guidance and public preservation repos |
| Glenn Corpes | Technical director | Historical engine/rendering context |
| Alex Trowers | Lead designer | Lore/design background |
| Community researchers | Players/modders | Save files, archival leads, validation feedback |

## See Also

- [Lore](https://github.com/dlprentice/Onslaught-Career-Editor/tree/main/lore) in Onslaught-Career-Editor (the companion app's repository): full team roster, development history and community history
