# TOTAL_S_GRADES

Status: active function note
Last updated: 2026-10-22 (research-campaign records removed)
Summary: `TOTAL_S_GRADES` at `0x0041c240`: counts S-ranked worlds against a goodie's threshold.

> Address: 0x0041c240 | Source: `references/Onslaught/Career.cpp` (`TOTAL_S_GRADES(int goodie_num)`)

## Status
- **Verified vs Source:** Yes

## Purpose
Counts completed worlds with S-rank and returns whether that count meets the unlock threshold for a given goodie row.

## Signature

Takes the goodie row number and returns a boolean.

## Behavior (Source-Parity)
1. Iterate all career nodes (`num_nodes`).
2. Convert each node's `mRanking` to grade and count `S` results.
3. Compare `found` against `goodies[goodie_num].GetNumber()`.
4. Return `true` when threshold is met.

## Notes
- This helper is called from `CCareer__UpdateGoodieStates` for S-rank milestone goodies.
- The callsites around goodies `74..77` align with source `TOTAL_S_GRADES(74..77)` conditions.

## Related Functions
- [CCareer__UpdateGoodieStates](../../saves/by-function/CCareer__UpdateGoodieStates.md) - Uses this helper for S-rank unlock milestones
- [CCareer__GetGradeFromRanking](CCareer__GetGradeFromRanking.md) - Grade conversion used in count logic
- [CCareer__GetGradeForWorld](CCareer__GetGradeForWorld.md) - Additional grade helper used by unlock logic
