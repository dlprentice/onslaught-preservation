# CD3DApplication__Initialize3DEnvironment

Status: active — instruction recheck and bounded original-code execution; full device acceptance open
Last updated: 2026-10-22 (research-campaign records removed; findings unchanged)
Summary: retail device creation and reset, mode-pointer lifetime, failed-init cleanup and the x87 precision the device leaves behind, with the modeled API boundaries stated.
Evidence: MEASURED — pristine instructions and 23 bounded original/candidate execution cases.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `references/Onslaught/d3dapp.cpp` | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0052af00`

## Identity

- Body `[0x0052af00,0x0052b753]`, 2,132 bytes, raw pristine-body SHA-256
  `bf98f3c6884486a9f4d40fed2a60d1b21641ea622fa85eb2aaeddc99a1a60379` (recomputed September 30).
- Source analogue: `references/Onslaught/d3dapp.cpp` lines 857-1033,
  `HRESULT CD3DApplication::Initialize3DEnvironment()`. That is the Direct3D 8 sample-framework body; it
  is an analogue of the retail Direct3D 9 body, not proof that they are the same.

## Interface

The receiver is in ECX and there is one stack argument, read as a bool; both exits (`0052b68b`,
`0052b751`) use `ret 4`. When the flag is true and a device already exists, the body resets it;
otherwise it calls CreateDevice. The flag is a retail addition: the released source takes no argument.
Completed modeled cases preserve EBX, EBP, ESI and EDI and restore the caller's stack.

The 32-bit result in EAX follows HRESULT success and failure. Success returns zero; failed-init cleanup
keeps the original failing HRESULT through its cleanup calls. When the mode is unchanged and the software
device fails, that failure is returned unchanged. HAL-to-REF recursion is present statically but was not
executed.

## What the body does

It applies the `cardid.txt` and CVar tweaks, builds the presentation parameters, applies screen-shape
scaling, creates or resets the device, falls back from a lockable back buffer, from multisampling and to
a friendly mode, updates the device stats, back buffer and cursor, calls the application's
initialisation virtual (slot 8, at `0052b65a`) and can retry through the REF device. Retail has no
separate RestoreDeviceObjects call here: the source's two-call sequence must not be read into the
retail body.

The source's outline is the same: choose the adapter, device and mode; adjust the window; fill the
presentation parameters; create the device; on success record caps, device text and back buffer,
initialise device objects and activate; on failure invalidate, delete and release, and for a HAL
failure select REF and retry.

Strings the body uses:

| Address | String |
| --- | --- |
| `0x0064c214` | `D3DA::I3DE OK` |
| `0x0064c224` | ` (sw vp)` |
| `0x0064c230` | ` (simulated mixed vp)` |
| `0x0064c248` | ` (mixed vp)` |
| `0x0064c254` | ` (simulated hw vp)` |
| `0x0064c268` | ` (hw vp)` |
| `0x0064c274` | ` (simulated pure hw vp)` |
| `0x0064c28c` | ` (pure hw vp)` |
| `0x0064c29c` | `Available texture memory: %d Mb` |
| `0x0064c2bc` | `Succeeded.` |
| `0x0064c2c8` | `Falling back to a friendly mode` |
| `0x0064c2e8` | `Falling back to no multisampling` |
| `0x0064c30c` | `Falling back to no lockable backbuffer` |
| `0x0064c334` | `Failed for %s.` |
| `0x0064c344` | `Failed for device lost.` |
| `0x0064c35c` | `Creating device...` |
| `0x0064c370` | `Going to safe mode` |
| `0x0064c384` | `cardid.txt` |
| `0x0064c390` | `c:\cardid.txt` |

Calls and callers:

- Callee `FatalError_LocalizedStringId` `0x0042d080`, one site.
- Callee `CDebugLog__AddMessage` `0x00441740`, eleven sites (earlier analysis called it `CConsole::Printf`).
- Callee at `0x004d1710`, two sites: the setup-message writer (not a global-tint helper, as earlier analysis had it).
- Callee `StringScratch_T3_004f7c70` `0x004f7c70`, two sites.
- Callee `CD3DApplication__LoadCardIdAndApplyVendorTweaks` `0x005286e0`, one site.
- Callee `CTweakSLONG__SetValueRounded` `0x00528ad0`, two sites.
- Callee `CD3DApplication__Initialize3DEnvironment` `0x0052af00`, one site.
- Callee `CD3DApplication__DisplayErrorMsg` `0x0052c4f0`, one site.
- Callee `CD3DApplication__SetDeviceCursorFromIcon` `0x0052c8d0`, one site.
- Callee `sprintf` `0x0055de9b`, one site.
- Callee `_DXGetErrorString9A` `0x005be628`, one site.
- Caller `CD3DApplication__Create` `0x005290a0`, one site.
- Caller `CD3DApplication__Initialize3DEnvironment` `0x0052af00`, one site.
- Caller `CD3DApplication__ForceWindowed` `0x0052ba50`, one site.
- Caller `CD3DApplication__Reset3DEnvironment` `0x0052bb80`, one site.

## Device boundaries and cleanup — September 30

The selected pristine body was reread and its raw digest above reproduced. An isolated x86
probe executes those unchanged instructions, then a relocated reconstruction at the
same address. Both use the same authored application/mode inputs. **23 cases agree, with nine
negative controls.** This is bounded execution with modeled dependencies, not Windows/D3D
runtime acceptance, a whole-function equivalence claim or an exact compiled match.

| Trigger | Measured retail observation |
| --- | --- |
| Six consecutive `D3DERR_DEVICELOST` results | Six 100-ms Sleep calls precede call seven. The iteration captures its mode pointer at `0052af94`–`0052afab`, then changes the index at `0052b01a`. In the fixture, selected mode becomes 0 but call seven still submits mode 1's 1024×768, format 21, depth format 77 and CreateDevice flags `0x40`. Refreshing the pointer early would change behavior. |
| Seventh consecutive device-lost result | Reaches the fatal-call boundary with arguments `FALSE, 0xd2, 10` (decimal 10); the fatal helper itself is not executed. |
| Ordinary friendly-mode fallback | Starts another loop iteration. The second attempt uses new mode 0's 640×480/format 22/depth 75, and setup-message state becomes `0xe6`, kind `0xff`. |
| Lockable-backbuffer or multisample failure | The corresponding retry removes the lockable flag or multisampling before retrying. These separate authored cases do not establish every combination of failures. |
| Mode unchanged, software device returns `0x80004005` | Returns that failure rather than claiming startup succeeded. |
| Modeled CreateDevice or Reset succeeds; slot 8 succeeds | Executes the later bookkeeping, calls slot 8, sets active state and returns zero. No separate restore call occurs. |
| Slot 8 returns `0x80004005` | Calls slot 5 at `0052b693`, slot 6 at `0052b69b`, then reloads the device and releases it at `0052b6ab` before nulling its member. Cleanup HRESULTs do not replace the original init failure. Replacing the device during slot 5 causes the replacement to be released. |

The remaining cases exercise windowed/fullscreen presentation fields, create-versus-reset
selection, both card-id paths, driver-management flags, multisample suggestion/COPY interaction,
vsync and screen-shape inputs. API calls are observed at explicit boundaries; success cases use
an authored fullscreen software-device record. Comparisons include arguments, presentation
parameters, callbacks, selected globals and the full authored application buffer. Completed
returns check stack cleanup and nonvolatile registers.

Three dependency families deliberately refuse when their models are removed (six controls).
A safe-mode threshold changed from six to five changes call-seven parameters; a misbound
backbuffer-count relocation changes its observed count; an instruction crossing the admitted
extent refuses. Candidate padding is not executable evidence. All 85 relocations have retained
literal/import, matched-object or whole-score placement witnesses; annotation-only placements
are refused.

Private receipt: `<maintainer evidence>/build/d3d-init-retail-20260930/`, result SHA-256
`c19669bdb6395d233dd09aed52ccdcab051c7190102999ec0f13af5b74459169`.

Limits: PC24/round-to-nearest is the configured emulator setting, not measured live-retail FPU
state. Card-file effects, logging, string helpers, window adjustment, COM services and application
virtuals are models. There is no general memory-read guard or stack-canary comparison. Real GPU
behavior, HAL-to-REF recursion, cursor/query paths, actual virtual bodies and full startup remain
unexecuted. Six FindMode loops plus their preferred-format exit trampoline independently match
528 bytes without relocations; that does not make either enclosing function exact. The current
candidate section is 2,144 padded bytes, with 2,129 executable bytes versus retail's 2,132.

## Precision setup — October 1 instruction recheck

The CRT-to-device chain was re-derived from the selected pristine specimen. CRT entry
`00560181` reaches the function pointer at `006532e8` through `00560226`/`0055dd7b`; its stored
value is `0055da76`. The precision helper `00560cb1` passes `(0x10000, 0x30000)` to `0056947e`.
The pinned x86 VC6 `FLOAT.H` identifies those as `_PC_53` and `_MCW_PC`. Its inspected mask
combination requests 53-bit precision while preserving the public rounding and exception-mask
settings. This request is not proof of the later gameplay precision.

WinMain calls device setup at `0051236e`. At `005290ba`, SDK version 31 goes through thunk
`005be622` and the verified `d3d9.dll!Direct3DCreate9` import at `005d8348`. Enumeration writes
flags `0x50`, `0x40`, `0x80` or `0x20` at `00529c21`, `00529cf8`, `00529dd2` and `00529ea9`;
`00529b09` copies the selected value into mode `+0x0c`. Creation loads it at `0052b2be`,
optionally ORing `0x100` from the boolean at `00662f3d`. Neither possibility contains
`D3DCREATE_FPU_PRESERVE` (`0x2`, checked in the pinned D3D9 header).

Microsoft documents that Direct3D initialization sets the calling thread to single precision
and nearest rounding unless preservation is requested. **PC24/nearest after creation is therefore
an inference from these flags and the API contract, not a measured raw control word.** Carrying
the CRT PC53 request forward unchanged is not justified.
[Microsoft's thread-state guidance](https://learn.microsoft.com/en-us/windows/win32/dxtecharts/top-issues-for-windows-titles#manipulation-of-the-floating-point-control-word),
[creation flags](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dcreate).

Reset calls at `0052b28d` and `0052b781` receive presentation parameters, with no behavior-flag
argument. The reviewed [Reset contract](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-reset)
does not establish the x87 word after reset. Library code can temporarily change it too:
`0055e128` saves/restores rounding around integer conversion; the object at `005896bd` saves
the public word at `+0x88` and requests PC53, with precision restoration at `005897ea`.
These inspected paths do not prove restoration on every library, callback or DLL path.

All 23 input range hashes were verified, with independent decoding of the 27 critical instruction
assertions, plus the import/pointer chain and pinned headers. Private readback:
`<maintainer evidence>/fpu-startup-root-20261001/readback-v02.json`, SHA-256
`0b55a5da558e89b6d0c55d24b8924226ff734462e9c3b49e362ad55ebb3c1630`.
No game/device call ran. The decisive remaining observation is control word **and thread identity**
before/after creation and both reset sites, then at the tested collision/projectile entries.
Windows and the installed Proton/DXVK path must be measured separately; authored arithmetic
witnesses do not establish Level 100 reachability.

## Open questions

- The concrete layout and read/write direction of every field and global the body touches.
- The complete set of indirect-call targets, and failure and null behaviour.
- Real driver and window behaviour, and what callers expect outside the modeled cases.
- Cheapest next falsifier: extend the probe to HAL-to-REF recursion with distinct adapter and device
  records, or replace one modeled application virtual with its original body. Real-device claims need a
  controlled copied-runtime run.
