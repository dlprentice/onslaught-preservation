# Version Overlay Patch

Status: historical patch note
Last updated: 2026-10-22 (retired AppCore/WinUI tools in the past tense)
Summary: the paired pointer and cave-string rows that show `V1.00 - PATCHED` in the version overlay, and the one
copied-game run that confirmed it.

> Patch note for the opt-in `V1.00 - PATCHED` marker bytes

## Scope

The Binary Patches page of the retired AppCore editor (Onslaught-Career-Editor [`4ac3c9ae`](https://github.com/dlprentice/Onslaught-Career-Editor/tree/4ac3c9ae32d97c1293858c49bf9cc485eb814f28), the last commit that has it) shipped one visible stable row that redirects the bottom-left version-format pointer when the user explicitly selects the marker. A hidden cave-string payload row is selected with that visible marker only. A bounded copied-game title/menu runtime smoke has confirmed the visible `V1.00 - PATCHED` marker in one local run; this document does not claim broader overlay, gameplay, or parity behavior.

The retired WinUI app's Windowed & Mods page also had Proof quick-pick controls named `Add PATCHED
marker` and `Clear PATCHED marker`. They only selected or cleared the
visible `version_overlay_use_patched_format_pointer` row; the AppCore catalogue's
dependency handling added the hidden
`version_overlay_patched_format_cave_string` payload when a copied profile was
prepared.

## Patch Pair

| Patch Id | File Offset | Purpose |
|---|---:|---|
| `version_overlay_use_patched_format_pointer` | `0x06416F` | Redirect the version-format pointer to a cave-hosted patched string |
| `version_overlay_patched_format_cave_string` | `0x1AA444` | Install the string payload `V%1d.%02d - PATCHED` in the code cave |

## Behavior

- Retail version-format pointer is redirected to a cave string.
- When the title/menu overlay path was exercised with version `1.00` in one copied-game run, the patched format rendered as `V1.00 - PATCHED` instead of the stock version-only display.
- These two patch rows are paired, but they are not applied automatically alongside unrelated patch selections.
- The visible `version_overlay_use_patched_format_pointer` row brings in the hidden `version_overlay_patched_format_cave_string` payload row.

## Safety Model

- The retired editor byte-verified both patches before writing them.
- It restored both through the normal `BEA.exe.original.backup` rollback path.
- They do not change gameplay logic; they only affect the version overlay string path when that path is exercised.

## Evidence

- [`patches/catalog/patches.v2.json`](https://github.com/dlprentice/Onslaught-Career-Editor/blob/4ac3c9ae32d97c1293858c49bf9cc485eb814f28/patches/catalog/patches.v2.json) (Onslaught-Career-Editor `4ac3c9ae`, retired)
- [`BinaryPatchEngine.cs`](https://github.com/dlprentice/Onslaught-Career-Editor/blob/4ac3c9ae32d97c1293858c49bf9cc485eb814f28/OnslaughtCareerEditor.AppCore/BinaryPatchEngine.cs) (same commit)
- [`patches/README.md`](https://github.com/dlprentice/Onslaught-Career-Editor/blob/4ac3c9ae32d97c1293858c49bf9cc485eb814f28/patches/README.md) (same commit)
- Copied-game runtime smoke artifact: retained in ignored local evidence storage.
- First captured title/menu frame: retained in ignored local evidence storage; public summary is only that the frame showed `V1.00 - PATCHED` in one local run.

## Notes

- This is a standalone opt-in visible marker row in the UI.
- The current visible proof is one copied-game title/menu run only. Other overlay paths, gameplay paths, version-cheat paths, long sessions, rebuild parity, and no-noticeable-difference parity remain separate proof.
