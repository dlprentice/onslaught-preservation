# Rendering

Status: active — folder index
Last updated: 2026-10-22
Summary: Render resources, trees, patches, palettes, particles, view distance, LOD constants and the default Direct3D state.

## Folders

| Folder | Covers |
| --- | --- |
| [terrain/](terrain/README.md) | Terrain draw-stage flags, the shade plane and per-node colour |

## Documents

| Document | Summary |
| --- | --- |
| [DXBattleLine.cpp Function Mappings](DXBattleLine.md) | the HUD battle-line renderer: its texture-backed object, terrain heightmap sampling, mesh triangulation, marker vertices and three-pass render. |
| [DXPalletizer.cpp - Function Mappings](DXPalletizer.md) | the nine-function octree colour quantiser that converts 32-bit textures to 8-bit palettised ones, its node layout, nearest-colour rule and console swizzle ta… |
| [DXParticleTexture.cpp Function Mappings](DXParticleTexture.md) | the particle-texture objects, their global list, and the engine-side particle bundle helpers that create, restore, render and destroy them. |
| [DXPatchManager.cpp](DXPatchManager.md) | retained patch-manager analysis; the Engine shutdown receiver is re-derived from pristine bytes, while other historical claims remain to audit. |
| [DXTrees.cpp - Function Mappings](DXTrees.md) | the fast tree batch: two card buffers built from the map, how a destroyed tree is hidden, and the fast/close selection facts the rebuild uses. |
| [The default render-state block — `0x004EB1E0`, re-derived from bytes](d3d-default-render-state-block.md) | what the default render-state block 0x004EB1E0 sets on the device, re-derived from bytes; it fixes the default state, not the state at any particular later d… |
| [Mesh, resource, and render static contract](mesh-resource-render-static-contract.md) | specimen-bound rendering and collision contracts, with bounded corrections to arithmetic association, float stores and ordered admission. |
| [The player camera, the cockpit attach, and what `HFOV` means](player-camera-attach-and-mesh-hfov.md) | original camera/projection findings, with a bounded recheck of position identities and aggregate result transport appended below. Other earlier claims were n… |
| [Render/resource static bridge](render-resource-bridge-static-contract.md) |  |
| [View distance, cull, and LOD constants — recovered from the retail binary](view-distance-and-lod-constants.md) |  |
