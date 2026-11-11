# Unit and Battle Engine damage and contact

Status: active — subsystem description of how damage, repair, shields and invulnerability are applied and how unit contact is admitted; no full-game observation
Last updated: 2026-11-11 (new document, written from the frozen notes formerly in the Toolkit's `reverse-engineering/` folder and checked against the decompilation's source)
Summary: the order of operations when something damages or repairs the player's Battle Engine and any other unit (shields, life, augmentation, death, shake, invulnerability, radio warnings), the rules for admitting a unit's contact with the thing it stands on, and the events a unit handles; with the cases that were run on the original function bodies and what remains open.
Evidence: SOURCE — Stuart's pinned `BattleEngine.cpp` (the Battle Engine's `Damage`), which has no counterpart for `Unit.cpp`; MEASURED — the decompilation's source for these four functions is listed as byte-matched against the retail executable, and the complete original bodies of `CBattleEngine::Damage` and `CUnit::Damage` were run in an isolated harness with authored inputs (41 and 61 cases); INFERRED — the consequences drawn from that order, each marked where it is drawn; UNKNOWN — everything the open questions list, including every question about live play.
Specimen: pristine Steam `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` (see the [retail specimen baseline](../platforms/pc/retail-specimen-baseline.md)).

Two virtual methods decide what a hit or a repair does to a unit: `CBattleEngine::Damage` for the player's Battle Engine and
`CUnit::Damage` for every other unit. Both are slot 40 of their class. Whatever hurts or repairs something calls that slot on the target with an
amount (positive hurts, negative repairs), the thing that caused it, a flag saying whether shields may take the hit
(default true) and the index of the mesh part that was hit (default -1, meaning none). The weapon side of the call, from a
round or explosion to the target, is in [the round and explosion hit path](cround-hit-damage-path.md); segmented units
hand the hit on as described in [destroyable segments](destroyable-segments-static-contract.md); what the player's flag
for invulnerability is and how a career sets it is in [god mode](cheats/god-mode.md).

## What the evidence is

- **The source.** Stuart's published source has the Battle Engine's `Damage`
  ([`references/Onslaught/BattleEngine.cpp:2127-2240`](https://github.com/dlprentice/Onslaught/blob/c3d8ac464259942b83fa8aa7f867c856e77b734d/BattleEngine.cpp#L2127-L2240); the pinned tree is described in the [README](../README.md#how-to-read-a-finding)) and
  the declaration of the virtual slot (`references/Onslaught/thing.h:176`). It has no `Unit.cpp`, so nothing below about
  `CUnit` rests on Stuart's text.
- **The decompilation.** [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) is the naming authority.
  Its `src/BattleEngine.cpp` (`CBattleEngine::Damage`), `src/Unit.cpp` (`CUnit::Damage`, `CUnit::Hit`,
  `CUnit::HandleEvent`) and `src/squad.cpp` are the text this page was checked against (at its commit `9759593`). Each of
  those four functions is a row of its [`docs/check/matched.tsv`](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/docs/check/matched.tsv),
  the table of functions whose compiled output matches the retail executable. A match fixes which operations run and in which
  order; it does not give values, and it does not say what the names of unnamed members mean. The decompilation's text for
  `CBattleEngine::Damage` is identical to Stuart's apart from the address comment (compared line by line when this page was
  written). Where the decompilation still calls a member `mUnknown…`, this page describes its role and does not use the placeholder.
- **Isolated execution of the original bodies.** For `CBattleEngine::Damage`, the original function and its five callees
  (the game's random generator, the C runtime's `rand`, the Battle Engine's shake routine, the cockpit's shake routine
  and the controller-rumble return) were assembled unchanged into a 32-bit Linux program and run natively under a
  syscall filter (read, write and exit only), on authored objects, a null attacker and a recording stand-in for the death
  routine: 41 cases, all as expected
  (`<maintainer evidence>/test-runs/re-audit-20260926/battleengine-damage/…/damage.json`, SHA-256
  `f6a2aab65ef85d1558332a3a3605845cd786a7c1c8949149dac52e9b2a6c130d`). The game's draw count there is inferred from the final
  seed and the static path, not counted directly. For `CUnit::Damage`, the original function and the one squad helper it
  calls were run in an emulator (Unicorn), with every other callee (virtual hooks, random numbers, mesh lookup,
  name comparison, effects, allocation, text) replaced by recording stubs: 50 cases and 11 further controls, all as expected
  (`<maintainer evidence>/unit-damage-branch-probe-root-20260930.json`, SHA-256
  `834a7233576e9e6f514d5eca52551bcd31e48300af12d77c57a88af34322f219`, and
  `<maintainer evidence>/unit-damage-extra-controls-root-20260930.json`, SHA-256
  `62b999dbae955fe518a094510c57d93f5bf88cdf303cf671229a4dceae4c1330`). The objects, names and inputs are authored,
  not taken from play; the floating-point state is a clean initial state, not an observed one. These runs bound the
  order and the strict comparisons below; they are not a game session.
- **One retail runtime capture.** A retained Level 521 capture of a running copy of the game recorded one invocation
  of the Battle Engine's `Damage` and its stores, in the order shields, augmentation, life, last-damage time, energy
  (an archived research record, not published). That is the order in which the source's stages below write those fields.
  The capture has gaps, so it does not establish the complete set of writes.
- **The PC demo.** The demo executable's twins of `CBattleEngine::Damage` and of the shared unit damage body (listed there
  under the name `CUnit::ApplyDamage`) have zero normalized instruction differences
  ([demo against retail](../platforms/demo/demo-vs-retail.md)); that shows those two bodies are not an artefact of one build.
  That page has no row for `CUnit::Hit` or `CUnit::HandleEvent`.

## Where the Battle Engine's Damage comes from

Besides weapons, the engine calls `Damage` on itself and others:

- **Ground impact.** `CBattleEngine::DeclareOnGround` damages the engine with `speed × 16 × cos²`, where the cosine is
  between its velocity and the ground normal, with no source and the shield flag false, so the hit goes to life and not
  to shields. It does nothing while the engine is dying (it explodes instead), while it stands on an object, or in walker
  state during a dash. It applies only above a speed of 0.2 outside walker state (jet and both morphing states) or 0.4 in walker
  state, and then the velocity is scaled by `1 - cos²`; below that speed, in jet state only, the velocity is multiplied by 0.9. Evidence: SOURCE, `references/Onslaught/BattleEngine.cpp:2949-2992`, the same text
  in the decompilation; MEASURED for the call itself: the complete retail `DeclareOnGround` was identified as the caller
  of slot 40 with a computed amount, a null source, a false shield flag and -1.
- **Thruster scorch.** With thrusters on, the engine damages every unit within a radius of 4 that is not itself, whose
  height is above the engine's height minus 2 and whose distance is under 2.5, by `0.2 / distance`, with the shield flag
  true and no mesh part. Evidence: SOURCE, `references/Onslaught/BattleEngine.cpp:1726-1744`; the retail agreement of this
  loop was not separately checked.

## The Battle Engine's order

The engine keeps life, energy and shields. Their maxima come from its configuration; in walker state every call copies
shields into energy (see [configuration values](battleengine/battleengine-config-values.md); those are Stuart's
defaults, and the Steam profile in use may differ). The steps run in this order on every call.

1. **Snapshot.** Life, shields and energy at entry are saved for the invulnerability step below.
2. **Positive amounts only: statistics.** The player's damage-taken statistic grows by the amount times 256, converted
   with the processor's current rounding mode (the retail code does not truncate): for an amount of 3/512 the statistic
   grew by 2 under round-to-nearest and round-up and by 1 under round-down and truncation. The statistic grows even when
   the engine is invulnerable and even when its life is already negative (measured). Which rounding mode the running game
   uses was not observed.
3. **Positive amounts, life not negative: the shield stage.** Damage reaching an engine whose life is already below zero
   changes neither life nor shields (measured: life -1 and shields 4 stay), but the time stamp and the statistic still
   happen. Otherwise:
   1. If shields are at least the amount, the shield share is `amount × efficiency / 100` (zero when the shield flag is
      false). The shield share comes off the shields **and off the amount**, and whatever remains of the amount goes on to
      life. With an efficiency below 100, shields that could cover the whole hit therefore still let the remainder through
      to life. Measured with efficiency 50, life 10, shields 4: an amount of 2 left life 9 and shields 3; with the shield
      flag false it left life 8 and shields 4. If the augmentation is not active and the walker part has an augmentation
      weapon, the shield share is added to the augmentation value.
   2. If the remaining amount is still more than the shields and the shield flag is true, the shields are emptied: the
      shields are added to the augmentation value (when it is not active; here there is **no** augmentation-weapon check),
      the amount is reduced by the shields and shields become zero. Efficiency is not applied in this arm. Measured: an
      amount of 6 against shields 4 left shields 0, life 8 and augmentation 6 (from 2).
   3. Life is reduced by what remains. If life is then below zero **and the vulnerability flag is exactly 1**, the death
      process starts at this point, before the time stamp and everything after it (measured at the recording stand-in:
      life -16 at entry to the death routine; afterwards energy 0, the stamp and the capped augmentation were written).
4. **Positive amounts: stamp and flash.** The last-damage time becomes the event clock, and when the source is not null a
   directional damage flash is added at the source's position. The flash path was read statically and was not part of
   the isolated runs (their source was null).
5. **The common tail, for every amount, including zero and negative.** The augmentation value is capped at 10. In
   walker state energy is set to shields, **before** any repair. A negative amount then repairs life up to the
   configured maximum and spends what is left on energy up to its maximum. Measured in walker state: an amount of
   -12 with life 10 (maximum 20) and shields 4 gave life 20 and energy 6 (the copy of 4, plus the 2 left over). An
   amount of exactly zero is therefore not an early return: in walker state it still copied shields into energy and
   capped augmentation (energy 4, augmentation 10 from 12).
6. **Shake and vibration.** The difference `(life at entry − life now) / 8` is halved when shields are non-zero, then
   capped at 0.25 and passed to the shake routine. That routine ignores values under 0.001 and otherwise draws
   three numbers from the game's shared random stream for the camera shake, four numbers from the C runtime generator
   for the cockpit shake when there is a cockpit, and triggers controller rumble. The difference is then capped at 0.05
   and `difference × 50` is added to the engine's vibration value. Neither cap is a lower bound, so **repairing life
   lowers the vibration** (measured: an amount of -3 took vibration from 1 to -8.375 and drew no random numbers). Each
   frame the vibration is multiplied by 0.7 and the rest is sent to the controller clamped between 0 and 1
   (SOURCE, `references/Onslaught/BattleEngine.cpp:1311-1328`).
7. **Invulnerability.** Only now, if the vulnerability flag is exactly 0, life, shields and energy are put back to their
   entry values. Nothing else is put back: the statistic, the time stamp, the augmentation value, the vibration and the
   shake and random-number state keep their new values. Measured: with the flag 0, an amount of 6 left life, shields and
   energy as they were, but augmentation went from 2 to 6, vibration changed, the random seed advanced and the cockpit's
   generator was drawn from; an amount of 30 (which kills a vulnerable engine) started no death. A repair is undone the same
   way.
   A flag value of 2 does neither: a lethal hit left life at -16, started no death (the death test is "equal to 1") and
   restored nothing (the restore test is "equal to 0").

The consequences for the player's engine, each INFERRED from the order above:

- An invulnerable engine is still shaken, still charges its augmentation and still counts damage taken; it is only
  spared the loss. A repair through this call is undone as well, so it cannot raise life or energy.
- Damage taken with shields up is split rather than blocked whenever efficiency is below 100: with the source default
  of 90, a hit that the shields could absorb entirely still costs a tenth of its size in life.
- A ground impact bypasses the shields entirely (shield flag false).

Unordered (not-a-number) amounts take the compiled comparisons' path, which differs from what the C text of the source
would suggest: in the isolated runs a not-a-number amount skipped the positive stage but entered the repair stage, left
life at its maximum and turned energy into a not-a-number. Nothing known passes such an amount; the case is recorded so
that a reimplementation does not rely on the C reading.

## Every other unit: `CUnit::Damage`

The base implementation serves units, buildings, vehicles and aircraft alike. Subclasses that override slot 40 mostly forward to it; the ones read for this page (decompilation source, read statically)
are, and the list is not claimed to be complete:
`CBuilding::Damage` first notes the time and may change its animation, then forwards when the building has a segments
controller or is not dying; `CHiveBoss::Damage` ignores damage whose source is an explosion and forwards the rest unchanged;
`CAirUnit::Damage` forwards, then once the unit is dying and has a smoke effect it starts that effect at one of the unit's
smoke emitters, flagged important when the cause was a round fired by a Battle Engine (it draws from the game's random
stream to pick the emitter when there are several); `CInfantryUnit::Damage` ignores all damage while the unit is dying
(stronger than step 2), knocks the unit down and throws it away from the cause when that is an explosion, a round with an
explosion radius or a Battle Engine, then forwards, and picks a directional death animation when the forwarded hit killed
a unit that was not thrown. The steps run in this order; "returns" means the later steps do not run.

1. **Squad notification.** If the unit belongs to a squad, the source is ammunition and the ammunition's owner is a unit,
   the squad's "recently attacked" time is set to the event clock plus 5 seconds. (An earlier reading, that this wrote a
   cooldown into the damaged unit itself, was wrong: the write goes to the squad. Measured with the real squad helper:
   with the clock at 10 the squad's value became 15 and the damaged unit's own field stayed untouched.) The only reader
   of that time in the decompilation's source is the test the HUD battle-line overlay uses to draw squads of the
   Forseti allegiance as red points while it is in the future ([battle line](../engine/render/DXBattleLine.md)); that
   reading is static.
2. **Dying suppression.** A dying unit whose profile carries the `Big` flag ignores damage whose source is an explosion
   (returns).
3. **Deploy scaling.** In deploy states 3, 4 and 5 the amount is multiplied by the profile's `DeployDamageMultiplier`.
4. **Split by sign.** A positive amount is damage; anything else goes to the repair arm in step 11. A damage arm returns
   at once when the unit's vulnerability flag is zero.
5. **Nexus restriction.** A unit whose mesh has a part named `nexus` (the check at construction is case-insensitive) takes
   no damage from explosions (returns), and for a hit that names a part, ignores it unless that part is the `nexus` part
   (returns). A hit with no part, or whose part index finds no part, passes. There is a further block in the code that
   measures an explosion against the nexus part's position; the explosion return just before it makes it unreachable in
   ordinary play (the two tests use the same bit with no change between them), so explosion geometry never decides
   anything here.
6. **Weak-point multiplier.** A unit whose mesh has a part named `weakpoint` multiplies by 5 any hit that names a part
   which is **not** called `weakpoint`; a hit on the `weakpoint` part, or with no part, is not multiplied. This is the
   reverse of what the names suggest, and the isolated runs reproduced it with synthetic part names.
   Whether any shipped unit relies on it is not checked here.
7. **Segmented units.** A unit with a segments controller hands the part index, the amount and the source to it and
   returns; steps 8 to 10 do not run for it.
8. **Hook, then shields.** A virtual hook (slot 107) receives the amount. Read statically (the isolated runs stubbed this hook): it adds the
   whole-number part of 100 × the amount to the unit's recent-damage level (so a hit under 0.01 adds nothing), capped at
   100, queues event 4005 only when the level was zero before the hit, and `CComponent`'s override also forwards the amount to
   its parent. Event 4005 lowers the level by 10 per frame; `GetShouldDoHitEffect` returns the level as
   the strength of the hit effect the mesh renderer asks for (`references/Onslaught/MeshRenderer.cpp:592`). Then, only
   when the shield flag is true, a hit no larger than the shields comes off the shields **at full value (there is no
   efficiency here) and returns**; a larger hit empties the shields and the rest goes on. With the flag false the shields
   are left alone and the full amount goes on. Because a full absorption returns here, it skips everything below,
   including the radio-warning draw.
9. **Life and death.** Life is reduced by the amount. Death needs life **below** zero (exactly zero does not die) and the
   unit not already dying. In that case: if the source is ammunition owned by a Battle Engine, the owner's player gets one
   count on the units-destroyed statistic; then, unless the profile carries `Retreat`, the die process starts and a
   second hook (slot 71) is called with the remaining amount and the source; finally a per-unit field is cleared (its role is not established).
10. **Particles.** After the damage arm, if shields are above 2 and the profile has a first particle effect, it is created at the
    source's position. INFERRED from steps 8 and 9: since a full absorption returned and a partial one emptied the shields,
    shields can still be above 2 here only when the hit did not use them (shield flag false).
11. **Repair arm.** A negative amount repairs only when `0 < life < maximum`. If the missing life is smaller than the repair,
    life becomes the maximum; otherwise life rises by it. Shields and the vulnerability flag play no part; a unit at zero or
    below is not revived (measured: at, below and above the maximum, and with shields on both sides of 2).
12. **Deferred death.** A profile with `Retreat` and a life below zero calls another hook (slot 100) here, for
    damage and repair paths that did not return earlier. Read statically, that hook is the retreat move: `CUnit`'s version
    sends the unit to the nearest safe side (`FindNearestSafeSide`, then `GoToPoint`) and sets deploy state 1 unless the
    state is already 1 or 2, and `CGillM` overrides it to walk back to where it came up. It does not mark the unit dying.
13. **Radio warnings.** Only profiles carrying `Wingman` take this path. It draws **one number from the game's shared
    random stream, modulo 3, before any threshold is looked at**, so such a unit consumes a random number on every call
    that reaches this step, whether or not a line is played (measured: one draw in every case). The draw chooses one of three lines for the speaker
    (a pilot named `Tara Fighter` or `Billy Fighter` by the profile's name, otherwise a default speaker). Then
    an else-if chain with strict comparisons, each branch also needing its own flag clear:

    | Order | Condition | Flags set |
    | --- | --- | --- |
    | 1 | life below 0 and the "dying" flag clear | dying, quarter, half |
    | 2 | life below 0.25 × maximum and the quarter flag clear | quarter, half |
    | 3 | life below 0.5 × maximum and the half flag clear | half |

    A branch whose flag is already set falls through to the next test; the three are one choice, not three lines at once.
    A line is submitted to the message box only when a message box exists and the line was found. Nothing but the unit's
    construction clears the three flags (searched in the decompilation's source), so a unit that is repaired does not repeat
    a line. Whether a line is actually shown or heard was not observed.

This page replaces the frozen notes on these functions that were in the Toolkit's `reverse-engineering/` folder (they remain in
the Toolkit's Git history). Those notes kept earlier readings that were later corrected and that this page does not repeat: the nexus and weak-point name tests taken the wrong way round, warning
thresholds of 0.25, 0.5 and 1.0 of maximum that re-arm, a repair that depends on shields, a nonpositive Battle Engine
amount that returns at once, and a damage cooldown written into the damaged unit.

## Contact: `CUnit::Hit`

When a unit's collision with another thing is reported, `CUnit::Hit` runs these steps:

1. If the unit has a squad, the squad is told what was touched; the squad passes it to its mission script's `Hit`
   event when the thing is a `CComplexThing` and the script's virtual machine is not already running (decompilation source:
   `CSquad`, `IScript::Hit`; read statically).
2. If the other thing is a unit, a per-frame "touched by a unit" marker is set. `CUnit::Move` clears it at the start of
   each frame, and no function in the decompilation's source reads it.
3. **Standing on something.** If the other thing can be walked on, a collision report exists with its first word
   non-zero, and the unit's `Gravity` query is above zero, the contact normals are tested against straight down (the vertical axis is Z):
   - if any contact's normal has `-Z` above **0.89** (about 27 degrees from level), the unit is standing on it;
   - if none does and the report holds **more than one** contact, the first **three** normals are added, normalised, and
     the unit stands if `-Z` of the result is above **0.69** (about 46 degrees).
   Standing means `DeclareOnObject(other)` followed by `DeclareOnGround()`.

   The `Gravity` gate is wider than one class (decompilation source, read statically): `CThing::Gravity` returns a small
   positive value by default, so ground units pass it, while the aircraft classes return zero unless the unit is dying.
   `CAirUnit::Gravity` returns a value that depends on the unit's size while dying; `CPlane`, `CBomber`, `CDiveBomber`
   and `CCarver` return a fixed small positive value only while dying. Other classes override it too: `CHiveBoss` always
   returns a small positive value, and `CCannon` returns zero, so a cannon never takes this branch.
4. The base class's `Hit` always runs afterwards.

Two details matter to a reimplementation.

- **The sum covers three normals even when there are two contacts.** The third slot holds whatever the collision
  producer left there. In experiments on the original sphere-against-mesh routine with authored contact sequences, two
  successful contacts followed by a miss left the third slot unchanged (two different initial contents survived), and a
  third blocking contact wrote the slot while the count stayed two. The dispatcher initialises the scalar fields of the
  report but not the normal array. Whether real triangle geometry produces these sequences was not measured.
- **The threshold decision depends on single-precision rounding.** The retail code stores the summed Y component as a
  single-precision value before using it and keeps the other two components at register precision; a plain normalise
  differs. Over 13,839 authored sets of normals, the earlier plain-normalise rewrite disagreed with the retail block in
  198 decisions at each of two control-word settings and in 588 at a third; the rewrite that keeps the rounding disagreed in
  none (a threshold of one instead changed 5,646, which shows the test could tell). The inputs are authored; the live
  floating-point setting was not observed.
  (`<maintainer evidence>/unit-hit-root-20261001/native/receipt.json`, SHA-256
  `5aee572fc271e2d3a9c0c55f6f0693ae9546df3832913e623d728cb8da18148f`; and
  `<maintainer evidence>/unit-hit-match-root-20261001/native/receipt.json`, SHA-256
  `9b45d9e6e039ba119d4b8c1aad58e64cc066af72ea1d090db47532179388e9bc`; the slot experiment is
  `<maintainer evidence>/report-normal-slot-20261001/root-reproduction.json`, SHA-256
  `a3ad28737868b6b26d09a1b9544552dc938fa04096130cad5a8eff84d0faad19`.)

## Events a unit handles: `CUnit::HandleEvent`

The scheduler delivers a due event to its target's slot 0; for units that is this handler, and anything it does not
handle goes to the base class. Four event numbers are handled; the decompilation's names for the numbers are still open.

| Event | What the handler does |
| --- | --- |
| 4001 | Updates the unit's weapon pitch: toward the AI's target when it has one and the current weapon fires a round, otherwise back to the rest value once ten seconds have passed since the last target, clamped between -π/2 and π. It then queues 4001 again after a random delay under 0.1 s. It does nothing, and does not requeue, while its enabling flag is clear or the unit is dying. |
| 4003 | Sets a flag if a current camera of a present player is within 50 units of the unit (the squared distance is below 2500; equality does not count), then queues 4003 again after `3 + a random fraction` seconds (3 to under 4). The random number is drawn after the camera tests. The first 4003 is queued on the next frame when the unit is initialised. The flag marks the unit as near a player's camera and several routines read it (decompilation source, read statically):
`CUnit::GetEmitter` takes a different path when it is clear, `CInfantryUnit::SetAnimMode` does nothing without it (infantry
animate only near a camera) and `CInfantryUnit::Move` acts only with it, and `CUnitAI` picks a re-plan delay of 1.5 to
under 2.5 seconds with it and 3 to under 5 without. |
| 4004 | Spawns the unit's configured explosion at its position, then schedules the unit's shutdown (`AddShutdownEvent`). |
| 4005 | Lowers the recent-damage level (step 8 above) by 10 and queues itself for the next frame while the level is above zero, otherwise sets it to zero. |

Event 4004 has two producers in the decompilation's source, both unit destruction paths aimed at the unit itself:
`CComponent::StartDieProcess` queues it 7.0 seconds ahead for a component whose profile carries `Big` and does not fall away
from its parent (the profile flag for falling away gives the component a velocity instead), and the mech's die process
queues it 3.5 seconds ahead. Its
explosion call is named `CUnit::SpawnExplosion` in the decompilation, which is the naming authority and which this page
follows; an earlier note called it a pickup spawner. All of this is static: no frequency or presentation was observed.

## Open questions

- **Live play.** None of the above was observed in a full game. The cheapest falsifier for the Battle Engine's order is a
  controlled run of a copied game with a debugger watching life, shields and energy across one hit of known size, with
  the efficiency read from the running configuration.
- **A non-null attacker.** The damage-flash path (allocation, list and lifetime) was not executed; the isolated cases used
  a null source.
- **The rounding and precision state of the running game** for the damage-taken statistic and for the contact threshold.
- **Retreat units and the kill count.** By the order above, a unit with `Retreat` whose life is negative does not start
  its die process and so is not marked dying by this function; each later damaging hit would again pass the death test
  and add to the units-destroyed statistic. Whether something else marks such a unit dying first is not established. The
  falsifier is two damaging hits on a negative-life `Retreat` unit counting the statistic.
- **Which units carry a `nexus` or `weakpoint` part**, and so whether the multiplier and the restriction matter in shipped levels.
- **Contact from real geometry.** Captured contact reports from the collision query, with the live floating-point
  setting, replayed through the threshold block.
- **Event names.** The authored names of 4001, 4003, 4004 and 4005, and what exactly the near-camera flag changes in the first branch of `CUnit::GetEmitter`.
