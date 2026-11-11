# Mission script commands: declared signatures and the behaviour of selected commands

Status: active — corrections and additions to the command registry; static evidence
Last updated: 2026-11-11 (new page)
Summary: what each registry record declares besides its name and handler (argument count, argument types, return flag and
type, in a new table), a check of the registry against the decompilation, and what 34 of the commands do, grouped by
subsystem and written from the matched code, including where a command does less or more than its name suggests.
Evidence: MEASURED (static) — the functions of the byte-matching decompilation,
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) (commit `9759593`), cited by function name. The
registry table and the `IScript` natives it lists are in the decompilation's `IScript` source and compile to the retail
bytes. Pinned source is Stuart Gillam's [public fork](https://github.com/dlprentice/Onslaught/tree/c3d8ac464259942b83fa8aa7f867c856e77b734d)
(`thing.h`, `actor.h`), cited where it backs a line. A name given by the decompilation for a field it does not
understand is quoted as "unnamed". No runtime capture of any command here is cited.
Specimen: pristine PC retail `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
the executable the decompilation matches.

The [command registry](mission-script-command-registry.md) pairs 144 command names with handlers and proves vocabulary
only. This page adds what the decompilation shows about the same table, and describes 34 of the commands, grouped by what
they act on: messages and the HUD, weather and effects, health and segments, animation and orders, helper functions and
the unit and Battle Engine queries. How the interpreter calls a native is in
[mission script runtime](script-runtime-events-and-waits.md#how-a-native-is-called).

## The registry against the decompilation

A differential check of the published registry TSV against the table in the decompilation's `IScript` source (the
`gScriptFunctions` array, which the decompilation's initializer function reproduces from the retail one):

- Both have 144 records, in the same order, and every command name is identical.
- For 143 of the 144, the handler named in the TSV is the entry point of the same-named `IScript` method in the
  decompilation. The exception is `SetSpeed`: its method body in the decompilation is empty, and the retail
  executable shares one do-nothing function among many classes, so the TSV's handler address for it is that shared
  function and not an entry of its own. That is why the registry page counts it as the one no-op handler.
- Every handler is a method of `IScript`; the interpreter calls it with the script object as receiver (the call itself is
  described in [mission script runtime](script-runtime-events-and-waits.md#how-a-native-is-called)).

Each record (`SScriptFunction`) holds, in order: the command name, a declared argument count, a "returns a value" flag,
seven declared argument-type slots, a declared return type and the handler. The registry page and the
[static contract](missionscript-iscript-static-contract.md) record the name and the handler; the other fields are in
[`mission-script-command-signatures.tsv`](mission-script-command-signatures.tsv), which lists all 144 records. The type
codes are int, float, string, bool, thing, position, and "any" (two commands, `Print` and `SetVar`, accept any). Of the
144 commands, 49 are flagged as returning a value.

Three limits on those fields:

- No function in the decompilation reads the declared count, types or flag; the interpreter's call path uses the call
  instruction's own argument count and return flag instead. The declared values are therefore the table's own record of
  each command's shape (probably what the script compiler used, which is not in the game), not something the game checks
  when a script runs.
- Nine commands (`SetAIState`, `HighlightHudPart`, `UnHighlightHudPart`, `Land`, `Dive`, `Surface`, `InitVariable`,
  `SetVariable` and `ShutdownVariable`) have a return type other than none although their flag says they return nothing.
  What the stored type means for them is open; none of these natives returns a value.
- The counts are the declared ones. A script may call a native with a different count; nothing stops it.

Evidence: MEASURED (static) for the differential (a comparison of the two tables, reproducible with a text search of the
decompilation) and for the record layout (`SScriptFunction`); the last two limits are the observation that nothing reads
the fields, from a search of the decompilation, which is a search count and not a proof about code the decompilation
does not contain.

## What the commands do

The groups below describe 34 of the 144 commands; the others are in the [registry](mission-script-command-registry.md) as
vocabulary only. "Gate" is the type check the command
makes on the thing it acts on (the thing named by the call, or the script's own thing): **unit** is the unit type bit,
**Battle Engine** the Battle Engine type bit, **component** the component type bit; **none** means no check. A failed gate
is silent unless a cell says otherwise. A command that returns a value allocates a new script value of the stated type.
Where a command does less or more than its name suggests, the cell says so.

### Messages and the HUD

| Command | Gate | What it does |
| --- | --- | --- |
| `GotoPlayerCamera` | none | Switches player 0's view to that player's preferred control view, first-person or third-person. No check that player 0 exists |
| `SwitchMessagesOn` | none | If the game has a message box, lets it advance its queue and tries to show the next message at once |
| `SwitchMessagesOff` | none | If the game has a message box, stops it advancing its queue. Nothing queued or showing is removed |
| `HighlightHudPart(i)` | none | Sets HUD part `i` to flashing. There are six parts, 0 to 5: health bar, energy bar, compass, battle-line map, radar, current weapon. The index is not range-checked |
| `UnHighlightHudPart(i)` | none | Sets HUD part `i` to on (not off); the same unchecked index |

### Weather and effects

| Command | Gate | What it does |
| --- | --- | --- |
| `SetWindVector(x, y, z)` | none | Stores the three floats as the global wind vector, which snow and the vertex shader read and which is also the console variable `atm_windvector`. The vector's fourth (padding) float is not set by the command |
| `SetRainDensity(d)` | none | Stores the float as the global rain density (also a console variable). No clamping |
| `SpawnParticle(name, pos)` | none | Looks up the named particle set and starts its effect at `pos` with no owner. A missing name logs "Can't find particle effect `<name>`" and does nothing else |
| `SpawnEscapePod()` | none | Needs the thing's render object (else nothing happens). Reads the emitter named `SpawnerF` (number 1) for a position and orientation, and creates an escape pod there: yaw and pitch from the emitter's forward direction, the thing's own position if the emitter position is exactly zero, zero velocity, allegiance 2 (neutral) and a start delay of 1.5 s |

### Visibility, velocity and health

| Command | Gate | What it does |
| --- | --- | --- |
| `SetVisible(b)` | none | Makes the thing visible when the argument is true and invisible otherwise. A squad passes it to its members |
| `SetVelocity(v)` | unit | Passes the vector to the thing's velocity setter. For actors that setter stores it as the velocity (`references/Onslaught/actor.h:25`); the base thing ignores it |
| `SetHealth(f)` | unit | If the unit has unit data, sets its life to `f` times a unit-data value that the decompilation's comment calls the unit's full life, so the argument is a fraction, not an absolute amount. No clamping |

### Destructible segments

| Command | Gate | What it does |
| --- | --- | --- |
| `SetSegmentHealth(name, h)` | unit, and it has a segment controller | Looks up the mesh part by name and writes `h` to that segment's current health. It does not change the segment's maximum or the controller's total. If the name is missing, or the part has no segment, it logs the text `FATAL ERROR: Could not find segment for '<name>` (the game's format string has an opening quote and no closing one) and carries on; if the thing has no render object or mesh it returns without logging anything. The part number indexes the segment array with no range check |
| `ResetSegmentHealth(name, h)` | same | As above, but writes both current and maximum health, and recomputes the controller's total health when it has a core segment. Same log text |
| `SetAllSegmentsHealth(h)` | same | Writes `h` as the current health of every segment that exists. The total is not recomputed |
| `SetSegmentVulnerable(name, b)` | same | Writes the segment's vulnerable flag and recomputes the controller's total health when it has a core segment. Same log text |

### Animation, deployment and orders

| Command | Gate | What it does |
| --- | --- | --- |
| `PlayAnimationWait(name, reset, loop)` | none | Starts the animation and suspends the script until it finishes. Its wait rules are in [mission script runtime](script-runtime-events-and-waits.md#the-animation-wait) |
| `Deploy()` | unit | If the unit's deploy state is 0 (not deployed), sets it to 3 (deploying) and plays the "deploying" animation. Otherwise nothing |
| `Undeploy()` | unit | If the unit's deploy state is 4 (deployed), sets it to 5 (undeploying) and plays the "undeploying" animation. Otherwise nothing |
| `Stop()` | none | Sends a go-to order to the thing's own current position; it does not call the thing's stop function. For a unit that sets its guide's destination to where it stands, unless the unit's AI is in mode 2 (see [follow waypoint commands](follow-waypoint-commands.md#what-the-order-does)); for a plain thing it does nothing |

### Vector, random and position helpers

| Command | Gate | What it does |
| --- | --- | --- |
| `SetY(v, y)` | none | Returns `v` with its Y component replaced by `y`; X, Z and the padding float are kept |
| `Normalise(v)` | none | Returns `v` scaled to length 1, or unchanged if its length is zero; the padding float is carried through |
| `GetFloatRand()` | none | Takes one value from the game's random stream (never negative), keeps its remainder modulo 65,536 and divides by 65,536: a float from 0 up to but not including 1. One value is consumed per call |
| `GetAngle(thing)` | none | The absolute angle in degrees, in the horizontal plane, between the acting thing's facing direction and the direction to `thing`, using the wrap-around rule of the Battle Engine's angle difference. Returns 0 if `thing` is empty |
| `GetSafePos()` | unit | Returns the unit's "safe position": the zero vector for every class except the hive boss. The hive boss's override returns its own position, or a point at its safe distance from the player's Battle Engine in the horizontal direction away from it, depending on the ground height at that point against the water level. Non-units return zero |
| `IsOverWater()` | none | True when the global water height is below the ground height at the thing's position, that is, when the sea covers the ground there |

### Unit state queries

| Command | Gate | What it does |
| --- | --- | --- |
| `IsEnemy()` | unit | True exactly when the unit's allegiance is 1 (Muspell). It does not compare the thing with the caller or the player |
| `SpawnersInUse()` | unit | True if any of the unit's spawners reports busy (a non-zero field the decompilation leaves unnamed) |
| `GetTarget()` | unit | Returns the unit's current target thing, or empty. For a plain unit that is its AI's target. For the Battle Engine the override returns the first lock that has not been fired and, failing that, cycles through the fired locks; **each call advances the Battle Engine's target index**, so calling it has a side effect |
| `IsFiring()` | unit | True if any of the unit's weapons is in the middle of a burst (burst count above 0 and below the mode's burst size). It is not the Battle Engine's own walker or jet firing query |
| `GetNumber()` | component | Returns the component's mount number; 0 for anything that is not a component |

### Battle Engine queries

| Command | Gate | What it does |
| --- | --- | --- |
| `InJetMode()` | Battle Engine | True unless the engine is "walking", where walking means: walker state and on the ground within the last half second. So it is true in jet state, during either morph, and in walker state after half a second off the ground |
| `GetWeaponAmmo()` | Battle Engine | A fraction from 0 to 1. For an engine whose configuration is named "Racer", the speed divided by 1.5, capped at 1; otherwise whatever the active part (walker, or jet in jet state) reports as its ammunition fraction. 0 for anything that is not a Battle Engine |
| `GetWeaponCharge()` | Battle Engine | A fraction from 0 to 1. For a "Racer", the distance from the engine's render position to the higher of the ground and the sea surface, divided by 5, capped at 1; otherwise the active part's weapon charge. 0 for anything that is not a Battle Engine |

Evidence: MEASURED (static) — each row is one `IScript` method read in the decompilation together with the function it
calls: `CMessageBox::SwitchMessagesOn` and `SwitchMessagesOff`, `CPlayer::GotoControlView`, `CHud` (the part-state array
and its six components), `CAtmospherics`, `CDestructableSegmentsController` (`SetSegmentHealth`, `ResetSegmentHealth`,
`SetAllSegmentsHealth`, `SetSegmentVulnerable`), `CUnit::StartDeploying` and `StartUndeploying`,
`CUnit`'s any-weapon test over `CWeapon::IsFiring`, `CUnit`'s any-spawner-busy test (a `CSpawner` query the decompilation
leaves unnamed), `CBattleEngine::IsWalking`, `GetWeaponAmmoPercentage`, `GetWeaponCharge` and `GetCurrentTarget`, the hive
boss's safe-position override (`CHiveBoss`), `CThing::IsOverWater`,
`CSeedUniformRandomNumberStream::Next`.


## What this page does not claim

- Behaviour with non-finite inputs. The compiled floating-point comparisons in several of these commands (`InJetMode`,
  `SpawnEscapePod`, `Normalise`, `GetAngle`, `IsOverWater`) treat unordered values in ways the C++ in the decompilation
  does not show. No command here is known to receive such a value, and none is described.
- What the HUD part numbers, the escape pod's start delay, the deploy-state numbers or the segment fields mean to the
  player. They are the decompilation's field values, not captured effects.
- Original C++ names. A registry name is the script-facing command; the decompilation names the `IScript` methods after
  those commands.
- Allocation failure. Every command that returns a value allocates its result; what happens when the allocator fails was
  not examined.

## Open questions

| Question | Cheapest check |
| --- | --- |
| What does the return type stored for the nine commands whose flag says they return nothing mean? | Search the shipped script compiler's output (not in this repository) or the compiled scripts for a use of those calls that expects a value |
| Is the segment part number ever outside the segment array in shipped scripts (the lookup has no range check)? | Compare every shipped segment command's part name with the unit's mesh part list |
| Does calling `GetTarget` from a script visibly change the Battle Engine's lock cycling? | In a copied runtime, call it from a level script while the player holds locks and watch the target index |
