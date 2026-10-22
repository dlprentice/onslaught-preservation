# DXFrontEndVideo.cpp - Function Mappings

Status: active static function map
Last updated: 2026-10-22 (reconstructed code and research-campaign records removed)
Summary: front-end Bink video playback: the `CDXFrontEndVideo` object, its double-buffered textures, open,
update and render, and the neighbouring `CDXGame` and `CBinkOpenThread` entries that used to be mistaken for
its base class.

> DirectX front-end video playback using the Bink library. Debug source path string for
> `DXFrontEndVideo.cpp`: `0x00650744`.

## Overview

This file implements video playback for the front-end/menu system using the RAD Game Tools Bink video library. It handles FMV (Full Motion Video) playback for cutscenes and intro videos displayed during menus.

**Class Hierarchy:**
```
CFrontEndVideo (base class)
  |
  +-- CDXFrontEndVideo (DirectX implementation)
```

## Class Structure

### CDXFrontEndVideo

**Vtable:** 0x005e5084

| Offset | Member | Type | Description |
|--------|--------|------|-------------|
| 0x00 | vtable | ptr | Virtual function table |
| 0x08 | m_pBink | HBINK | Bink video handle |
| 0x0C | m_pTextures[0] | ptr | Double-buffered texture 0 |
| 0x10 | m_pTextures[1] | ptr | Double-buffered texture 1 |
| 0x14 | m_nCurrentTexture | int | Current texture index (0 or 1) |
| 0x18 | m_bFrameReady | bool | Frame decoded and ready |
| 0x1C | m_bCopyComplete | bool | Frame copied to texture |
| 0x20 | m_nWidth | int | Video/texture width |
| 0x24 | m_nHeight | int | Video/texture height |
| 0x28 | m_nParam | int | Parameter for callbacks |
| 0x2C | m_nFadeAlpha | int | Fade-in alpha (0-255) |

### CFrontEndVideo (Base Class)

Earlier notes overclaimed the base-class constructor and destructor. RTTI resolves vtable `0x005e5078` to
`CBinkOpenThread`, not `CFrontEndVideo`, and `0x005e509c` to `CDXGame`. The `CFrontEndVideo` base lifecycle
is still unrecovered; do not use `0x00541f10`, `0x00541f30` or `0x00541120` as evidence about it.

Slot 8 of the inherited vtable is `CGame__Shutdown` (`0x0046c990`), matching `CGame::Shutdown` in the source.

---

## How the FMV wrapper embeds it

`CDXFMV__ctor_base` (`0x0053f0f0`) constructs an embedded `CDXFrontEndVideo` at `this+0x10` after installing
the base `CFMV` vtable and before installing the `CDXFMV` vtable; `CDXFMV__DestructorBody` tears that object
down before `CMonitor__Shutdown(this)`. This links the `DXFMV.CPP` wrapper to this file's video object
statically only.

## The CDXFrontEndVideo cluster (0x00541200-0x00541d30)

Vtable `0x005e5084` slot 0 is `CDXFrontEndVideo__scalar_deleting_dtor`, a `RET 0x4` delete-flag wrapper that
conditionally frees the object and returns it. The cluster covers construction, the default-size fallback,
open, init and close, the width and height accessors, render and update. Its callers include
`CFEPMultiplayerStart__ctor`, `CDXFMV__ctor_base`, `CFEPCommon__Init`/`StartVideo`/`StopVideo`/`Shutdown`,
`CFrontEnd__RenderVideoQuadScaledToWindow`, `CFrontEnd__Process` and the `CDXFMV` call sites.

`CDXFrontEndVideo__Render` uses two byte-flag helpers: `CDXFrontEndVideo__ClearByteFlag` (`0x00441e20`)
writes zero to the byte at ECX, and `CDXFrontEndVideo__SetByteFlagAndReturnOld` (`0x00441e30`) reads the old
low byte at `[ECX]`, writes `1` and returns the old value in `AL`.

Runtime Bink playback, asynchronous scheduling, Direct3D texture upload, the visible front-end video and the
complete class layouts remain open.

---

## Functions (12 total)

### CDXFrontEndVideo::CDXFrontEndVideo (Constructor)
| Property | Value |
|----------|-------|
| Address | 0x00541200 |
| Name | `CDXFrontEndVideo__CDXFrontEndVideo` |
| Interface | Receiver in ECX; no stack arguments; returns nothing |
| Returns | void |

**Purpose:** Initializes a CDXFrontEndVideo instance. Sets up vtable and zeroes member variables.

**Key Operations:**
- Sets vtable to 0x005e5084
- Clears Bink handle (this+0x08 = 0)
- Clears texture pointers (this+0x0C, this+0x10 = 0)
- Initializes flags (this+0x2C = 0)

---

### CDXFrontEndVideo Scalar Deleting Destructor
| Property | Value |
|----------|-------|
| Address | 0x00541220 |
| Name | `CDXFrontEndVideo__scalar_deleting_dtor` |
| Interface | Member with the receiver in ECX; takes `delete_flags` (byte); returns a pointer |
| Returns | this |

**Purpose:** Scalar deleting destructor wrapper. Vtable `0x005e5084` slot 0 points here; `RET 0x4` proves one stack argument after `this`, and the body conditionally frees memory when `delete_flags & 1` is set.

---

### CDXFrontEndVideo::SetDefaultSize
| Property | Value |
|----------|-------|
| Address | 0x00541240 |
| Name | `CDXFrontEndVideo__SetDefaultSize` |
| Interface | Receiver in ECX; no stack arguments; returns an int |
| Returns | 1 (always) |

**Purpose:** Sets default video dimensions to 512x512.

**Key Operations:** stores 512 (`0x200`) in both the width and the height field and returns 1.

---

### CDXFrontEndVideo::Close
| Property | Value |
|----------|-------|
| Address | 0x00541260 |
| Name | `CDXFrontEndVideo__Close` |
| Interface | Receiver in ECX; no stack arguments; returns nothing |
| Returns | void |

**Purpose:** Closes the video and releases the Bink handle.

**Key Operations:**
- Calls CloseVideo() to release resources
- Clears Bink handle (this+0x08 = 0)

---

### CDXFrontEndVideo::Open
| Property | Value |
|----------|-------|
| Address | 0x005412e0 |
| Name | `CDXFrontEndVideo__Open` |
| Interface | Member with the receiver in ECX; takes `video_path` (string), `fallback_width` (int), `fallback_height` (int), `open_flags` (int), `async_open` (int), `callback_cookie` (int); returns nothing |
| Returns | void |

**Purpose:** Opens a video file for playback using the Bink library.

**Key Operations:**
- Calls RADSetMemory to configure memory allocation
- Stores dimensions (this+0x20, this+0x24)
- Handles async loading via thread
- Copies filename to global buffers
- Calls InitVideo() for synchronous loading

**Related Strings:**
- Uses global filename buffer at 0x008a9834
- Uses backup filename buffer at 0x008a9938

---

### CDXFrontEndVideo::InitVideo
| Property | Value |
|----------|-------|
| Address | 0x00541430 |
| Name | `CDXFrontEndVideo__InitVideo` |
| Interface | Receiver in ECX; no stack arguments; returns nothing |
| Returns | void |

**Purpose:** Initializes video playback after file is opened. Creates textures and prepares first frame.

**Key Operations:**
- Gets Bink handle from global (0x008a9830)
- On failure: prints "failed to find file", triggers error handling
- Calls BinkDoFrame, BinkNextFrame to prepare first frame
- Allocates 2 `CUMTexture` objects for double buffering (via `OID__AllocObject` and `CUMTexture__ctor_base`)
- Calculates power-of-2 texture dimensions (min 128, capped by display size)
- Configures each texture through `CUMTexture__ConfigureByMode` with the selected size, mode 5 (or 4 when `0x008a9a54` is set) and 1
- Sets m_bFrameReady = 1, m_bCopyComplete = 0

The `CUMTexture` allocation and configuration evidence is static; it does not prove runtime Bink texture upload or GPU behaviour.

**Bink API Calls:**
- `_BinkDoFrame_4(hBink)` - Decode current frame
- `_BinkNextFrame_4(hBink)` - Advance to next frame

**Error Strings:**
- "failed to find file" (0x0065076c)
- "couldn't create UMTex %d" (0x00650728)

---

### CDXFrontEndVideo::CloseVideo
| Property | Value |
|----------|-------|
| Address | 0x00541650 |
| Name | `CDXFrontEndVideo__CloseVideo` |
| Interface | Receiver in ECX; no stack arguments; returns nothing |
| Returns | void |

**Purpose:** Closes video and releases all resources.

**Key Operations:**
- Prints "Closing FMV\n"
- Waits for async open thread if running ("Waiting for open thread")
- Releases both texture objects
- Gets playback summary via BinkGetSummary
- Prints stats: "%i frames played, %i frames skipped (%i%%)"
- Calls BinkClose to release handle
- Clears Bink handle (this+0x08 = 0)
- Prints "done."

**Bink API Calls:**
- `_BinkGetSummary_8(hBink, summary)` - Get playback statistics
- `_BinkClose_4(hBink)` - Close video handle

---

### CDXFrontEndVideo::GetWidth
| Property | Value |
|----------|-------|
| Address | 0x00541770 |
| Name | `CDXFrontEndVideo__GetWidth` |
| Interface | Receiver in ECX; no stack arguments; returns an int |
| Returns | Video width |

**Purpose:** Returns the video width: the Bink handle's width field (offset `0x00`) when a handle is open,
otherwise the cached width.

---

### CDXFrontEndVideo::GetHeight
| Property | Value |
|----------|-------|
| Address | 0x00541780 |
| Name | `CDXFrontEndVideo__GetHeight` |
| Interface | Receiver in ECX; no stack arguments; returns an int |
| Returns | Video height |

**Purpose:** Returns the video height: the Bink handle's height field (offset `0x04`) when a handle is open,
otherwise the cached height.

---

### CDXFrontEndVideo::Render
| Property | Value |
|----------|-------|
| Address | 0x00541790 |
| Name | `CDXFrontEndVideo__Render` |
| Interface | Member with the receiver in ECX; takes `x` (float), `y` (float), `z` (float), `scale_x` (float), `scale_y` (float), `packed_argb` (unsigned int), `centered` (int); returns an int |
| Returns | 1 (always) |

**Purpose:** Renders the current video frame as a textured quad.

**Key Operations:**
- Handles async file loading completion
- Decodes next frame via BinkDoFrame/BinkNextFrame
- Double-buffer texture management (toggles between textures 0 and 1)
- Locks texture, copies frame via BinkCopyToBuffer
- Handles fade-in animation (m_nFadeAlpha increments by 0x11 per frame)
- Applies color modulation based on fade alpha
- Sets up D3D render states and draws quad primitive

**Bink API Calls:**
- `_BinkDoFrame_4(hBink)` - Decode frame
- `_BinkNextFrame_4(hBink)` - Advance frame
- `_BinkCopyToBuffer_28(hBink, dest, pitch, height, x, y, flags)` - Copy to texture

**Error Strings:**
- "Failed lock" (0x0065080c)
- "DXFEV: LockRect failed: %s" (0x006507f0)

---

### CDXFrontEndVideo::Update
| Property | Value |
|----------|-------|
| Address | 0x00541d30 |
| Name | `CDXFrontEndVideo__Update` |
| Interface | Member with the receiver in ECX; takes `wait_for_frame` (byte); returns an int |
| Returns | 0 = playing, 1 = finished, -1 = waiting |

**Purpose:** Updates video playback state, checks for completion.

**Key Operations:**
- Returns 0 if no video loaded
- Calls BinkWait to check if frame ready
- If waitForFrame and not ready, returns -1
- Advances frame if needed via BinkDoFrame/BinkNextFrame
- Checks completion by comparing current frame to total frames
- Returns 1 when video is complete

**Bink API Calls:**
- `_BinkWait_4(hBink)` - Check if ready for next frame
- `_BinkDoFrame_4(hBink)` - Decode frame
- `_BinkNextFrame_4(hBink)` - Advance frame

**Completion check:** returns 1 when the Bink handle's current-frame and total-frame fields (offsets
`0x08` and `0x0C`) are equal, otherwise 0.

---

### CDXGame::CDXGame (Owner Correction)
| Property | Value |
|----------|-------|
| Address | 0x00541f10 |
| Name | CDXGame__ctor |
| Interface | Receiver in ECX; no stack arguments; returns a pointer |
| Returns | this |

**Purpose:** Earlier notes called this the `CFrontEndVideo` constructor. The function calls `CGame__ctor`, then installs the `CDXGame` secondary vtable at `0x005e509c`; RTTI resolves that vtable to `CDXGame`, and Stuart source defines `CDXGame : CGame`.

---

### CBinkOpenThread::CBinkOpenThread (Owner Correction)
| Property | Value |
|----------|-------|
| Address | 0x00541120 |
| Name | CBinkOpenThread__ctor |
| Interface | Receiver in ECX; no stack arguments; returns a pointer |
| Returns | this |

**Purpose:** Earlier notes called this the `CFrontEndVideo` destructor. The function calls the waiting-thread constructor at `0x00528bc0`, installs vtable `0x005e5078`, and RTTI for that vtable resolves to `CBinkOpenThread`. The adjacent `0x00541140` vtable-slot body is not yet recovered.

`0x00528bc0` is `CWaitingThread__ctor_base`. The neighbouring helpers are `CBinkOpenThread__WorkerMain`, `CBinkOpenThread__Init`, `CBinkOpenThread__WaitForThread`, `CBinkOpenThread__StartAsync`, `CBinkOpenThread__RunSync`, `CBinkOpenThread__IsRunning`, `CBinkOpenThread__Lock`, and `CBinkOpenThread__Unlock`. Xrefs tie the cluster to `CDXFrontEndVideo__Open/Update/InitVideo/CloseVideo/Render`, Bink voice queue pumping, Goodies loading polling, mission object-code async loading, and message-box voice/text reveal. Runtime Bink, media and thread scheduling behaviour and the exact class layouts remain open.

---

### CDXGame Scalar Deleting Destructor (Owner Correction)
| Property | Value |
|----------|-------|
| Address | 0x00541f30 |
| Name | CDXGame__scalar_deleting_dtor |
| Interface | Member with the receiver in ECX; takes `flags` (byte); returns a pointer |
| Returns | this |

**Purpose:** Earlier notes called this the `CFrontEndVideo` scalar destructor. The function calls `CDXGame__dtor_thunk`, checks the delete flag, optionally frees `this`, and returns `this`.

---

## Vtable Layout

### CDXFrontEndVideo vtable (0x005e5084)
| Index | Offset | Address | Function |
|-------|--------|---------|----------|
| 0 | 0x00 | 0x00541220 | CDXFrontEndVideo__scalar_deleting_dtor |
| 1 | 0x04 | 0x00405930 | (inherited) |
| 2 | 0x08 | 0x005019C0 | (inherited) |
| 3 | 0x0C | 0x00405930 | (inherited) |
| 4 | 0x10 | 0x00405930 | (inherited) |
| 5 | 0x14 | 0x00619AD0 | (inherited) |
| 6 | 0x18 | 0x0046FF10 | (inherited) |
| 7 | 0x1C | 0x00541F30 | CDXGame::scalar_deleting_dtor (inheritance through this table is not yet revalidated) |
| 8 | 0x20 | 0x0046C990 | CGame__Shutdown (inherited `CDXGame`/`CGame` shutdown) |
| 9 | 0x24 | 0x0046F7E0 | (inherited) |
| 10 | 0x28 | 0x004014A0 | (inherited) |
| 11 | 0x2C | 0x004DB8C0 | (inherited) |

### CBinkOpenThread vtable (0x005e5078, resolved by RTTI)
| Index | Offset | Address | Function |
|-------|--------|---------|----------|
| 0 | 0x00 | 0x00541140 | CBinkOpenThread vtable-slot body, not yet recovered |
| 1 | 0x04 | 0x00469C40 | (inherited) |
| 2 | 0x08 | 0x00619A78 | (inherited) |

---

## Bink Video Library Integration

The game uses RAD Game Tools' Bink video codec (binkw32.dll) for FMV playback.

**Imported Functions:**
| Function | Parameters | Purpose |
|----------|------------|---------|
| BinkOpen | (filename, flags) | Open video file |
| BinkClose | (hBink) | Close video |
| BinkDoFrame | (hBink) | Decode current frame |
| BinkNextFrame | (hBink) | Advance to next frame |
| BinkWait | (hBink) | Check timing |
| BinkCopyToBuffer | (hBink, dest, pitch, h, x, y, flags) | Copy frame to buffer |
| BinkGetSummary | (hBink, summary) | Get playback stats |
| BinkSetVolume | (hBink, track, volume) | Set audio volume |
| BinkSetSoundTrack | (tracks, trackIDs) | Configure audio |
| BinkSetSoundSystem | (open, param) | Set sound output |
| BinkOpenDirectSound | (hwnd) | DirectSound output |

**BINK handle (partial):**

| Offset | Field |
| --- | --- |
| `0x00` | width |
| `0x04` | height |
| `0x08` | total frames or current frame |
| `0x0C` | the other of the two |

Earlier notes disagree on which of `0x08` and `0x0C` holds the total and which the current frame; the
completion test compares the two, so it does not decide.

---

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x00650744 | debug source path of `DXFrontEndVideo.cpp` | Debug path |
| 0x0065076c | " failed to find file" | Error message |
| 0x00650728 | "couldn't create UMTex %d" | Texture allocation error |
| 0x00650784 | "Bink video closing. %i frames played, %i frames skipped (%i%%)\n" | Stats |
| 0x006507c4 | "Waiting for open thread" | Async loading |
| 0x006507e0 | "Closing FMV\n" | Close message |
| 0x0065080c | "Failed lock" | Texture lock error |
| 0x006507f0 | "DXFEV: LockRect failed: %s" | D3D error |

---

## Related Classes

- **CDXFMV** - Lower-level FMV wrapper (RTTI at 0x00650620)
- **CFMV** - Base FMV class (RTTI at 0x00650638)
- **CBinkOpenThread** - Async video loading thread (RTTI at 0x006506D0)
- **CUMTexture** - Unmanaged texture class used for video frames (RTTI at 0x0062d8a8)

---

## Global Variables

| Address | Type | Description |
|---------|------|-------------|
| 0x008a9830 | HBINK | Global Bink handle |
| 0x008a982c | char | Async loading flag |
| 0x008a9834 | char[100] | Video filename buffer |
| 0x008a9938 | char[100] | Backup filename buffer |
| 0x008a97d0 | char[52] | Pending filename buffer |
| 0x008a9804 | int | Async param 1 |
| 0x008a9808 | int | Async param 2 |
| 0x008a9a40 | int | Callback parameter |
| 0x008a9a3c | int | Loading parameter |
| 0x008a9a54 | int | 32-bit texture mode flag |

---

## Notes

1. **Double Buffering:** Uses two textures to avoid frame tearing during playback
2. **Power-of-2 Textures:** Texture dimensions are rounded up to nearest power of 2 (min 128)
3. **Async Loading:** Supports background file loading via thread
4. **Fade-In:** Videos fade in gradually (alpha increments by 17 per frame)
5. **Memory Management:** Uses RADSetMemory callback for custom allocator integration

---

## Cross-References

- Called from CFrontEnd during menu FMV playback
- Uses CTexture::FindTexture for fallback placeholder texture
- Related to -skipfmv command line parameter
