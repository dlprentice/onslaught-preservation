# Save Goodies quick reference

Status: active quick reference
Last updated: 2026-10-22 (retired AppCore/WinUI tools in the past tense)
Summary: where the Goodie states live in a `.bes` save and the corrections an editor must keep.

The authoritative format and evidence boundaries are in [goodies-system.md](goodies-system.md). Unlock copy shown by the product is owned by `companion/OnslaughtToolkit.Godot/Careers/GoodieUnlockRequirementService.cs` in Onslaught-Career-Editor.

## Storage

- Save size: `10004` bytes
- Version word: `0x4BD1`
- True Goodie base: `0x1F46`
- Entry offset: `0x1F46 + index * 4`
- Stored entries: `300`
- Displayable entries: indices `0..232`
- Reserved entries: indices `233..299`; preserve them

| Raw dword | State | Product display |
| ---: | --- | --- |
| `0` | unknown | Locked |
| `1` | instructions | Locked with hint |
| `2` | new | Gold badge |
| `3` | old | Blue badge |

MissionScript Goodie indices are one-based: `script index = save index + 1`. Script index `0` is invalid.

## Consequential boundaries

- Patch only a real copied baseline; never synthesize a save or write in place.
- Preserve every byte outside explicitly selected displayable Goodie dwords.
- Goodies `71..73` have source unlock hooks and shipped texture resources, but the observed ordinary wall path moves from `70` to `74`; hidden reachability remains unproven.
- Goodie `232` maps to cutscene `33` and lacks a matching `goodie_232_res_PC.aya` in the checked PC archive set.
- Goodie `228` is at `0x22D6`. The old `0x22D4` aligned-view value is not `mCareerInProgress`; that flag is at file offset `0x248A`.

The companion's [`CareerSave`](https://github.com/dlprentice/Onslaught-Career-Editor/blob/51129bab45489e5e45ee1c047cbcd8072bf4cc50/companion/OnslaughtToolkit.Godot/Careers/CareerSave.cs) (Onslaught-Career-Editor `51129bab`) and its tests now own the byte-preserving Goodie edit.
