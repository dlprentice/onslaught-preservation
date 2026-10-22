# DXPalletizer.cpp - Function Mappings

Status: active static function map
Last updated: 2026-10-22 (reconstructed signatures and research-campaign records removed)
Summary: the nine-function octree colour quantiser that converts 32-bit textures to 8-bit palettised ones, its
node layout, nearest-colour rule and console swizzle tables.

> Colour palette quantisation for 8-bit indexed textures. The functions are found from the
> `DXPalletizer.cpp` debug source path string at `0x00651d60`.

## Interfaces

Every function except the two swizzles is a member with the receiver in ECX; the swizzles are `__cdecl`.

| Address | Function | Arguments and result |
| --- | --- | --- |
| `0x0054e500` | `DXPalletizer__InsertColor` | four colour bytes (three channels and alpha or a fourth channel) and the bit depth; returns a node pointer |
| `0x0054e670` | `DXPalletizer__BuildPalette` | the output palette words |
| `0x0054e6e0` | `DXPalletizer__AssignPaletteIndices` | a pointer to the palette counter and the minimum pixel count; returns an `int` |
| `0x0054e790` | `DXPalletizer__CollapseOctreeNode` | none |
| `0x0054e950` | `DXPalletizer__FreeOctreeNode` | a free-self flag byte; returns the node pointer |
| `0x0054e9d0` | `DXPalletizer__Palletize` | source RGBA, width, height, requested palette size, output index and palette references, and flags for source alpha, allocating outputs, swizzling, preserving alpha, expanding a half palette and copying palette tiles |
| `0x0054ef70` | `DXPalletizer__FindNearestColor` | four colour values; returns the palette index byte |
| `0x0054f090` | `DXPalletizer__SwizzleBlock` | block width, block height, source block, destination block; returns an `int` |
| `0x0054f380` | `DXPalletizer__SwizzleTexture` | width, height, source indices, destination; returns an `int` |

The exact workspace, octree-node, palette and swizzle layouts, the console texture format and runtime
texture output remain unproven.

## Overview

DXPalletizer implements an **octree-based color quantization** system for converting 32-bit RGBA textures to 8-bit indexed (palettized) textures. This is a common technique in game engines for reducing texture memory while maintaining visual quality.

The system uses:
- **Octree data structure** - 16-entry child nodes (2^4 for RGBA bit levels)
- **Color frequency tracking** - Counts pixels per color region
- **Manhattan distance** - For nearest-color matching in palette lookup
- **Console texture swizzling** - Morton order reordering for GPU cache efficiency

## Functions (9 total)

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x0054e9d0 | DXPalletizer__Palletize | ~610 | Main entry point - converts RGBA to indexed |
| 0x0054e500 | DXPalletizer__InsertColor | ~432 | Insert color into octree, creating nodes as needed |
| 0x0054e6e0 | DXPalletizer__AssignPaletteIndices | ~176 | Recursively assign palette indices to leaf nodes |
| 0x0054e790 | DXPalletizer__CollapseOctreeNode | ~448 | Collapse octree nodes to reduce colors |
| 0x0054e670 | DXPalletizer__BuildPalette | ~112 | Extract final palette from octree |
| 0x0054e950 | DXPalletizer__FreeOctreeNode | ~128 | Recursively free octree node memory |
| 0x0054ef70 | DXPalletizer__FindNearestColor | ~256 | Find closest palette entry using Manhattan distance |
| 0x0054f380 | DXPalletizer__SwizzleTexture | ~528 | Swizzle texture for console GPU (Morton order) |
| 0x0054f090 | DXPalletizer__SwizzleBlock | ~560 | Swizzle individual texture block (16x16 or smaller) |

---

## Function Details

### DXPalletizer__Palletize (0x0054e9d0)

**Main quantization entry point**

**Algorithm:**
1. Allocates octree root node (0x54 bytes)
2. Iterates all source pixels, inserting into octree
3. Collapses octree to fit target palette size
4. Builds final palette from remaining nodes
5. Maps each pixel to nearest palette entry
6. Optionally swizzles output for console GPU

**Memory allocations:**
- Line 0xee (238): Octree root node - 0x54 bytes
- Line 0xf4 (244): Palette buffer - paletteSize * 4 bytes
- Line 0x136 (310): Index buffer - width * height bytes
- Line 0x147 (327): Temp index buffer - width * height bytes

---

### DXPalletizer__InsertColor (0x0054e500)

**Insert color into octree**

Takes the colour bytes and the current bit depth, which starts at 7.

**Octree node layout (0x54 bytes):**

| Offset | Field |
| --- | --- |
| `0x00` | colour bytes r, g, b, a (centre of the region) |
| `0x04` | maximum bounds per channel (`0xFF` initially) |
| `0x08` | pixel count in this region |
| `0x0C` | leaf flag (1 for a leaf) |
| `0x10` | node flags |
| `0x14` | sixteen child node pointers (one per combination of the four channel bits) |

**Algorithm:**
- Walks down octree from MSB to LSB of each color channel
- Creates child nodes as needed (16 children per level for 4-bit index)
- At depth 0 (leaf), stores exact color and increments pixel count
- At higher depths, stores region center color

---

### DXPalletizer__AssignPaletteIndices (0x0054e6e0)

**Assign palette indices to leaf nodes**

Takes a pointer to the running palette index counter and the minimum pixel count a leaf needs.

**Algorithm:**
- Recursively traverses octree
- Leaf nodes with pixelCount >= threshold get assigned a palette index
- Non-leaf nodes recurse into all 16 children
- Returns total pixels assigned

---

### DXPalletizer__CollapseOctreeNode (0x0054e790)

**Collapse octree to reduce palette size**

Takes no arguments.

**Algorithm:**
- Checks if all children are leaves
- If so, merges children into parent:
  - Sums pixel counts
  - Sets isLeaf = 1
  - Frees child nodes
- If not, recursively collapses children first
- Called repeatedly until palette fits target size

---

### DXPalletizer__BuildPalette (0x0054e670)

**Extract palette from octree**

Takes the palette buffer.

**Algorithm:**
- Recursively walks octree
- For each node with assigned index (index >= 0):
  - Writes RGBA color to `paletteBuffer[index * 4]`
- Iterates all 16 children recursively

---

### DXPalletizer__FreeOctreeNode (0x0054e950)

**Free octree node and children**

Takes a flag byte saying whether to free the node itself.

**Algorithm:**
- Recursively frees all 16 children
- If shouldFree & 1, frees self via OID__FreeObject (OID_Free)
- Returns node pointer

---

### DXPalletizer__FindNearestColor (0x0054ef70)

**Find nearest palette entry**

Takes the four colour components and returns the index byte.

**Algorithm:**
- Uses **Manhattan distance** (sum of absolute differences)
- Distance = |r1-r2| + |g1-g2| + |b1-b2| + |a1-a2|
- Iterates palette entries from ECX pointer
- Palette count at offset 0x400 from palette base
- Returns index of closest match

---

### DXPalletizer__SwizzleTexture (0x0054f380)

**Swizzle texture for console GPU**

Takes the width, the height, the source indexed pixels and the output buffer.

**Algorithm:**
- Validates dimensions are powers of 2 (up to 1024)
- Divides texture into 128x64 blocks (or smaller for small textures)
- Calls SwizzleBlock for each block
- Uses lookup tables at:
  - 0x00651760: Small texture swizzle table
  - 0x00651960: Large texture swizzle table
  - 0x00651c60: Block index table
  - 0x00651ce0: Morton order table

---

### DXPalletizer__SwizzleBlock (0x0054f090)

**Swizzle individual texture block**

Takes the block width (up to 128), the block height (up to 64), the source block and the output block.

**Morton Order Tables:**
- 0x00651ce0: 4x8 lookup table for Morton indices
- Used to reorder pixels for GPU texture cache coherency

---

## Data References

| Address | Type | Purpose |
|---------|------|---------|
| 0x00651d60 | string | Debug source path of `DXPalletizer.cpp` |
| 0x00651760 | int[128] | Small texture swizzle table |
| 0x00651960 | int[128] | Large texture swizzle table |
| 0x00651c60 | int[] | Block index lookup table |
| 0x00651ce0 | int[32] | Morton order lookup (4x8) |
| 0x006fbe44 | uint | Palette scaling factor 1 |
| 0x006fbe54 | uint | Palette scaling factor 2 |

---

## Technical Notes

### Octree Color Quantization

The octree structure efficiently represents the color space:
- 8 bits per channel = 8 levels of tree depth
- Each node can have up to 16 children (2^4 for RGBA)
- Leaf nodes represent actual colors used
- Branch nodes represent color regions

### Console Swizzling (Morton Order)

Console GPUs (PS2/Xbox) use different texture memory layouts than PC:
- **Linear**: Row-by-row (PC standard)
- **Morton/Z-order**: Interleaved bits for better cache locality

The swizzle functions convert linear indexed textures to Morton order for console GPU compatibility.

### Memory Allocation Pattern

All allocations go through `OID__AllocObject`, which takes the size, a memory type, the debug source
file and the debug line:
- type 0x5f: Octree nodes
- type 0x61: Pixel/palette buffers

---

## Call Graph

```
DXPalletizer__Palletize
    |
    +-> OID__AllocObject (octree root)
    +-> DXPalletizer__InsertColor (for each pixel)
    |       +-> OID__AllocObject (child nodes)
    |
    +-> DXPalletizer__AssignPaletteIndices
    +-> DXPalletizer__CollapseOctreeNode
    |       +-> DXPalletizer__FreeOctreeNode
    |
    +-> DXPalletizer__BuildPalette
    +-> DXPalletizer__FindNearestColor (for each pixel)
    +-> DXPalletizer__SwizzleTexture (optional)
            +-> DXPalletizer__SwizzleBlock
    +-> DXPalletizer__FreeOctreeNode (cleanup)
```

---

## Related Files

- **DXTexture.cpp** - Texture loading, uses palletizer for 8-bit textures
- **tgaloader.cpp** - TGA image loading, may feed into palletizer
- **imageloader.cpp** - Base image loading class

---

## Discovery Method

Found via xref search to debug path string at 0x00651d60:
- 5 xrefs from 2 functions
- 0x0054e500: 1 xref (InsertColor)
- 0x0054e9d0: 4 xrefs (Palletize - multiple allocations)

Helper functions discovered by analyzing call targets within the main functions.

---

## Status

- [x] All 9 DXPalletizer functions are named and their interfaces recorded.
- [x] Static call graph, xref, debug-path, and table-address evidence is documented.
- [x] Swizzle table addresses are identified.
- [ ] Swizzle table values and exact console texture format identity are not fully decoded.
- [ ] Runtime texture output, exact source identity, exact structure layouts, BEA patching, and rebuild parity remain unproven.
