# Mission scripting

Status: active — folder index
Last updated: 2026-10-22 (summaries filled, titles in sentence case)
Summary: The MSL language, its command registry, the IScript interface and the script VM's data types.

## Documents

| Document | Summary |
| --- | --- |
| [DataType.cpp - Function Mappings](DataType.md) | the mission-script datatype classes (int, float, bool, string, position, thing pointer): factory, vtables, operator slots, layouts and the GETTOP reassign rule. |
| [The Mission script-command registry, recovered from shipped data](mission-script-command-registry.md) | 144 script commands are paired one-to-one with 144 unique handler addresses by the game's own data, and every handler resolves to a known function. This prov… |
| [mission-script-command-registry.tsv](mission-script-command-registry.tsv) | Mission-script command index, name and retail handler address. |
| [MissionScript / IScript static contract](missionscript-iscript-static-contract.md) | Static evidence for the retail MissionScript and IScript interpreter; not runtime script proof. |
| [missionscript-vm-datatype-opcode-schema.v1.json](missionscript-vm-datatype-opcode-schema.v1.json) | Machine-readable schema of the script VM's datatypes and opcodes. |
| [MSL Command Reference](msl-commands.md) | MSL command and mission scripting verb lookup. |
| [MSL mission scripting language](msl-scripting.md) | The `.msl` mission language: conventions and representative examples. |
