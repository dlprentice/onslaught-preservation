# Mission script runtime: native calls, events and waits

Status: active — subsystem description from static evidence, with one runtime observation
Last updated: 2026-11-11 (new page)
Summary: how a thing's mission script runs: the one shared interpreter, how a script command (a "native") is called,
the built-in events a script can handle and what raises each, and how `Pause`, the message waits and the animation wait
suspend a script and bring it back.
Evidence: MEASURED (static) throughout, unless a section says otherwise. Each behaviour was read from the functions of
the byte-matching decompilation, [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) (commit `9759593`),
which compile to the retail executable's bytes, and agrees with the maintainer's earlier static reads of the same
executable. Its function names are cited as written there (`IScript::HandleEvent`,
`CVM::Run`). Pinned source is Stuart Gillam's, from the
[public fork](https://github.com/dlprentice/Onslaught/tree/c3d8ac464259942b83fa8aa7f867c856e77b734d) (`thing.h`,
`game.h`); it does not contain the mission-script runtime. One runtime observation (the `Pause` section) is marked.
UNKNOWN items are listed at the end with the cheapest check for each.
Specimen: pristine PC retail `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
the executable the decompilation matches.

This page describes the interpreter side of mission scripting: what happens between a script asking for something and
the game doing it. The command vocabulary is in the [command registry](mission-script-command-registry.md), the
language in [MSL mission scripting language](msl-scripting.md), and the bounded static boundary in the
[MissionScript / IScript static contract](missionscript-iscript-static-contract.md). Following a waypoint path is
[its own page](follow-waypoint-commands.md); the effect of individual commands is in the
[command signatures and behaviour page](mission-script-registry-corrections.md) for 34 of them.

## What runs a script

There is one interpreter, a single global object (`CVM`, the decompilation's `MISSION_SCRIPT_VM`), and it runs one
script at a time. Each thing that has a mission script owns a script object (`IScript`, a monitor object that handles
scheduled events). The script object holds:

- the thing the script belongs to (its default thing) and the compiled code, a private copy made for that thing;
- the thing the next command acts on, which is the default thing unless a command call names another (below);
- the waypoint state used by the two follow commands (see [follow waypoint commands](follow-waypoint-commands.md));
- the suspended interpreter copies that the wait commands made, and one separate slot for the animation wait.

Destroying a script object deletes its suspended copies, so a script that is waiting disappears with the thing that
owns it.

A run starts at an entry point (an event handler, or the point where a suspended script resumes) and ends when the
handler returns or when something sets the interpreter's stop flag. Four limits shape every run:

- The interpreter refuses to start a run while one is in progress, and logs an error instead.
- A run is cut off after 10,000 instructions: the game logs "Infinite loop in script" and stops the run. Nothing is
  saved, so that script call is abandoned for good.
- Starting an event with values still on the operand stack logs "stack not empty on call".
- When a run ends normally the operand stack must be back at the depth it had when the call began, or the game logs
  "stack was different size when exiting"; either way the stack is then emptied.

Once the level is lost (`GAME_STATE_LEVEL_LOST`, value 4 in the game-state enumeration at
`references/Onslaught/game.h:42-54`), no script code runs again. Every entry point (the built-in events, the timer and
every resume) checks the game state and, if the level is lost, throws away the values it was about to use instead of
running. A script that is suspended when the level is lost therefore never continues.

Evidence: MEASURED (static) — `CVM::Run`, `CVM::CallEvent`, `IScript::Init`, `IScript::Ready`, `IScript::Hit`,
`IScript::HandleEvent`, `IScript::~IScript`, and the pinned `game.h` for the state numbering. No runtime capture of a
run cut off by the instruction limit.

## How a native is called

A command in a script compiles to a call instruction whose operand carries three things: which native (an index into
the 144-entry [command registry](mission-script-command-registry.md)), how many arguments the call site pushed, and
whether the native returns a value. The instruction does the following (`CInstructionOP_CALL::Execute`):

1. It pops the arguments off the operand stack into one shared global argument array (the last argument pushed is the
   last array slot).
2. If the script object's current target thing is empty, it logs "FATAL ERROR: Can't call function '`<name>`' on NULL
   object", pushes the integer 0 in place of a result, discards the arguments and does not call the native.
3. Otherwise it calls the native as a method of the script object with three arguments, in this order: the argument
   array, the argument count and a pointer to a result slot. The count is the call site's, not the registry's; the
   natives index the array directly and do not check it. The shared array has room for 7 values (the decompilation's
   `gScriptFunctionArgs`, sized to the registry record's seven type slots), and the call instruction does not compare the call
   site's count with that size, so a call site that pushed more than 7 arguments would write past the array. No shipped
   script is known to do so; none was checked.
4. It deletes the argument values, so a native that wants to keep one must clone it.
5. It delivers the result. A native whose call site expects a value but left the result slot empty logs "ERROR: function
   '`<name>`' was expecting return value!" and pushes nothing. A native whose call site expects no value pushes the
   integer 1 as a placeholder, which the statement's remove-top instruction then discards; if such a native returned a
   value anyway it logs "ERROR: script function '`<name>`' returned unexpected value" and the value is lost.
6. It sets the script object's current target back to the default thing.

Two consequences matter to script authors. First, the current-target mechanism is how `thing.Command()` works: a
separate pointer instruction stores the receiver, and the very next native call acts on it and then reverts. Most
natives act on that thing without checking its type, and the checks they do make are listed in the
[command signatures and behaviour](mission-script-registry-corrections.md). Second, a native that suspends the script (the wait
commands) cannot deliver its result to the live operand stack, because that stack is emptied when the run ends. The
call instruction therefore pushes the result or placeholder onto the saved copy's stack when the stop flag is set, so
the resumed script finds it.

The registry record for each native holds, in the decompilation's table, the command name, its declared argument count,
whether it returns a value, up to seven declared argument types, a return type and the handler. The declared counts and
types are listed in the [command signatures and behaviour](mission-script-registry-corrections.md); this page does not claim that
the interpreter enforces them at run time, and the call path above does not.

Evidence: MEASURED (static) — `CInstructionOP_CALL::Execute`, `CInstructionOP_POINTER::Execute`, the `gScriptFunctions`
table, and `CVM::Run`.

## The built-in events

A compiled script has 13 event slots. Each holds the entry point of a handler, or nothing. Eight are used by the game:
0 init, 1 arrived, 2 timer, 3 died, 4 hit, 5 started_dying, 6 ready and 7 shutdown (slots 8 to 12 are placeholders no
code raises). The names are the ones the decompilation gives the table; they match the lifecycle callbacks written in
mission scripts. Raising an event for a slot with no handler does nothing: the call returns at once and discards the
event's argument. Before the first event a script object ever runs, the compiled file-scope initialisation code (the
`vars` defaults) runs once, when a flag in the compiled script is set (`CVM::CallEvent`; the decompilation leaves the flag
unnamed, and it is read from the compiled file). INFERRED: the flag is set when the file has such initialisation code;
no compiled script was checked for it.

| Slot | Event | Raised by | Argument |
| --- | --- | --- | --- |
| 0 | `init` | the thing's `INIT_SCRIPT` event, queued for the next frame by `SetScript` when the script object is created | none |
| 6 | `ready` | the thing's `READY_SCRIPT` event. For a thing that is not a unit, queued for the next frame by the `init` handler (`CComplexThing::HandleEvent`). For a unit, queued by its AI: when the AI is built for a unit that has a script and was not released by a spawner, and when a spawned unit stops following its emitter's path (`CUnitAI`'s constructor and its follow-emitter handler) | none |
| 1 | `arrived` | the end of a path followed by `FollowWaypoint` (not `FollowWaypointWait`) | the second `FollowWaypoint` argument, as an integer |
| 2 | `timer` | the script's own timer message, scheduled by `SetTimer` | none |
| 3 | `died` | see the list after the table: each raiser deletes the script object right afterwards | none |
| 4 | `hit` | `CComplexThing::Hit`, when the other thing is a complex thing and the script exists; also relayed to a squad's script when one of its members is hit (the squad's member-hit method, called from `CUnit::Hit`) | the other thing |
| 5 | `started_dying` | the die process of features and of units. Other complex things do not raise it: their die process schedules shutdown first, which deletes the script object | none |
| 7 | `shutdown` | the thing's `SHUTDOWN` event, only while the game state is at most "playing" and only if the script object still exists | none |

Notes on the table:

- `hit`, `arrived` and `timer` are skipped, not queued, if the interpreter is already running when they reach the
  script (`IScript::Hit`, `IScript::Arrived`, and the timer case of `IScript::HandleEvent`). Whether that can happen in
  play is open (see the end).
- `died` is raised from these places, and every one of them deletes the script object straight after raising it:
  `CComplexThing::AddShutdownEvent` (which `CThing::StartDieProcess` reaches for a plain complex thing that has no die
  process of its own); `CUnit::Remove`; `CBuilding::HandleEvent`, on the event that `CBuilding::StartDieProcess`
  schedules for the next frame when the building has a script (`CHiveBoss::HandleEvent` has the same body and the linker
  folds the two into one function); `CBattleEngine::StartDieProcess`; and the explode path of `CMine`. A search of the
  decompilation for calls of `IScript`'s `Died` found these and no others.
- Because `died` deletes the script object, a thing that dies the ordinary way never raises `shutdown`; `shutdown`
  is reached when something schedules the thing's `SHUTDOWN` event while the script object is still alive, for example
  the `Shutdown` command.
- A unit gets `init` from the thing's own scheduling and `ready` from its AI, as the table says, so a unit built
  without a `CUnitAI` never raises `ready`. The order of a unit's `init` and `ready` inside one frame depends on when each
  event was queued and is open: nobody has traced it for a shipped unit. The [level 100 construction order](../level100-construction-order.md)
  lists the first-frame events things get when a level is built.
- The built-in events are separate from named events. `PostEvent("name")` schedules a named event for the next frame; its
  listeners are the `event("name")` functions registered at `init`, and the match is an exact, case-sensitive string
  comparison. If no listener has registered any event at all the game logs "No listeners for posted event" (except for
  `game playing`).

Nothing in the shipped game uses `arrived` or `timer`. In the maintainer's parse of every compiled mission-script
object in the shipped game, no object has a handler in either slot, no event function listens for those names, and no
loose mission script calls `SetTimer` (a private census, `<maintainer evidence>/`; reproducible only with the
retail data, which this repository does not carry). The two events and the commands that raise them are therefore
mechanism without any shipped use.

Evidence: MEASURED (static) — `CComplexThing::SetScript`, `CComplexThing::HandleEvent`,
`CComplexThing::AddShutdownEvent`, `CComplexThing::StartDieProcess`, `CComplexThing::Hit`, `CFeature::StartDieProcess`,
`CUnit::StartDieProcess`, `CUnit::Remove`, `CUnit::Hit`, `CBuilding::StartDieProcess`, `CBuilding::HandleEvent`,
`CBattleEngine::StartDieProcess`, `CUnitAI` (constructor and follow-emitter handler), the `IScript` notification methods,
`CVM::CallEvent`, `CScriptEventNB::PostEvent`. For who raises each event, a search of the decompilation's source for every
call of the `IScript` notification methods (`Init`, `Ready`, `Arrived`, `StartedDying`, `Hit`, `Died`, `Shutdown`) found the
callers named above, and `Arrived` is called only from the waypoint-following code described in
[follow waypoint commands](follow-waypoint-commands.md). A search finds only what the decompilation contains.
MEASURED (corpus) for the last paragraph, from private receipts.

## Commands that only schedule an event

Several natives do nothing themselves; they queue an event for a later frame. Event numbers are reused across
unrelated receivers, so a number never identifies a recipient by itself.

| Command | What it queues | Recipient |
| --- | --- | --- |
| `Die` | start-die-process, next frame | the thing the command acts on |
| `Shutdown` | thing shutdown, next frame | the thing the command acts on |
| `PostEvent` | a named event, next frame | the named-event hub, which runs every listener of that name |
| `SetTimer` | the script's timer message, after the given number of seconds | the script object, which raises `timer` |
| `Pause` | the script's resume message, after the given number of seconds | the script object |
| `FollowWaypoint` / `FollowWaypointWait` | the script's follow-step message, next frame | the script object |

The script object handles three messages, numbered 2000, 2001 and 2002: 2000 runs one waypoint step, 2001 resumes a
suspended script and 2002 raises `timer`. The thing's own 2000 (shutdown) and 2001 (`INIT_SCRIPT`) are different
messages, sent to a different recipient, and the game's 2001 (finished pre-run) is a third.

An event is scheduled through the event manager, which runs it on a frame boundary. An event due within about a twentieth of
a second runs next frame; later ones are placed by frame. The [event scheduler page](../../engine/world/event-manager-scheduler-semantics.md)
gives the rule. A `Pause` of a few frames or less is therefore a next-frame resume, and a longer one is quantised to
the manager's frame buckets.

Evidence: MEASURED (static) — `IScript::Die`, `IScript::Shutdown`, `IScript::PostEvent`, `IScript::SetTimer`,
`IScript::Pause`, `IScript::HandleEvent`, `CEventManager::AddEvent`; pinned `thing.h` and `game.h` for the unrelated
2000 and 2001 numbers.

## Suspending a script: the saved interpreter copy

All of the wait commands suspend a script the same way. The command copies the whole live interpreter state into a new
saved copy, adds the copy to the script object's list of saved copies and sets the interpreter's stop flag. The run
then ends after the current instruction. The copy holds: the compiled code in use, the program counter, the whole
operand stack (up to 128 values), the compare flag, the stop flag, the stack depth at the start of the call and the
local-call depth. The live operand stack is then emptied without deleting the values, which now belong to the copy.

The saved program counter is already past the call instruction, because the interpreter increments it before it
executes the instruction. A resumed script therefore carries on with the instruction after the wait command.

To resume, the owner restores the copy into the live interpreter (the stack values move back; the "running" flag is
cleared), removes it from the list, deletes it, and continues the run from the saved counter. The run restarts with the
compare flag, the local-call depth and the stop flag reset to zero, whatever the copy held. If the level is lost at
that moment the owner empties the stack instead.

The wait commands differ only in what resumes the copy:

| Command | Suspends | Resumed by |
| --- | --- | --- |
| `Pause(seconds)` | yes | the resume message (2001), scheduled for now plus the delay, with the copy as its data |
| `PlayCharMessageWait`, `PlayPCharMessageWait` | yes | the resume message, scheduled 0.05 s after the message box finishes the message |
| `PlayAnimationWait` | yes | the thing finishing the animation (`FinishedPlayingAnim`) |
| `FollowWaypointWait` | yes | the end of the path (see [follow waypoint commands](follow-waypoint-commands.md)) |

### Pause

`Pause(seconds)` reads the delay as a float, saves the copy, sets the stop flag and queues the resume message at the
current event time plus the delay. The resume handler restores the copy and continues it. Nothing but the clock resumes it.

Runtime observation (MEASURED, runtime, one case): a time-travel trace of a copied runtime of a Level 100 play-through,
on an executable that differs from the pristine specimen only in one four-byte field, recorded one call of the `Pause`
native. Specimen for this observation: the maintainer's patched lab copy of `BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`, which differs from the pristine specimen in exactly
four contiguous bytes (checked now by byte comparison); the trace's own executable was not hashed when it was recorded, so
this is the copy that fits the description, not a proved identity. At its entry the interpreter's stop flag was clear and the script object's list of saved copies was empty; at
its return the flag was set and the list held one copy; the return went to the interpreter's call instruction. The
trace file is not retained and the receipts are held privately (`<maintainer evidence>/`); the trace did not decode the
delay or the scheduled time, so those rest on the static reading above. In the maintainer's corpus count the Level 100 scripts
contain 35 authored `Pause` calls, for example a half-second pause that separates setting a zone as reached from unsetting it.

### The message waits

`PlayCharMessageWait` and `PlayPCharMessageWait` save the copy and stop the script, then take a scheduled-event record
from the event manager, fill it with the resume message (delay 0.05 s, recipient the script object, data the copy) and
attach it to the message they queue in the message box. They are the plain forms plus that record: the two forms differ
only in that the `P` form passes a script-supplied priority (a fourth script argument) where the other uses a fixed
priority of 10. The message box schedules the attached record when it finishes showing the message (its finish event),
so the script resumes 0.05 s after the message ends, and the box starts the next message 0.2 s after that.

Two silent failures follow from the code. If the event manager has no free scheduled-event record, the command returns
after saving the copy and nothing ever resumes it. If the game has no message box, no message is queued, so the record is never scheduled and the
script stays suspended. Neither is known to happen in shipped play.

### The animation wait

`PlayAnimationWait(name, resetFrame, forceLooped)` has no wait argument: the wait is the command itself. Its second and
third arguments are the arguments of the thing's animation call. The pinned `thing.h` names them `reset_frame` and
`force_looped` (`references/Onslaught/thing.h:284-285`). The command:

1. logs "Called PlayAnimWait on the non base script object" if the target thing's own script is not this script
   object, and carries on;
2. returns at once, without suspending, if the thing has no render object or mesh;
3. deletes any earlier animation copy this script object was holding, so a second animation wait before the first
   finishes drops the first suspended script for good (there is one animation slot per script object);
4. starts the animation by name, saves the copy and stores it in the animation slot.

The script resumes when the thing's animation reports that a non-looping animation reached its end. The animation
update calls the thing's "finished playing" function only when the animation is neither a looping mode nor forced to
loop, so `forceLooped` true, or a looping animation, never resumes the script. Many classes override that function, and the animation wait resumes only if the override ends in the base function
(`CComplexThing::FinishedPlayingCurrentAnimation`, the one that tells the script):

- Four classes pass the notification on for animations they do not handle, and consume the ones they do: `CUnit` for
  deploying, undeploying, pre-fire, firing and post-fire; `CBuilding` for opening, closing, shutting and unshutting;
  `CComponent` for hit, retract, Activate and Deactivated (the names it compares, ignoring case; a plain "deactivate" is not one of them); and `CBoat` for deploying and undeploying.
- Eleven classes never call the base function at all, for any animation, so a `PlayAnimationWait` on a thing of one of them
  never resumes: `CBattleEngine`, `CCarver`, `CCannon`, `CFenrir`, `CDiveBomber`, `CGroundAttackAircraft`, `CDropship`,
  `CGillMHead`, `CInfantryUnit`, `CPlane` and `CSentinel`. Each override handles its own animation chain (for example `CFenrir` starts its shutdown
  when its die animation ends, and `CCannon` switches from its activate animation to its active one) and returns without
  notifying the script.

A wait on an animation that its class consumes therefore does not resume.

Evidence: MEASURED (static) — `CVM::operator=`, `CVM::Run`, `IScript::Pause`, `IScript::PlayCharMessageWait`,
`IScript::PlayPCharMessageWait`, `IScript::PlayAnimationWait`, `IScript::FinishedPlayingAnim`,
`IScript::HandleEvent`, `CMessageBox::HandleEvent`, `CAnimation::Process`, `CAnimation::SetAnimMode`,
`CComplexThing::FinishedPlayingCurrentAnimation` and the class overrides named (a search of the decompilation's source for
`FinishedPlayingCurrentAnimation` lists every override; only the four named first call the base). MEASURED (runtime) for the one `Pause`
call only. The overrides' effect on the animation wait is a static reading: no captured run has an animation wait on a
consuming class.

## Open questions

| Question | Cheapest check |
| --- | --- |
| Can `hit`, `arrived` or `timer` be raised while the interpreter is running (so the guard drops them)? | Break on the guard in a copied runtime during a level with scripted hits and a path-following unit; or search for a call path that runs a script inside a native |
| Does any shipped script wait on an animation whose class consumes the finished notification, leaving the script suspended? | List each shipped `PlayAnimationWait` call's animation name against the class of its target (the [animation usage census](../../formats/cmsh-animation-usage.md) lists the names), then run the matching level |
| Does a wait inside a local call behave as the code reads? The run resets the local-call depth to zero on every resume, so a return from the local function after a resume would end the run instead of returning to the caller. The maintainer's census of shipped compiled scripts found no local-call instruction, so shipped content does not exercise it | Compile or patch a script that waits inside a local call in a copied runtime and watch the return |
| Does the event manager ever run out of scheduled-event records during a message wait? | Read the record pool size and its high-water mark in a copied runtime during the busiest message level |
