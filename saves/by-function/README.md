# Save functions

Status: active — folder index
Last updated: 2026-10-22
Summary: Function-level contracts for writing, reading and sizing career saves and the options file.

## Documents

| Document | Summary |
| --- | --- |
| [CCareer__Blank](CCareer__Blank.md) | rebuilds the authored graph, preserves options and unused storage, and leaves nine Goodies at instruction state. |
| [CCareer__SizeOfSaveGame](CCareer__GetSaveSize.md) | counts initialized active binding rows; this is allocation sizing, not loader validation. |
| [CCareer__Load](CCareer__Load.md) | raw career copy, version admission and distinct load modes; size validation belongs to callers. |
| [CCareer__Save](CCareer__Save.md) | serializes career, active bindings and runtime tail; tail construction also refreshes the packed display-mode global. |
| [CCareer__SaveWithFlag](CCareer__SaveWithFlag.md) | sets the live progress word before serialization; Load does not clear that word. |
| [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md) | original reset produces nine instruction states; canonical progression reads and separate pending/count bookkeeping matter. |
| [CCareer__UpdateThingsKilled](CCareer__UpdateThingsKilled.md) |  |
| [CFEPLoadGame__StartLoad](CFEPLoadGame__DoLoad.md) | original menu-load composition preserves live volumes and conditionally forwards the entire read buffer to default-options persistence. |
| [CFEPOptions__WriteDefaultOptionsFile](CFEPOptions__WriteDefaultOptionsFile.md) | fixed output filename and unchecked write/close results, independently rechecked against original code. |
| [CFEPSaveGame__CreateSave](CFEPSaveGame__CreateSave.md) | explicit save checks the slot adapter's result, but that adapter discards a close error after a complete item write. |
