# CCareer__IsEpisodeAvailable

Status: active function note
Last updated: 2026-10-22 (research-campaign records removed)
Summary: `CCareer__IsEpisodeAvailable` at `0x00421570`: which campaign completions unlock each multiplayer episode.

> Address: 0x00421570 | Source: `references/Onslaught/Career.cpp`

## Status
- **Verified vs Source:** Yes (the retail body matches the source switch table and its `mComplete` checks)

## Purpose
Episode unlock check - controls MP level availability. Determines whether a multiplayer episode/level pack is available based on campaign progress.

## Signature

Takes the episode number and returns a boolean (`CCareer::IsEpisodeAvailable(int ep)` in the source).

## Unlock Table (Source)
Source (`references/Onslaught/Career.cpp`): `CCareer::IsEpisodeAvailable(ep)`

| Episode | Condition |
|---------|-----------|
| 0 | Always available |
| 1 | Always available |
| 2 | `COMPLETE_LEVEL(110)` |
| 3 | `COMPLETE_LEVEL(231)` or `COMPLETE_LEVEL(232)` |
| 4 | `COMPLETE_LEVEL(331)` or `COMPLETE_LEVEL(332)` |
| 5 | `COMPLETE_LEVEL(431)` or `COMPLETE_LEVEL(432)` |
| 6 | `COMPLETE_LEVEL(521)` or `COMPLETE_LEVEL(522)` or `COMPLETE_LEVEL(523)` or `COMPLETE_LEVEL(524)` |
| 7 | `COMPLETE_LEVEL(621)` or `COMPLETE_LEVEL(622)` |
| 8 | `COMPLETE_LEVEL(741)` or `COMPLETE_LEVEL(742)` |

## Notes
- Multiplayer has 15 levels: 6 co-op + 6 skirmish + 3 versus
- Some MP levels require campaign node completion to unlock
- Explains why `test_no_nodes` save had 3/6 skirmish and 3/6 co-op LOCKED
- Called at runtime, not stored directly in save file
- The retail body confirms this gate checks `CCareerNode.mComplete` (`node+0x04 == 1`) for the world set in each case; it does not use link states.

## Related Functions
- CCareer__GetNodeFromWorld (in the decompilation notes, not yet published) - Used to resolve world ids into `CCareerNode*`
- [CCareer__Update](CCareer__Update.md) - Marks nodes complete, affecting `COMPLETE_LEVEL(...)`
- [Career graph semantics](../../saves/career-graph.md) - Distinguishes node-complete gates (episodes) vs link-complete gates (career map world unlock)
