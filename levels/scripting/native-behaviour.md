# Mission-script natives: what each one does

Status: active — static behaviour of 33 mission-script natives, with the names that mislead; no runtime capture
Last updated: 2026-11-11 (new document)
Evidence: MEASURED — each handler and the code it hands off to is a function of onslaught-decomp that the decompilation lists as matching the retail bytes, so its source is the retail behaviour, read statically; SOURCE — the pinned Onslaught source for the base-class behaviour it contains; INFERRED — what the player sees as a result; UNKNOWN — the open questions at the end.
Summary: what `SetObjective`, `SetVisible`, `SetTimer`, `SetVar`, the weather natives, `SpawnEscapePod`, `PlayAnimationWait` and the other natives listed below really do, how a native is called, and which names mislead (the "variable" natives are HUD text slots, `SetVar` is a per-thing tuning hook, `SetTimer` queues a `timer` event, `InJetMode` means "not walking").
Specimen: pristine Steam `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` (the file onslaught-decomp matches).

A native is a function the script interpreter calls by name: `SetObjective()`, `thing.SetVisible(0)`, `SetTimer(5.0)`. The
[command registry](mission-script-command-registry.md) shows that the game pairs 144 names with 144 handlers and says
nothing about what a handler does. This document says what 33 of them do. The natives whose behaviour is long enough
to need their own page are described in [the HUD natives](native-hud-and-objectives.md) (objective markers, HUD part
flashing, and the four on-screen text slots behind `InitVariable`, `SetVariable`, `GetVariable` and
`ShutdownVariable`) and [the segment natives](native-segment-health.md) (five natives that set the health and
vulnerability of a unit's destroyable segments). The natives that spawn things, move things along waypoints, show
messages, run cutscenes or control cameras are not covered here.

## How this was established

- Every native here is the `IScript::<Name>` function in
  [`src/MissionScript/IScript.cpp`](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp)
  of [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) at commit `9759593`. That repository's
  [`docs/check/matched.tsv`](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/docs/check/matched.tsv)
  lists each of them, and each function they call that this document cites, as compiling to the retail function's bytes.
  A matching function does what the retail function does, so the behaviour below is MEASURED by byte comparison against
  the specimen. It is static evidence: no native was run under a controlled capture, so what each one does to the
  screen is inferred from the code that consumes its result and is labelled as such.
- Where a native hands its work to another function (a thing's virtual method, the HUD, the weather statics), that
  function was read in the same tree. Behaviour that Stuart Gillam's published source also contains is cited as
  `references/Onslaught/<file>:<line>`, the pinned fork described in the README's
  [How to read a finding](../../README.md#how-to-read-a-finding) (commit `c3d8ac4`). The natives themselves are not in
  that source.
- "Shipped use" counts call sites in the loose `.msl` scripts under `data/MissionScripts` of the Steam installation,
  with `//` and `/* */` comments removed first. It is a corpus observation: it shows that scripts call a native, not that
  the game reads these loose files rather than packed copies, which the
  [static contract](missionscript-iscript-static-contract.md) leaves open.

## How a call runs

All of this is from `CInstructionOP_POINTER::Execute` and `CInstructionOP_CALL::Execute`
([`AsmInstruction.cpp`](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/AsmInstruction.cpp#L381)),
and from the native table `gScriptFunctions`
([`IScript.cpp`](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L52)).

- **The receiver.** A call written `thing.Native(...)` first makes `thing` the script's current target; a bare
  `Native(...)` acts on the script's own thing. When the native returns, the target goes back to the script's own thing,
  so one `thing.` applies to one call only. A null receiver does not run the native: the interpreter logs that it cannot
  call the function on a null object, pushes the integer 0 as the result and carries on.
- **Arguments.** Each table record declares a name, an argument count, whether the native returns a value, up to seven
  argument types and a return type. The handler reads its arguments with the conversions the datatype classes provide:
  an integer widens to a float, and any nonzero integer is true. The interpreter checks the return flag: a native that
  returns a value must set one, and a native that does not must not, or the interpreter logs an error. A native that
  returns nothing leaves the integer 1 on the stack.
- **Gates.** Many natives test the receiver's thing type first and do nothing when it does not match. A setter then
  returns silently; a getter returns zero, 0.0 or an empty string. The gate is named in the table below. The natives
  have no way to report that a gate failed.

## The natives

Argument names are descriptive; the registry gives only types. "Any" means no gate. Line numbers link to the handler.

### Marking, showing and hiding things

| Native | Receiver | What it does | Shipped use |
| --- | --- | --- | --- |
| `SetObjective()` ([L1231][d-obj]) | any thing | Marks the receiver as an objective: adds it to the world's objective set and sets its marked flag. Marking twice changes nothing. The compass and the battle-line map draw one marker per member of that set. A complex thing's shutdown unmarks it. See [the HUD natives](native-hud-and-objectives.md#objective-markers). | 298 sites, 221 files, 68 levels |
| `UnsetObjective()` ([L1237][d-unobj]) | any | The reverse: removes the receiver from the set and clears the flag; unmarking an unmarked thing changes nothing. | 250 sites, 217 files, 59 levels |
| `IsObjective()` → bool ([L1243][d-isobj]) | any | True when the receiver's marked flag is set. A complex thing answers from the flag; the base thing class always answers false (`references/Onslaught/thing.h:139` and `:274`). | 9 sites, 9 files, levels 22 and 100 |
| `SetVisible(flag)` ([L1222][d-vis]) | any | Nonzero calls the receiver's `MakeVisible`; zero calls `MakeInvisible`. For ordinary things these clear and set the invisible flag (`references/Onslaught/thing.h:157-158`); squads override both. | 62 sites, 8 files, levels 621, 622, 731, 732, 741, 742; only the literals `0` (hide) and `1` (show again), often on `GetComponent(n)` receivers |

### Health, velocity and position

| Native | Receiver | What it does | Shipped use |
| --- | --- | --- | --- |
| `SetHealth(fraction)` ([L1124][d-health]) | unit | Sets the unit's life to `fraction` times the unit data's starting life, the value `CUnit::Init` gives a new unit and `CUnit::GetMaxLife` returns when there is no segments controller. Does nothing if the unit has no unit data. It writes the unit's own life only: for a unit that has a segments controller, `GetHealth` reads the controller instead (`CUnit::GetLife`), so the written value is not what `GetHealth` reports for it. | 3 sites: `0.001` in the two Carrier scripts (levels 331, 332), `500` on a target called "Rocket" in level 500 (open question 6) |
| `SetVelocity(vector)` ([L522][d-vel]) | unit | Passes the vector to the receiver's `SetVelocity`. The base thing class ignores it (`references/Onslaught/thing.h:143`); an actor stores it as its velocity (`references/Onslaught/actor.h:25`). Replaces the velocity; it does not add to it. | 2 sites, the ejector scripts of levels 621 and 622, each with the vector (0, 0, −2) from `CreatePosition` |
| `SetPos(position)` ([L1510][d-pos]) | any | Calls the receiver's `Teleport` with the position. `CThing::Teleport` sets the position and moves the thing there (`references/Onslaught/thing.cpp:430`); `CActor::Teleport` also sets the previous position, so the move is not interpolated, and updates the thing's map-who entry. Velocity is untouched. The `Teleport` native does the same with a position or the name of another thing. | none |

### Weather

All four write a static cell of `CAtmospherics`
([`Atmospherics.cpp`](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/Atmospherics.cpp#L15))
with no clamp and no gate, and need no receiver. The cells are cleared each time a level finishes loading (`CGame::PostLoadProcess` calls
`CAtmospherics::InitialiseAll` and `SetupAll`) and are also exposed as the console variables `atm_windvector`, `atm_raindensity`, `atm_snowdensity` and
`atm_lightningdensity`, so the console and a script write the same memory.

| Native | What it does | Who reads the cell | Shipped use |
| --- | --- | --- | --- |
| `SetSnowDensity(d)` ([L1987][d-snow]) | Sets the snow density. | `CSnow::Render` draws `d × 1000` falling flakes, limited to the range 0 to 1000, and skips snow entirely when `d` is 0 (`DXSnow.cpp`, [L324][d-snowcount]). | 10 sites in 4 files: level 22 (a stepped sequence from 0.1 to 0.7), levels 100 and 512 (a weather script that starts at 0.1 and raises it by 0.1 every 10 seconds while it is below 0.9) and level 110 (sets 1) |
| `SetWindVector(x, y, z)` ([L1975][d-wind]) | Sets the wind vector from three floats. | Snow only: `CSnow::Render` takes the wind's X and Y as the sideways drift of the falling flakes, with a fixed fall speed (`DXSnow.cpp`), and the snow-settling shader constant uses the wind's direction with Z replaced by 1 (`VertexShader.cpp`, [L836][d-vs]). | none |
| `SetRainDensity(d)` ([L1981][d-rain]) | Sets the rain density. | No function in the decompilation reads it; only the console variable exposes it. | none |
| `SetLightningDensity(d)` ([L1993][d-light]) | Sets the lightning density. | No function in the decompilation reads it; only the console variable exposes it. | none |

The wind vector is the engine's `FVector`, which is three floats and a fourth padding float
([`maths.h`](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/maths.h#L32)).
`SetWindVector` builds the vector from its three arguments and the three-float constructor does not set the padding
word, so the word stored with the wind is whatever the compiled function leaves in the temporary. Nothing cited above
reads it. The weather statics' only readers in the decompilation are the snow code, which makes "no reader" for rain and
lightning a finding about the 99.4 % of the game's functions that onslaught-decomp reproduces, not about the five
sources it leaves out (see open question 5).

### Time, waiting and spawning

| Native | Receiver | What it does | Shipped use |
| --- | --- | --- | --- |
| `SetTimer(seconds)` ([L1036][d-timer]) | none (acts for the script) | Schedules one event, number 2002, for the script after `seconds`, on the global event manager (`CEventManager::AddEvent`, the time-from-now overload, `references/Onslaught/eventmanager.cpp:143-146`). When it is delivered, `IScript::HandleEvent` starts the script's `timer` event handler with no argument, but only if the interpreter is not already running a script: a timer that fires while the interpreter is busy is dropped, not queued. There is no way to cancel it, and each call schedules another. It does not touch the HUD timers (`VARIABLE_TIMER` is a text-slot style: see [the HUD natives](native-hud-and-objectives.md#the-four-text-slots)). | none |
| `PlayAnimationWait(name, resetFrame, forceLooped)` ([L851][d-anim]) | thing with a mesh | Starts the named animation on the receiver and suspends the script until it finishes; see below. | 24 sites, 9 files: `"opening"` or `"closing"` with `TRUE, FALSE` in the hive-boss and gun scripts, two `"Hit"` calls with `FALSE, FALSE` |
| `SpawnParticle(name, position)` ([L1486][d-part]) | none (not used) | Looks the name up in the particle-effect set and starts that effect at the position with no owner. An unknown name logs "Can't find particle effect" and does nothing else. | 6 sites in 3 files: two effects in each of the level 521, 522 and 530 hive-boss scripts |
| `SpawnEscapePod()` ([L1629][d-pod]) | thing with a render thing | Creates a `CEscapePod`: a small rocket with an engine trail, neutral allegiance, zero initial velocity, and a start delay of 1.5 seconds in its init data (the field that delays when a persistent collision-seeking thing starts colliding; the pod's use of it is not traced). It appears at the position of the receiver's mesh emitter named `SpawnerF` (index 1), with yaw and pitch taken from that emitter's +Y axis; if that position is exactly the origin it appears at the receiver's own position instead. Each move the pod adds a small thrust along its nose to its velocity (`CEscapePod::Move`). A receiver with no render thing spawns nothing. | 4 sites in 4 files: `Cutscene_Lost` and `camera` in levels 741 and 742 |

**`PlayAnimationWait` in order.** (1) If the script is not the receiver's own mission script, it logs "FATAL ERROR: Called
PlayAnimWait on the non base script object" and carries on. (2) If the receiver has no render thing or no mesh it returns
at once without suspending, so the script does not wait. (3) If an earlier wait on this script is still saved, that
saved state is dropped. (4) It looks the animation up by name, ignoring case (`CMesh::GetAnimModeByName`), and starts it
with `CComplexThing::SetAnimMode`; the two flags are `resetFrame` and `forceLooped`. (5) It copies the interpreter's
state, stops the interpreter and keeps the copy. (6) Later, `CAnimation::Process` calls the thing's
`FinishedPlayingCurrentAnimation` when a non-looping animation passes its last frame, and
`CComplexThing::FinishedPlayingCurrentAnimation` calls `IScript::FinishedPlayingAnim`, which restores the copy and
continues the script after the `PlayAnimationWait` call (or cleans the interpreter instead if the level has been lost). Evidence is
the functions named, all matching. Two consequences are read from the source and not observed: an unknown name gives
`AM_INVALID`, for which `CAnimation::Process` does nothing, and a forced-looping animation never reports finishing, so in
either case nothing resumes the script. Whether each shipped use reaches the resume path is open question 7.

### Queries about the receiver

**The Z axis.** Heights in the engine's world are compared as stored, and the engine's Z axis points down: `CSnow::Render` makes snow fall along +Z, and the ejector scripts launch their seats with a velocity whose Z is −2. This is inferred from those two uses, not from a definition, and it is what makes `IsOverWater` and the Racer's height gauge read as they do.

| Native | Receiver | What it returns | Shipped use |
| --- | --- | --- | --- |
| `GetNumber()` → int ([L1053][d-num]) | component | The component's mount number on its parent unit (the index it passes to its parent's mesh when it looks up its emitter, `CComponent::mNumber`, set from the mount at `Component.cpp` [L301][d-compmount]). 0 for any other receiver. | 2 sites in the level 512 `Tube` script, used as a delay for staggering several tubes |
| `GetWeaponAmmo()` → float ([L975][d-ammo]) | Battle Engine | The current weapon's store as a fraction of the configuration's capacity, limited to 1; 0 when there is no current weapon. For the `Racer` configuration it is instead the vehicle's speed divided by 1.5, limited to 1. 0 for any other receiver. See [weapon stores](../../mechanics/battleengine/battle-engine-weapon-stores.md). | none |
| `GetWeaponCharge()` → float ([L1000][d-charge]) | Battle Engine | The current weapon's charge; for the `Racer` configuration the distance between the vehicle and whichever of the terrain height and the water level is numerically smaller, divided by 5 and limited to 1 (a height gauge; see the note on the Z axis above). 0 for any other receiver. | none |
| `GetWeaponName()` → string ([L985][d-wname]) | Battle Engine | The current weapon's internal physics name, not its localised display name; an empty string for any other receiver. | none |
| `InJetMode()` → bool ([L1914][d-jet]) | any | True when the receiver is a Battle Engine that is not walking. `CBattleEngine::IsWalking` is true only in the walker state and only if the engine touched the ground within the last half second, so `InJetMode` is also true while the engine is morphing and while a walker is falling for more than half a second, and false for anything that is not a Battle Engine. | 5 sites in 5 files, always as `thing.InJetMode() == FALSE` (levels 100, 311, 312) |
| `IsOverWater()` → bool ([L1924][d-water]) | any | True when the water level is numerically below the terrain height at the receiver's position (`CThing::IsOverWater`, `references/Onslaught/thing.cpp:543`). The engine's Z axis points down (see the note above), so this is true where the water surface lies above the ground. | none |
| `GetVariable(slot)` → float ([L1349][d-getvar]) | none | The time cell of one of the four HUD text slots; see [the HUD natives](native-hud-and-objectives.md#the-four-text-slots). | none |

### Per-thing tuning: `SetVar`

`SetVar(name, value)` ([L657][d-setvar]) calls the receiver's virtual `SetVar` with the name and the value.
It is not a variable store. Each class that has tunable behaviour overrides it and compares the name against its own
list; a name the class does not know falls through to the base class, which logs "Warning: Uknown var '<name>' in call
to SetVar" (the misspelling is the game's; `references/Onslaught/thing.cpp:827-829`). The decompilation shows two
overrides, so these are the only names that do anything:

| Class | Names | Effect |
| --- | --- | --- |
| `CHiveBoss` ([`HiveBoss.cpp`](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/HiveBoss.cpp#L172)) | `hb_maxvelx`, `hb_maxvely`, `hb_maxvelz` | the guide's maximum velocity on each axis |
| | `hb_rotate_speed` | the boss's rotation speed |
| | `hb_core_top_inner_rotate_speed`, `hb_core_top_outer_rotate_speed`, `hb_core_mid_inner_rotate_speed`, `hb_core_mid_outer_rotate_speed`, `hb_core_bot_inner_rotate_speed`, `hb_core_bot_outer_rotate_speed` | the rotation speed of each of the six core rings |
| | `hb_safe_dist`, `hb_min_height_above_ground` | the safe distance and the minimum height |
| `CFenrir` ([`Fenrir.cpp`](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/Fenrir.cpp#L98)) | `fenrir_diedelay` | the delay before the Fenrir's die event fires once it is dying |

Shipped use: 56 sites in 8 files, all in the level 521, 522 and 530 hive-boss scripts and the Fenrir scripts of levels
741 and 742. A name is compared as a string, so a misspelt name logs the warning and changes nothing.

## Names that mislead

| The name suggests | What the code does |
| --- | --- |
| `InitVariable`, `SetVariable`, `GetVariable`, `ShutdownVariable` store and read script variables | They drive four on-screen text rows in the objective panel. The first argument is a text id, not a variable name; `GetVariable` takes a slot index 0 to 3. ([HUD natives](native-hud-and-objectives.md#the-four-text-slots)) |
| `SetVar` is the setter for those variables | It is a hook into the receiving thing's class, which recognises a few fixed names. (above) |
| `SetTimer` starts the on-screen timer | It queues a `timer` event for the script. The on-screen timer is a `SetVariable` style (`VARIABLE_TIMER`). |
| `SetObjective` completes or announces an objective | It marks a thing for the compass and the battle-line map. Objective results are `PrimaryObjectiveComplete` and its relatives, which this document does not cover. |
| `HighlightHudPart` changes a colour | It makes the part blink; `UnHighlightHudPart` returns it to normal, not to hidden. ([HUD natives](native-hud-and-objectives.md#hud-part-flashing)) |
| `SetHealth(x)` sets health to `x` | It sets life to `x` times the unit's starting life, and `GetHealth` ignores it for units with segments. |
| `ResetSegmentHealth` and `SetSegmentHealth` differ only in name | `ResetSegmentHealth` also sets the segment's maximum health and refreshes the controller's remembered total. ([segment natives](native-segment-health.md)) |
| `SetVisible` only shows | Zero hides and nonzero shows. |
| `SetPos` is a smooth move | It is `Teleport` to a position: an instant move that also resets the actor's previous position. |
| `InJetMode` is true only in jet mode | It is true for any Battle Engine that is not walking, including while morphing. |
| `GetWeaponAmmo` is a count | It is a fraction of the configuration's capacity (speed for the Racer). |
| `GetWeaponName` is the name the player sees | It is the internal physics name. |
| `SetWindVector` writes a four-component vector | It sets three components from its arguments; the record's fourth word is padding that the script does not set. |
| `SetRainDensity` and `SetLightningDensity` make rain and lightning | Nothing in the decompiled game reads them; only snow responds to its density. |

## Open questions

Each is static. The cheapest falsifier is a controlled run of a one-line script in a copy of a level, which this
document did not do.

1. **Loose or packed scripts.** The counts above come from the loose files. Whether the retail game reads them, or packed
   copies, is the [static contract](missionscript-iscript-static-contract.md)'s open question.
2. **The `timer` event's script spelling.** The decompilation lists the event as named `timer` and numbered 2, in a
   table whose names it marks as its own choice (`SCRIPT_EVENT_NAMES`, `ScriptObjectCode.cpp`); no shipped script
   defines it, so how a script declares the handler, and that `SetTimer` reaches it, is unobserved. Falsifier: a script
   that calls `SetTimer(1.0)` and declares the handler, run once.
3. **Declared types of the text-slot natives.** The native table declares `GetVariable` as taking a float and returning
   an integer, and `InitVariable`, `SetVariable` and `ShutdownVariable` as returning a float although they are flagged as
   returning nothing (`HighlightHudPart` and `UnHighlightHudPart` are likewise declared as returning an integer and flagged as returning nothing); the handlers read an integer slot index, return a float, and return nothing. Whether the script
   compiler consumes the declared types is not established here. No shipped script calls `GetVariable`.
4. **Whether `SetHealth` matters for segmented units.** `SetHealth` and `GetHealth` use different values when a unit has
   a segments controller; whether the damage code reads the written life for such a unit is not traced here.
5. **Readers of rain and lightning density.** onslaught-decomp leaves out five of the game's source files and the
   functions they define; the claim that nothing reads those two cells holds for the rest of the game. Falsifier: search
   the left-out functions listed in the decompilation's `docs/SCORE.md` for the two cells.
6. **`SetHealth(500)` in level 500.** One script passes 500 where the other two pass 0.001. As a fraction of starting
   life that is five hundred times the starting life; what the target's starting life is, and whether the value is
   intended, is not established.
7. **Which `PlayAnimationWait` uses resume.** `CBuilding`'s `FinishedPlayingCurrentAnimation` answers for four named
   animations itself and passes the rest to the base class; whether each animation the shipped scripts wait for reaches
   `IScript::FinishedPlayingAnim` is not traced.
8. **A native called on a thing of the wrong type.** The gates make the call silent; whether any shipped script relies on
   that is not checked.

[d-obj]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1231
[d-unobj]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1237
[d-isobj]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1243
[d-vis]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1222
[d-health]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1124
[d-vel]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L522
[d-pos]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1510
[d-snow]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1987
[d-snowcount]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/DXSnow.cpp#L324
[d-wind]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1975
[d-rain]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1981
[d-light]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1993
[d-timer]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1036
[d-anim]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L851
[d-part]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1486
[d-pod]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1629
[d-num]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1053
[d-compmount]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/Component.cpp#L301
[d-ammo]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L975
[d-charge]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1000
[d-wname]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L985
[d-jet]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1914
[d-water]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1924
[d-vs]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/VertexShader.cpp#L836
[d-getvar]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1349
[d-setvar]: https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L657
