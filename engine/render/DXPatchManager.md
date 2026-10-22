# DXPatchManager.cpp

Status: active — historical subsystem notes with scoped corrections below
Last updated: 2026-10-22 (reconstructed code and research-campaign records removed; findings unchanged)
Summary: retained patch-manager analysis; the Engine shutdown receiver is re-derived from pristine bytes, while other historical claims remain to audit.
Source File: retail `DXPatchManager.cpp` label (implementation absent from pinned source); caller `references/Onslaught/DXEngine.cpp` | Binary: pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> DirectX terrain patch manager for LOD (Level of Detail) rendering
> Debug source path string for `DXPatchManager.cpp`: `0x0065211c`

## Engine receiver correction — September 26

In pristine `<maintainer evidence>/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
`CDXEngine::ShutDown` sets ECX to the global `0x009c64d8` at `0x0053d462`,
then calls `0x005506e0` at `0x0053d467`. Earlier notes described that receiver
as Engine fields, which was wrong. The caller is the case-distinct
`ShutDown` method in slot 3, not base `Shutdown` in slot 0; see the
interface correction (archived research record, not published).
This verifies the call and receiver, not every historical assertion about the
callee's body, object lifetime or complete subsystem behavior.

## Device lifecycle identity — September 27

`0x0048f320` is `CLandscapeVB__InitDeviceObjects`, formerly
`CLandscapeVB__RestoreAndRebuildIfDirty`. Fresh complete-body and caller/RTTI
checks place it in the initialization interface, not the restoration phase.
The [platform note](../source/core/platform-system.md#retail-device-lifecycle--september-27-correction)
records the source/retail list and ordering differences. Its body calls
`0x00500120`, now `CVBuffer__InitDeviceObjects`; it retains that return while
conditionally invoking `0x0048f210` based on receiver member `+0x40`.
No full terrain/resource algorithm or historical field-name claim is certified.

## Name corrections — 2026-07-28

Superseded in place against the 2026-07-27 function-name table. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at the area index (in the decompilation notes, not yet published).
Old cell text is quoted below rather than deleted, so a reader who remembers the
withdrawn label can tell it was corrected and not lost.

| Address | Superseded label | Current name | Correction |
| --- | --- | --- | --- |
| `0x0048f320` | `CDXPatch__RestoreAndRebuildIfDirty` | `CLandscapeVB__InitDeviceObjects` | class corrected historically; lifecycle method rederived September 27 |
| `0x0048f620` | `CDXEngine__RenderPostMissionOverlayAndMenu` | `CLevelBriefingLog__Render` | class prefix and suffix both moved |
| `0x00550380` | `CDXPatch__Constructor` | `CLandscapeVB__ctor` | class prefix and suffix both moved |

Where a row's **suffix** moved rather than only its class prefix, the behavioural
text beside it in this note was written for the old name. This sweep corrected
names against the export and re-derived no behaviour, so read any such gloss as
unverified against the new name until it is re-measured.

---

## Overview

DXPatchManager manages terrain patches for the landscape LOD system. It allocates pools of `CDXPatch` objects at different detail levels (likely near/medium/far) and manages landscape textures with mipmap levels.

The system uses three patch pools with different vertex buffer configurations:
- Pool 1: 800 patches, vertex size 2 (low detail)
- Pool 2: 300 patches, vertex size 4 (medium detail)
- Pool 3: 90 patches, vertex size 8 (high detail)

Each patch contains vertex buffer data for terrain geometry rendering.

## Classes

### CDXPatchManager
Main manager class that owns patch pools and landscape textures.

**Layout (inferred):**

| Offset | Field |
| --- | --- |
| `+0x00` | pool for detail level 1 |
| `+0x04` | array of 48 `CLandscapeTexture` |
| `+0x08` | pool for detail level 2 |
| `+0x0C` | count for pool 2 |
| `+0x10` | pool for detail level 3 |
| `+0x14` | count for pool 3 |

### CDXPatch
Individual terrain patch with vertex buffer data.

**Layout (inferred), 0x50 bytes, derived from `CVBuffer`:**

| Offset | Field |
| --- | --- |
| `+0x00` | vtable, `0x005e5114` |
| `+0x2C` | grid origin X used by the rebuild |
| `+0x30` | grid origin Z used by the rebuild |
| `+0x34` | height-sample step |
| `+0x38` | vertex count, `(grid_step+1)^2` |
| `+0x3C` | allocation slot, 16-bit (`-1` = free) |
| `+0x40` | rebuild dirty/ready flag |
| `+0x44` | grid size/source step (2, 4 or 8) |
| `+0x4C` | copy of the tile record's metadata |

### CDXPatchPool (helper struct)
Pool of patches at a specific detail level.

**Layout (inferred):** `+0x00` the patch array, `+0x04` the pool capacity.

## Functions (13 documented rows)

| Address | Name | Size | Notes |
|---------|------|------|-------|
| 0x0048f1e0 | CDXPatch__CreateGridVertexBuffer | 0x30 | Creates a grid vertex buffer from one `grid_step` argument |
| 0x0048f210 | CDXPatch__RebuildHeightGridVertexBuffer | 0x110 | Rebuilds height-sampled grid vertices |
| 0x0048f2f0 | CDXPatch__SetGridOriginStepAndRebuild | 0x30 | Sets patch grid origin/step fields and rebuilds vertices from `CDXLandscape__UpdateLOD` callsite `0x00546fe6` |
| 0x0048f320 | CLandscapeVB__InitDeviceObjects | 0x1e | September 27: DeviceObject initialization interface; earlier field/rebuild semantics remain separately bounded |
| 0x00550380 | CLandscapeVB__ctor | 0x20 | Sets vtable to 0x005e5114 |
| 0x005503a0 | CDXPatch_T3_005503a0 | 0x10 | Thunk to the `CVBuffer` destructor. Earlier analysis called it `CDXPatch__Destructor_thunk`; no `CDXPatch` type descriptor exists in the image and no vtable owns this address, so the class prefix is unproven. |
| 0x005503b0 | CDXPatchManager__ReleasePatches | 0x20 | Releases patch pool via vtable call |
| 0x005503d0 | CDXPatchManager__ResetPatchSlots | 0x30 | Resets all slot indices to -1 (0xFFFF) |
| 0x00550400 | CDXPatchManager__AllocatePatchSlot | 0x30 | Finds free slot, returns patch pointer |
| 0x00550430 | CDXPatchManager__Init | 0x250 | Main initialization, creates 3 pools |
| 0x005506e0 | CDXPatchManager__Shutdown | 0x50 | Frees all pools and textures |
| 0x00550730 | CDXPatch__FreeData | 0x20 | Frees patch data buffer at +0x0C |
| 0x00550750 | CDXPatchManager__DeserializeAll | 0x98 | Loads patch data from resource file |

## Function Details

### CDXPatchManager__Init (0x00550430)

**Interface:** a member taking the three pool counts (`RET 0xc`).

**Called from:** DXEngine initialization (0x0053d5f0) with parameters (800, 300, 90)

**Purpose:** Initializes the patch manager with three pools of terrain patches at different LOD levels.

**Key Operations:**
1. Allocates CDXPatchManager structure (0x1C bytes)
2. Creates patch pool 1 with `pool1Count` patches, LOD level 2
3. Creates patch pool 2 with `pool2Count` patches, LOD level 4
4. Creates patch pool 3 with `pool3Count` patches, LOD level 8
5. Allocates 48 CLandscapeTexture objects (0x9C4 bytes total, 0x34 each)
6. Calls CLandscapeTexture__SetupMipLevel for 3 LOD levels x 16 textures

**Memory allocations:**
- Pool 1: `800 * 0x50 + 4 = 64,004 bytes`
- Pool 2: `300 * 0x50 + 4 = 24,004 bytes`
- Pool 3: `90 * 0x50 + 4 = 7,204 bytes`
- Textures: `0x9C4 = 2,500 bytes`

### CDXPatch__LoadFromFile (0x00550750)

**Interface:** a `CDXPatch` member taking the chunk reader.

**Called from:** CResourceAccumulator__ReadResourceFile (0x004d7200)

**Purpose:** Loads patch vertex data from a resource file during level loading.

**Key Operations:**
1. Reads 3 rows x 16 columns of 4-byte values (mip data) from file
2. Reads count value for vertex data
3. Allocates vertex buffer (`count * 2` bytes)
4. Reads vertex data from file
5. Sets loaded flag at offset +0x08

### CDXPatchManager__AllocatePatchSlot (0x00550400)

**Interface:** a member on the patch pool taking a 16-bit slot id (`RET 0x4`); returns the patch.

**Purpose:** Finds a free patch slot and marks it as allocated.

**Returns:** Pointer to allocated patch, or NULL if pool is full.

**Algorithm:** scans the pool for the first patch whose slot (`+0x3c`) is `-1`, stores the slot id there
and returns that patch; returns null when the pool is exhausted.

### CDXPatchManager__ResetPatchSlots (0x005503d0)

**Interface:** takes the patch pool in ECX.

**Purpose:** Marks all patches in pool as free by setting slot index to -1.

**Used for:** Level unload/reload, freeing all terrain patches.

## Vtables

### CDXPatch vtable at 0x005e5114
```
+0x00: 0x00550320  (no function boundary recovered yet)
+0x04: 0x0048f320  (CLandscapeVB__InitDeviceObjects)
+0x08: 0x00500250  (CVBuffer method)
+0x0C: 0x00500280  (CVBuffer__Release)
+0x10: 0x005002b0  (CVBuffer__ReleaseManaged)
+0x14: 0x00619c40  (unknown)
+0x18: 0x00551fb0  (destructor with free)
+0x1C: 0x00405930  (unknown)
+0x20: 0x00552410  (unknown)
+0x24: 0x00552470  (release resource at +0x6C0)
```

## Related Classes

- **CVBuffer** - Base class for DirectX vertex buffers (vbuffer.cpp)
- **CLandscapeTexture** - Landscape texture with mipmap levels (LandscapeTexture.cpp)
- **CResourceAccumulator** - Resource file loader (ResourceAccumulator.cpp)

## Constants

| Value | Meaning |
|-------|---------|
| 0x50 | CDXPatch structure size (80 bytes) |
| 0x34 | CLandscapeTexture structure size (52 bytes) |
| 0x1C | CDXPatchManager structure size (28 bytes) |
| 0xFFFF | Free slot marker |
| 0x30 | Number of landscape textures (48) |
| 0x10 | Textures per LOD level (16) |

## LOD System

The patch manager implements a terrain LOD system:

| LOD Level | Patch Count | Vertex Grid | Use Case |
|-----------|-------------|-------------|----------|
| 2 | 800 | 3x3 | Distant terrain |
| 4 | 300 | 5x5 | Medium distance |
| 8 | 90 | 9x9 | Near terrain |

Vertex count per patch: `(level + 1)^2`
- LOD 2: 9 vertices
- LOD 4: 25 vertices
- LOD 8: 81 vertices

## Xrefs to Debug Path (0x0065211c)

| Address | Function | Line# | Context |
|---------|----------|-------|---------|
| 0x0055044d | CDXPatchManager__Init | 0x54 | OID__AllocObject call |
| 0x00550479 | CDXPatchManager__Init | 0x11 | Patch pool allocation |
| 0x005504f4 | CDXPatchManager__Init | 0x11 | Patch pool allocation |
| 0x0055057d | CDXPatchManager__Init | 0x11 | Patch pool allocation |
| 0x005505f1 | CDXPatchManager__Init | 0x5b | Texture array allocation |
| 0x005507b5 | CDXPatchManager__DeserializeAll | 0x94 | Vertex buffer allocation |

## Notes

1. **Not in Stuart's source:** DXPatchManager.cpp is likely a PC port addition or DirectX-specific implementation not present in the original console source.

2. **Memory management:** Uses OID__AllocObject (0x005490e0) with allocation type 0x35 for all allocations.

3. **Exception handling:** Multiple Unwind@* functions in exception handler chain for cleanup on allocation failure.

4. **Relationship to DXLandscape:** Works closely with CDXLandscape for terrain rendering, providing the patch geometry that gets textured and rendered.

## Static evidence per function (2026-05)

| Address | Function | Static evidence |
| --- | --- | --- |
| `0x0048f1e0` | `CDXPatch__CreateGridVertexBuffer` | `RET 0x4`: one stack argument, the grid step. Stores it at `+0x44`, computes `(grid_step+1)^2` at `+0x38`, clears patch fields, writes slot marker `+0x3c = 0xffff`, and calls `CVBuffer__Create` with `0x14`-byte vertices and flags `0x102`. |
| `0x0048f210` | `CDXPatch__RebuildHeightGridVertexBuffer` | Locks the buffer, walks a square grid from the X/Z origin at `+0x2c/+0x30` with step `+0x34`, samples `CWorld__GetHeightSamplePacked16`, writes `0x14`-byte vertex rows, unlocks, and marks `+0x40`. |
| `0x0048f2f0` | `CDXPatch__SetGridOriginStepAndRebuild` | Earlier analysis called it `CDXLandscape__SetUpdateBoundsAndRebuildVB`. `RET 0x10`: four stack arguments after the receiver. `CDXLandscape__UpdateLOD` calls it at `0x00546fe6` straight after `CDXPatchManager__AllocatePatchSlot` returns a patch, passing two tile coordinates scaled by `8`, a grid step of `4 >> lod_slot` and the tile record's metadata from `[ESI+0x0b]`. The body stores them at `+0x2c`, `+0x30`, `+0x34` and `+0x4c`, then calls `CDXPatch__RebuildHeightGridVertexBuffer`. |
| `0x0048f320` | `CLandscapeVB__InitDeviceObjects` | Slot 1 of vtable `0x005e5114`. Calls the `CVBuffer` initialiser, rebuilds when `+0x40` is nonzero, and returns the initialiser's result. |
| `0x00550380` | `CLandscapeVB__ctor` | The vector-constructor calls at `0x005504ab`, `0x0055052a` and `0x005505ad` use it for each `0x50`-byte pool entry. Calls `CVBuffer__ctor_base`, installs vtable `0x005e5114` and returns the receiver. |
| `0x005503a0` | `CDXPatch_T3_005503a0` | The vector-destructor calls at `0x005504a6`, `0x00550525` and `0x005505a8` pass it beside the constructor. Tail-jumps to `CVBuffer__dtor_base`. |
| `0x005503b0` | `CDXPatchManager__ReleasePatches` | Passed as a callback at `0x005506f0` over 8-byte pool entries; releases the array through vtable slot 0 with delete flag `3` and clears the pointer. |
| `0x005503d0` | `CDXPatchManager__ResetPatchSlots` | `CDXLandscape__Reset` (`0x00545392`) and `CDXEngine__InvalidateLandscapeTilesAndPatchSlots` (`0x005473d5`) pass a pool in ECX. Walks the entries with `0x50` stride writing `0xffff` at `+0x3c`. |
| `0x00550400` | `CDXPatchManager__AllocatePatchSlot` | `CDXLandscape__UpdateLOD` calls it at `0x00546fa6` with one stack slot id. |
| `0x00550430` | `CDXPatchManager__Init` | `CDXEngine__Init` calls it at `0x0053d6c3` with `800`, `300` and `90`. Allocates the pool table and three `0x50`-byte patch arrays, constructs the entries, creates grid vertex buffers for steps `2`, `4` and `8`, allocates 48 `CLandscapeTexture` entries and initialises three 16-texture mip groups. |
| `0x005506e0` | `CDXPatchManager__Shutdown` | Destroys the pool table through `CDXLandscape__DestroyArrayWithCallback`, frees the count header, clears the pool pointer, releases the landscape-texture vector and clears its pointer. |
| `0x00550730` | `CDXPatch__FreeData` | Reached from `0x005120cb`. Frees the data pointer at `+0x0c` through `CDXMemoryManager__Free` when it is set, then clears it. |
| `0x00550750` | `CDXPatch__LoadFromFile` | `CResourceAccumulator__ReadResourceFile` calls it at `0x004d7875`. Reads `3x16` dwords into `+0x10` and a data count into `+0xd0`, allocates `count*2` bytes (DXPatchManager.cpp line `0x94`), reads 16-bit data into `+0x0c` and marks `+0x08` loaded. |

`0x0048f180` is `CLandscapeTexture__InvalidateTileMaskOrRefreshAll`.

The vtable at `0x005e5114` is only partly recovered: slot 0 points at `0x00550320`, which has no function
boundary yet; the region around it calls `0x005503a0` at `0x0055035c`. The exact `CDXPatch`,
`CDXPatchManager`, patch-pool, `CLandscapeTexture` and serialised patch-data layouts, runtime terrain
rendering and LOD behaviour remain unproven.
