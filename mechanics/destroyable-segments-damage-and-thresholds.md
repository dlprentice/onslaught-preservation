# Destroyable segments: damage, thresholds and the core cascade

Status: active — static description of how a segmented building or boss takes damage and when its death starts; no runtime capture of the whole path
Last updated: 2026-11-11 (new page)
Evidence: MEASURED, static — every function named below is in the byte-matching decompilation, and the original-code cases on the Level 100 Warehouse (linked below) agree where they overlap; one field read was repeated on the retail executable for this page. SOURCE — only the lines of Stuart's source cited for the crosshair rule and under "Aim position". UNKNOWN — live behaviour on a real building, listed under "Open questions".
Summary: how a unit built from destroyable segments divides its life between segments, what a hit does, the two thresholds (30% starts the unit's death, 50% sets a latch), what the death cascade does when the unit dies by another route, which segment the aim point uses, and what the part-availability test returns. Break ordering is in the [static contract](destroyable-segments-static-contract.md).
Specimen: pristine Steam `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

A *segmented unit* is a unit whose mesh is built from parts that break separately: the buildings with destroyable
parts and the Hive Boss. It has a *controller* that keeps one *segment* per mesh part, and its life is the life of those
segments, not a single number. This page is about the numbers: how life is divided, what one hit changes, and what the
two thresholds do. How a segment breaks (the order of rubble, effects, spawner removal and child scheduling) is in the
[destroyable segments static contract](destroyable-segments-static-contract.md). The original-code cases on the Level 100
Warehouse, which exercise the same controller with supplied inputs, are in
[the Warehouse section of the `CRound::Hit` note](cround-hit-damage-path.md#warehouse-segmented-explosion-report).

## How to read the evidence here

- Function names are those of the decompilation,
  [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), at commit
  [`9759593`](https://github.com/dlprentice/onslaught-decomp/tree/9759593ee6f6103f936080ac0435275e6ce9e06a). The
  segment classes are in `src/DestroyableSegment.cpp`, the controller in `src/DestructableSegmentsController.cpp`, the
  part-availability bridge in `src/MCDestructableSegments.cpp`, and the callers in `src/Unit.cpp`, `src/Building.cpp`
  and `src/HiveBoss.cpp` (each linked from [the commit's tree](https://github.com/dlprentice/onslaught-decomp/tree/9759593ee6f6103f936080ac0435275e6ce9e06a/src)).
  The controller and segment spellings differ (`Destructable…` and `Destroyable…`); both are retail's.
- Each function cited compiles to the retail bytes (the decompilation's [score](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/docs/SCORE.md)
  lists them). A byte match says what the function does as code. It does not say which game situations reach it, and
  it does not give the original source's names: the decompilation names some of these methods by their position
  because the original name is unknown, and this page calls them by their role.
- The maintainer's earlier static reads of the same retail bodies agree with every threshold and ordering below
  (archived research record, not published). Where one of those reads disagreed with the decompilation, this page
  follows the decompilation and says so ("Corrections").
- Stuart's published source has no copy of any segment file (the decompilation's file headers say so). Nothing here is
  measured at runtime except what the Warehouse note above records.

## The pieces

**The controller** is created by exactly two classes: `CBuilding::Init` (which passes 2.0 as the core fall distance,
the mode argument TRUE and a fourth argument 0) and `CHiveBoss::Init` (10.0, FALSE and 1). `CBuilding::Init` deletes the
controller again if the mesh had no core segment at all. Its fields that matter here are the segment array (one slot per
mesh part), the root segment (the primary core), the owning unit, a *cached total health*, and a one-shot *latch*.
(Decompilation: both `Init` functions, the controller constructor, `ProcessNode`.)

**A segment** has current health, maximum health, a *vulnerable* flag (initially set), a *destroyed* flag, the time and
amount of its last damage, a parent, a set of children, and a *size* (its share of the unit's size). Chained
damage-level meshes of one part share that part's segment. (Decompilation: `CDestroyableSegment` and its constructor.)

**Segment types** are chosen from the part's name and structure when the controller is built:

| Type | Chosen when | What a hit does |
| --- | --- | --- |
| Core | the part name starts with `core` or `CORE`; the first one met is the root, called core 1 | core 1 ignores damage; every other core takes it, and at zero health spawns rubble and breaks |
| Swap | the part has damage-level meshes chained to it | takes damage; a change of damage stage spawns rubble, and at zero health it breaks |
| Extra | any other part | takes damage; at zero health it notes the direction the attacker was moving and breaks |
| Extra using its mesh | the part name starts with `x1` or `X1` | as Extra; its own mesh is thrown out as rubble |
| Component | an attached component unit | ignores damage; breaking it starts the component unit's death |

The base damage step does nothing for a segment that is not vulnerable (`CDestroyableSegment::Damage` tests the flag
first), and the Core, Swap and Extra versions all call it. Core 1 and the component segments never lose health to a hit. (Decompilation: `CreateSegment`, `ProcessNode`, and each
class's `Damage`.)

## How a segment gets its health

After the segments are built, `CDestructableSegmentsController::Init` gives each mesh-part segment a share of the
unit's life: its size divided by the total size of all parts below the root, multiplied by the unit's life value from
its unit data (the value that `CUnit::GetMaxLife` returns for a unit with no controller). Both its current and its
maximum health start at that share. Two cases differ: core 1 gets zero, and every other core gets five times its share.
An extra that uses its mesh, in a unit that has any core, gets a current health of 0.001 and keeps the constructor's
default of 1.0 as its maximum. A segment's size is the
largest of its part's three bounding-box axis values. Component segments are not in the array, so they keep the
constructor's default of 1.0 for both health values. (Decompilation: `Init`, `CDestroyableSegment::SetLife`, the Core
and Extra-using-mesh `SetLife` overrides.)

At the end of `Init` the controller caches a *total health*: the *total-health sum* described next, taken over the root.
That cached figure is the reference for both thresholds.

## Two sums over the segment tree

Both sums start at the root, add the segment's own contribution if it has one, and then add the result for every child;
a segment with no contribution still has its children visited, and each child applies the same tests. A segment makes
no contribution when it is not vulnerable or when it is *under a falling core*: it is, or has an undestroyed ancestor
that is, a core in its falling state (see "A core that falls" below). The two sums differ in what a contributing segment
adds, and the active sum has one more test.

| Sum | Used for | A counted segment adds |
| --- | --- | --- |
| Active health (`GetActiveHealth`) | the death threshold, the latch, the unit's life readout | its **maximum** health, and only while its current health is not zero |
| Total health (`GetTotalHealth`) | the cached total at build time, the target health bar, the mission native `GetRealHealth` | its **current** health, with no zero test |

The consequence is the one that matters for play. A damaged segment that still has health keeps contributing its full
share to the active sum. The active sum falls only when a segment's health reaches zero, when a script makes it
invulnerable, or when a core above it starts to fall. The thresholds therefore trip on how many segments have been
destroyed, weighted by their shares, and not on accumulated wear. The total-health sum, by contrast, falls with every
point of damage; the target health bar is that sum divided by the cached total, clamped to the range 0 to 1
(`CUnit::GetLifeUnknown4f9a40` over `CUnit::GetMaxLife`, in `CHud::RenderTargetIndicator`).

Two helper rules complete the picture. When no segment of the unit is vulnerable, the controller's life query returns 1.0
and its maximum query returns 1.0 instead of summing, so such a unit reads as alive at full life.
`CUnit::GetLife` and `CUnit::GetMaxLife` use these two queries for a segmented unit. Stuart's crosshair code counts a
building under the crosshair only while its life is above zero
([`references/Onslaught/BattleEngine.cpp:2328`](https://github.com/dlprentice/Onslaught/blob/c3d8ac464259942b83fa8aa7f867c856e77b734d/BattleEngine.cpp#L2328),
`CBattleEngine::CalcUnitOverCrossHair`).

The cached total is set when the controller is built and refreshed from the *active* sum by three mission natives
(table below); changing a segment's health by script does not refresh it unless the native says so.

## What one hit does

`CUnit::Damage` runs its own unit-level checks first (they belong to the unit-damage description, not to this page). For
a unit that has a controller it then passes the part index, the amount and the source to the controller's `Damage` and
returns: the shield and life handling of an ordinary unit never runs for a segmented unit. `CBuilding`'s override of
`Damage` forwards to `CUnit::Damage` whenever the building has a controller, even while it is dying. The controller's
`Damage` does this, in order:

1. **Part index -1: nothing is applied.** The call skips straight to the latch step. A damage source that supplies no
   part index therefore cannot damage a segmented unit.
2. **The part has no segment:** if the owner has a render mesh, a warning naming the mesh and the part number is logged
   and nothing is applied; the call then also skips to the latch step. With no render mesh, the function returns
   without the latch step.
3. **Otherwise the segment's own `Damage` runs** (the table above).
4. **The death check runs after every hit that reached a segment**, whether or not that segment changed. The owner's
   `StartDieProcess` (the unit's virtual die entry) is called when either:
   - *every core child of the root is destroyed* (`AreChildrenDestroyed`); a root whose children include no core counts
     as already destroyed, and a root with no children at all logs a warning and counts as destroyed too; or
   - *the active health is strictly below 30% of the cached total.* The 0.3 is a double-precision constant, so the
     product is formed in double precision and compared strictly: exactly 30% does not trip it. The Warehouse note
     records the same comparison from the original code.
5. **The latch step.** If the latch is not already set, it is set when the life query (active health, or 1.0 with no
   vulnerable segment) is strictly below half of the maximum query (the cached total, or 1.0). With no vulnerable
   segment the pair is 1.0 against 0.5, so the latch cannot be set in that state.

`StartDieProcess` is not a once-only call: `CUnit::StartDieProcess` returns at once when the unit is already dying, and
the `CBuilding` and `CHiveBoss` versions begin by calling it and return if it did, so later hits that still satisfy
the check do nothing more. (Decompilation: `CUnit::Damage`, `CDestructableSegmentsController::Damage`,
`CDestroyableCoreSegment::AreChildrenDestroyed`, `CUnit::StartDieProcess`, `CBuilding::StartDieProcess`,
`CHiveBoss::StartDieProcess`.)

### The latch

Once set, the latch is never cleared in the reconstructed source. Its only reader there is `CBuilding::RenderImposter`,
which draws nothing for a building whose controller has the latch set; otherwise it draws the distant imposter as usual.
So crossing half of the cached total removes a building's distance imposter, while the 30% threshold starts its death.
No other reader of the field appears in the reconstructed source. (Decompilation: `CBuilding::RenderImposter` and the
controller's `Damage`, `DamageRandomly` and cascade methods, the only writers.)

## `HalfDestroy`: the random burst

The mission native `HalfDestroy` calls `CUnit::DamageRandomly`. For a unit with a controller that calls the
controller's `DamageRandomly`:

1. It collects the controller's segments into a temporary set, skipping empty slots and repeats, so a segment shared by
   chained parts appears once, in the order of first appearance in the array.
2. For each segment in that set whose type is beyond Swap (Extra, Extra using its mesh, Component), it draws once from the
   game's random generator, and on an even result applies 100000 damage with the owning unit as the source. Cores and
   Swap segments are never touched, and a Component ignores the damage, so in practice the Extra segments go, each
   with a one-in-two chance.
3. It runs the latch step from "What one hit does".

It does not run the death check, so `HalfDestroy` alone never starts the unit's death; a later hit that reaches a segment
does, if the active health has meanwhile dropped below 30%. A unit with no controller instead has its life divided by a
random factor between 1.5 and 3.0. (Decompilation: `IScript::HalfDestroy`, `CUnit::DamageRandomly`,
`CDestructableSegmentsController::DamageRandomly`.)

## The death cascade

`CUnit::StartDieProcess`, after it marks the unit dying and adjusts the side counters and the score, calls a controller method
that the decompilation names by its position. This page calls it the *death cascade*. It does this:

1. Return, doing nothing, if every core child of the root is already destroyed.
2. Return, doing nothing, if the active health is strictly below 30% of the cached total (the same double-precision,
   strict comparison as the death check).
3. Otherwise make the root and every segment below it vulnerable (`ActivateAll`), apply 100000 damage to each *immediate
   child of the root* with the owning unit as the source (`DamageChildren`), and set the latch.

So the cascade is a catch-up for a unit that dies while it is still mostly intact. The ordinary route, a hit that
passes the death check in `Damage`, enters `StartDieProcess` with the same condition already true, so one of the two vetoes
fires and the cascade does nothing. Any other route into `StartDieProcess` on a segmented unit that is still above 30%
gets the full effect. The decompilation shows two such routes, the `START_DIE_PROCESS` event that any thing can be sent
and a spawned unit's AI after its spawner has died; whether either reaches a segmented unit in the shipped levels was
not traced. The sequence is: make everything vulnerable, so the damage cannot be refused; then knock out the root's direct
children with the huge amount; then let each child's break pass the order down. Deeper segments are not damaged by
the cascade itself: a break orders the segment's own children to break, at once under a core, after a random delay of
up to a second under a Swap segment, and after a random delay of up to a fifth of a second under the other types, the
delays coming from the C library's `rand` and not from the game's generator
(`CDestroyableSegment::ScheduleChildBreaks`, the existing contract's subject).

The root's children take the 100000 damage through their own `Damage` overrides: a Component child ignores it, and
the others reach zero health and break. (Core 1 is the root itself, so it is never one of these children.)
(Decompilation: `CUnit::StartDieProcess`, the controller's cascade method, `CDestroyableSegment::ActivateAll`,
`CDestroyableSegment::DamageChildren`, `CDestroyableSegment::ScheduleChildBreaks`.)

### A core that falls

A second thing is also called a core cascade in the decompilation, and it is separate from the above. When a core
segment is told to break while its health is not zero and it is not already under a falling core, it does not break at
once. It enters a *falling* state, adds the owning unit's gravity to its fall speed every frame (starting from its parent
core's current speed), and accumulates the distance. When the distance reaches the controller's core fall distance (2.0 for
a building, 10.0 for the Hive Boss) it spawns rubble and breaks. If a core is told to break while it is already under a
falling core, that call does nothing. While it falls it is excluded from both sums, which is
the "under a falling core" rule above, and the motion controller drops and tilts its part by the distance fallen
(`CDestroyableCoreSegment::Break`, `HandleEvent`, `CanBreak`, `CDestructableSegmentsController::GetCoreFall`,
`CDestructableSegmentsMotionController::GetPartTransform`). The Warehouse note records a positive-health core entering
this state and being left out of the sums. The fall's timing and the rubble it produces have not been observed in a running game.

## Part availability

The motion controller of a segmented unit has a virtual that sets bit 0 of a per-part flags word. The base class's
comment in the decompilation says bit 0 hides the part from collision; the mesh collision volume and the static-shadow
builder both read it. The segmented unit's version sets the bit for a part that is chained to another, and otherwise
sets it when the controller's `CanUse` says the part is not usable. It changes no other bit.

`CanUse(part)` returns:

- **If the part has a segment:** by default, whether the segment is not destroyed. One exception comes first: when the
  controller's mode argument is FALSE and the segment is core 1, the part is unusable once either death condition holds
  (all core children of the root destroyed, or active health strictly below 30% of the cached total), although core 1 is
  never destroyed by damage. The building controller is built with the mode TRUE, so this exception does not apply to
  buildings; the Hive Boss controller is built with FALSE, so it does apply to the boss.
- **If the part has no segment:** TRUE, unless the part's type value is 5 and its parent has a segment, in which case
  whether that parent segment is not destroyed.

The same motion controller gives the damage stage the renderer uses for a Swap part and reports when the controller's
changed flag was set. (Decompilation: `CDestructableSegmentsController::CanUse`, `CDestructableSegmentsMotionController::Unknown6`
and `Unknown7`, `MeshCollisionVolume.cpp`, `StaticShadows.cpp`. The meaning of part type 5 is not given here.)

## Aim position

The unit method `CUnit::GetTargetablePos` returns the point at which things aim. For a unit with a controller it calls
the controller's `GetCentre`, otherwise the unit's centre. `GetCentre` visits the mesh parts in ascending order and keeps
the part whose segment is a core with health above zero and with the highest core number (a tie keeps the earlier part),
then evaluates that part's world pose for the point. With no such part, it returns the unit's centre position. Core 1
has zero health, so it is never chosen: once every core above the first is destroyed, the aim point falls back to the
unit's centre. The Hive Boss overrides `GetTargetablePos` with the centre, so it never uses this selection. The
callers include the AI classes (`DiveBomberAI`, `GroundAttackAI`, `MechAI` and others, on their targets) and, in Stuart's
source, `CBattleEngine::UpdateAutoAim` at
[`references/Onslaught/BattleEngine.cpp:2382`](https://github.com/dlprentice/Onslaught/blob/c3d8ac464259942b83fa8aa7f867c856e77b734d/BattleEngine.cpp#L2382),
although Stuart's auto-aim clears its target when that target is a building
([`BattleEngine.cpp:2585-2590`](https://github.com/dlprentice/Onslaught/blob/c3d8ac464259942b83fa8aa7f867c856e77b734d/BattleEngine.cpp#L2585-L2590)).
How [Battle Engine aiming](battleengine/battle-engine-aiming.md) uses the point is in its own note.
(Decompilation: `CDestructableSegmentsController::GetCentre`, `CUnit::GetTargetablePos`, `CHiveBoss::GetTargetablePos`.)

## Mission natives that change these numbers

| Native | Effect on the controller (`IScript::…` in the decompilation) |
| --- | --- |
| `SetSegmentHealth` | sets the named segment's *current* health only; no refresh of the cached total. Setting zero removes the segment from the active sum without marking it destroyed |
| `SetAllSegmentsHealth` | the same for every segment |
| `ResetSegmentHealth` | sets the named segment's current and maximum health, then refreshes the cached total from the active sum |
| `SetSegmentVulnerable` | sets the named segment's flag, then refreshes the cached total from the active sum |
| `SetAllSegmentsVulnerable` | sets the flag on every segment, then refreshes the cached total |
| `HalfDestroy` | the random burst above |
| `GetRealHealth` | returns the total-health sum (`CUnit::GetLifeUnknown4f9a40`; the unit's own life for a unit with no controller) |

Each native does nothing unless the script's owner is a unit with a controller. They name the segment by its mesh-part
name, and a name with no segment logs a fatal-error message and changes nothing. The registry rows are in
[`levels/scripting/mission-script-command-registry.tsv`](../levels/scripting/mission-script-command-registry.tsv).

## Corrections to earlier notes

- The existing [static contract](destroyable-segments-static-contract.md) names several of these functions with older
  working names. The correspondence, so that readers can join the two: the controller dispatch row is `Damage`; the
  core-child state gate is `AreChildrenDestroyed`; the base, core and swap slot-3 rows are the three `Damage` methods; the
  bulk refresh is `SetAllSegmentsVulnerable`, and the flag it writes is the *vulnerable* flag (it is called an active
  flag in the earlier notes).
- The earlier notes on the active sum describe its contribution as the segment's *remaining* life. The retail body reads
  the *maximum* health field for that contribution, and the current-health field only for the not-zero test (repeated
  directly on the pristine specimen for this page, which also found the total-health sum reading the current field).
  The Warehouse note's description of the same sum ("initial values for enabled, non-collapsing segments whose current
  health is nonzero") agrees with the maximum-health reading.
- An earlier note names the part-availability predicate with a `CUnitAI__` prefix; its receiver is the segment
  controller, which the motion controller's constructor stores (so the method is the controller's `CanUse`).
- An earlier note names the aim-position method `CDiveBomber__SelectTarget`, and one version described a
  distance-and-allegiance target search. The method selects no target: it returns a position for the unit it belongs to,
  and the dive-bomber AI is one of several callers.
- An earlier note read the missing-part branch of the controller's `Damage` as falling through to the latch step even when
  the owner has no render mesh. The decompilation returns there, and as it matches the retail bytes this page follows it.

## Evidence boundary

All of the above is static: what the code does, read from matched reconstructions and from the retail bodies the
maintainer read earlier. The Level 100 Warehouse cases exercise parts of the same code with supplied inputs. No
controlled runtime capture of a segmented unit taking real hits, crossing 30% or 50%, or dying by the cascade is part
of this page's evidence, and a threshold result stated here is a statement about what the code computes, not a measured
player-visible event. The earlier research records also hold coverage-only traces showing that the random-burst
routine ran during level openings (archived research record, not published); they do not say which segment, draw or
amount occurred, and are not used.

## Open questions

- **Live behaviour of the thresholds.** Does a building in a real level start dying when a hit takes its active health
  below 30% of the cached total, and does a core 1 part of the Hive Boss disappear at the same moment? Cheapest
  falsifier: a controlled run of the original game against one segmented building with a known damage source and
  amount, recording the die call and the part's availability after each hit.
- **The mode argument.** The third constructor argument is TRUE for buildings and FALSE for the Hive Boss, and the only
  effect found is the `CanUse` exception above. Whether anything else reads it is not established beyond the
  reconstructed source. Cheapest falsifier: find every access to the field in the retail executable.
- **Part type 5.** The `CanUse` fallback follows a parent segment for parts of type value 5; what such a part is (an
  attachment, a marker, a collision-only part) is not stated by this repository's mesh notes.
- **The latch readers.** Only `CBuilding::RenderImposter` reads the latch in the reconstructed source; a reader that reaches
  the field through another view of the object would not appear there.
- **Whether the active sum's maximum-health reading is what players see.** The unit's life query feeds the crosshair
  rule above and other callers of `CUnit::GetLife`; no capture shows the stepwise behaviour this implies for a
  building taking sub-lethal hits.
