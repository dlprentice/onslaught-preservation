# DXTrees.cpp - Function Mappings

Status: active static function map
Last updated: 2026-10-22 (reconstructed code and research-campaign records removed)
Summary: the fast tree batch: two card buffers built from the map, how a destroyed tree is hidden, and the fast/close selection facts the rebuild uses.
Evidence: MEASURED — pristine instructions; the fast/close selection section is the rebuild-cited part.
Specimen: pristine `<maintainer evidence>/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `C:\dev\ONSLAUGHT2\DXTrees.cpp` (allocator file string `0x006529b0`) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> DirectX-specific tree rendering system for environmental vegetation

## Overview

DXTrees.cpp implements the specialized fast-tree batch rendered after ordinary
world objects and the global `CImposter` batch. It is not the owner of the close
tree mesh/far-imposter decision. `CDXTrees` keeps one buffer for standing cards
and one for a height-gated horizontal supplement.

## Focused retail-tree correction (2026-07-22)

This focused read-back supersedes the older shadow/LOD guesses later in this
note:

- `CRTTree__Init` (`0x004DD7B0`) owns both a `CMesh` and a six-view
  `CImposter`. `CRTTree__VFuncSlot02_BuildRenderOutputs` (`0x004DD960`) submits
  the mesh when horizontal camera distance is at or inside
  `g_MeshQualityDistance`, or while the tree is falling. The image value at
  `0x006321A0` is `30.0`; boot options can overwrite it from
  `defaultoptions.bea` OptionsTail `+0x0C`. The installed max-quality snapshot
  read on 2026-07-22 stores `70.0` (`0x428C0000`) there. The separate capability
  branch in `CRTTree__Init` writes `45.0`.
- `CRTTree__VFuncSlot03_UpdateVisibilityState` (`0x004DD850`) queues
  `CDXEngine__RenderImposterBillboardSet` (`0x00543300`) outside that boundary.
  The helper calls `CDXImposter__BuildQuadGeometry` six times: four faces whose
  basis advances by about `-π/2`, then two faces tilted by `+π/2` and `+3π/2`.
  Serialized half-extents are scaled by `0.99`. The exact six atlas cells and
  extents for every Level 100 pine are recorded in the
  Level 100 asset note (`rebuild/OnslaughtRebuild.Godot/Assets/Level100/README.md` in Onslaught-Career-Editor).
- `CDXTrees__BuildTreeGeometry` emits an additional primary standing card per
  tree. Its CTree virtual selector at `0x004F6540` computes
  `(tree_object_address >> 4) & 3`; a placement ordinal is not equivalent static
  evidence. The second buffer is a horizontal square using serialized `VIEW` 4
  and half-size `selected_standing_half_width * 0.7`.
- `CDXTrees__Render` always draws the primary buffer. It draws the horizontal
  buffer only when absolute camera-height minus sampled-ground-height exceeds
  `20.0`; that comparison is not horizontal range LOD.
- Default/world rendering enables alpha test with reference `8` and
  greater-or-equal comparison. The close mesh pass uses anisotropic stage-zero
  minification, linear mip filtering, max anisotropy `4`, and `-1` mip bias.
  The fast batch uses point min/mag and alpha reference `8`; its mip filter
  setting is not established here.
  The observed `0x008554FC = 1` chooses its unlit white-factor `MODULATE2X`
  branch before active Level 100 fog.

## Function list

| Address | Function |
| --- | --- |
| `0x0055a350` | `CDXTrees__CDXTrees` |
| `0x0055a360` | `CDXTrees__scalar_deleting_dtor` |
| `0x0055a380` | `CDXTrees__dtor` |
| `0x0055a390` | `CDXTrees__Init` |
| `0x0055a3b0` | `CDXTrees__ReleaseBuffers` (returns `int`) |
| `0x0055a400` | `CDXTrees__Reset` |
| `0x0055a420` | `CDXTrees__BuildTreeGeometry` |
| `0x0055aa10` | `CDXTrees__Render` |
| `0x0055ae40` | `CDXTrees__HideTree` (takes the tree object) |

All are members with the receiver in ECX. Slot 1 of the `CDXTrees` vtable (`0x005e59d8`) points at
`0x005019c0`, a stub shared with other classes whose body is `XOR EAX,EAX; RET`.

**Key Features:**
- One standing fast card per retained tree owner
- A separate camera-elevation-gated horizontal card buffer
- Quadtree-based enumeration of tree owners
- Vertex buffer locking for dynamic hiding of destroyed trees

## Class Structure

### CDXTrees

**Size:** ~0x14 bytes (estimated)

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x00 | void* | vtable | Points to 0x005e59d8 |
| 0x04 | ??? | ??? | Inherited from base class |
| 0x08 | CVBufTexture* | m_pTreeBuffer1 | Main tree vertex buffer |
| 0x0C | CVBufTexture* | m_pTreeBuffer2 | Secondary tree vertex buffer |
| 0x10 | int | m_nTreeCount | Number of trees in buffers |

### Vtable (0x005e59d8)

| Index | Address | Function |
|-------|---------|----------|
| 0 | 0x0055a360 | CDXTrees__scalar_deleting_dtor |
| 1 | 0x005019c0 | VFuncSlot_09_005019c0 |
| 2 | 0x00405930 | (inherited) |
| 3 | 0x00405930 | (inherited) |
| 4 | 0x0055a3b0 | CDXTrees__ReleaseBuffers |

Slots 5-15 after the table hold float and data values, not further function pointers.

## Functions

### CDXTrees__CDXTrees (0x0055a350)
**Constructor**

Stores the `CDXTrees` vtable pointer.

---

### CDXTrees__scalar_deleting_dtor (0x0055a360)
**Scalar Deleting Destructor**

MSVC-generated destructor that optionally frees memory.

---

### CDXTrees__dtor (0x0055a380)
**Destructor**

Restores the `CDXTrees` vtable pointer and calls the base-class destructor at `0x00512d50`.

---

### CDXTrees__Init (0x0055a390)
**Initialize**

Registers itself with the shader render list at `0x00855bb0` through `CShaderBase__Init`
(`0x00512ca0`, called at `0x0055a393`-`0x0055a399`) and sets both buffer pointers (`this+0x08`,
`this+0x0C`) to NULL.

---

### CDXTrees__ReleaseBuffers (0x0055a3b0)
**Release Vertex Buffers**

Destroys and frees each `CVBufTexture` that exists, nulls both pointers and returns 0.

---

### CDXTrees__Reset (0x0055a400)
**Reset**

Releases the buffers through its own virtual slot `+0x10` (`ReleaseBuffers`), then unlinks
itself from the render list at `0x00855bb0` through `CShaderBase__UnlinkFromRenderObjectLists`
(`0x00512cc0`).

---

### CDXTrees__BuildTreeGeometry (0x0055a420)
**Build Tree Geometry** - Main function

Iterates through the world quadtree to find all tree objects and builds vertex/index buffers for rendering them as billboards.

**Debug References:**
- Line 0x5E (94): First CVBufTexture allocation
- Line 0x6A (106): Second CVBufTexture allocation

**Algorithm:**
1. Release existing buffers if present
2. Allocate two new CVBufTexture objects through `CDXMemoryManager__Alloc`
   (size 0x68, memory type 0x1f, `DXTrees.cpp` lines 94 and 106)
3. Configure vertex format: FVF 0x152 (XYZ | NORMAL | DIFFUSE | TEX1), 0x24 bytes per vertex
4. Configure index format: 0x65, 2 bytes per index
5. Iterate through quadtree levels 4 down to 0 while the grid shift runs 0 up to 4
   (`0x0055a55e`, `0x0055a9d1`-`0x0055a9e2`): the grid is 64 cells across at level 4 and 4 at level 0
6. For each cell, query CMapWho for tree objects (flag 0x2000000)
7. For each tree, create one encoded standing quad and one horizontal quad (4 vertices and 6 indices each)
8. Add vertices with UV coordinates from tree texture atlas

**Key Constants:**
- Vertex size: 0x24 (36 bytes)
- 4 vertices per tree billboard
- 6 indices per tree (2 triangles)
- Uses flag 0x2000000 to identify tree objects

---

### CDXTrees__Render (0x0055aa10)
**Render Trees**

Renders both prepared fast-tree buffers.

**Algorithm:**
1. Check if tree count > 0
2. If buffers not built, call BuildTreeGeometry
3. Set up render states (blending, alpha test, etc.)
4. Bind texture
5. Render first buffer (main trees)
6. Render the second buffer only when the absolute difference between the camera height and the
   ground height sampled under the camera exceeds 20 units
7. Restore render states

**Key Features:**
- Camera-elevation gate for the horizontal supplement (20.0-unit threshold)
- Multiple render state changes for alpha blending
- The primary buffer is drawn with `RenderIndexedNoValidate`, the horizontal one with `RenderIndexed`

---

### CDXTrees__HideTree (0x0055ae40)
**Hide Tree**

Hides one tree's cards in both buffers. Its only caller is
`CRTTree__Destructor` (`0x004de001`), which passes its own `this`: the argument
is the `CRTTree`, whose `+0x30` word is the tree's card index (written at
`0x0055a82a`, or `0xffff` at `0x0055a98c`).

**Algorithm:**
1. Return if the index is negative or either buffer is missing.
2. Standing buffer: lock the tree's four 0x24-byte vertices and zero dwords 3-5
   of each (`+0x0c`, `+0x30`, `+0x54`, `+0x78`). Standing vertices hold the tree
   centre in dwords 0-2 and the corner offset in dwords 3-5, the FVF normal slot
   (`0x0055a686-0x0055a6d7`), so each card collapses onto its centre.
3. Horizontal buffer: zero dwords 0-2 of each vertex (`+0x00`, `+0x24`, `+0x48`,
   `+0x6c`; `0x0055af26-0x0055af72`), which are the real corner positions there.
4. Unlock each buffer.

## Related Systems

### CVBufTexture
Vertex buffer wrapper class with texture support. Key methods used:
- `SetVBFormat(format, flags, stride, count, mode)`
- `SetIBFormat(format, flags, size, mode)`
- `SetPersist()`
- `AddVertices(data, count)`
- `AddIndices(data, count)`
- `RenderIndexed(start, count, base, flags)`
- `RenderIndexedNoValidate(start, count, flags)`
- `LockRange(offset, size, ppData, flags)`
- `Unlock()`

### CMapWho
Quadtree-based spatial partitioning system. Used to find tree objects in world cells.
- Entry flag 0x2000000 identifies tree objects
- GetOwner() returns CThing pointer

### tree.cpp
See the retained `CTree__UpdateFallingTree` (in the decompilation notes, not yet published)
note for the individual falling-tree path.

## Global References

| Address | Usage |
|---------|-------|
| 0x00854e6c | Flag affecting vertex buffer format |
| 0x00704290 | Quadtree level pointers |
| 0x009cc160 | Matrix data for rendering |
| 0x009cc190-19c | Render parameters |

## Callers

| Address | Function | Context |
|---------|----------|---------|
| 0x0046cfe2 | CGame__LoadLevel | Called during level load |
| 0x0055aa2e | CDXTrees__Render | Called if buffers not built |

## Notes

1. **Two-Buffer System**: The first buffer owns standing fast cards. The second owns horizontal `VIEW`-4 cards gated by camera height above/below sampled ground; it is not a shadow buffer or horizontal-distance LOD.

2. **Quadtree Integration**: Tree geometry is built by iterating through the CMapWho quadtree system, which provides efficient spatial queries.

3. **Dynamic Hiding**: Trees can be hidden at runtime (when destroyed) by zeroing their vertex positions, avoiding the need to rebuild the entire buffer.

4. **Allocation**: Both CVBufTexture objects are allocated through `CDXMemoryManager__Alloc` (size 0x68, memory type 0x1f, `DXTrees.cpp` lines 94 and 106).
