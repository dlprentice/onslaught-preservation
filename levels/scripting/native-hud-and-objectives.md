# Script-driven HUD: objective markers, part flashing and the text slots

Status: active — static behaviour of nine natives that drive the HUD; no runtime capture
Last updated: 2026-11-11 (new document)
Evidence: MEASURED — the handlers and the HUD, world and thing code they call are functions of onslaught-decomp that the decompilation lists as matching the retail bytes, read statically; the six `HUD_*` and six `VARIABLE_*` constant values are read from the retail script header `onsldef.msl`; SOURCE — the pinned Onslaught source for the base thing class; INFERRED — what appears on screen; UNKNOWN — the open questions at the end.
Summary: what `SetObjective`, `UnsetObjective`, `IsObjective`, `HighlightHudPart`, `UnHighlightHudPart`, `InitVariable`, `SetVariable`, `GetVariable` and `ShutdownVariable` change, and which part of the HUD reads the change: objective markers on the compass and the battle-line map, a two-state blink on six HUD parts, and four text rows in the objective panel whose six display styles are the `VARIABLE_*` constants.
Specimen: pristine Steam `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` (the file onslaught-decomp matches).

These nine natives are part of [the natives overview](native-behaviour.md), which explains how a native is called, how the
evidence is gathered and what the "shipped use" counts are. Function names are those of
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) at commit `9759593`; each line link below points into
that commit, whose
[`docs/check/matched.tsv`](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/docs/check/matched.tsv)
lists every function cited here as matching the retail bytes. The names `_312_FORSETI_BUILDING` and similar in the
[script examples](msl-scripting.md) are text ids; the [HUD overlay contract](../../engine/frontend/hud-frontend-overlay-static-contract.md)
says that the registry alone does not prove visible flashing or variable display, and this page supplies the static
reading of both. Nothing here was observed on screen.

## Objective markers

`SetObjective()` and `UnsetObjective()` call `CThing::SetObjective(TRUE)` and `(FALSE)` on the script's current target,
with no type gate ([`IScript.cpp` L1231](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1231)).
`CThing::SetObjective` ([`thing.cpp` L269](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/thing.cpp#L269);
the same function is at `references/Onslaught/thing.cpp:269-287` in the [pinned source](../../README.md#how-to-read-a-finding))
works on two things together: the thing's "marked objective" flag and its membership of the world's objective set
(`CWorld::GetObjectiveThingNB`). Setting adds the thing to the set and raises the flag only if the flag is not already
raised; clearing removes it and lowers the flag only if the flag is raised. So both natives are idempotent. A complex thing
that shuts down unmarks itself (`CComplexThing::Shutdown`, `references/Onslaught/thing.cpp:644`), so a script need not
unmark a thing that dies.

`IsObjective()` returns the flag. A complex thing reports it; the base thing class always reports false
(`references/Onslaught/thing.h:139` and `:274`).

Two HUD routines walk the objective set:

- `CDXBattleLine::Update` adds one overlay point per objective to the battle-line map, in yellow
  ([`BattleLine.cpp` L15](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/BattleLine.cpp#L15)).
- `CCompass::Render` draws an objective marker sprite on the compass ring for each objective, at the bearing of the thing
  from the Battle Engine, relative to the engine's yaw
  ([`Compass.cpp` L234](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/Compass.cpp#L234)).

That a marker appears on screen for a marked thing is inferred from those two loops. The set is separate from the
mission's objectives as the player reads them: completing or failing an objective is done by
`PrimaryObjectiveComplete` and its relatives, which are not covered here.

Shipped use: `SetObjective` 298 sites in 221 files across 68 levels, `UnsetObjective` 250 sites in 217 files across 59
levels, `IsObjective` 9 sites in the level 22 and 100 target-zone and firing-range scripts.

## HUD part flashing

The HUD keeps a state for each of six parts, `CHud::mPartState`, with three values: off (0), on (1) and flashing (2).
The part numbers are the constants of the retail script header `onsldef.msl`, which the decompilation's `EHudPart`
follows:

| Constant | Value | Read by |
| --- | ---: | --- |
| `HUD_HEALTH_BAR` | 0 | `CDXCompass`, which draws the health and energy bars |
| `HUD_ENERGY_BAR` | 1 | `CDXCompass` |
| `HUD_COMPASS` | 2 | `CDXCompass::Render`: the compass ring |
| `HUD_BATTLE_LINE_MAP` | 3 | `CHud::Render` (see below) |
| `HUD_RADAR` | 4 | `CHud::RenderWeaponPanel`: the radar outline |
| `HUD_CURRENT_WEAPON` | 5 | `CHud::RenderWeaponPanel`: the weapon charge display |

- `HighlightHudPart(part)` stores 2 in the part's state and `UnHighlightHudPart(part)` stores 1
  ([`IScript.cpp` L1210](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1210)).
  Neither checks that the index is one of the six, and neither touches a thing, so no receiver is needed. A
  highlight is therefore a blink and an un-highlight returns the part to normal; neither can hide a part.
- `CHud::IsComponentVisible` answers false for off, true for on and, for flashing, the current flash phase
  ([`Hud.cpp` L2195](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/Hud.cpp#L2195)).
  `CHud::Render` recomputes the phase every frame as the whole quarter-seconds of the game time, taken modulo 2
  ([L2063](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/Hud.cpp#L2063)),
  so a flashing part is drawn for a quarter of a second and hidden for the next, twice a second.
- `CHud::Render` also writes the battle-line map's state itself every frame, to on while the message box has no current
  message and to off while one is shown, except when the state is already flashing, which it leaves alone. A script that
  highlights the battle-line map therefore keeps it visible through messages, until it un-highlights it, and the next
  frame's write then follows the message box again.
- `CHud::Reset` sets all six parts to on, so a flash does not survive a HUD reset
  ([L102](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/Hud.cpp#L102)).
  Within the decompilation the only writers of the array are the HUD's constructor, `Reset` and `Render`, and these two
  natives.

Shipped use: 13 sites of each native, in two scripts: the level 22 script (6 each) and the level 100 script (7 each).
They highlight a part, show a tutorial message and un-highlight it, for example `HighlightHudPart(HUD_COMPASS)`.

## The four text slots

`InitVariable`, `SetVariable`, `GetVariable` and `ShutdownVariable` are named like a script variable store. They are
not one. The world object holds four text slots, and the four natives are thin wrappers over `CWorld::AddText`,
`SetTextTime`, `GetTextTime` and `RemoveText`
([`IScript.cpp` L1337](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/MissionScript/IScript.cpp#L1337),
[`world.cpp` L967](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/world.cpp#L967)).
The rows they feed are drawn by the HUD in its objective panel at the right edge of the screen.

Each slot holds a style (0 means the slot is free), a text id, the localised string for that id, a time, a goal and the
game time at which the slot was claimed (`CWorld::mTextState` and its neighbours,
[`world.h` L216](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/world.h#L216)).
The slots start free, and both the world's constructor and `CWorld::Clear` free them.

| Native | Call | What happens |
| --- | --- | --- |
| `InitVariable` | `InitVariable(textId, style)` | Takes the first slot whose style is 0: stores the style and the text id, looks up the localised string for the id, sets the time and goal to 0 and stamps the current game time. When all four slots are in use the call is dropped without a message. A style of 0 leaves the slot looking free. |
| `SetVariable` | `SetVariable(textId, value, goal)` | For every slot whose text id matches: if its style is 3 (the countdown), stores *the current game time plus `value`* as the time and ignores `goal`; for any other style stores `value` as the time and `goal` as the goal. It matches on the id only and does not check that the slot is in use. |
| `GetVariable` | `GetVariable(slot)` | Returns a float for slot number 0 to 3, which is an index, not a text id and not checked against the range: for style 3 the stored time minus the current game time, never below 0, for any other style the stored time. |
| `ShutdownVariable` | `ShutdownVariable(textId)` | Sets the style of every slot with that id to 0, which frees it for the next `InitVariable`; the other fields are left as they were. |

The text id is a text constant such as the `_312_…` ids of the level scripts, resolved by the game's string table. A script
that wants a fifth row at the same time gets nothing and no error.

### The six styles

The style is the second argument of `InitVariable`. The constants are those of the retail script header `onsldef.msl`;
the formats are those of the HUD routine that draws the rows
([`Hud.cpp` L749](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/Hud.cpp#L749)),
in which the decompilation has not yet settled a descriptive name. A row is drawn only while its slot's style is not 0,
and only if its text fits the panel's current width.

| Style | Constant | What the row shows |
| ---: | --- | --- |
| 1 | `VARIABLE_NUMBER` | the stored time as a whole number |
| 2 | `VARIABLE_NUMBER_AND_THRESHOLD` | the number and, beside it, the goal in brackets; the pair flashes when the number is within 1 of the goal |
| 3 | `VARIABLE_TIMER` | the remaining time as minutes and seconds, counting down: `SetVariable` made the stored time a deadline, and `GetVariable` and the row both read deadline minus now |
| 4 | `VARIABLE_PERCENTAGE` | the stored time as a whole number; the format string ends in a lone percent sign, and whether the game prints it is not checked |
| 5 | `VARIABLE_PERCENTAGE_AND_THRESHOLD` | the number and the goal in brackets, as style 2; the pair flashes when the number is within a tenth of the goal |
| 6 | `VARIABLE_TIME` | the stored time as minutes, seconds and two decimals of a second |

The panel opens while any slot is in use and closes when none is
([`Hud.cpp` L749](https://github.com/dlprentice/onslaught-decomp/blob/9759593ee6f6103f936080ac0435275e6ce9e06a/src/Hud.cpp#L749)).
The timer style is the only one for which `SetVariable`'s value means "seconds from now"; for the others it is a value to
show. That is why `VARIABLE_TIMER` is a style of this family and not a use of `SetTimer`, which schedules a script event
(see [the natives overview](native-behaviour.md#the-natives)).

Shipped use: `InitVariable` 77 sites in 41 files across 32 levels, `SetVariable` 146 sites in 45 files across 36 levels,
`ShutdownVariable` 26 sites in 18 files across 14 levels, `GetVariable` none. The
[script examples](msl-scripting.md#variables-and-ui-display) show the usual pairing: an `InitVariable` in `init()` and a
`SetVariable` each time a count changes.

## Open questions

1. **Nothing was seen on screen.** The marker, the blink, the rows and their formats are read from code. Falsifier: run a
   copy of a level whose script sets an objective, highlights `HUD_COMPASS` and initialises one row of each style, and
   record the frames.
2. **Style 4's percent sign.** The row's format string ends in a lone percent sign, which a C formatting routine may drop
   or print. Falsifier: one `VARIABLE_PERCENTAGE` row, read on screen.
3. **Rows that are drawn only if they fit.** The HUD skips a row whose text is wider than the panel's current width;
   whether that happens for the shipped texts in any language is not checked.
4. **The panel routine's name.** The decompilation keeps an address-based placeholder name for the routine that draws the
   rows; earlier documents in this repository use other descriptive names for it. This page does not settle the name.
5. **Who else writes the world text slots.** Within the decompilation the only callers of the slot-writing functions are
   the three natives that write, and only the world's constructor and `CWorld::Clear` free slots otherwise; the five
   left-out source files have not been checked.
