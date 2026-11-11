# Known bugs and reports

Status: active — reported problems with the original game, and the save-editing mistakes that crashed it, each with the evidence it rests on
Last updated: 2026-11-11 (secondary-objective rule corrected against CEndLevelData::IsAllSecondaryObjectivesComplete; migrated from the Toolkit's frozen bug note; save offsets re-derived against the save format and the tracked gold save; ranking mechanism added from the decompilation)
Summary: what players and contributors have reported as wrong in *Battle Engine Aquila* on Steam, which reports have a
mechanism that can be read from the code, and the early save-patching mistakes that corrupted careers and how the save
layout shows what went wrong.
Evidence: MEASURED — the tracked gold career save, read at the offsets named below; MEASURED (static) — functions of
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) at commit `9759593` that are listed there in
`docs/check/matched.tsv` as matching the retail executable byte for byte, read for what they do and not run; the
reports themselves are leads, not measurements: most are Discord posts summarised in [community history](community-history.md),
and the Tentacle Base report, the Steam-crash confirmation by superdeveloper1337, desimbr's 11 September remark about the gold save, NDjeneralBN's remark that the Red Aquila was never meant to be playable and the three S-rank tips come only from the frozen Toolkit note
this page was migrated from, not from community history; UNKNOWN — the cause of every report in the table below,
the ranking one included (a ranking mechanism is readable, but nobody has shown that any grade is unreachable).
Specimen: pristine Steam retail `BEA.exe`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The gold save is `tests_shared/fixtures/gold_career_save.bin` in
[Onslaught-Career-Editor](https://github.com/dlprentice/Onslaught-Career-Editor/tree/51129bab45489e5e45ee1c047cbcd8072bf4cc50)
at the commit the README names, SHA-256 `0c17e47db9d666e9b26ef88d43d0a25e7cbfbf4f88c8005cc748965050e506fb`, 10,004 bytes.

This page keeps two kinds of entry apart. A **report** is something a player or former developer said they saw; it is a
lead, not a measurement, and nothing here reproduces it. A **mechanism** is a statement about what the game's code does,
read from the decompilation or the save file. Where the two meet, the entry says so. People are credited by the Discord
handle used in [community history](community-history.md), which also holds the dates and context.

## Reports about the original game

| Report | Who and when | What is known |
| --- | --- | --- |
| On the Steam version the Fenrir is meant to attack the main HQ once it gets close enough and never does. | BermudaMaster, 19 January 2025 | No cause and no fix recorded. Not reproduced here. |
| Part-way through the Tentacle Base boss fight the starting tentacles sometimes pick ally ships as targets and stop shooting anything, repeatedly rather than once. | A community report; the reporter and date were not kept with the note this entry comes from | Cause unknown. The weakest entry on the page: no name, no date, not reproduced. |
| In co-op the Red Aquila's indicators, seen from the player's own side, are still blue. | NDjeneralBN, 28 July 2022 | The reporter added that the Red Aquila was never meant to be playable. The note this entry comes from read that as a sign that the multiplayer interface was not fully adapted for the red side; nothing here tests either. |
| Tabbing out of a mission and back runs the game at two to three times speed on a 144 Hz display; a new mission resets it. | Jeppi, 15 May 2026 | Unanswered as of the 6 November 2026 reading of the server. Not reproduced here. |
| The menu can open during the victory screen inside a short window, and holding space can confirm an options prompt over and over. | BermudaMaster, summer 2025 | Reported as small oddities; no cause recorded. |
| Some missions seem to have a broken ranking: players cannot reach certain grades whatever they do. | Players (no names kept); desimbr commented on where the targets live on 3 March 2023 | A mechanism is readable from the code; see the next section. |

## Ranking: where the grade targets come from

The two notes of the former developer's comment disagree on whether the per-mission targets are stored in the level data
or in the game code ([community history](community-history.md#what-members-learned-about-the-game)); the code points to the
level file, and also shows what else decides a mission's rank. This is a static reading of four matching functions
(`CGame::FillOutEndLevelData`, `CWorld::LoadWorld`, `CEndLevelData::IsAllSecondaryObjectivesComplete`,
`CCareer::GetGradeFromRanking`); no run has been captured to compare against. The ranking section of the
[game system](../engine/source/gameplay/game-system.md#ranking-calculation-system) page gives the same outline from the pinned
internal source; this page adds the retail (matched) reading and the details below.

- **The targets come from the level file.** `CWorld::LoadWorld` reads, per level, a score for S, a score for D, a time
  limit, a full-score time, a percentage-score time and a score percentage, and hands them to the game object. A base
  world loaded underneath a level reads the same fields, but the level's own values are applied afterwards and win.
- **Time scales the score.** When the percentage-score time is later than the full-score time, `CGame::FillOutEndLevelData`
  multiplies the final score by 1 up to the full-score time, then falls linearly to the score percentage at the
  percentage-score time, and stays there. The ranking is then a straight line from 0 at the D score to 1 at the S score:
  at or above the S score it is exactly 1; below the D score the code first sets -1 and then clamps it to 0 (letter E); a
  score exactly equal to the D score would give 0, which the code lifts to 0.001 so that it reads as D.
- **A level whose two times are not set in that order skips this**, so its ranking stays at the starting value of 1 (S) apart
  from the objective rule below. Which levels are like that has not been read out.
- **Secondary objectives cap or floor the rank.** The rule depends on `CEndLevelData::IsAllSecondaryObjectivesComplete`,
  which looks at the status of each secondary objective. It returns false if any objective has failed, and also false if
  none is either complete or failed. Otherwise it returns true. On a level that has secondary objectives,
  `CGame::FillOutEndLevelData` then does one of two things. If the function returns true, a ranking below 0.4 is raised to
  0.4. If it returns false, a ranking above 0.6 is lowered to 0.6. In the converter that turns a ranking into a letter
  (`CCareer::GetGradeFromRanking`), 1.0 is S, zero or less is E, and otherwise the letter is D minus the whole number part of
  four times the ranking, so 0.4 is C and 0.6 is B. In practice, on a level with secondary objectives, a failed objective
  caps the rank at B however high the score is. If none has failed but at least one is complete, the rank is at least C. An
  objective that is still pending (neither complete nor failed) does not cap the rank on its own, but if every objective is
  pending the function returns false and the cap applies.

What this does not say: whether the game sets objectives that are still pending to failed at the end of a level, before
this function is called (the reading above is of the function itself, not of what status the objectives hold by then);
which missions have an S target that the achievable score cannot reach (nobody has computed that
from the level files), or whether the report that some grades are impossible is true for any mission. The save-side layout
of a rank is in the [grade system](../saves/grade-system.md).

## Save-patching mistakes that crashed or corrupted careers

The first public save editor (Onslaught Career Editor 0.1.0, 9 September 2025, see [community history](community-history.md))
wrote some values at the wrong offsets, and a patched save made some levels crash. These entries are resolved; they stay
here because the same mistakes are easy to make again, and the correct layout is in the [save format](../saves/save-format.md).

**The first and third entries involve a two-byte misalignment.** The retail loader copies the career block from just after
the 2-byte version word (`CCareer::Load` checks the version word, then copies the whole career structure from file
offset 2; [save format](../saves/save-format.md)). A career field at career offset *n* is therefore at file offset *n* + 2,
and the real 4-byte values start at file offsets whose remainder modulo 4 is 2. An editor that treated the file as 4-byte
aligned from offset 0 read and wrote such values two bytes early. This is a reading of the loader and the save layout, not
a reproduction of the crash. The second entry is a different mistake: a documented offset that was simply wrong.

| Mistake | What the correct layout is | Evidence |
| --- | --- | --- |
| Patched saves crashed when "Assault Force Fenrir (Evo)" and "Air Raid (Evo)" were about to start. Reported by desimbr and, on the Steam build, by superdeveloper1337 on 10 September 2025; on 11 September desimbr said a gold save file loaded fine, and that patched saves caused his crash. | The cause was found on 23 February 2026 as an unlock-all routine that wrote through the misaligned view and so corrupted neighbouring dwords, notably in the link table. The fix was to write at the true offsets and to change a link only from 0 (not complete) to 1 (complete), leaving a 2 (the game's own "alternate path" bookkeeping) as it is. | The crash is a report, and its attribution to misaligned writes is that later diagnosis; no controlled reproduction is archived here. The link states and the 0-to-1 rule are in [career links](../saves/career-links.md) and the [career graph](../saves/career-graph.md). |
| The five kill counters were documented at offset 0x23A4, so a patcher wrote kills into the Goodie array instead. The gap to the real offset is 0x52 bytes, not two, so this is a wrong number rather than the misalignment. | The counters are five dwords at file offset 0x23F6; the low 24 bits of each are the count and the top byte is preserved ([save format](../saves/save-format.md#kill-counters-and-slots)). | MEASURED: in the gold save the five counts read 3221, 9738, 3002, 3953 and 1024 from 0x23F6, and the same read at 0x23A6 (the documented offset 0x23A4 read through the true view, two bytes on) gives zeros. Offset 0x23A4 lies inside the Goodie array, which ends at 0x23F6. |
| "Career in progress" was set at offset 0x22D4, which is not the flag. That offset is where the shifted view puts Goodie 228 (two bytes before its true position). | The flag is at file offset 0x248A. Goodie 228 is at 0x1F46 + 228 × 4 = 0x22D6, so a write at 0x22D4 straddles Goodies 227 and 228 instead of touching the flag ([Goodies save contract](../saves/goodies-system.md#corrected-offset-boundary)). | MEASURED: the gold save holds 1 at 0x248A. The layout is from the save-format table; the effect of the write is arithmetic on that layout, not a captured run. |

## Reported S-rank tips

Not bugs, but the frozen note carried them with the reports. They are hearsay from one player, vandal_117 (March 2023),
and have not been tried here.

| Mission (as the player numbered it) | What was reported |
| --- | --- |
| Thunderhead (3.3) | A speed-run start with the Lancer configuration gave an S on the first try. |
| Warspite (4.3) | Leave buildings standing in earlier missions so they can be destroyed in this one for the ranking. |
| Final mission | Beat the boss in under 4:20 and then destroy all the fighters; the time alone is not enough, kills count too. |

The Warspite tip fits a separate report that destroyed buildings on an island stay destroyed in later missions
([community history](community-history.md#what-members-learned-about-the-game)); whether the score counts them is not
checked here.

## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| Does the game set a secondary objective that is still pending to failed at level end? | Read the end-of-level path that fills the end-level data and the objective status changes, or log each objective's status at the moment `CGame::FillOutEndLevelData` runs |
| Do any missions have an S score that the level's scoring cannot reach? | Read each level file's S score, D score and scoring times (the fields `CWorld::LoadWorld` reads) and compare with the best score a run can reach |
| Why does the Fenrir not attack the HQ on Steam? | Run the mission in a copy and watch the Fenrir's target selection near the HQ; compare with the Onslaught CE port |
| Is the tab-out speed-up in the retail game or only in particular display setups? | Tab out of a mission on a 60 Hz and a 144 Hz display and time the game clock against the real clock; [runtime time dependence](../engine/runtime-time-dependence.md) lists the clock sources |
| Did early patchers' crashes come only from the misaligned writes? | Write the same edits at the misaligned and the true offsets into two copies of the gold save and load both in a copied game |
