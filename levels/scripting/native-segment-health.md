# Segment health and vulnerability natives

Status: active — static behaviour of five natives that set a unit's segment health and vulnerability; no runtime capture
Last updated: 2026-11-11 (new document)
Evidence: MEASURED — the five handlers and the segments-controller and segment functions they call are functions of onslaught-decomp that the decompilation lists as matching the retail bytes, read statically; INFERRED — the effect on play; UNKNOWN — the open questions at the end.
Summary: `SetSegmentHealth`, `ResetSegmentHealth`, `SetAllSegmentsHealth`, `SetSegmentVulnerable` and `SetAllSegmentsVulnerable` change a segment's current health, its maximum health or its vulnerable flag on a unit that has a segments controller, find a segment by mesh-part name, and differ in whether they also refresh the controller's remembered total, which the unit's death test compares against.
Specimen: pristine Steam `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` (the file onslaught-decomp matches).

These natives are part of [the natives overview](native-behaviour.md), which explains how a native is called, how the
evidence is gathered and what the "shipped use" counts are. They act on the destroyable-segment system described in the
[destroyable segments static contract](../../mechanics/destroyable-segments-static-contract.md) (break ordering); this page
describes only what the natives change. Names are those of
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) at commit `9759593`, whose
[`docs/check/matched.tsv`](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/docs/check/matched.tsv)
lists every function cited here as matching the retail bytes. The decompilation spells the class
`CDestructableSegmentsController` and the segments `CDestroyableSegment`; those are the names used here.

## What they act on

A unit that is built from segments owns a `CDestructableSegmentsController` (`CUnit::mSegments`); the decompilation shows
`CBuilding::Init` and `CHiveBoss` creating one. The controller holds one `CDestroyableSegment` pointer for each part of
the unit's mesh, a pointer to the primary core segment, and a remembered total health. Each segment has a current health,
a maximum health, a vulnerable flag and a list of child segments
([`DestroyableSegment.h` L58](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DestroyableSegment.h#L58)).

All five natives start with the same gate: the script's current target must be a unit (`THING_TYPE_UNIT`) and must have a
controller. Otherwise they do nothing and say nothing (the handlers are at
[`IScript.cpp` L511](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L511),
[L537](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L537)
and [L911](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L911) to L940).
The three natives that take a name pass it to the controller, which looks it up as a **mesh part name**: the unit's render
thing, its mesh, `CMesh::GetMeshSubpart(name)`, the part's number, and the controller's pointer for that number. If the
unit has no render thing or no mesh, the call returns without a message. If the name is not a part of the mesh, or the
part has no segment, the controller logs a message that begins "FATAL ERROR: Could not find segment for" and the call
returns; the message is not fatal and the script goes on.

## What each one writes

| Native | Writes | Refreshes the remembered total | Shipped use |
| --- | --- | --- | --- |
| `SetSegmentHealth(name, health)` ([`DestructableSegmentsController.cpp` L172][d-set]) | the named segment's current health | no | 27 sites in one file, the level 530 hive-boss script |
| `ResetSegmentHealth(name, health)` ([L194][d-reset]) | the named segment's current health and its maximum health, both to `health` | yes, if the unit has a core | 54 sites in 2 files, the level 521 and 522 hive-boss scripts |
| `SetAllSegmentsHealth(health)` ([L236][d-setall]) | the current health of every segment that exists | no | 3 sites in the level 530 hive-boss script; four more, two in each of the level 521 and 522 scripts, are commented out |
| `SetSegmentVulnerable(name, flag)` ([L246][d-vuln]) | the named segment's vulnerable flag | yes, if the unit has a core | 54 sites in 2 files, levels 521 and 522 |
| `SetAllSegmentsVulnerable(flag)` ([L270][d-vulnall]) | the vulnerable flag of every segment that exists | yes, if the unit has a core | 2 sites, one each in levels 521 and 522 |

"Refreshes the remembered total" means that the controller sets its remembered total health to its core segment's
active health (below). The health natives store the value as given, with no clamp: a script can set a current health above the
maximum, and the level 530 script does (see below). The flags are read with `IsTrue`: an integer is true when nonzero and a bool is its own value, while a float, string,
thing or position argument would count as true whatever its value (see [how a call runs](native-behaviour.md#how-a-call-runs)). The shipped scripts pass integer or bool literals.

`ResetSegmentHealth` and `SetSegmentHealth` are the same call with one difference: the reset also sets the maximum, and
refreshes the total. Because `SetSegmentVulnerable` also refreshes the total, a script that wants the total to reflect a
new health calls `ResetSegmentHealth` and then `SetSegmentVulnerable`, which is the order the level 521 and 522 scripts use for each
segment.

## What the stored values mean

All of this is read from `CDestroyableSegment` and `CDestructableSegmentsController`, and is static.

- **Damage lowers current health only.** `CDestroyableSegment::Damage` subtracts the amount from the current health of a
  vulnerable segment, clamps it at zero and does nothing to a segment that is not vulnerable
  ([`DestroyableSegment.cpp` L117](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DestroyableSegment.cpp#L117)).
  A segment that is not vulnerable keeps its health whatever hits it. It is not immune to breaking, though: the core and
  extra segment types test the health again after the base step and break a segment that is not yet destroyed when its
  health is at or below zero, and the swap type breaks a segment whose health is exactly zero, whether or not it is
  vulnerable (a core segment numbered 1 returns before any of this). So a segment whose health a script has set to zero
  breaks on its next hit even while it is not vulnerable (`CDestroyableCoreSegment::Damage`,
  `CDestroyableExtraSegment::Damage`, `CDestroyableSwapSegment::Damage`).
- **Active health.** `CDestroyableSegment::GetActiveHealth` adds, over a segment and all of its descendants, the
  *maximum* health of each segment that is vulnerable, has a nonzero current health and does not lie under a core segment
  that is already cascading (`CanBreak` false). `GetTotalHealth` adds the *current* health of each vulnerable segment not
  under a cascading core
  ([L89](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DestroyableSegment.cpp#L89)).
  The remembered total is a snapshot of the core's active health taken by the refreshes in the table.
- **The unit's life.** `CDestructableSegmentsController::GetLife` is 1.0 when no segment is vulnerable and otherwise the
  core's active health; `CUnit::GetLife` (and so the `GetHealth` native) returns it for a unit that has a controller
  ([`DestructableSegmentsController.cpp` L119](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DestructableSegmentsController.cpp#L119),
  [`Unit.cpp` L693](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/Unit.cpp#L693)).
  The `GetMaxLife` side returns the remembered total, also 1.0 when no segment is vulnerable
  ([L147](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DestructableSegmentsController.cpp#L147)).
- **The death test.** After a segment takes damage, `CDestructableSegmentsController::Damage` starts the unit's die
  process when the core's children are all destroyed or when 0.3 times the remembered total is greater than the core's
  active health
  ([L48](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DestructableSegmentsController.cpp#L48)).
  The remembered total is therefore the reference for that test: a script that makes the controller remember a total with
  `ResetSegmentHealth` or the vulnerability natives sets the figure that 30 % is measured against.

## How the shipped scripts use them

The only scripts that call these natives are the three hive-boss scripts (levels 521, 522 and 530). Read as a corpus
observation of the loose scripts, not as a runtime result:

- Levels 521 and 522 switch every segment to not vulnerable in `init()` with `SetAllSegmentsVulnerable(FALSE)`; the
  two `SetAllSegmentsHealth(1000000.0)` lines that level 530 uses at that point are present in these scripts but commented
  out. In the launch sequence they give each named core and shield segment its health with `ResetSegmentHealth("core2",
  core_health)` and then make it vulnerable with `SetSegmentVulnerable("core2", TRUE)`, using one value for the cores and
  another for the shield cylinders. The segment names are mesh part names (`core2`, `core3`, `core4` and cylinder parts).
- Level 530 calls `SetAllSegmentsHealth(1000000.0)` on a thing named "Hive Support" and on the boss itself in `init()`,
  under a script comment that this makes them indestructible; later it sets the named core and shield segments with
  `SetSegmentHealth` and calls `SetAllSegmentsHealth(10.0)` on the support. Neither native refreshes the remembered
  total, so after these calls the total is still the figure from the last refresh.

## Open questions

1. **Runtime confirmation.** The tables above are read from code. Falsifier: in a copy of level 521 or 530, call each
   native and read the segment and controller values back with a debugger or a status report.
2. **`SetHealth` on a segmented unit.** See the [overview](native-behaviour.md#open-questions): the written life and the
   life `GetHealth` reports are different values for a unit with a controller.
3. **Who else reads the remembered total.** The death test above and the life ratio read it; this page does not list every
   reader, and the damage path beyond the segment natives is not described here.
4. **Level 530's use of very large health values.** What "indestructible" means for the boss depends on how its damage path
   reaches a segment's current health; this page does not trace it.

[d-set]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DestructableSegmentsController.cpp#L172
[d-reset]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DestructableSegmentsController.cpp#L194
[d-setall]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DestructableSegmentsController.cpp#L236
[d-vuln]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DestructableSegmentsController.cpp#L246
[d-vulnall]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DestructableSegmentsController.cpp#L270
