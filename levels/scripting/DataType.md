# DataType.cpp - Function Mappings

Status: active static function map
Last updated: 2026-10-22 (decompiler-style signatures and research-campaign records removed)
Summary: the mission-script datatype classes (int, float, bool, string, position, thing pointer): factory,
vtables, operator slots, layouts and the GETTOP reassign rule.

> Source file: `MissionScript/DataType.cpp`. Debug source path strings: `DataType.cpp` at `0x0064cc80`,
> `DataType.h` at `0x0064c628`.

## GETTOP assign slots — 2026-08-18

Independently re-read from specimen `74154bfa…` (file offset VA − 0x400000).
`CInstructionOP_GETTOP` (`0x0052e9c0`) calls virtual slot `+0x14` of the existing value, passing the peeked value,
when `[symbol+8]` is already live. Slot `+0x14` is the sixth vtable dword.

| Vtable | Class | `+0x14` | Table name | Body (HIGH) |
| --- | --- | --- | --- | --- |
| `0x005e4af8` | CInt | `0x0052d2a0` | `CIntDataType__Assign` | reads rhs through slot `+0x30`, stores EAX at `this+4` |
| `0x005e4ea4` | CFloat | `0x0052f170` | `CFloatDataType__Assign` | reads rhs through slot `+0x34`, stores the float at `this+4` |
| `0x005e4d50` | CBool | `0x0052e460` | `CBoolDataType__Assign` | reads rhs through slot `+0x3c`, stores AL at `this+4` |
| `0x005e4df8` | CThingPtr | `0x0052f430` | `CThingPtrDataType__Print` | reads rhs through slot `+0x40`, then sets the reader at `this+4` — Print is the table label |
| `0x005e4da4` | CPosition | `0x0052f5d0` | `CPositionDataType__VFunc_5_0052f5d0` | reads rhs through slot `+0x44`, then copies four dwords onto `this+4..+0x10` |
| `0x005e4e4c` | CString | `0x004014c0` | `SharedVFunc__NoOpOneArg_004014c0` | `ret 4` — a live string is **not** rewritten by GETTOP |

First write of a null `symbol+8` still clones through virtual slot `+0x48` (CString
clone is `0x0052f2c0`). POP still deletes and replaces. Only the GETTOP
*reassign* path is a no-op for strings. Authored reason open.

---

## Name corrections — 2026-07-28

Superseded in place against the 2026-07-27 function-name table. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at the area index (in the decompilation notes, not yet published).
Old cell text is quoted below rather than deleted, so a reader who remembers the
withdrawn label can tell it was corrected and not lost.

| Address | Superseded label | Current name | Correction |
| --- | --- | --- | --- |
| `0x0052ea40` | `CAsmInstruction__ExecuteCall` | `CInstructionOP_CALL__ExecuteCall` | class prefix moved; suffix unchanged |
| `0x0052f430` | `CStringDataType__Print` | `CThingPtrDataType__Print` | class prefix moved; suffix unchanged. **2026-08-18 body:** the Print suffix is the table label; the body is assign via `CGenericActiveReader__SetReader` on `this+4` |

---

## Overview

DataType.cpp implements the **mission script data type system** - a polymorphic class hierarchy for representing different data types (int, float, bool, string, position, thing pointer) used by the mission scripting engine.

The retained `missionscript-vm-datatype-opcode-schema.v1.json` accounts for the
six serialized datatype ids `1..6` (int, float, string, bool, thing pointer, and
position) created by `0x0052ec60 CDataType__CreateFromType`. Runtime datatype
behavior and exact layouts remain separate proof.

## String, thing-pointer and position slots

The `CStringDataType` and `CThingPtrDataType` tails, the shared `CDataType` scalar-deleting destructor wrapper and the
`CPositionDataType` arithmetic slots. This is static retail-binary evidence only; exact source identity, runtime MissionScript behavior, concrete layouts beyond observed fields, trailing CPosition dword semantics, and rebuild parity remain unproven.

| Address | Interface | Evidence |
| --- | --- | --- |
| `0x0052f2c0` | `CStringDataType__Clone`: member with the receiver in ECX; no stack arguments; returns a pointer | Allocates an 8-byte CString object, installs vtable `0x005e4e4c`, allocates/copies a heap string from `this+0x04`, and null-terminates the clone buffer. |
| `0x0052f360` | `CStringDataType__Equals`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Reads rhs through datatype vtable slot `+0x38` and compares the returned string against `this+0x04`. |
| `0x0052f430` | `CThingPtrDataType__Print`: member with the receiver in ECX; takes `rhs` (pointer); returns nothing | Table name is Print. Body is assign: reads the thing from rhs through slot `+0x40` and passes it to `CGenericActiveReader__SetReader` for the reader at `this+4`. Independently re-read 2026-08-18. |
| `0x0052f470` | `CThingPtrDataType__Clone`: member with the receiver in ECX; no stack arguments; returns a pointer | Allocates an 8-byte thing-pointer datatype, copies `this+0x04`, registers the clone field with `CSPtrSet__AddToHead` when needed, and installs vtable `0x005e4df8`. |
| `0x0052f550` | `CThingPtrDataType__ScalarDeletingDestructor`: member with the receiver in ECX; takes `flags` (byte); returns a pointer | Calls `CThingPtrDataType__Destructor` and frees `this` when `flags&1` is set. |
| `0x0052f570` | `CThingPtrDataType__Destructor`: member with the receiver in ECX; no stack arguments; returns nothing | Removes `this+0x04` from the pointed object's `CSPtrSet` when present and restores base vtable pointer `0x005e4b4c`. |
| `0x0052f670` | `CDataType__ScalarDeletingDestructor`: member with the receiver in ECX; takes `flags` (byte); returns a pointer | Shared CDataType scalar-deleting destructor wrapper reused by CInt/CFloat/CBool/CPosition vtable heads; calls `CDataType__Destructor` and frees `this` when `flags&1` is set. |
| `0x0052f690` | `CStringDataType__InitFromString`: member with the receiver in ECX; takes `source_text` (string); returns a pointer | Installs CString vtable `0x005e4e4c`, allocates/copies `source_text`, null-terminates it, and returns `this`. |
| `0x0052f720` | `CStringDataType__ScalarDeletingDestructor`: member with the receiver in ECX; takes `flags` (byte); returns a pointer | Calls `CStringDataType__Destructor` and frees `this` when `flags&1` is set. |
| `0x0052f740` | `CStringDataType__Destructor`: member with the receiver in ECX; no stack arguments; returns nothing | Frees the string buffer at `this+0x04` and restores base vtable pointer `0x005e4b4c`. |
| `0x0052f790` | `CStringDataType__ReadFromBuffer`: member with the receiver in ECX; takes `bytecode_reader` (pointer); returns a pointer | Reads a 4-byte length from the bytecode buffer, allocates `length+1`, reads string bytes, and appends a null terminator. |
| `0x0052f8a0` | `CPositionDataType__SubtractPosition`: member with the receiver in ECX; takes `rhs` (pointer); returns a pointer | Reads rhs through datatype vtable slot `+0x44`, allocates a 0x14-byte CPosition object, installs vtable `0x005e4da4`, and stores observed x/y/z differences. |
| `0x0052f920` | `CPositionDataType__ScaleByFloat`: member with the receiver in ECX; takes `rhs` (pointer); returns a pointer | Reads rhs float through datatype vtable slot `+0x34`, allocates a 0x14-byte CPosition object, installs vtable `0x005e4da4`, and stores observed x/y/z scaled values. |

## Factory and float slots

`CDataType__CreateFromType` and the adjacent `CFloatDataType` arithmetic, comparison and assignment slots. This is static retail-binary evidence only; exact source identity, runtime MissionScript behavior, concrete layouts beyond observed fields, exact type enum names, and rebuild parity remain unproven.

| Address | Interface | Evidence |
| --- | --- | --- |
| `0x0052ec60` | `CDataType__CreateFromType`: `__cdecl`; takes `type_id` (int), `bytecode_reader` (pointer); returns a pointer | Factory called from `CScriptObjectCode__ReadSymbolTable`; switches serialized `type_id` 1..6, installs observed datatype vtables, and reads initial payload bytes from `bytecode_reader`. Type 2 installs `CFloatDataType` vtable `0x005e4ea4`; type 4 installs the observed `CBoolDataType` vtable region `0x005e4d50`. |
| `0x0052ef50` | `CFloatDataType__Add`: member with the receiver in ECX; takes `rhs` (pointer); returns a pointer | Float add slot at data pointer `0x005e4ea8`; reads rhs through datatype vtable slot `+0x34`, allocates an 8-byte `CFloatDataType`, installs vtable `0x005e4ea4`, and stores the sum. |
| `0x0052efc0` | `CFloatDataType__Subtract`: member with the receiver in ECX; takes `rhs` (pointer); returns a pointer | Float subtract slot at data pointer `0x005e4eac`; reads rhs through slot `+0x34`, allocates an 8-byte `CFloatDataType`, and stores `this+0x04 - rhs`. |
| `0x0052f030` | `CFloatDataType__Multiply`: member with the receiver in ECX; takes `rhs` (pointer); returns a pointer | Float multiply slot at data pointer `0x005e4eb0`; reads rhs through slot `+0x34`, allocates an 8-byte `CFloatDataType`, and stores the product. |
| `0x0052f0a0` | `CFloatDataType__Divide`: member with the receiver in ECX; takes `rhs` (pointer); returns a pointer | Float divide slot at data pointer `0x005e4eb4`; reads rhs through slot `+0x34`, allocates an 8-byte `CFloatDataType`, and stores `this+0x04 / rhs`. |
| `0x0052f110` | `CFloatDataType__Equals`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Float equality slot at data pointer `0x005e4ebc`; reads rhs through slot `+0x34` and compares against `this+0x04`. |
| `0x0052f140` | `CFloatDataType__NotEquals`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Float inequality slot at data pointer `0x005e4ec0`; reads rhs through slot `+0x34` and compares against `this+0x04`. |
| `0x0052f170` | `CFloatDataType__Assign`: member with the receiver in ECX; takes `rhs` (pointer); returns nothing | Float assignment slot at data pointer `0x005e4eb8`; reads rhs through slot `+0x34` and stores the returned float at `this+0x04`. |
| `0x0052f190` | `CFloatDataType__LessThan`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Float less-than slot at data pointer `0x005e4ec4`; returns whether `this+0x04 < rhs`. |
| `0x0052f1c0` | `CFloatDataType__GreaterThan`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Float greater-than slot at data pointer `0x005e4ec8`; returns whether `this+0x04 > rhs`. |
| `0x0052f1f0` | `CFloatDataType__LessOrEqual`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Float less-or-equal slot at data pointer `0x005e4ecc`; returns whether `this+0x04 <= rhs`. |
| `0x0052f220` | `CFloatDataType__GreaterOrEqual`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Float greater-or-equal slot at data pointer `0x005e4ed0`; returns whether `this+0x04 >= rhs`. |

## Int slots

The `CIntDataType` arithmetic and comparison head and the base destructor. This is retail-binary evidence only; exact source identity, runtime MissionScript behavior, concrete layouts beyond observed fields, and rebuild parity remain unproven.

| Address | Interface | Evidence |
| --- | --- | --- |
| `0x0052d0a0` | `CIntDataType__Add`: member with the receiver in ECX; takes `rhs` (pointer); returns a pointer | Reads `rhs` through vtable slot `+0x30`, allocates an 8-byte CInt object, and stores the sum. |
| `0x0052d110` | `CIntDataType__Subtract`: member with the receiver in ECX; takes `rhs` (pointer); returns a pointer | Reads `rhs` through slot `+0x30`, allocates an 8-byte CInt object, and stores the difference. |
| `0x0052d180` | `CIntDataType__Multiply`: member with the receiver in ECX; takes `rhs` (pointer); returns a pointer | Reads `rhs` through slot `+0x30`, allocates an 8-byte CInt object, and stores the product. |
| `0x0052d1f0` | `CIntDataType__Divide`: member with the receiver in ECX; takes `rhs` (pointer); returns a pointer | Reads `rhs` through slot `+0x30`, allocates an 8-byte CInt object, and stores the integer quotient. |
| `0x0052d260` | `CIntDataType__Equals`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Returns `this+0x04 == rhs_value`. |
| `0x0052d280` | `CIntDataType__NotEquals`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Returns `this+0x04 != rhs_value`. |
| `0x0052d2a0` | `CIntDataType__Assign`: member with the receiver in ECX; takes `rhs` (pointer); returns nothing | Stores the integer value returned by `rhs` at `this+0x04`. |
| `0x0052d2c0` | `CIntDataType__LessThan`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Returns `this+0x04 < rhs_value`. |
| `0x0052d2e0` | `CIntDataType__GreaterThan`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Returns `this+0x04 > rhs_value`. |
| `0x0052d300` | `CIntDataType__LessOrEqual`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Returns `this+0x04 <= rhs_value`. |
| `0x0052d320` | `CIntDataType__GreaterOrEqual`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Returns `this+0x04 >= rhs_value`. |
| `0x0052d390` | `CDataType__Destructor`: member with the receiver in ECX; no stack arguments; returns nothing | Base destructor that restores the base CDataType vtable pointer. |

## Boolean datatype slots

Static evidence identifies three adjacent boolean datatype vtable slots.
The factory/type-id mapping installs `CFloatDataType` vtable `0x005e4ea4` for
type 2 and the observed `CBoolDataType` vtable region for type 4. Exact source
identity, concrete layouts, runtime MissionScript behavior, and rebuild parity
remain unproven.

| Address | Interface | Evidence |
| --- | --- | --- |
| `0x0052e420` | `CBoolDataType__Equals`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Bool equality slot at data pointer `0x005e4d68`; `RET 0x4`, rhs read through datatype vtable slot `+0x3c`, compare against the byte at `this+0x04`. |
| `0x0052e440` | `CBoolDataType__NotEquals`: member with the receiver in ECX; takes `rhs` (pointer); returns a bool | Bool inequality slot at data pointer `0x005e4d6c`; `RET 0x4`, rhs read through datatype vtable slot `+0x3c`, compare against the byte at `this+0x04`. |
| `0x0052e460` | `CBoolDataType__Assign`: member with the receiver in ECX; takes `rhs` (pointer); returns nothing | Bool assignment slot at data pointer `0x005e4d64`; `RET 0x4`, rhs read through datatype vtable slot `+0x3c`, store returned byte at `this+0x04`. |

## Class Hierarchy (from RTTI)

```
CDataType                    (base class)
  +-- CIntDataType          (integer values)
  +-- CFloatDataType        (floating point; type-id 2 installs vtable 0x005e4ea4)
  +-- CBoolDataType         (boolean byte value; type-id 4 installs observed vtable region 0x005e4d50)
  +-- CStringDataType       (null-terminated strings)
  +-- CPositionDataType     (3D vector positions)
  +-- CThingPtrDataType     (smart pointers to game things)
```

**RTTI Strings Found:**
- `.?AVCDataType@@` at 0x0064c598
- `.?AVCIntDataType@@` at 0x0064c5b0
- `.?AVCBoolDataType@@` at 0x0064cb20
- `.?AVCPositionDataType@@` at 0x0064cbe0
- `.?AVCFloatDataType@@` at 0x0064cc00
- `.?AVCThingPtrDataType@@` at 0x0064cc20
- `.?AVCStringDataType@@` at 0x0064cc40

## VTable Addresses

| Class | VTable Address | First Entry |
|-------|----------------|-------------|
| CIntDataType | 0x005e4af8 | CDataType__ScalarDeletingDestructor |
| CFloatDataType | 0x005e4ea4 | CDataType__ScalarDeletingDestructor |
| CStringDataType | 0x005e4e4c | CStringDataType__ScalarDeletingDestructor |
| CBoolDataType / boolean result (observed vtable region) | 0x005e4d50 | CDataType__ScalarDeletingDestructor |
| CThingPtrDataType | 0x005e4df8 | CThingPtrDataType__ScalarDeletingDestructor |
| CPositionDataType | 0x005e4da4 | CDataType__ScalarDeletingDestructor |
| CDataType (base) | 0x005e4b4c | (abstract base) |

## Functions (38 total)

### Factory Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052ec60 | CDataType__CreateFromType | Factory - creates data type from type ID (1-6 switch) |

**Type IDs in CreateFromType:**
- 1 = CIntDataType (size 8, vtable 0x005e4af8)
- 2 = CFloatDataType (size 8, vtable `0x005e4ea4`)
- 3 = CStringDataType (size 8, vtable 0x005e4e4c)
- 4 = CBoolDataType / boolean result (size 8, observed vtable region `0x005e4d50`; slots include `0x005e4d64`, `0x005e4d68`, and `0x005e4d6c`)
- 5 = CThingPtrDataType (size 8, vtable 0x005e4df8)
- 6 = CPositionDataType (size 0x14, vtable 0x005e4da4)

### CDataType (Base Class)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052d390 | CDataType__Destructor | Base destructor - sets vtable to base |
| 0x0052f670 | CDataType__ScalarDeletingDestructor | Scalar deleting destructor wrapper |

### CIntDataType (Integer Values)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052d0a0 | CIntDataType__Add | Returns new CIntDataType with sum |
| 0x0052d110 | CIntDataType__Subtract | Returns new CIntDataType with difference |
| 0x0052d180 | CIntDataType__Multiply | Returns new CIntDataType with product |
| 0x0052d1f0 | CIntDataType__Divide | Returns new CIntDataType with quotient |
| 0x0052d260 | CIntDataType__Equals | Returns bool (this == other) |
| 0x0052d280 | CIntDataType__NotEquals | Returns bool (this != other) |
| 0x0052d2a0 | CIntDataType__Assign | Assigns value from other |
| 0x0052d2c0 | CIntDataType__LessThan | Returns bool (this < other) |
| 0x0052d2e0 | CIntDataType__GreaterThan | Returns bool (this > other) |
| 0x0052d300 | CIntDataType__LessOrEqual | Returns bool (this <= other) |
| 0x0052d320 | CIntDataType__GreaterOrEqual | Returns bool (this >= other) |

### CFloatDataType (Floating Point)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052ef50 | CFloatDataType__Add | Returns new CFloatDataType with sum |
| 0x0052efc0 | CFloatDataType__Subtract | Returns new CFloatDataType with difference |
| 0x0052f030 | CFloatDataType__Multiply | Returns new CFloatDataType with product |
| 0x0052f0a0 | CFloatDataType__Divide | Returns new CFloatDataType with quotient |
| 0x0052f110 | CFloatDataType__Equals | Returns bool (this == other) |
| 0x0052f140 | CFloatDataType__NotEquals | Returns bool (this != other) |
| 0x0052f170 | CFloatDataType__Assign | Assigns value from other |
| 0x0052f190 | CFloatDataType__LessThan | Returns bool (this < other) |
| 0x0052f1c0 | CFloatDataType__GreaterThan | Returns bool (this > other) |
| 0x0052f1f0 | CFloatDataType__LessOrEqual | Returns bool (this <= other) |
| 0x0052f220 | CFloatDataType__GreaterOrEqual | Returns bool (this >= other) |

### CStringDataType (Strings)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052f2c0 | CStringDataType__Clone | Creates copy of string data type |
| 0x0052f360 | CStringDataType__Equals | String comparison (strcmp) |
| 0x0052f430 | CThingPtrDataType__Print | Assign / rebind the thing slot at `this+4` via SetReader (Print is the table label) |
| 0x0052f690 | CStringDataType__InitFromString | Initialize from C string |
| 0x0052f720 | CStringDataType__ScalarDeletingDestructor | Scalar deleting destructor |
| 0x0052f740 | CStringDataType__Destructor | Frees string buffer |
| 0x0052f790 | CStringDataType__ReadFromBuffer | Read string from DXMemBuffer |

### CPositionDataType (3D Vectors)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052f8a0 | CPositionDataType__SubtractPosition | Returns new position (this - other) |
| 0x0052f920 | CPositionDataType__ScaleByFloat | Returns new position (this * scalar) |

### CThingPtrDataType (Smart Pointers)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052f470 | CThingPtrDataType__Clone | Creates copy with reference counting |
| 0x0052f550 | CThingPtrDataType__ScalarDeletingDestructor | Scalar deleting destructor |
| 0x0052f570 | CThingPtrDataType__Destructor | Releases thing reference |

## Layouts

| Class | Size | Fields |
| --- | --- | --- |
| `CDataType` (base) | 4 | `+0x00` vtable |
| `CIntDataType`, `CFloatDataType`, `CBoolDataType` | 8 | `+0x04` the integer, float or bool value |
| `CStringDataType` | 8 | `+0x04` pointer to the NUL-terminated string |
| `CPositionDataType` | `0x14` | `+0x04` x, `+0x08` y, `+0x0C` z, `+0x10` a fourth float (use unknown) |
| `CThingPtrDataType` | 8 | `+0x04` reference to the game thing (reference-counted) |

## Error Messages

| Address | String |
|---------|--------|
| 0x0064cc58 | "FATAL ERROR: unknown data type type %d" |
| 0x005fdc28 | "ERROR_INVALID_DATATYPE" |
| 0x005fe7e4 | "ERROR_DATATYPE_MISMATCH" |

## Related Functions (Not in DataType.cpp)

These functions reference DataType.cpp path but are from other source files:

| Address | Name | Source File | Notes |
|---------|------|-------------|-------|
| 0x0052d040 | CAsmInstruction__GetAttributeValue | AsmInstruction.cpp | Gets attribute, returns CIntDataType on error |
| 0x0052d3d0 | CAsmInstruction__SpawnFromOpcode | AsmInstruction.cpp | Creates instruction from opcode |

## Memory Allocation

All data types use `OID__AllocObject()` for allocation with:
- Pool ID: 0x18 (data types pool) or 0x76 (string data)
- Line number tracking for debugging

## Notes

1. **Factory type-id mapping in the retail binary** - type `2` installs `CFloatDataType` vtable `0x005e4ea4`, while type `4` installs the observed `CBoolDataType` region containing `CBoolDataType__Assign`, `CBoolDataType__Equals`, and `CBoolDataType__NotEquals`. Exact original enum spelling remains unproven.

2. **Virtual method dispatch** - All operations (Add, Subtract, etc.) call virtual methods on the other operand via vtable offsets:
   - 0x30 = GetAsInt()
   - 0x34 = GetAsFloat()
   - 0x38 = GetAsString()
   - 0x40 = GetAsThing()
   - 0x44 = GetAsPosition()
   - 0x48 = Clone()

3. **Exception handling** - All functions set up SEH (Structured Exception Handling) via ExceptionList manipulation

4. **Unwind handlers** - 6 exception unwind handlers at 0x005d69c0-0x005d6a63 reference DataType.cpp for cleanup

## Discovery Method

Found via xrefs to debug path string at 0x0064cc80. 19 total references:
- 7 in CDataType__CreateFromType (factory cases)
- 6 in Unwind@ exception handlers
- 6 in other DataType class methods
