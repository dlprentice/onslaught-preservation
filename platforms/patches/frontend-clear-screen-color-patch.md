# Frontend clear-screen color patches

Status: historical copied-executable presets with bounded title-screen and navigated-menu observations.
Last updated: 2026-10-22 (retired AppCore/WinUI tools in the past tense)
Summary: three mutually exclusive immediates that change the front end's clear-screen colour, and what controlled
copied runs showed.

These mutually exclusive rows change the immediate passed to the DirectX frontend clear-screen path. The exact byte definitions were rows of the patch catalogue of the retired AppCore editor (Onslaught-Career-Editor [`4ac3c9ae`](https://github.com/dlprentice/Onslaught-Career-Editor/tree/4ac3c9ae32d97c1293858c49bf9cc485eb814f28), the last commit that has it); the table below records them.

| Item | Value |
| --- | --- |
| Function | `0x00540F70 CDXFrontEnd__RenderStart` |
| Source anchor | `references/Onslaught/DXFrontend.cpp` |
| VA / file offset | `0x00540F88` / `0x140F88` |
| Original | `3F 1F 1F 00` (`0x001F1F3F`) |
| Dark red | `1F 1F BF 00` (`0x00BF1F1F`) |
| Dark green | `1F BF 1F 00` (`0x001FBF1F`) |
| Black | `00 00 00 00` |

Controlled copied-profile runs reached both the title screen and a navigated Goodies menu for each color. The observed margins stayed in the selected red, green, or black family after frontend shading. Each run launched only the copied executable, used scoped input, stopped the managed process, and left installed/source executable and source save/options hashes unchanged.

The retired WinUI app exposed the three rows as normal patches and as equivalent quick picks, which selected or cleared the same mutually exclusive catalogue entries; they were not a second patch format.

## Boundary

This changes a clear-screen background immediate, not textures, menu art, fonts, HUD colors, mission UI, or gameplay rendering. It does not prove every frontend state, every machine, or rebuild parity. The rows were meant only for copied executables.
