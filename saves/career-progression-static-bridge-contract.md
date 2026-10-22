# Career progression static bridge

Status: active routing note
Last updated: 2026-10-22 (research-campaign records removed)
Summary: where each career-progression concern is documented, from source vocabulary to retail save bytes.

This page connects source-side career vocabulary to the retail save and static
function evidence without claiming runtime persistence or source identity.

| Concern | Canonical evidence |
| --- | --- |
| Retail file layout and byte preservation | [`save-format.md`](save-format.md) |
| Campaign nodes and links | [`career-graph.md`](career-graph.md) and [`career-links.md`](career-links.md) |
| Source architecture | [`../engine/source/gameplay/career-system.md`](../engine/source/gameplay/career-system.md) and [`../engine/source/gameplay/game-system.md`](../engine/source/gameplay/game-system.md) |
| Career update/recalculation | [`../mechanics/career/CCareer__Update.md`](../mechanics/career/CCareer__Update.md) and [`../mechanics/career/CCareer__ReCalcLinks.md`](../mechanics/career/CCareer__ReCalcLinks.md) |
| Mission result handoff | `CGame__FillOutEndLevelData.md` (in the decompilation notes, not yet published), `CGame__DeclareLevelWon.md` (in the decompilation notes, not yet published), and `CGame__DeclareLevelLost.md` (in the decompilation notes, not yet published) |
| Secondary-objective predicate | `CEndLevelData__IsAllSecondaryObjectivesComplete.md` (in the decompilation notes, not yet published) |

`level_structure`, `CCareer`, `CGame`, and `CEndLevelData` are safe bridge
vocabulary for implementation planning. This evidence does not prove runtime
save/load behavior, mission outcome persistence, campaign-map UI behavior,
Goodie recomputation, exact source-to-retail layout identity, or rebuild parity.
