# DXBattleLine.cpp Function Mappings

Status: active static function map
Last updated: 2026-10-22 (decompiler-style signatures and research-campaign records removed)
Summary: the HUD battle-line renderer: its texture-backed object, terrain heightmap sampling, mesh
triangulation, marker vertices and three-pass render.

> Debug source path string for `DXBattleLine.cpp`: `0x00650324`. Functions found: 13.

## Names

Ten helpers this note uses were unnamed in earlier analysis and now carry names:
`CHeightField__Collide` (`0x0047eb80`), `CHeightField__Normal` (`0x0047ec60`), `PCLTShell__STS`
(`0x00513820`), `D3DStateCache__SetState114Raw` (`0x00513930`), `PCLTShell__D3D_SetTexture` (`0x00513a50`),
`CEngine__DrawIndexedPrimitives` (`0x00513c70`), `CWaterRenderSystem__ValidateVBufferAndMarkReady`
(`0x00527cc0`), `CDXLandscape__ValidateDeviceAndUpdateValidSoFar` (`0x00527d20`),
`CVBufTexture__DrawSpriteEx` (`0x00555be0`) and `CDXTexture__GetAnimatedFrame` (`0x00558690`).

---

## Overview

CDXBattleLine is a DirectX rendering class that visualizes the "battle line" on the HUD - the tactical map showing territory control and unit positions. It inherits from CTexture and manages heightmap sampling, BattleLine mesh construction, marker vertex updates, and multi-pass rendering.

`CDXBattleLine__BuildMesh` allocates and uses a separate 0x18-byte `Triangulate` work object, so the
helper island at `0x004f7170..0x004f7940` belongs to `Triangulate`, not to `CDXBattleLine`:
`Triangulate__CreateQuadMesh` (`0x004f7170`), `Triangulate__InsertPointOrAppendVertex` (`0x004f7460`),
`Triangulate__SplitTriangleAtPointAndLegalizeEdges` (`0x004f74b0`),
`Triangulate__TryFlipSharedEdgeForQuality` (`0x004f7660`), `Triangulate__FindTriangleByDirectedEdge`
(`0x004f78c0`) and `Triangulate__RelaxMeshByEdgeFlips` (`0x004f7940`). Its context is
`CDXBattleLine__BuildMesh` (`0x0053a5e0`), `CDXBattleLine__RenderTriOverlayPass` (`0x0053b470`) and
`CHud__RenderBattleline` (`0x00487d10`).

`CHud__RenderBattleline` calls `CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices`
(`0x00414cb0`) at `0x00488071`. That helper calls `SharedState__IsTimer88PendingAndState7CZero`
(`0x004e6610`) at `0x00414d1c` and `CDXBattleLine__AppendOverlayVertex` (`0x0053b5f0`) at `0x00414ce2`
and `0x00414d35`; it walks the battle-line list `0x00855140` and the influence/deferred list
`0x008550a0`, appending yellow and red overlay vertices.

`0x0053a140` is a one-instruction `JMP 0x00556d90` thunk into the `CDXSurf` destructor, named
`CDXBattleLine__DestructorThunk` so that it is not confused with the destructor itself. The overlay append
helper takes three stack arguments (`RET 0xc`).

Runtime battle-line rendering and teardown, the exact `CDXBattleLine`/`CDXSurf` list and vertex layouts and
source-body identity remain open.

## Class Structure

### Vtable at 0x005e4f64

| Offset | Address | Function | Notes |
|--------|---------|----------|-------|
| 0x00 | 0x0053a120 | CDXBattleLine__scalar_deleting_dtor | Proven slot 0 only |
| 0x04 | 0x0053a010 | (no recovered function boundary) | Calls InitMipLevels / UpdateHeightmap through a trampoline |
| 0x08 | 0x0053a040 | (no recovered function boundary) | JMP to `0x00557060` |
| 0x0C | 0x005572c0 | CTextureSequence__ReleaseIfLoaded | Inherited-looking |
| 0x10 | 0x00558600 | (CTexture method) | Inherited |
| 0x14 | 0x00556e90 | (CTexture method) | Inherited |
| 0x18 | 0x00556fc0 | CDXSurf__SetupSurface | Virtual call in Constructor |
| 0x1C | 0x00405930 | (unknown) | - |
| 0x20 | 0x005593a0 | (unknown) | - |

### Object Size

- Size: 0x158 bytes (344 bytes)
- Allocated via OID__AllocObject with alignment 2

### Member Offsets (Partial)

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x00 | vtable* | vtable | Points to 0x005e4f64 |
| 0x04 | CTexture* | m_pBaseTexture | Line/gradient texture |
| 0x08 | CTexture* | m_pOverlayTexture | Created in LoadTextures |
| 0x0C | CTexture* | m_pMarkerTexture | "hud\marker.tga" |
| 0x14 | CTexture* | m_pBEMarkerTexture | "hud\V2\BattleEngineMarker.tga" |
| 0x18 | int | m_nBaseOffset | Base offset for vertex data |
| 0x1C | CIBuffer* | m_pIndexBuffer | Index buffer for mesh |
| 0x20 | int | m_nTriCount | Triangle count from mesh |
| 0x24 | byte | m_nState | State (2 = ready for rendering) |
| 0x48 | float | m_fScaleX | X scale for marker positioning |
| 0x4C | float | m_fScaleY | Y scale for marker positioning |
| 0x50 | float | m_fOffsetX | X offset for marker positioning |
| 0x54 | float | m_fOffsetY | Y offset for marker positioning |
| 0x58 | int | m_overlayPulseBoost | Computed in AppendOverlayVertex |
| 0x5C | int | m_overlayBufferLocked | Set/cleared around dynamic overlay VB lock |
| 0x60 | int | m_overlayVertexCount | Reset by Populate helper; capped at 500 |
| 0x64 | int | m_originX | First constructor argument |
| 0x68 | int | m_originY | Second constructor argument |
| 0x70 | CVBuffer* | m_pVertexBuffer | Vertex buffer for markers |
| 0x74 | ? | m_pRenderTarget | Render target reference |
| 0x78 | CVBuffer* | m_pDynamicVB | 500-vertex dynamic buffer |
| 0x7C | void* | m_dynamicVBWriteCursor | Current write cursor after lock |
| 0x1C (obj) | int | m_nVertexCount | Vertex count from mesh |
| 0x1D (obj) | CIBuffer* | m_pMeshIB | Mesh index buffer |

## Functions

### CDXBattleLine__Constructor (0x0053a050)

**Interface:** Member with the receiver in ECX; takes `origin_x` (int), `origin_y` (int); returns nothing

Initializes the HUD battleline field block. `CHud__Init` passes ECX as the newly allocated field block, then stack constants `-7` and `14`; the function stores those values at `this+0x64/+0x68`, allocates the 0x158 texture-backed CDXBattleLine/CDXSurf object, installs vtable `0x005e4f64`, and creates the line texture as 128x1 or 128x128 based on hardware flags.

**Key Operations:**
1. Stores `origin_x` at offset 0x64 and `origin_y` at offset 0x68
2. Allocates CTexture via OID__AllocObject (0x158 bytes)
3. Calls CTexture__ctor to initialize base class
4. Sets the vtable to `0x005e4f64`
5. Creates texture: 128x128 if (0x00888a90 & 0x20) || 0x0089c924, else 128x1
6. Calls InitMipLevels to initialize texture mip levels

**Called from:** CHud__Init (0x00481450)

---

### CDXBattleLine__scalar_deleting_dtor (0x0053a120)

**Interface:** Member with the receiver in ECX; takes `delete_flags` (byte); returns a pointer

Scalar deleting destructor at vtable slot `0x005e4f64[0]`. `RET 0x4` proves one stack flag after ECX; the body calls `CDXBattleLine__DestructorThunk`, frees `this` when `delete_flags & 1`, and returns `this`.

**Called from:** Vtable slot 0

---

### CDXBattleLine__DestructorThunk (0x0053a140)

**Interface:** Receiver in ECX; no stack arguments; returns nothing

One-instruction `JMP 0x00556d90` thunk to the real `CDXSurf__dtor`; the base destructor at `0x00556d90` is described in `DXSurf.cpp.md` (in the decompilation notes, not yet published).

**Called from:** CDXBattleLine__scalar_deleting_dtor (0x0053a120)

---

### CDXBattleLine__LoadTextures (0x0053a150)

**Interface:** Receiver in ECX; no stack arguments; returns nothing

Loads marker textures and creates vertex/index buffers for battle line rendering.

**Key Operations:**
1. Finds "hud\marker.tga" texture (offset 0x0C)
2. Allocates CVBuffer (0x2c bytes) for markers (offset 0x78)
3. Creates dynamic vertex buffer (500 vertices, stride 0x14, flags 0x44)
4. Finds "hud\V2\BattleEngineMarker.tga" texture (offset 0x14)
5. Allocates overlay CTexture (0x158 bytes, offset 0x08)
6. Creates 128x128 texture with mipmaps

**Called from:** CHud__LoadTextures (0x00481650)

---

### CDXBattleLine__Setup (0x0053a280)

**Interface:** Receiver in ECX; no stack arguments; returns an int

Sets up the battle line for rendering by setting state to 2 and rebuilding the mesh.

**Key Operations:**
1. Saves 0x00889010, sets it to 1
2. Sets state byte at offset 0x24 to 2
3. Calls BuildMesh to generate terrain mesh
4. Restores 0x00889010
5. Returns 1

**Called from:** 0x00481af0 (via JMP)

---

### CDXBattleLine__UpdateHeightmap (0x0053a390)

**Interface:** Receiver in ECX; no stack arguments; returns nothing

Updates the heightmap data by sampling terrain at grid positions. Uses circular mask (radius 0x844 = 2116) to limit area.

**Key Operations:**
1. Gets battle bounds from `CHeightField__RecomputeGridExtentsAndHeightRange`
2. Calculates center and extent with 1.21x padding
3. Iterates over grid (-0x30 to +0x30 in both axes)
4. For each point in circular mask:
   - Samples terrain height via 0x0047eb80
   - Calculates intensity value (0-3 range)
   - Writes to heightmap buffer as short values

**Called from:** BuildMesh (0x0053a5e0)

---

### CDXBattleLine__BuildMesh (0x0053a5e0)

**Interface:** Receiver in ECX; no stack arguments; returns nothing

Builds the mesh for battle line rendering using triangulation and height data.

**Key Operations:**
1. Gets battle bounds and calculates mesh extents
2. Calls UpdateHeightmap to sample terrain
3. Allocates triangulation mesh via OID__AllocObject (0x18 bytes)
4. Creates a Triangulate work mesh via `Triangulate__CreateQuadMesh` (0x400 capacity)
5. Calculates scale/offset for coordinate mapping (offsets 0x48-0x54)
6. Iterates through units at 0x0067a748, transforms positions
7. Stores triangle/vertex counts (offsets 0x1C/0x20)
8. Creates dynamic vertex buffer if needed (offset 0x1C obj)
9. Allocates vertex position array (8 bytes per vertex)
10. Creates index buffer via CIBuffer__Constructor
11. Copies indices with triangle reordering

Triangulate calls:

- `0x0053a712` calls `Triangulate__CreateQuadMesh`.
- `0x0053a7a4` calls `Triangulate__InsertPointOrAppendVertex`.
- `0x0053a7c0` calls `Triangulate__RelaxMeshByEdgeFlips`.
- These calls operate on the Triangulate work object returned by `Triangulate__CreateQuadMesh`; runtime overlay mesh behavior and rebuild parity remain unproven.

**Called from:** CDXBattleLine__Setup (0x0053a280)

**Line references in debug:** 0x145, 0x161, 0x165, 0x170

---

### CDXBattleLine__InitMipLevels (0x0053a930)

**Interface:** Receiver in ECX; no stack arguments; returns nothing

Initializes mip levels for the battle line texture with gradient data.

**Key Operations:**
1. Gets mip level count from 0x00558690
2. For each mip level:
   - Locks texture surface
   - Fills with gradient values (-0x400 to -0xf70 range)
   - Left half: -0x400 (darker)
   - Right half: varies based on position
3. Unlocks texture

**Called from:** CDXBattleLine__Constructor (0x0053a050)

---

### CDXBattleLine__UpdateVertexBuffer (0x0053aa40)

**Interface:** Member with the receiver in ECX; takes `hud_y` (float), `use_unit_marker_offsets` (int); returns nothing

Updates the vertex buffer with marker positions for rendering.

**Key Operations:**
1. Locks vertex buffer from offset 0x70
2. Iterates 8 times with base offset, calls SetupVertex
3. Iterates through unit list at 0x0067a748
4. For each unit, calculates position and calls SetupVertex with intensity value
5. Unlocks vertex buffer

`RET 0x8` and the two `CDXBattleLine__Render` callsites prove the `hud_y` / mode-flag stack pair.

**Called from:** CDXBattleLine__Render (0x0053abe0)

---

### CDXBattleLine__SetupVertex (0x0053ab40)

**Interface:** `__cdecl`; takes `out_vertex` (float pointer), `screen_base_y` (float), `screen_offset_x` (float), `screen_offset_y` (float), `source_xy` (float pointer), `intensity` (float), `mode` (byte); returns nothing

Sets up a single 0x20-byte marker vertex with position, texture coordinates, and intensity. Two `UpdateVertexBuffer` callsites push seven arguments and then add `ESP,0x1c`, confirming the cdecl shape.

**Key Operations:**
1. Calculates world position from input position and offsets
2. Sets Z=0.9, W=0.5 for clip space
3. If mode == 0:
   - Calculates texture coordinates from position (×0.0078125)
   - Sets intensity value
4. If mode != 0:
   - Sets alternate UV mapping

**Called from:** CDXBattleLine__UpdateVertexBuffer (0x0053aa40)

---

### CDXBattleLine__Render (0x0053abe0)

**Interface:** Receiver in ECX; no stack arguments; returns nothing

Main render function that draws the battle line with multiple passes.

**Key Operations:**
1. Checks 0x0067a748 (unit list) exists
2. Sets render states (0x009c68ac=0, 0x009c690d=1)
3. Calculates Y position based on split-screen mode
4. Calls UpdateVertexBuffer
5. Renders in 3 passes (indices 0, 1, 2 via 0x00527cc0):
   - Pass 0: Full battle line with stencil
   - Pass 1: Masked area rendering
   - Pass 2: Battle engine markers
6. Each pass configures:
   - Texture stages (`RenderState_Set`/`0x00513bc0`, `0x00513820`)
   - Sampler states (0x00513930)
   - Alpha blending
7. Renders markers for units at 0x008a9a98+0x2a4 range
8. Uses 0x00555be0 for marker sprite rendering with rotation

**Called from:** CHud__RenderBattleline (0x00487d10)

---

### CDXBattleLine__RenderTriOverlayPass (0x0053b470)

**Interface:** Receiver in ECX; no stack arguments; returns nothing

Render helper called from `CDXBattleLine__Render` after the base battleline passes. The body unlocks the dynamic overlay buffer if `this+0x5c` says it is still locked, binds the marker texture at `this+0x0c`, configures two overlay draw passes, and submits `this+0x60` vertices from the buffer at `this+0x78` when the count is nonzero.

**Called from:** CDXBattleLine__Render (0x0053abe0)

---

### CDXBattleLine__AppendOverlayVertex (0x0053b5f0)

**Interface:** Member with the receiver in ECX; takes `world_x` (float), `world_y` (float), `color_rgb` (unsigned int); returns nothing

Appends one dynamic overlay marker vertex. `RET 0xc` and the two `CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices` callsites prove ECX plus three stack arguments: `world_x`, `world_y`, and the color constants `0xffff00` / `0xff0808`. The body lazily locks the dynamic buffer, computes a pulsing color boost at `this+0x58`, projects the point into HUD space, writes a 0x14-byte overlay vertex, and increments the count at `this+0x60` up to 500.

**Called from:** CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices (0x00414cb0)

---

### CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices (0x00414cb0)

**Interface:** Member with the receiver in ECX; no stack arguments; returns nothing

Earlier analysis assigned this helper to `CExplosionInitThing`; it is a `CDXBattleLine` overlay helper.

**Key Operations:**
1. Resets the dynamic overlay vertex count at offset `+0x60`
2. Walks the battle-line source list at `0x00855140`
3. Appends yellow overlay vertices through `CDXBattleLine__AppendOverlayVertex`
4. Walks the influence/source list at `0x008550a0`
5. Filters the second list through `CExplosionInitThing__HasSpawnDelayElapsedAndNotTriggered`
6. Appends red overlay vertices through `CDXBattleLine__AppendOverlayVertex`

**Called from:** `CHud__RenderBattleline` (0x00487d10)

**Boundary:** static evidence only. Runtime overlay rendering, the concrete list layouts and source identity beyond the checked caller and body remain unproven.

---

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x00650324 | debug source path of `DXBattleLine.cpp` | Debug path |
| 0x00650348 | "hud\V2\BattleEngineMarker.tga" | BE marker texture |
| 0x00650368 | "hud\marker.tga" | Generic marker texture |
| 0x00650378 | "battleline_method" | CVar name (?) |
| 0x0062d1b8 | "hud\v2\BattleLineOutline.tga" | Outline texture (used in CHud) |

## Related Globals

| Address | Type | Name | Notes |
|---------|------|------|-------|
| 0x0067a748 | void* | g_pUnitList | Unit list for markers |
| 0x00889010 | int | — | Render state flag |
| 0x00888a90 | int | — | Hardware capability flags |
| 0x0089c924 | int | — | Unknown render flag |
| 0x008a9d84 | void* | — | Render target/device |
| 0x008a9a98 | int[] | — | Unit array base |
| 0x009c68ac | int | — | Z-buffer write flag |
| 0x009c690d | byte | — | Alpha blend flag |

## Related Functions (External)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0047ef20 | CHeightField__RecomputeGridExtentsAndHeightRange | Heightfield-owned grid extent / height range helper consumed by battle-line mesh and heightmap updates (earlier analysis assigned it to `CDXBattleLine`). |
| 0x0047eb80 | CHeightField__Collide | Sample terrain height |
| 0x0047ec60 | CHeightField__Normal | Unknown terrain function |
| 0x004f7170 | Triangulate__CreateQuadMesh | Allocates and seeds the BattleLine Triangulate work mesh. |
| 0x004f7460 | Triangulate__InsertPointOrAppendVertex | Inserts/appends BattleLine mesh points into the Triangulate work object. |
| 0x004f74b0 | Triangulate__SplitTriangleAtPointAndLegalizeEdges | Splits a containing triangle and legalizes new shared edges. |
| 0x004f7660 | Triangulate__TryFlipSharedEdgeForQuality | Flips shared edges when static geometric quality tests improve. |
| 0x004f78c0 | Triangulate__FindTriangleByDirectedEdge | Finds or rotates triangle triplets by directed edge. |
| 0x004f7940 | Triangulate__RelaxMeshByEdgeFlips | Performs dirty-flagged edge-flip relaxation passes. |
| 0x00558690 | CDXTexture__GetAnimatedFrame | Get texture/surface manager |
| 0x00555be0 | CVBufTexture__DrawSpriteEx | Render sprite with rotation |
| 0x00513bc0 | PCLTShell__SRS | Cached render-state setter |
| 0x00513820 | PCLTShell__STS | Set texture stage state |
| 0x00513930 | D3DStateCache__SetState114Raw | Set sampler state |
| 0x00513a50 | PCLTShell__D3D_SetTexture | Set texture |
| 0x00513c70 | CEngine__DrawIndexedPrimitives | Draw indexed primitives |
| 0x00527cc0 | CWaterRenderSystem__ValidateVBufferAndMarkReady | Check render pass enabled |
| 0x00527d20 | CDXLandscape__ValidateDeviceAndUpdateValidSoFar | Check stencil enabled |
| 0x00527da0 | CVBufTexture__MarkAccepted | Apply/mark accepted stencil pass |

## Inheritance

```
CTexture (0x158 bytes)
  |
  +-- CDXBattleLine
```

## Notes

1. The battle line is a tactical HUD element showing territorial control
2. Uses triangulated mesh for terrain-following visualization
3. Multiple render passes for different effects (outline, fill, markers)
4. Supports split-screen multiplayer (position calculations)
5. Unit markers rendered with rotation based on facing direction
6. Hardware capability flags affect texture resolution (128x128 vs 128x1)
