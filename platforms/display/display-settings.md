# Display Settings & Screen Mode Analysis

Status: mixed — retained display evidence with scoped parser and options-callback corrections
Last updated: 2026-10-22 (research-campaign records and decompiler-style code removed)
Summary: display/settings reference; bounded options/device execution remains distinct from real driver and full-menu acceptance.
Source File: pinned `references/Onslaught/d3dapp.cpp` and `CLIParams.cpp`; Binary: pristine
`BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> **Source**: static analysis of BEA.exe (Steam release)
> **Date**: December 2025
> **Related**: See `../windowed-mode-analysis.md` for windowed mode investigation

## Overview

Battle Engine Aquila retail imports `d3d9.dll` for rendering, but parts of its app-shell/menu flow still resemble older DirectX sample-framework wiring (`d3dapp.cpp` style command routing). Display initialization is handled by `CD3DApplication`. The game supports fullscreen mode with various resolutions, and has vestigial windowed mode support that does not behave robustly in the retail build.

## Key Functions

| Address | Function | Purpose |
|---------|----------|---------|
| 0x005286e0 | `CD3DApplication__LoadCardIdAndApplyVendorTweaks` | Retail `cardid.txt` tweak loader; opens the supplied path, parses adapter/range/tweak rows, scans `0x0089c018` CVar entries, and applies matching tweak values |
| 0x00528f80 | `CD3DApplication__ctor` | Constructor/init; seeds global app pointer, defaults, and 640x480 creation dimensions |
| 0x005290a0 | `CD3DApplication__Create` | D3D app create path; Direct3DCreate9, device-list build, window create, environment init, timer start |
| 0x00529350 | `CD3DApplication__BuildDeviceList` | Adapter/device/mode enumeration and HAL/REF/depth/texture/MSAA probes |
| 0x0052af00 | `CD3DApplication__Initialize3DEnvironment` | Device create/reset path with cardid/CVar tweaks, presentation parameters, fallbacks, cursor/stats/backbuffer state |
| 0x0052b760 | `CD3DApplication__Resize3DEnvironment` | D3D reset and resource restore helper after size/mode changes |
| 0x0052b840 | `CD3DApplication__ToggleFullscreen` | Fullscreen/windowed toggle and `ForceWindowed` fallback path |
| 0x0052ba50 | `CD3DApplication__ForceWindowed` | Fallback: selects compatible windowable adapter/device/mode |
| 0x0052bb80 | `CD3DApplication__Reset3DEnvironment` | Optional select-device dialog and environment reset path |
| 0x0052bc80 | `CD3DApplication__SelectDeviceProc` | Stdcall device-selection dialog callback (adapter/device/mode/MSAA) |
| 0x0052c430 | `CD3DApplication__Cleanup3DEnvironment` | D3D cleanup/refcount logging path |
| 0x0052c4f0 | `CD3DApplication__DisplayErrorMsg` | Retail fatal/error dispatch for D3D init/reset failures |
| 0x0052c8d0 | `CD3DApplication__SetDeviceCursorFromIcon` | Icon mask/color to D3D cursor surface converter |
| 0x0052c730 | `CD3DApplication__SetResolution` | Stores requested width/height; no in-function clamp |
| 0x0052c780 | `ScreenShape_UpdateAspectScale` | Applies 4:3 vs 16:9 scaling based on `g_ScreenShape` |
| 0x005be622 | `Direct3DCreate9` | `d3d9.dll` import thunk |
| 0x005be628 | `_DXGetErrorString9A` | HRESULT-to-C-string mapper |

### Direct3D runtime tail (0x005be622-0x005c9c66)

- `Direct3DCreate9` (`0x005be622`) is a six-byte import thunk that jumps through the IAT pointer at
  `0x005d8348`. `CD3DApplication__Create` pushes SDK version `0x1f` at `0x005290bc` and stores the
  returned interface at `CD3DApplication +0x32e9c`.
- `_DXGetErrorString9A` (`0x005be628`) maps an HRESULT to a string. It has 21 direct call sites and one
  `RET 0x4` at `0x005c9c66`, and returns one of 3,497 distinct literal strings or the `Unknown` fallback.

Imported `d3d9.dll` behaviour, runtime error reporting and the completeness of the HRESULT table remain
open.

### cardid.txt and CVar tweak loader (0x005286e0-0x00528b00)

- `CD3DApplication__LoadCardIdAndApplyVendorTweaks` takes the path of `cardid.txt`, parses its
  Version/Vendor/Device/range/tweak rows against the current adapter record, scans the global CVar list
  at `0x0089c018`, logs `Setting tweak`, and calls the matched CVar's setter.
- `CVar__Init` links a CVar record into the list at `0x0089c018`; it takes the name and the initial value
  (`RET 0x8`).
- `CVar__SetValueRounded` rounds its float argument and stores the integer at `this+0x0c` (`RET 0x4`).
- `CEngine__InvokeCallbackIfStateMinusOne` takes one argument and calls the receiver's first virtual only
  when `this+0x0c == -1`.

The exact `cardid.txt` grammar, the CVar layout and runtime Direct3D behaviour remain open.

### Options detail and tweak path

`LandscapeDetail_SetLevel`, `LandscapeDetail_GetLevel`, `CTreeDetail__SetQualityLevel`,
`CMultiSample__GetSampleCountLabel`, `CReconnectInterface__VFunc_07_00527d00` and the `CTweak`
constructor and destructors form one static display/options path: the landscape detail globals
`0x009c7c54`/`0x009c7c56`, tree quality forwarded to `CRTMesh__SetQualityLevel`, the MSAA label fallback
`0xd4`, and the `-landscape0/-landscape1/-landscape2` command-line setters. Runtime options-menu, tweak and
device behaviour remain open.

### Direct3D application shell (0x00528f80-0x0052cd20)

The `CD3DApplication` vtable is at `0x005e4ad0` and includes `CD3DApplication__Create` and
`CD3DApplication__MsgProc`.

- `CD3DApplication__Init` (`0x00528f80`) sets the global application pointer `0x0089c0f4`, initialises ten
  adapter-info blocks, installs the vtable, clears the device, window, ready and timer fields, and sets
  640x480 creation dimensions.
- `CD3DApplication__Create` (`0x005290a0`) takes the instance handle, calls `Direct3DCreate9(0x1f)`, builds
  the device list, registers and creates the window when needed, initialises the environment, starts the
  performance timer and marks the application ready.
- `CD3DApplication__BuildDeviceList` (`0x00529350`) enumerates adapters, devices, modes, depth-stencil,
  texture and multisample support, with widescreen modes allowed through `0x0089c0ac`.
- `CD3DApplication__Initialize3DEnvironment` (`0x0052af00`) takes a flag to reuse the existing device,
  applies the cardid/CVar tweaks, builds the presentation parameters, creates or resets the device, falls
  back from lockable back buffer, multisampling and friendly modes, updates stats, back buffer and cursor
  state, and calls the initialisation virtual. There is no separate restore call: that sequence belongs to
  the released Direct3D 8 source.
- `CD3DApplication__Resize3DEnvironment`, `CD3DApplication__ToggleFullscreen`,
  `CD3DApplication__ForceWindowed` and `CD3DApplication__Reset3DEnvironment` are the reset, toggle,
  fallback and dialog-commit shell around the device.
- `CD3DApplication__SelectDeviceProc` is a four-argument `__stdcall` Win32 dialog procedure for the
  adapter, device, mode and MSAA controls.
- `CD3DApplication__Cleanup3DEnvironment` releases the application's Direct3D state and logs device and
  interface reference counts.
- `CD3DApplication__DisplayErrorMsg` maps HRESULT failures to localised fatal string ids `0xb6` to `0xc5`
  and returns the input error code.
- `CD3DApplication__SetResolution` stores the width at `this+0x330bc` and the height at `this+0x330c0`;
  it does not clamp.
- `ScreenShape_UpdateAspectScale` writes `this+0x32e90` from the back-buffer dimensions and
  `g_ScreenShape`.
- `CD3DApplication__SetDeviceCursorFromIcon` converts a Win32 icon's mask and colour bitmaps into a
  Direct3D cursor surface.
- `CD3DApplication__PerfTimerCommand` returns timer values as `double` through `QueryPerformanceCounter`,
  falling back to `timeGetTime`.

Runtime Direct3D behaviour and the exact application, dialog and object layouts remain open.

### CD3DApplication::Init (0x00528f80)

Sets default values:
- Default resolution: 640x480
- Default mode: Fullscreen
- Initializes D3D object pointers to NULL

### CD3DApplication::BuildDeviceList (0x00529350)

Enumerates display adapters and modes:
- Queries available resolutions from D3D
- Filters modes based on minimum requirements (640x480)
- Checks for widescreen mode support via `ALLOW_WIDESCREEN_MODES` config
- Populates internal mode list for Video Options menu

### CD3DApplication::Initialize3DEnvironment (0x0052af00)

Critical function for display mode setup:
- Checks `m_bWindowed` flag to determine fullscreen vs windowed
- Creates D3D device with appropriate presentation parameters
- Handles device creation failures with fallback options
- Sets up swap chain and back buffers

The [September 30 device-boundary recheck](CD3DApplication__Initialize3DEnvironment__0052af00.md#device-boundaries-and-cleanup--september-30)
records 23 modeled original/candidate cases and nine negative controls. Safe-mode selection can
leave the current attempt using the old mode pointer; ordinary friendly-mode fallback refreshes
it on the next iteration. Failed initialization invalidates, deletes, then reloads/releases the
current device while preserving the original failure code. These observations correct the
compatibility contract; they do not establish real driver behavior or a complete byte match.

### CD3DApplication::SetResolution (0x0052c730)

Stores the requested width and height as the creation dimensions and does nothing else: there is no
clamp in this setter. Minimum and default handling happens in mode enumeration and the command-line and
configuration flow.

## Key Data Addresses

### Global Instances

| Address | Type | Description |
|---------|------|-------------|
| 0x0089c0f4 | `CD3DApplication*` | Global D3D application instance pointer |

### Configuration Flags

| Address | Type | Description |
|---------|------|-------------|
| 0x00662f3e | byte | Guard flag for `-forcewindowed` — `CCLIParams+0x186`, **BSS: `0x00` at image load**, set to `0x01` at runtime by `-testeur` only. *(Corrected 2026-07-28; previously read "canonical Steam hash `74154bfa...` = 0x01; some historical baselines reported 0x00". That value was read at file offset `0x262F3E`, which is `.rsrc`, not this variable. See [windowed-mode-analysis.md](windowed-mode-analysis.md).)* |
| 0x0082b484 | int | Aspect ratio mode: 1=16:9, 2=1:1, else=4:3 |

## Structure Offsets

### CD3DApplication (instance at 0x0089c0f4)

| Offset | Type | Field | Description |
|--------|------|-------|-------------|
| 0x32e64 | bool | m_bWindowed | 0=fullscreen, non-zero=windowed |
| 0x330bc | DWORD | m_dwCreationWidth | Requested render width |
| 0x330c0 | DWORD | m_dwCreationHeight | Requested render height |

## Key Strings

| Address | String | Context |
|---------|--------|---------|
| 0x0064be10 | `"ALLOW_WIDESCREEN_MODES"` | Config file key for enabling 16:9 modes |
| 0x0064bba8 | `"Video Options"` (Unicode) | Menu title string |
| 0x006244a0 | `"-forcewindowed"` | CLI parameter string |

## Command-Line Parameters

### -res W H

Sets custom resolution:
```
BEA.exe -res 1920 1080
```

Parsed in `CCLIParams::GetParams(char *text)`, stored at offsets 0x164/0x168. Minimum enforced: 640x480.

### -forcewindowed

Attempts to run in windowed mode:
```
BEA.exe -forcewindowed
```

**Parser correction, September 26:** on the pristine specimen identified above,
guard `0x00662f3e` is BSS and the startup initializer explicitly clears its
object-relative field at `0x00423ad6`. The standalone example is therefore
rejected by this parser gate. `-testeur -forcewindowed`, in that order, enables
the branch on the canonical receiver. Earlier claims of an enabled pristine
guard or a result applying to “every build” were wrong or unproven. See the
[parser evidence and runtime limits](../command-line/CLIParams__ParseCommandLine.md#windowed-guard-and-logger-boundaries).
Actual fullscreen/windowed presentation is a separate acceptance question.

## Aspect Ratio Handling

The game supports multiple aspect ratios, controlled by the value at 0x0082b484:

| Value | Aspect Ratio | Notes |
|-------|--------------|-------|
| 1 | 16:9 | Widescreen mode |
| 2 | 1:1 | Square pixels (rare) |
| other | 4:3 | Default/standard |

Widescreen modes are gated by the `ALLOW_WIDESCREEN_MODES` configuration option, which may need to be enabled in a config file or via external patch.

## Resolution Constraints

- **Minimum**: 640x480 observed in mode enumeration and command-line/config handling; `SetResolution` itself does not clamp
- **Default**: 640x480 (set in `Init`)
- **Maximum**: Limited by display adapter capabilities (enumerated in `BuildDeviceList`)

## Localization (0x00524830)

`0x00524830` is **not** the Video Options handler in this build; it is `Localization__GetStringById` (string lookup by id and `g_LanguageIndex`).

The retail Video Options surface is now mapped through
the page-processing callback at `0x0051f600`, `CFEPOptions__Update`,
`CFEPOptions__SaveDefaultOptions`,
`CFEPOptions__WriteDefaultOptionsFile`, and
`CFEPOptions__TransitionNotification @ 0x0051F7E0`.
The last identity corrects the older `CFEPOptions__EnsureOptionsContext` label:
two calls in the trace-hashed, replayable manual Options TTD trace receive the
transition-from page id, return to `CFrontEnd__SetPage`, reuse the same frontend
options context, and reset its session; this matches Stuart's timed
`CFrontEnd::SetPage -> TransitionNotification(mTransitionFrom)` call. The
missing producer receipt leaves the capture-time executable hash unbound.
Individual sub-item behavior below those mapped handlers remains open.

## September 27 options-processing recheck

The complete callback `[0x0051f600,0x0051f666)` is 102 bytes, SHA-256
`fecdbd8d9e28c4f63d197af85582e19191bc7267d12e2202580b12b81c15febc`.
The common frontend caller at `0x00466dc4` dispatches slot 2 with one DWORD
state argument: active 0, inactive 3, transitioning-from 2, transitioning-to 1.
The surviving `FEPGoodies.h:56` and `FrontEnd.cpp:677–694` bind this interface
to `Process`, replacing the earlier `ProcessInput` interpretation. The pinned
source lacks the Options implementation and base-page header; this does not
recover an original field name or its complete implementation.

Before testing that argument, the callback normalizes DWORD `this+4`:

| Initial word | Final word with the pristine helper |
| --- | --- |
| 0 or 1 | 1 |
| 2, 3 or 4 | 4 |
| 5 | 6 |
| Unsigned values above 5, including negative bit patterns | Unchanged |

The helper at `0x00466990` returns constant 2. The retail callback does not
perform the pinned source's controller count. Normalization runs on inactive
pages too. A nonzero full-DWORD page-state argument then returns; only zero
reads the pointer at `0x0089bc30`, without a null check. Context `+0x10`
nonzero returns. Otherwise `+0x0c == 1` calls the frontend transition entry
at `0x00466ae0`, ECX=`0x0089d758`, with arguments `(0x12,30)`; other values
call the larger persistence helper at `0x0051f500` with argument 1. The callback
does not check either result or itself clear the context words. Residual EAX
varies by exit and is not an integer result contract; both exits use `RET 4`.

Twenty-one isolated cases execute the unchanged callback, its 24-byte table
and the six-byte constant helper. Both authored 24-byte surrogate buffers,
their guards, the global pointer, final ESP, nonvolatile registers and
intercepted call arguments match. Complete retail objects, all registers,
flags and stack contents were not compared; writer ECX is observational only.
Two separate counterfactuals distinguish helper result 1 from 2 and low-byte
from full-DWORD state testing. Transition/persistence callees are intercepted;
this proves neither device detection nor actual settings publication or menu
acceptance. Exact records and limitations are in
`VALIDATION.md` in Onslaught-Career-Editor.

## Known Issues

1. **Windowed mode is multi-gate**: the parser gate `0x00662f3e` is closed at load in every build (BSS) and is opened only by `-testeur`; beyond it, startup fullscreen flow can still force fullscreen. *(Corrected 2026-07-28; previously read "Canonical Steam hash `74154bfa...` already has `0x00662f3e = 0x01`; inconsistent windowed startup is primarily startup-flow behavior unless a variant binary has this byte at `0x00`.")*

2. **Widescreen requires config**: 16:9 modes may not appear in Video Options without enabling `ALLOW_WIDESCREEN_MODES`.

3. **Resolution changes may require restart**: Some resolution changes may not take effect until game restart.

## Related Documentation

- `../windowed-mode-analysis.md` - Detailed investigation of windowed mode failure
- `../widescreen-patch-analysis.md` - Analysis of community widescreen patches
- `CLIParams.cpp/_index.md` - Full CLI parameter documentation
