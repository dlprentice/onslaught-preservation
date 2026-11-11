# Mission scripting

Status: active — folder index
Last updated: 2026-11-11 (rows added for the three script-native pages; earlier: 2026-11-06 registry summary cell completed)
Summary: The MSL language, its command registry, the IScript interface and the script VM's data types.

## Documents

| Document | Summary |
| --- | --- |
| [DataType.cpp - Function Mappings](DataType.md) | the mission-script datatype classes (int, float, bool, string, position, thing pointer): factory, vtables, operator slots, layouts and the GETTOP reassign rule. |
| [The Mission script-command registry, recovered from shipped data](mission-script-command-registry.md) | 144 script commands are paired one-to-one with 144 unique handler addresses by the game's own data, and every handler resolves to a known function. This proves registry vocabulary only, not C++ symbols, signatures or semantics. |
| [mission-script-command-registry.tsv](mission-script-command-registry.tsv) | Mission-script command index, name and retail handler address. |
| [MissionScript / IScript static contract](missionscript-iscript-static-contract.md) | Static evidence for the retail MissionScript and IScript interpreter; not runtime script proof. |
| [missionscript-vm-datatype-opcode-schema.v1.json](missionscript-vm-datatype-opcode-schema.v1.json) | Machine-readable schema of the script VM's datatypes and opcodes. |
| [MSL Command Reference](msl-commands.md) | MSL command and mission scripting verb lookup. |
| [MSL mission scripting language](msl-scripting.md) | The `.msl` mission language: conventions and representative examples. |
| [Mission-script natives: what each one does](native-behaviour.md) | How a native is called, and what 33 of them do: marking, health and position, weather, time and spawning, and queries; the names that mislead and the open questions. |
| [Script-driven HUD: objective markers, part flashing and the text slots](native-hud-and-objectives.md) | What nine natives change in the HUD: objective markers, the flash state of six HUD parts and the four text slots behind the variable natives, with the six display styles. |
| [Script natives for segment health](native-segment-health.md) | What the five segment natives write to a unit's destroyable segments, and what the stored values mean. |
