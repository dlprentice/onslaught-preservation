# Retail PC executable

Status: active — folder index
Last updated: 2026-10-22 (summaries filled, titles in sentence case)
Summary: The retail executable's identity, PE mapping and the DLLs it ships with.

## Documents

| Document | Summary |
| --- | --- |
| [Executable analysis (BEA.exe)](executable-analysis.md) | The retail `BEA.exe`: PE identity, hashes, size, DLL imports, Direct3D 9 and branding. |
| [Game binaries contract — DLLs and helper executable](game-binaries.md) | Identities, version, import and export censuses and roles of the five non-main PE files. |
| [Complete non-main binary export table](game-binary-exports.md) | complete named ordinal/RVA export appendix for the four non-main DLLs. |
| [Patch-surface PE mapping (pristine specimen)](pe-mapping.md) | `file offset = VA − 0x400000` is only valid inside a section's raw range. `.data` VirtualSize is far larger than SizeOfRawData, so most runtime globals (incl… |
| [Retail specimen baseline](retail-specimen-baseline.md) | which retail executable and corpus files probes trust, their hashes, and the state of the installed copy. |
