# CFEPOptions__WriteDefaultOptionsFile

> Address: 0x0051f680 | Source counterpart absent from the pinned partial checkout

Specimen: pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Status: active bounded retail writer contract; older caller receipts remain separate
Summary: fixed output filename and unchecked write/close results, independently rechecked against original code.
Source File: `FEPOptions.cpp` is absent from the pinned partial source; no source-body equivalence claimed | Binary: pristine `BEA.exe.original.backup`.

Last updated: 2026-10-22 (research-campaign records and decompiler-style code removed)

## Status
- **Source comparison:** `references/Onslaught/FEPOptions.cpp` is absent; the earlier source-verification claim is withdrawn. The complete retail body is the authority here.

## Purpose
Low-level helper that writes a serialized options/career buffer to `defaultoptions.bea`.

## Signature
A free function (`__cdecl`, the caller cleans up 8 bytes) taking a data pointer and an `int` size; it
returns nothing.

## Verified Behavior (BEA.exe)

1. Opens `defaultoptions.bea` for write:
   - `fopen("defaultoptions.bea", "wb")`
2. If open succeeds:
   - `fwrite(data, size, 1, file)`
   - `fclose(file)`
3. If open fails:
   - passes a diagnostic message `"Couldn't write defaultoptions"` via `CDebugLog__Printf`.

The path is the literal at `0063fc74`, not CLI-writable buffer `0063db18`.
`-defaultoptionsname` redirects the boot read, not this write. Both `fwrite`
and `fclose` return values are ignored. The complete body returns with plain
`RET`, not `RET 8`. No internal allocation or serialization happens here;
caller owns `data` and `size`.

The September 19 [controls](../save-options-startup-compatibility.md#september-19-independent-recheck)
execute this original body with intercepted file functions under success,
open-failure, short-write and close-error conditions. Its call is separately
made by the driver after startup returns; these tests do not show that WinMain
saves automatically or establish actual durable publication. The caller chains
below remain static/dated evidence, not newly executed menu paths.

## Call Chains and Side Effects (Verified)

### 1) Load-game path (`CFEPLoadGame__DoLoad`, 0x00461e20)
- Reads selected `.bes` into `out_buf` using `PCPlatform__ReadSaveFile`.
- Calls `CCareer__Load(&CAREER, out_buf, 1)`.
- On successful load, if `0x0082b5b0 == 0`, calls:
  - `CFEPOptions__WriteDefaultOptionsFile(out_buf, size)`.

**Side effect:** the currently loaded save buffer can overwrite `defaultoptions.bea` (global-options snapshot behavior).

### 2) Async-save tick path (`Platform__AsyncSaveCareer`, 0x004d2580)
- Calls platform tick helper.
- If `0x0082b5b0 != 0`, clears it and triggers `CD3DApplication__Reset3DEnvironment(1,1)`.
- If previous flag value was `2`, allocates a temp buffer, serializes via `CCareer__Save`, then calls:
  - `CFEPOptions__WriteDefaultOptionsFile(dest, size)`, then frees.

**Side effect:** asynchronous runtime save-state transitions can update `defaultoptions.bea`.

### 3) PauseMenu-driven path (`0x004d06e0`)
- Serializes `CAREER` with `CCareer__Save`.
- Optionally writes selected save slot via `PCPlatform__WriteSaveFile`.
- Also calls:
  - `CFEPOptions__WriteDefaultOptionsFile(buf, size)`.

**Side effect:** this path can update both a slot save and `defaultoptions.bea` in the same flow.

### 4) Main-menu process path (`CFEPMain__Process`, 0x00462640)
- Additional direct caller xref at `0x004628df` is now recovered inside `CFEPMain__Process`.
- Same branch also calls `CCareer__Save` at `0x00462893` and conditionally `PCPlatform__WriteSaveFile`, confirming a full save+defaultoptions chain in main-menu process logic.

## Notes
- This function is central to why `defaultoptions.bea` behaves as a global settings sink, even when actions begin from save-load/save-menu flows.
- Related docs:
  - `../Career.cpp/CCareer__Save.md`
  - `../FEPLoadGame.cpp/CFEPLoadGame__DoLoad.md`
  - `_index.md` (FEPOptions.cpp)
