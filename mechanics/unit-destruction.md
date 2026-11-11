# Unit destruction: the death sequence

Status: active — how a unit starts dying, what each kind of unit does while it dies and when the object is removed; static evidence only
Last updated: 2026-11-11 (first version; written from the matched decompilation and Stuart's published source)
Evidence: MEASURED (static) — each function named below is a function of the retail executable that
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) reproduces byte for byte (its `docs/check/matched.tsv`
lists it as matched), read here at commit
[`9759593`](https://github.com/dlprentice/onslaught-decomp/tree/9759593ee6f6103f936080ac0435275e6ce9e06a); SOURCE —
Stuart Gillam's `thing.cpp`, `thing.h` and `eventmanager.h` for the base-class behaviour; INFERRED — one name join,
marked where it occurs; UNKNOWN — everything about play: no run observed any of it, and the open questions at the end
name what would settle them.
Specimen: pristine Steam `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` (the
executable the decompilation is matched against).
Summary: a unit's death is two separate steps, a start step that marks it dying and a removal step that deletes it, and
the first does not schedule the second; this page gives the shared start step, the shared removal step, what each kind
of unit does in between, the delays before removal, the order of the script notifications, and how aircraft crash.

## Result

- Death has two phases. The start phase (`StartDieProcess`) sets the dying flag, adjusts the game's counters and tells
  the unit's mission script. The removal phase is a `SHUTDOWN` event that ends in the object being deleted. For a unit,
  the start phase does **not** schedule the removal phase; each kind of unit decides how and when that happens.
- Four removal routes exist in the units covered here: the shared `CUnit::Remove` (pods, cannons, ground vehicles and
  some components), a delayed event that explodes the unit and then shuts it down (Mechs without the shatter property,
  and some components), an immediate explosion and shutdown (Mechs with the shatter property, crashing aircraft), and
  a per-class countdown (tentacles). The start functions of buildings, the Hive Boss and air units queue no removal.
- The delays before removal are fixed in the code: 0.05 s for pods, cannons and most components, 0.5 s for ground
  vehicles, 3.5 s for a Mech without the shatter property, 7 s for a component that has the Big property set but not
  Detach. A tentacle blows off one bone every tenth of a second, highest-numbered first, and is shut down with the last.
- The call that older notes in the Toolkit's frozen `reverse-engineering/` tree describe as a "profile drop" pickup is
  `CUnit::SpawnExplosion` in the decompilation, which creates the unit's own configured explosion (the same definition
  field the building and tentacle paths use); the function itself creates no pickup.

How to read the names: `CUnit::StartDieProcess` is the function the decompilation's table calls
`CUnit__StartDieProcess`. Where the decompilation has not named a function or field from the source, this page
describes it instead of repeating a placeholder name. Dying and shutdown flags are `TF_DYING` and
`TF_DECLARED_SHUTDOWN` (`references/Onslaught/thing.h:43-45`; see
[How to read a finding](../README.md#how-to-read-a-finding) for the pinned source).

## The two phases in Stuart's base classes

Stuart's published `CThing` has the simple version, and the units depart from it.

- `CThing::StartDieProcess` sets `TF_DYING` and calls `AddShutdownEvent` at once; it returns false if the thing is
  already dying (`references/Onslaught/thing.cpp:193-203`).
- `CThing::AddShutdownEvent` does nothing if `TF_DECLARED_SHUTDOWN` is set; otherwise it sets that flag and queues
  event `SHUTDOWN` (2000, `thing.h:35`) for the next frame (`NEXT_FRAME` is -1.0, `eventmanager.h:14`;
  `thing.cpp:183-190`).
- `CComplexThing` wraps both: `StartDieProcess` calls the mission script's `StartedDying` after the base succeeds
  (`thing.cpp:728-738`), and `AddShutdownEvent` calls the script's `Died`, deletes the script object and clears the
  pointer before the base does its work (`thing.cpp:711-724`).
- The `SHUTDOWN` event reaches `CThing::HandleEvent`, which calls the virtual `Shutdown` (`thing.cpp:159-177`);
  `CComplexThing::HandleEvent` first calls the script's `Shutdown` if a script is still attached and the game is not past
  the playing state (`thing.cpp:674-687`). `CThing::Shutdown` removes the thing from the world and deletes it
  (`thing.cpp:102-111`).

The decompiled `CUnit::StartDieProcess` calls neither base version: it sets `TF_DYING` itself and, as the sections below
show, schedules nothing. That is why every unit class needs its own removal route.

## What starts a death

Evidence for this section: the decompiled bodies of the functions named, each matched to retail.

- **Life below zero.** `CUnit::Damage` subtracts damage from shields and then life. If life is below zero and the unit
  is not already dying, it credits the Battle Engine player's units-destroyed statistic when the damaging round came from
  a Battle Engine, and then, unless the unit's definition sets the Retreat property, calls `StartDieProcess` followed by
  the virtual slot-71 hook (a no-op in the base class; it is the shatter debris of Mechs, below).
- **Segmented units.** `CDestructableSegmentsController::Damage` calls the owner's `StartDieProcess` after damaging a
  segment when all of the core's children are destroyed or the core's remaining active health has fallen below 30% of the
  controller's total. It does not test the dying flag first, so it can call again on a unit already dying; the shared
  start step then returns false. A broken component segment (`CDestroyableSegmentComponent::Break`) calls
  `StartDieProcess` on its component unit. See [destroyable segments](destroyable-segments-static-contract.md).
- **AI.** `CUnitAI::Unknown10`, an event handler the decompilation has not named, calls `StartDieProcess` on its unit
  when the unit's spawner has gone or is dying and the unit is vulnerable.
- **Aircraft contact and fatal damage** start removal directly; see [Aircraft](#aircraft).

`CBattleEngine`, `CRound`, `CMine`, `CInfantryUnit`, `CFeature` and `CWarspiteDome` have their own
`StartDieProcess`; they are not described here (the Battle Engine's note was removed, see
[DECOMP-BOUND.md](../DECOMP-BOUND.md), and rounds are in [the round hit path](cround-hit-damage-path.md)).

## The shared start step: `CUnit::StartDieProcess`

Evidence: the decompiled body of `CUnit::StartDieProcess`, matched to retail; ordering is the order of statements in
that body.

It returns false, doing nothing, if `TF_DYING` is already set. Otherwise it does these things in this order and
returns true:

1. Stops every sound the unit is playing.
2. Sets `TF_DYING`.
3. If the unit has a definition record, adjusts the world's counters for the unit's allegiance. Allegiance 0 (Forseti) is
   one case and 1 (Muspell) the other; for either it decrements the world counter for the unit's behaviour type, sets
   `TF_REMOVED_UNIT_TYPE`, and calls `GAME.IncScore` with the type's priority weight, negated for Forseti and positive
   for Muspell. A neutral unit (allegiance 2) skips all of this. The decompilation shows what is adjusted; what the
   running score is used for is outside this page.
4. If the unit has a destroyable-segments controller, runs the controller's catch-up. That does nothing when the core's
   children are all destroyed or the core's active health is already below 30% of the total (the same test as the
   death trigger above). Otherwise it activates every segment, damages the core's children by 100000, and sets a flag on
   the controller. So a segmented unit killed by plain life loss still loses its remaining segments, one that died by the
   segment rule does not repeat that.
5. If the unit has a mission script, calls its `StartedDying` notification, which runs the script's `started_dying()`
   callback (the join from the `SCRIPT_EVENT_STARTED_DYING` event to that MSL callback is by name only; INFERRED).
   While the level is lost the call cleans the script virtual machine instead.
6. Calls `ClearSpawners`: forgets the current spawner and then removes each spawner from the unit's spawner list and
   shuts it down.

It returns true only for the first call. Every override below begins by calling it (directly or through its base class)
and returns false at once if it returned false, except the shatter case of `CMech`, which continues regardless, and
`CFenrir`, which calls it later (see below).

## The shared removal step: `CUnit::Remove`

Evidence: the decompiled body of `CUnit::Remove` and of `CUnit::ReleaseChildren`, `CUnit::SpawnExplosion` and
`IScript::Died`, matched to retail.

`CUnit::Remove` is called by pods, cannons, ground vehicles and one case of the components. In order it:

1. **Releases child units** (`ReleaseChildren`): for each unit in the child list, if this unit is dying it calls the
   child's `StartDieProcess`, otherwise the child's `Shutdown`; then it drops the list entry. Called from `Remove`, the
   unit is always dying, so children die with the parent through their own start step.
2. **Clears spawners** again (`ClearSpawners`; the start step already did, so this repeats harmlessly for anything added
   since).
3. **Spawns the unit's explosion** (`SpawnExplosion`): if the unit has a definition record, it creates the explosion
   whose index the definition names, fills an initialiser (the explosion's behaviour data, the unit's allegiance, attached
   to the unit, using the attached radius, volumetric allowed, and a collision type of ground if the unit is on the
   ground, water if in water, otherwise none) and, if creation succeeded, initialises it at the unit's position. What
   the explosion then does is the business of `CExplosion` (see [the round hit path](cround-hit-damage-path.md)).
4. **Ends the mission script**: if a script is attached, calls `Died`, deletes the script object and clears the pointer.
5. **Schedules removal**: queues event `SHUTDOWN` for this unit at the current event-manager time plus the unit's
   virtual slot-112 delay. The base `CUnit` returns 0.05 s; `CGroundVehicle` overrides it to 0.5 s.

`Remove` queues the event directly. It does not call `AddShutdownEvent`, so it does not set `TF_DECLARED_SHUTDOWN`.

## The delayed-explosion event

Evidence: the decompiled `CUnit::HandleEvent`, the unit-event constants at the top of `Unit.cpp`, and Stuart's
`thing.cpp` for the calls it makes.

Two overrides (`CMech` and `CComponent`) queue unit event 4004 instead of calling `Remove`. The decompilation gives the
number no name beyond a comment ("explodes and shuts the unit down"). `CUnit::HandleEvent` handles it by calling
`SpawnExplosion` and then `AddShutdownEvent`. `AddShutdownEvent` is Stuart's `CComplexThing` version
described above: it calls the script's `Died` and deletes the script, sets `TF_DECLARED_SHUTDOWN` and queues `SHUTDOWN` for the
next frame. The `SHUTDOWN` event then runs the shutdown below. Because the script is already gone, `CComplexThing`'s
script-shutdown call is skipped.

## Removal: `SHUTDOWN` and `CUnit::Shutdown`

Evidence: the decompiled `CUnit::Shutdown`, plus `thing.cpp:102-111, 633-647` for the base versions.

`CUnit::Shutdown` stops the unit's sounds, deletes its weapons, shuts down each spawner, applies the child rule from
`ReleaseChildren` again (children of a dying parent get `StartDieProcess`, others `Shutdown`), stops and discards the
unit's thruster and effect links, removes the unit from the world's unit lists, and calls the base `Shutdown`.
`CComplexThing::Shutdown` removes the name-registry entry and clears the unit's objective status, and `CThing::Shutdown`
removes the object from the world and deletes it. None of these functions (nor `Unit.cpp`'s) mentions
`TF_DECLARED_SHUTDOWN`, so a unit queued by `Remove`, which does not set the flag, is deleted the same way.

## What each kind of unit does

Evidence: the decompiled `StartDieProcess` of each class (and the functions it calls), matched to retail. Each override
below first calls the shared start step and returns false if that returned false, except where noted.

| Class | After the shared start step | How the object is removed |
| --- | --- | --- |
| `CGroundUnit` (base of vehicles, Mechs, cannons, infantry, mines) | Resets its bobbing phase (`mBobPhase`) to zero, then returns true | Left to the subclass |
| `CGroundVehicle` (for example Target Tank and Target Truck, see [the Level 100 construction order](../levels/level100-construction-order.md)) | Calls `Remove` | `SHUTDOWN` 0.5 s later |
| `CCannon` (fixed emplacements) | Calls `Remove` | `SHUTDOWN` 0.05 s later |
| `CPod` (pods a script launches) | Calls `Remove` | `SHUTDOWN` 0.05 s later |
| `CMech` (and `CWarspite`, `CGillM`, `CThunderHead`) | Depends on the unit definition's Shatter property: see below | Immediately, or event 4004 after 3.5 s |
| `CComponent` (and `CGillMHead`) | Depends on the Big and Detach properties: see below | `SHUTDOWN` 0.05 s later, a move away from the parent with no removal queued here, or event 4004 after 7 s |
| `CTentacle` (a component) | Starts a bone countdown: see below | `AddShutdownEvent` when the last bone is gone |
| `CBuilding` | Releases children and, if it has no segments controller, explodes and scatters debris: see below | Not by this function |
| `CSimpleBuilding` | Removes the building's static shadow | Not by this function; see below |
| `CHiveBoss` | If it has a script, queues event 5000 for the next frame | Not by this function |
| Air units (`CAirUnit` and subclasses) | Releases children, stops and deletes its particle links | Not by this function; see [Aircraft](#aircraft) |

**Mechs.** `CMech::StartDieProcess` reads the Shatter property of the unit definition (the physics-script statement
`CUnitShatter`; its stored value is a boolean, because `CUnitShatter::Apply` writes true for any non-zero payload and
false otherwise). With Shatter set it calls the ground-unit start step, then `SpawnExplosion` and `AddShutdownEvent`
unconditionally, and returns the start step's result: so the explosion, the script's `Died` and the next-frame
`SHUTDOWN` all happen in the dying call, and they happen again on a second call (the explosion repeats; `AddShutdownEvent`
is guarded by the declared flag). Without Shatter it returns false if the start step returned false, otherwise releases
children and queues event 4004 for 3.5 s ahead (decompiled constants). `CMech`'s slot-71 hook, which `CUnit::Damage`
calls right after `StartDieProcess`, does nothing without Shatter; with it, every mesh part whose type is 1 becomes a
"Generic Mesh" particle thrown out from the part's world position with a random velocity (the second place the
property is read).

**Components.** `CComponent::StartDieProcess` tests two definition properties. The first is the Big property (the
statement `CComponentBig` sets it; `CUnitBig` sets the same field for units); the second is the Detach property
(`CComponentDetach`). If both are clear it runs the shared start step and, when that succeeded, calls `Remove`
(`SHUTDOWN` 0.05 s later). Otherwise it runs the start step, releases children and then: with Detach set, gives the component a
velocity of its parent's velocity plus 0.4 times the horizontal unit vector from the parent to the component plus the
parent's orientation applied to the vector (0, 0.4, 0), which the decompilation's comment describes as the component
falling away from its parent; with Detach
clear (so Big set) it queues event 4004 for 7 s ahead. The detach arm queues no removal at all in this function; the
decompilation's own comment says such components clip to the ground, and what removes them is not established here.

**Tentacles.** `CTentacle::StartDieProcess` calls the start step of `CUnit` directly (the decompilation notes that
retail skips `CComponent`'s version), stores the number of bones its motion controller has in `mBonesLeft`, spawns the
unit's explosion at the head position and releases children. While dying, `CTentacle::Move` blows off the bone named
after the current bone number each time the event-manager time passes the next-bone time, with a small explosion at that
bone's part, sets the next time 0.1 s ahead and decrements the count; when the count reaches zero it calls
`SpawnExplosion` and `AddShutdownEvent`. So the shutdown is declared at the last bone's blow-off: a tentacle with N bones takes at least (N-1) times 0.1 s from its
first blow-off (decompiled constants; the time of the first blow-off depends on the initial next-bone time, which this
page did not trace).

**Buildings.** `CBuilding::StartDieProcess` releases children. If the building has a destroyable-segments controller it does nothing more
there, and its normal rendering continues (`CBuilding::Render` only returns early for a dying building that has no
controller). Without a controller it creates the definition's explosion at the building's position, sets its life to
-1, creates the explosion's named particle effect when the definition's explosion index is not -1, and then creates 40
"Generic Mesh" particle effects around the building (each from three random bytes minus 128 scaled by 0.0003125,
displaced 20 times that and from one unit below the building's position) and hands each live one to the building-debris
initialiser. Either way, if the building has a mission script it queues event 5000 for the next frame, and
`CBuilding::HandleEvent` answers 5000 by calling the script's `Died`, deleting the script and clearing the pointer
(`CHiveBoss` queues the same event and has the same handler body, which the linker merged with `CBuilding`'s). No function of
`Building.cpp` declares a shutdown; see the open questions.

**Simple buildings.** `CSimpleBuilding::StartDieProcess` calls the static-shadow manager's `UpdateVisibility` for the
building with its second parameter true. That parameter is named `remove` in the decompilation, and with it set the
function marks every shadowed part of the building not visible and, when nothing changed, detaches the shadow from the
building, so a dying simple building loses its static shadow at once. Removal is by `CSimpleBuilding::Move`, which runs only
while dying: the building sinks under gravity, bursts one small explosion on its surface per `Move` call, and when
it has sunk to the ground (the test compares the map's ground height plus 0.5 with the building's Z) it calls
`DeclareOnGround`, which for a dying building calls `SpawnExplosion` and `AddShutdownEvent` (the decompilation's file
comment says the same in words).

**The Fenrir** replaces the air-unit start step: its `StartDieProcess` sets `TF_DYING` and queues its own die event after
a delay set by the script variable `fenrir_diedelay`; the handler then plays the "die" animation, spawns 50 surface
explosions, posts the script event "fenrir blowing up", clears `TF_DYING` and calls `CAirUnit::StartDieProcess`, which now
runs the shared step and the air-unit cleanup. This is why its dying flag is cleared before the call.

## When the object goes away

Evidence: the delays are the decompiled constants above; update counts follow the ring arithmetic of
[the event-manager scheduler](../engine/world/event-manager-scheduler-semantics.md) (a fixed 20 updates per second, a
delay entering the ring at `floor((delay - 0.001) * 20)` buckets ahead and delivered one update later than that bucket
count). Nothing here was observed running.

| Route | Delay | Nominal updates until `SHUTDOWN` or the explosion event |
| --- | --- | --- |
| `Remove` on pods, cannons, components (neither property) | 0.05 s | 1 (the next update) |
| `Remove` on ground vehicles | 0.5 s | 10 |
| Mech without Shatter (event 4004, then `SHUTDOWN` the next frame) | 3.5 s | 70, then one more |
| Component with Big set, Detach clear (event 4004, then `SHUTDOWN` the next frame) | 7 s | 140, then one more |
| Mech with Shatter, tentacle at its last bone, crashing aircraft | none | the next update |

Because the scheduler compares floating-point times by bucket rather than by a per-event comparison, a due time can land
one update either side of these nominal counts; the scheduler page owns that boundary. A unit that is dying but not yet
shut down is still in the world and still receives events already queued for it. The Target Tank's behaviour in the
interval is in [the round hit path](cround-hit-damage-path.md).

## Order of the mission-script notifications

Evidence: the decompiled call order in the functions above and `thing.cpp:711-738`.

- `StartedDying` is always first, from the shared start step, in the same call as the transition.
- `Died` follows in the same update for `Remove` routes (pods, cannons, vehicles, components without the properties) and
  for the Shatter Mech (through `AddShutdownEvent`); at the 4004 event for delayed Mechs and components; with the last
  bone for a tentacle; and one update later (event 5000) for a building or Hive Boss that has a script.
- `Died` is always followed by deleting the script object, so the `Shutdown` script notification of the later `SHUTDOWN`
  event cannot run for these units, because `CComplexThing::HandleEvent` finds no script.
- When the level has been lost, the `StartedDying`, `Died` and `Shutdown` calls clean the script machine instead of
  running the callbacks (`IScript::StartedDying`, `Died` and `Shutdown`).

[The MSL scripting page](../levels/scripting/msl-scripting.md) lists the `started_dying()` and `died()` callbacks and says
the call times are not established; these are the static call points in the engine. The join from the engine's
`SCRIPT_EVENT_DIED` to the `died()` callback is by name only (INFERRED).

## Aircraft

Evidence: the decompiled `CAirUnit::StartDieProcess`, `CAirUnit::Move`, `CPlane::Hit`, `CSmallAirUnit::Hit` and
`CBigAirUnit::Hit`, matched to retail.

The air-unit start step (`CAirUnit::StartDieProcess`, inherited by the air classes that do not override it; the only
override in the decompilation is `CFenrir`'s, described above) runs the shared step, releases children, and then
removes, stops and deletes every particle link in its two link lists (trails and engines). It does not schedule removal,
call `Died` or set the declared flag: a dying aircraft stays in the world, tumbling (`CAirUnit::Move` gives a dying
aircraft a third of its definition's turn rate on all three Euler axes), until one of the following calls `SpawnExplosion`
and `AddShutdownEvent`:

- **Fatal damage in `CAirUnit::Move`.** After the base movement it tests whether life is below zero and also below
  minus the definition's life value (strictly: life exactly equal to the negative life value survives) and the Retreat
  property is clear. While life is negative, a smoke effect is moved to an emitter point each call until shutdown is
  declared.
- **Plane contact in `CPlane::Hit`.** If the Retreat property is clear and the other thing is not a friendly aircraft
  (a Battle Engine is never exempt), then when the other thing is a unit, a tree or a walkable thing the plane calls
  `ConfirmedKill` on the other unit if it is one (what that does is not described here), then `SpawnExplosion` and
  `AddShutdownEvent`. The test does not look at the plane's own life or dying flag. It then runs the small-air-unit hit
  below.
- **Dying small aircraft in `CSmallAirUnit::Hit`.** With Retreat clear and `TF_DYING` set, touching a unit, a tree or a
  walkable thing explodes and shuts the aircraft down. `CBigAirUnit::Hit` does the same for a walkable thing only.

Which of these reaches a given aircraft in play, how a dying aircraft moves, and the effect of `ConfirmedKill` are not
described by these functions. The Target Drone of Level 100 is a `CPlane`; its timing is in
[the Level 100 final wave](../levels/level100-final-drone-wave.md).

## Scripted half-destruction

Evidence: the decompiled `IScript::HalfDestroy`, `CUnit::DamageRandomly` and
`CDestructableSegmentsController::DamageRandomly`, matched to retail.

The mission-script command `HalfDestroy` (in [the command registry](../levels/scripting/mission-script-command-registry.md))
does nothing unless the script's thing is a unit. For a unit it calls `CUnit::DamageRandomly`, which is not a death call:
with a segments controller it asks the controller to damage random segments (each distinct segment of a type above the
swap type is damaged by 100000 with probability one half, then the controller's below-half flag is set if its life is
under half its reference value); without one it divides the unit's life by a random number between 1.5 and 3.0 (`1.5`
plus `1.5` times a random fraction), writing the life directly: no shields are used and no death is started. It reaches
death only if a later damage call finds the life below zero.

## Open questions

- **No run has observed any of this.** The cheapest check is a log of `StartDieProcess`, `Remove`, `AddShutdownEvent` and
  `SHUTDOWN` delivery times for a Target Tank, a pod, a Mech with and without Shatter, a component and a building in a
  controlled level, on the retail executable or on a build of [Onslaught CE](https://github.com/dlprentice/onslaught-ce)
  with logging; it would settle the delays and the order in the tables above.
- **What removes a destroyed building.** No function of `Building.cpp` calls `AddShutdownEvent`, and `CBuilding::Render`
  stops drawing a dying unsegmented building. This page searched only the building source for the shutdown call. A
  search of the base classes and of level teardown, plus the first two bullets' log, would settle whether a destroyed
  building is ever deleted before the level ends.
- **What the Retreat, Big and Detach properties mean in play** and which authored units set them (the decompilation
  names the fields after their offsets and gives only the property classes `CUnitRetreat`, `CUnitBig`,
  `CComponentBig` and `CComponentDetach`). Reading the unit definitions of the retail game with the decompilation's
  property list would settle which units set which.
- **Which units set Shatter**, and whether a second `StartDieProcess` ever reaches a Shatter Mech (the segments
  controller calls without checking the dying flag, but a Mech with a segments controller was not shown): a second call
  would spawn a second explosion.
- **What removes a detached component** that has queued nothing.
- **The score adjustment's use.** Step 3 of the start step changes `GAME.IncScore` by the unit type's priority weight;
  where the total is read was not traced.
- **Dying aircraft motion** and the exact first tick of a tentacle's bone countdown were not traced.
