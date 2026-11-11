# Cheat codes

Status: active — the retail cheat table and what each cheat does
Last updated: 2026-11-11 (autosave and screen-dump effects and the index 2 search corrected; migrated from the Toolkit's frozen cheat note and rewritten as a subsystem page; every effect re-read against the decompilation)
Summary: the retail PC build has six cheats, each switched on by a code word inside the name of the save that is loaded;
this page says what each one changes, how far the evidence for each goes, and how they differ from the four names in
the internal source.
Evidence: MEASURED (static) — the matching functions of [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp)
at commit `9759593`, each listed there in `docs/check/matched.tsv` as matching the retail executable byte for byte
(named per section below), read for what they do; SOURCE — Stuart Gillam's published
`FEPSaveGame.cpp` and `game.cpp` at the pinned commit; hand-test reports with no archived capture — MALLOY and TURKEY
(December 2025) and Maladim (March 2026); UNKNOWN — the open questions at the end.
Specimen: pristine Steam retail `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
(see the [retail specimen baseline](../../platforms/pc/retail-specimen-baseline.md)).

A cheat in *Battle Engine Aquila* is not typed in during play. The game looks at the name of the career save that is
loaded and turns a cheat on when the name contains that cheat's code word. The player-facing consequences are three
visible changes (every Goodie available, every level open, a God ON / God OFF line in the pause menu) and three that
no archived run shows working (a free camera, a Goodies-wall developer view and a version display that has no known
effect). The internal source that Stuart Gillam published uses four different code words; the retail table was changed
and extended.

## How a cheat switches on

The check is the function `CFEPSaveGame::IsCheatActive`, which takes the cheat's index and answers yes or no. Its
behaviour, read from the decompilation's matching copy and, for the internal build, from the published source:

- **The code words are stored scrambled.** The retail table holds six rows of 256 bytes. The function recovers a
  code word by combining the first nine bytes of its row with the nine-character key `HELP ME!!`, which sits beside
  the table in plain text, so a plain search of the executable for a cheat name finds nothing. The remaining bytes of a
  row are never read. The function does not write a terminator of its own, so the nine
  recovered bytes must end the word with a zero, which makes a retail code word at most eight characters long.
- **The name is matched as a substring, and case matters.** The function takes the save name, turns each wide
  character into one byte by keeping its low byte (`FromWCHAR`), and asks the C library's `strstr` whether the recovered
  word occurs anywhere in it. So `MyMALLOYSave` counts, `malloy` does not, and one name can carry several code words,
  because every cheat is a separate query.
- **Two things make every cheat true at once.** The function answers yes for every index when the `-autoconfigtest`
  command-line flag is set, and when the runtime all-cheats flag is set (see [The all-cheats state](#the-all-cheats-state)).
  Neither depends on the save name.
- **Which name is checked.** The name is the one held by the front end's save-game page. In the decompilation it is
  written when a save is picked in the directory list (`CFEPDirectory` hands the picked name to `CFEPLoadGame`, which copies
  it to the save-game page) and when a name is typed on the virtual keyboard (`CFEPVirtualKeyboard`). The PC save list is backed by file names
  ([`CPCMemoryCard` backend](../../saves/cpcmemorycard-pc-save-backend-semantics.md)), so a save file whose name contains
  a code word presents that name when it is loaded.
- **The call sites are few and fixed.** In the decompilation's source every call passes a constant index, and the callers
  are `CFEPGoodies::Process` (indices 0 and 5), `CFEPLevelSelect::IsWorldUnlocked` (1), the pause-menu constructor (3)
  and `CGame::ReceiveButtonAction` (4). No call passes index 2. The decompilation's tree holds 5,449 of the retail
  executable's 5,482 functions, all matching; the other 33 are in four files of Microsoft's DirectX SDK sample code that the tree leaves out
  (a fifth left-out source is a data block with no functions; [its README](https://github.com/dlprentice/onslaught-decomp#readme)). So no matched function passes
  index 2, and a caller would have to be in that sample code, which is not where a save-name check would be expected.

## The retail table

| Index | Code word | What it does | Evidence |
| ---: | --- | --- | --- |
| 0 | `MALLOY` | Every Goodie cell on the wall is treated as already viewed, so all are shown unlocked and can be opened. | Static; the display effect also seen with a patched copy; hand-test report |
| 1 | `TURKEY` | The level-select page treats every world as open. | Static; hand-test report |
| 2 | `V3R5IOF` | None known: no caller. | Static (absence) |
| 3 | `Maladim` | Adds a God ON / God OFF line to Controller Options in the pause menu. | Static; hand-test report |
| 4 | `Aurore` | Lets the free-camera button work. | Static only |
| 5 | `latête` (the third character is the Latin-1 letter `ê`) | Makes the Goodies wall show each Goodie's unlock condition. | Static only |

The third character of index 5 is one byte in the table, equal to Latin-1 and Windows-1252 `ê` (U+00EA). It is not the
two-byte UTF-8 form. Because the comparison keeps only the low byte of each character of the name, a name that contains the
character `ê` matches.

## What each cheat does

### `MALLOY`: every Goodie

Read from `CFEPGoodies::Process` and the Goodies page's state lookup (the page draws in `CFEPGoodies::Render`). Each
time the page processes, it asks cheat 0 and stores the answer. While that answer is yes, the lookup that tells the page
a cell's state returns "old", the state of an unlocked Goodie that has been opened, for every cell that maps to a Goodie.
The wall then draws those cells lit, and choosing one loads it. A cell that maps to no Goodie stays unknown.

The same display flag, forced on in a copied executable, produced the unlocked display on the wall in controlled runs
([Goodies gallery display override](../../platforms/patches/goodies-gallery-display-unlock-patch.md)); that observation
used the patch, not the name. Reports of hand testing in December 2025 say the name works in the Steam build; no
capture is archived.

One side effect follows from the same reading. Choosing a cell writes "old" into the career's state for that Goodie
(`set_goodie_state` in the Goodies page source), and under the cheat the cell reads as "old" whatever the career held. So
after the cheat has been used the career in memory can hold Goodies it never earned. Whether that reaches a saved file is
the open persistence question in the [Goodies save contract](../../saves/goodies-system.md#claim-boundary); until a cell
is opened, the [Goodie states](../../saves/goodies-system.md) in the save are untouched.

### `TURKEY`: every level

Read from `CFEPLevelSelect::IsWorldUnlocked`, which the level-select page calls to decide whether a world can be drawn
as open, picked and started. With cheat 1 on, the function returns yes before it looks at the career map. Without it, a
world is open if it is the training world or if one of the links leading to it is complete, as the
[career graph](../../saves/career-graph.md#retail-unlock-gate-steam-beaexe) describes. The check itself writes nothing to the
career (static reading); winning a level while it is on updates the links in the usual way. Reports of hand testing in
December 2025 say every campaign level opened.

### `V3R5IOF`: nothing known

The retail table decodes to `V3R5IOF`. The internal source's entry at this index is `V3R5ION`, with the comment "Show
version number" (`FEPSaveGame.cpp`, lines 543-563 of the [pinned source](https://github.com/dlprentice/Onslaught/blob/c3d8ac464259942b83fa8aa7f867c856e77b734d/FEPSaveGame.cpp#L543-L563)),
and the published source has no caller for it either: its only call to `IsCheatActive` is the Goodies one. The retail
spelling differs in the last letter, and no retail caller is known, so a version display is a hypothesis about the
internal build, not something this page can say retail does. What would settle it is in the open questions.

### `Maladim`: the God item

Read from the pause-menu constructor, which asks cheat 3 while it builds the Controller Options list. When the answer is
yes it adds one item whose label follows player 1's god flag in the career: God ON if it is 1, God OFF otherwise.
The pause menu's item handlers (`CPauseMenu::ButtonPressed` and `CPauseMenu::MenuItemChanged`) call
`CPlayer::SetIsGod` for player 1 when the item is chosen. The cheat does not set the flag
by itself; it only shows the item. The flag lives in the career save and is applied to the Battle Engine when the player
is built, and the whole mechanism, including what it does to damage and energy, is in [God mode](god-mode.md).

Hand testing on 2026-03-15 and 2026-03-29 saw the line appear under Controller Options, saw normal combat damage stop
sticking while it was on, and saw hull already lost stay lost; no capture is archived. Which bar refills on turning the
item on again, and whether water or other hazards bypass the protection, are open questions on the god-mode page.

### `Aurore`: the free camera

Read from `CGame::ReceiveButtonAction`, in the case for the free-camera toggle button. With cheat 4 on, the case switches
the free camera on or off for every player that exists; with it off, the button does nothing. The published source has
no such gate there (`game.cpp`, the `if (1)` in the `BUTTON_TOGGLE_FREE_CAMERA` case, lines 2587-2590 of the
[pinned source](https://github.com/dlprentice/Onslaught/blob/c3d8ac464259942b83fa8aa7f867c856e77b734d/game.cpp#L2587-L2590)),
and the decompilation records it as a retail difference. So in retail the debug camera is a cheat, and in the internal
build it was always available.

In a copied-profile comparison, a scoped press of `F` reached this gate in the clean build without entering the toggle,
and entered it once the gate was patched out ([free-camera gate patch](../../platforms/patches/free-camera-aurore-gate-bypass-patch.md)).
No run has put the code word in a save name and watched the camera switch; how the camera is steered once it is on is
not documented here.

### `latête`: the Goodies developer view

Read from the same functions as `MALLOY`. Cheat 5 is checked after cheat 0 each time the Goodies page processes, and its
answer wins: while it is on, the state lookup returns "instructions" for every cell that maps to a Goodie, whatever
the career holds and whatever `MALLOY` says. For that state the page draws the cell's glow dim, as it does for a locked
Goodie, but draws the label in full white, shows the "to unlock" heading, and shows the Goodie's unlock condition in place
of its title, for the Goodies the page has such text for. Choosing a cell does not open it, because only "new" and "old"
cells open. So it is not an unlock: it is a view of what each Goodie asks of the player. Nobody has watched it work from
a save name; the account is a static reading.

## The all-cheats state

Index 0 to 5 are all true under two conditions that need no save name. The first is the `-autoconfigtest` command-line
flag. The second is a runtime flag that `CGame::Update` sets when an `-autoconfigtest` run reaches the end of its scripted
sequence (the sequence and its other effects are in [command-line parameters](../../platforms/command-line/cli-parameters.md)).
A player cannot set it from a save name.

The same state changes other parts of the game that have nothing to do with cheat words: no autosave after a level, race or campaign
(`CFrontEnd::Init`), the front end's F8 screen-dump key, in a level the B key asking for a screen dump (`CGame::DrawGameStuff`;
without the flag, B grabs a single frame to a file only under `-testeur`), the game's frame-rate line going to the
setup-history file, and the music (`CMusic::Play`) always starting track 8. The list is of the effects read here and may
not be complete. They read the flag themselves rather than asking `IsCheatActive`. In the
decompilation's source, the Goodies page, the God item and the free-camera case all go through `IsCheatActive`, not the
flag; an earlier note that said several of them read the flag directly is not borne out there.

## A button that is named like a cheat

The front end has an action called `BUTTON_FRONTEND_CHEAT`. In the retail controller code (`CController::DoMappings`) it is
sent when both Shift keys are held; in the published source it is sent when the two buttons named `LEFT1` and `RIGHT1` for this purpose are held on a pad
(`Controller.cpp`, lines 399-410), and the E3 build adds a stick condition. It is not the save-name mechanism. In the decompilation's source, `CFrontEnd::ReceiveButtonAction` toggles a
flag on it that no function there reads, and the only page that reacts is the debrief page (`CFEPDebriefing::ButtonPressed`),
which sets a 0.1-second fast-forward timer. Nothing about the code word check is triggered by it.

## The internal source's four names

The published `FEPSaveGame.cpp` holds four code words, written in plain text, with its own comments for what they are for:

| Index | Internal code word | Comment in the source | Retail code word at that index |
| ---: | --- | --- | --- |
| 0 | `105770Y2` | unlock all goodies | `MALLOY` |
| 1 | `!EVAH!` | unlock all levels | `TURKEY` |
| 2 | `V3R5ION` | show version number | `V3R5IOF` |
| 3 | `B4K42` | god mode available | `Maladim` |

In the retail table, indices 0, 1 and 3 do what the internal comments describe, index 2 has no known effect, and
indices 4 and 5 have no internal counterpart. The internal
`IsCheatActive` also answers yes on a PlayStation 2 development kit (`FEPSaveGame.cpp:556-559`); the retail function has
no such branch and instead has the two flags above. The published snapshot does not contain `FEPLevelSelect.cpp` or the
pause-menu source, so for indices 1 and 3 the comments are the only source evidence of what they did. The retail names
are not in the source, and who changed them, and why, is not documented. The internal names are not accepted by the retail
build: no retail row decodes to them.

## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| Does `V3R5IOF` do anything in retail? | Run a copied profile with a save named with it and watch the front end and a level for any version text (a static caller search is already done: none in the matched tree) |
| Does `Aurore` in a save name switch the free camera on from the toggle key? | Copied profile, save named with it, load a level, press the toggle key, read the player's camera state |
| Does `latête` show unlock conditions on the wall as read here? | Copied profile, save named with it, open the Goodies wall and read the heading and text for a cell that is locked in the save |
| Does opening a Goodie under `MALLOY` change the saved file? | Open one cell with the name set, save the career, compare the file with its previous copy |
| Which retail build change replaced the four internal names, and when? | A statement from someone who worked on the PC release, or an earlier retail or demo build with a different table |

## Related pages

- [God mode](god-mode.md) — the flag, its save location and its effects.
- [`CFEPSaveGame::IsCheatActive`](IsCheatActive.md) — the function note, with the field-identity correction.
- [Goodies save and unlock contract](../../saves/goodies-system.md) and [career graph](../../saves/career-graph.md) —
  what the first two cheats bypass.
- [Command-line parameters](../../platforms/command-line/cli-parameters.md) — `-autoconfigtest`.
- [Frontend save and load semantics](../../saves/frontend-save-load-semantics.md) — the six-entry table in its page context.
- Patches that force the same checks in a copied executable:
  [Goodies display override](../../platforms/patches/goodies-gallery-display-unlock-patch.md) and
  [free-camera gate](../../platforms/patches/free-camera-aurore-gate-bypass-patch.md).
