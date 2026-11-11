# Community Resources

Status: active — speedrun, community and tool links, with their sources
Last updated: 2026-11-11 (the extractor's author is credited by name only; earlier: private conversation partners and unsourced quotations removed; dated record and reference links corrected)
Summary: speedrun records and techniques, community research, similar games, external archives and tools, and the sources this page draws on.

## Speedrun Resources

- **Speedrun.com**: https://www.speedrun.com/battle_engine_aquila#Any
- **BermudaMaster's Twitch**: https://www.twitch.tv/bermudamaster
- **World record as of Nov 2025**: Sub-56 minutes (BermudaMaster). Check the board above for newer times.

---

## Speedrun Techniques (from BermudaMaster)

**Menu Skip**: Holding spacebar (confirm key) keeps confirming options on select screens. This skips cutscenes and the transition between level start and actual gameplay.

**Victory Screen Glitch**: Opening the menu during the victory screen shows both simultaneously. Can exit level to reach results screen slightly faster.

**Death from Above Issues**: Something about the "Red Map issue" causes problems.

**Hitbox Issues**: Some objects' hitboxes don't exist - attacks can phase through them. Discovered after hours of optimizing single levels.

**Blinding the Enemy**: Destroying ALL turrets makes air support stay on the map and clear the island much faster in the NEXT mission. If even one turret stays, all air support leaves when it's destroyed.

---

## Racing Challenges (from vandal_117)

- **NOT impossible** - contrary to 2013 IGN article claiming impossible
- Fly close to surface for speed boost
- Tiny gap between "too close" (physics launch) and "boost zone"
- Easier on water but still get launched if too close
- Last challenge: can shoot ship and buildings before starting, can fly under the ship

---

## Similar Games (for inspiration)

- **Gun Metal** (Steam) - similar mech combat
- **AirMech** - closest modern equivalent to BEA
- **Supreme Commander** - unit designs similar (Aeon = Forseti, Cybran = Muspell)
- **AEROMACHINA** - ground/flight combat, demo on Steam

---

## External Archives

- **Lost Toys Website** (archived): https://web.archive.org/web/20030622111235/http://www.losttoys.com/
- **Post-Mortem** (GDM April 2003): https://ia600907.us.archive.org/33/items/GDM_April_2003/GDM_April_2003.pdf
- **GDC Europe 2002**: "Cross Platform Console Development" PowerPoint (found
  by David via Internet Archive, March 2025); exact source identity and
  technical synthesis are now indexed in
  [`development-sources.md`](development-sources.md) and
  [`README.md`](../engine/README.md)
- **vandal_117's gold save**: Legitimate all-S-rank career file shared Sept 12, 2025

---

## Emulator Compatibility (found by Jeppi, Feb 2022)

- **Cxbx-Reloaded (Xbox)**: https://github.com/Cxbx-Reloaded/game-compatibility/issues/251
- **DXVK**: https://github.com/doitsujin/dxvk/issues/1757
- **PCSX2 (PS2)**: https://github.com/PCSX2/pcsx2/commit/05b8e80ac874b48c83f44c521d0b076b100992c2

---

## External Tools

### AYAResourceExtractor
- **Repo**: https://github.com/stuart73/AYAResourceExtractor
- **Author**: Stuart Gillam
- **Purpose**: Extract 3D models, textures from .aya files
- **Output**: FBX (binary and ASCII)
- **Note**: Animations not yet extractable
- **Blender import**: Turn off extra import options to avoid crash
- **Model scale**: Battle Engine is ~7.6m tall based on model calculations (April 2023)
- **Model quirks**: Models are asymmetrical, which shows up when they are 3D printed
- **Use cases**: Gmod SNPCs, C&C Generals mods, 3D printing (thin parts break during support removal)

### Onslaught Source Reference
- **Repo**: https://github.com/stuart73/Onslaught
- **Contents**: Career.cpp/h, d3dapp.cpp, FEPGoodies.cpp, etc.
- **Note**: Internal PC build, not console port

---

## Sources

The `references/Onslaught/` paths cite Stuart's published source at the pinned commit [`c3d8ac4`](https://github.com/dlprentice/Onslaught/tree/c3d8ac464259942b83fa8aa7f867c856e77b734d) of the public reference fork; this repository has no `references/` folder (see the [README](../README.md#how-to-read-a-finding)).

- `references/Onslaught/Career.cpp` - Stuart's internal PC build source
- `references/Onslaught/Career.h` - Struct definitions
- `game/` - Optional local ignored overlay for a user-owned BEA installation or
  copied runtime files used during local analysis
- Community hex-diffing of retail saves
- Community Discord conversations, parsed Dec 2025; the raw dumps are not published (see [community-history.md](community-history.md))
- Private LinkedIn conversations with people who worked on the game; not reproduced here
