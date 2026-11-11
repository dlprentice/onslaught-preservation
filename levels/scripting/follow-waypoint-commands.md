# FollowWaypoint and FollowWaypointWait

Status: active — subsystem description from static evidence; extends the waypoint path contract
Last updated: 2026-11-11 (new page)
Summary: what the two path-following script commands do: how the path name is looked up, what each command checks and
logs, what order it gives the unit, what ends a followed path and what happens then, and what is the same on the PS2 and
Xbox builds. Path loading, the start node, the arrival radii and the per-level routes stay in
[named waypoint paths](../../mechanics/waypoint-paths.md).
Evidence: MEASURED (static) — the functions of the byte-matching decompilation,
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) (commit `9759593`): `IScript::FollowWaypoint`,
`IScript::FollowWaypointWait`, `IScript::UpdateWaypointFollowing`, `IScript::HandleEvent`, `CWaypointManager::FindNearest`,
`CGuide::GoToPoint`, `CUnit::GoToPoint`, `CAirUnit::GoToPoint`, `CNormalSquad::GoToPoint`, `CUnitAI`. Pinned source
is Stuart Gillam's [public fork](https://github.com/dlprentice/Onslaught/tree/c3d8ac464259942b83fa8aa7f867c856e77b734d)
(`thing.h`), which declares the base `GoToPoint` and `Stop` but contains no mission-script runtime. The "Other builds"
section is MEASURED (static) from private receipts. No runtime capture of either command is cited.
Specimen: pristine PC retail `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
the executable the decompilation matches.

The script runtime that these commands rely on (suspending a script, the stop flag, the event numbers 2000 and 2001) is
described in [mission script runtime](script-runtime-events-and-waits.md). Waypoints themselves, their file format and
height adjustment, and the route each Level 100 and World 110 unit takes, are in
[named waypoint paths](../../mechanics/waypoint-paths.md); this page does not repeat them.

## Name lookup

Both commands find their first node with `CWaypointManager::FindNearest(name, position)`:

- It walks every loaded path in load order and takes the **first** path whose name equals the requested name,
  comparing without regard to case. A second path with the same name is never consulted.
- Within that path it returns the node nearest to the position, by squared 3D distance, with a strict "smaller than"
  against a running best that starts at 9,999,999 (a squared distance, so about 3,162 units). A tie therefore keeps the
  earlier entry in the path's list, and a node whose squared distance is not below that starting value is never chosen. The path's list order and the start-node results are in
  [named waypoint paths](../../mechanics/waypoint-paths.md#following).
- An unknown name, or a path with no usable nodes, returns nothing.

The position is that of the **thing the command acts on**, which is the script's own thing unless the call names another
thing first (the `thing.Command()` form). It is not necessarily the thing that owns the script.

## The two commands compared

| | `FollowWaypoint(name, value)` | `FollowWaypointWait(name)` |
| --- | --- | --- |
| Declared arguments | a string and an integer | a string |
| Suspends the script | no | yes, until the end of the path |
| Unknown path | logs "Cant find waypoint path '`<name>`'" and returns; no order is given | logs "FATAL ERROR: Cant find waypoint path '`<name>`'" and returns without suspending |
| Target is not the script's own thing | gives the go-to order to the nearest node, but starts no following: nothing steps the unit along the path, and nothing is logged | logs "FATAL ERROR:  Cant Follow waypoint way for other object" and returns without suspending; no order is given |
| Called while a path is already being followed | replaces the current node with the new nearest one, clears the waiting flag, and does not start a second step cycle (one is already running) | returns at once without logging and without suspending: the script carries on immediately |
| What the integer does | stored, and handed to the `arrived` event | not applicable |
| End of the path | the unit's stop function is called and the `arrived` event is raised with the stored integer | the unit's stop function is called and the script resumes after the command; no `arrived` event is raised |

Notes:

- The "waiting" flag belongs to `FollowWaypointWait`. A `FollowWaypoint` call from another handler of the same script
  while a `FollowWaypointWait` is pending clears that flag, so at the end of the new path the pending script is **not**
  resumed; it stays suspended until its script object is destroyed. This is a static reading with no capture.
- `FollowWaypointWait` called while a path is already being followed returns immediately, so an author who expects it to
  block gets no wait and no warning.
- The stored integer is written before the target check, so a `FollowWaypoint` aimed at another thing still overwrites
  the script's stored value.

Evidence: MEASURED (static) — `IScript::FollowWaypoint`, `IScript::FollowWaypointWait`, `IScript::UpdateWaypointFollowing`.

## What the order does

Each command gives the unit a go-to order for the nearest node. The step cycle then runs once a frame (message 2000,
re-queued for the next frame each time): it measures the flat distance from the script's own thing to the current node
and, when that is below the arrival radius, takes the node's own target as the next node and gives a new go-to order
for it. It issues no order between nodes. The radii, the self-link check, and what each unit class does when the path
ends are in [named waypoint paths](../../mechanics/waypoint-paths.md#following).

What a go-to order does depends on the class of the thing it is sent to:

| Thing | What `GoToPoint` does |
| --- | --- |
| A plain thing | nothing: the base function is empty (`references/Onslaught/thing.h:293`) |
| A unit | passes the point to the unit's guide, if the unit has one |
| An aircraft (planes and dropships) | first limits the point's height so that it is no lower than the unit's minimum altitude above the ground or the sea, whichever is higher, then passes it to the guide |
| A normal squad | stores the point as the squad's destination; what the squad does with it is not covered here |

The guide stores the point as its destination and goes into its "go to a point" mode, with one exception: if the unit's
AI is in its mode 2 and the order does not carry the override flag, the order is ignored. Neither follow command
passes the override flag. The AI's modes are 0 (follow its own waypoints), 1 (fight) and 2 (follow an emitter: set for a
unit released by a spawner that has an emitter type, with a release time ten seconds ahead). The unit AI's own waypoint
following is separate from these commands: both end in the same go-to order, and nothing here shows how the two interact
when a script and the AI both direct one unit.

How a guide turns its destination into movement depends on the unit class. A ground vehicle's guide plans a path over
the unit's occupancy grid and follows its cells; the steering rules are not described here.

Evidence: MEASURED (static) — `CThing::GoToPoint` in the pinned `thing.h`; `CUnit::GoToPoint`, `CAirUnit::GoToPoint`,
`CNormalSquad::GoToPoint`, `CGuide::GoToPoint`, `CUnitAI` (modes and the follow-emitter event).

## The arrived event

At the end of a path followed by `FollowWaypoint`, after stopping the unit, the script object raises `arrived` with the
stored integer wrapped as an integer value. The raise is skipped if the interpreter is already running or the level is
lost. The integer has no authored name in anything this repository holds. In the maintainer's census of the shipped
compiled scripts, `FollowWaypoint` is called at 19 sites with the second argument 0 at 13 of them and 1 at 6; the 1
sites are in loose scripts of levels 600, 731, 732, 741 and 742. No shipped
script has an `arrived` handler (see [mission script runtime](script-runtime-events-and-waits.md#the-built-in-events)),
so the integer, and the event, have no effect on any shipped level.

Evidence: MEASURED (static) for the raise, `IScript::UpdateWaypointFollowing` and `IScript::Arrived`; MEASURED (corpus)
for the call-site counts, from private receipts that need the retail data.

## Other builds

The arrival test is the same on the PS2 and Xbox builds that were read. In each, only the flat distance is computed,
the radius is 2 for the default, 4 for a non-unit with an unnamed type flag and the unit class's own radius (2, 5 or 8)
for units, and a node counts as reached only when the distance is strictly below the radius, so equality does not end a leg. Neither
command supplies a radius. The three Level 100 radii (2, 5 and 8) match on every build read. One difference remains:
when a node's next node is itself, the PC and PS2 builds log the self-link error and end the path, while the Xbox builds
end the path without logging.

| Build | SHA-256 of the program |
| --- | --- |
| PS2, German demo | `5700b5d0b39554e49afe65e079ad8109fe6688c2aa5e6f0e0ed5afcefd034584` |
| PS2, Europe | `87cb89b020cf107b3ba4612ac6bc86ed3fcbd6dd985e2cd3978bf897be96b655` |
| PS2, USA | `4cfed76f0b0cdf84377a4d5b1613fd197c27be9a3814743590fecba22ba4e166` |
| Xbox, USA retail | `e8adc9d6940ae1a5fa9fac0fe28e398bfffd01758c2740a536b930c37c83985b` |
| Xbox, Europe retail | `266387500a056752f45301a03772fa57fdc747cf0eda46d39bbb915c5db2f234` |
| Xbox, Issue 11 demo disc | `ac07835e4b8cf38312e672cb7dc17f28a732abbc05a5e4f1760aaa78a5377ed9` |

Evidence: MEASURED (static) — a reconstruction of the arrival-test function from each of the six programs (the PS2
programs are the canonical ELF files; the Xbox programs are the XBE files), compared with the PC function. The
receipts are held privately (`<maintainer evidence>/`) and this page did not reproduce them. The Xbox build's retained
self-link message has no pointer to it in any of the three images, which is why it is read as unused.

## Open questions

| Question | Cheapest check |
| --- | --- |
| Is `FollowWaypoint` ever called on another thing in shipped scripts (the form that gives one order and no following)? | Scan the shipped compiled scripts for calls of the command that are preceded by a receiver instruction |
| Do a script and the unit's own AI both direct one unit at the same time, and which order wins? | In a copied runtime, send a unit with its own waypoint AI a script path and log the guide's destination each frame |
| Does a pending `FollowWaypointWait` really stay suspended when a later `FollowWaypoint` replaces the path? | Script both calls from two handlers in a copied runtime and watch whether the first script resumes |
