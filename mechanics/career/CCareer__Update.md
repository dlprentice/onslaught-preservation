# CCareer__Update

Status: active function note
Last updated: 2026-10-22 (research-campaign records removed)
Summary: `CCareer__Update` at `0x0041bd00`: how a finished mission updates slots, kills, ranking, links and goodies.

> Address: `0x0041bd00`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::Update()`)

## Status
- **Verified vs Source:** Yes

## Purpose
Update career progress from the current `END_LEVEL_DATA` snapshot.

This is the “mission finished” entry point: it updates slots/kills, updates node completion + ranking, recalculates links, then recomputes goodies.

## Signature

A `CCareer` member with no arguments and no return value (`CCareer::Update()` in the source).

## High-Level Flow (Source-Parity)
1. If `END_LEVEL_DATA.mFinalState != GAME_STATE_LEVEL_WON`:
   - `UpdateGoodieStates()` and return.
2. Copy `END_LEVEL_DATA.mSlots` into `mSlots` (slots are overwritten, not accumulated).
3. `UpdateThingsKilled()` (adds per-level kill deltas into career totals).
4. Resolve the finished node by `END_LEVEL_DATA.mWorldFinished`:
   - If not found: fatal error.
5. Update ranking if improved (`if END_LEVEL_DATA.mRanking > node->mRanking`).
6. Set `node->mComplete = TRUE`.
7. Set `mCareerInProgress = TRUE` (persisted in save).
8. `ReCalcLinks()` (unlock/mark links; handles world 500 special-case).
9. `UpdateGoodieStates()` (recompute goodies based on new progress).

## Static anchors

`CCareer__Update` calls `CCareer__ReCalcLinks` after a won level, and the world-500 slot branch connects to `CGame__SetSlot`, `IScript__SetSlotSave` and `IScript__GetSlotBitValue`. Runtime progression and save outcomes, the concrete Career/CGame layouts and gameplay outcomes remain separate proof.

## Related Functions
- [CCareer__ReCalcLinks](CCareer__ReCalcLinks.md) - Update link completion/broken state
- [CCareer__UpdateGoodieStates](../../saves/by-function/CCareer__UpdateGoodieStates.md) - Goodie unlock recomputation
- [CCareer__UpdateThingsKilled](../../saves/by-function/CCareer__UpdateThingsKilled.md) - Kill counter accumulation
- [CCareer__GetGradeFromRanking](CCareer__GetGradeFromRanking.md) - Converts ranking to grade
