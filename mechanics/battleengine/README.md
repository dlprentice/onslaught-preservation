# Battle Engine

Status: active — folder index
Last updated: 2026-10-22
Summary: The player's Battle Engine: aiming, weapon stores, walker dash, morph timing and configuration values.

## Folders

| Folder | Covers |
| --- | --- |
| [contracts/](contracts/README.md) | Per-function behaviour contracts for Battle Engine weapons, contact predicates, shock shake and collision shape |

## Documents

| Document | Summary |
| --- | --- |
| [Battle Engine auto-aim, launch position and Gun emitters](battle-engine-aiming.md) | how the Battle Engine picks an auto-aim target and blends its aim offsets, where each player round starts (the cockpit mesh's Gun emitters) and in which dire… |
| [Battle Engine weapon stores, charge and firing state](battle-engine-weapon-stores.md) | the Aquila's ammo and heat stores, when a shot spends them, cooling, the Missile Pod and Pulse Cannon Pod charge law, what an empty store blocks, and what `I… |
| [BattleEngine Default Configuration Values](battleengine-config-values.md) | BattleEngine default config and combat/movement constants. |
| [battleengine-target-acquisition-static-contract-v1.json](battleengine-target-acquisition-static-contract-v1.json) |  |
| [BattleEngine Target-Acquisition Static Contract v1](battleengine-target-acquisition-static-contract-v1.md) |  |
| [Walker dash: the retail timing window](walker-dash.md) | a walker dash needs the opposite hard press to have started more than half of `mDashTime` and less than `mDashTime` before (0.1 to 0.2 s). The pinned source … |
| [walker-transform-morph-timing-v1.json](walker-transform-morph-timing-v1.json) |  |
| [Walker-to-jet raw-state timing](walker-transform-morph-timing-v1.md) |  |
