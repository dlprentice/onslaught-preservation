# CFrontEnd__SetPage

Status: active — caller transport and complete dispatch body rechecked
Last updated: 2026-10-22 (research-campaign records removed; findings unchanged)
Summary: exact receiver/stack transport and immediate/timed notification order; runtime callback effects stay open.
Evidence: MEASURED — static pristine instructions freshly decoded and source/caller correspondence. No SetPage runtime execution is claimed.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00466ae0`

## September 27 bounded caller recheck

The pristine options callback, now identified as `CFEPOptions__Process`, passes
`ECX=0x0089d758`, page `0x12` and the second argument `30` to this address when its
page-state argument is zero and the options context selects that action. In the
21-case isolated experiment this callee was intercepted: its own transitions,
notifications and interpretation of `30` were not executed or revalidated.
See the [options recheck](../../platforms/display/display-settings.md#september-27-options-processing-recheck).
The complete body is rechecked below.

## September 27 complete dispatch-body recheck

Fresh entry decoding covers all 177 pristine bytes, SHA-256
`06a8d37bc755e5341ca9156650d7caf2612e2a92978ce70baaa61bc765b6c018`.
The function copies incoming ECX into ESI. Its two explicit DWORDs are page at
entry stack+4 and time at+8; both returns use RET 8. The page is typed `int`
here; that is not a recovered EFrontEndPage typedef. The timed branch
interprets time as signed 32-bit via FILD and stores a float; this does not
establish its unit or the upstream clock.

The static sequence, correlated against pinned `FrontEnd.cpp:563–592`, is:

1. If active-page field `+0x1f8` is `-1`, replace it with transition-source
   field `+0x1fc` before choosing the branch.
2. With time zero, dispatch active page slot 8 at `0x00466b12`
   (source-correlated `DeActiveNotification`). **After that callback returns**,
   reload the active-page word at `0x00466b19`, push it, and call destination
   slot 6 at `0x00466b29` (`TransitionNotification`). Reload the active word
   again at `0x00466b33` before destination slot 7 at `0x00466b3c`
   (source-correlated `ActiveNotification`). Only afterward store the requested
   page into `+0x1f8`. Callback side effects could therefore affect later reads;
   this is not a snapshot of the original page taken before all callbacks.
3. With nonzero time, store zero bits at count field `+0x204`, copy current
   page to `+0x1fc`, store requested page at `+0x200`, set active page to `-1`,
   and store converted time at `+0x208`. Then dispatch destination slot 6 at
   `0x00466b8a`, with source-page DWORD pushed from `+0x1fc`.

Both slot-6 calls transport the source-page argument at callee stack+4 and
receiver in ECX. EDX coincidentally still holds the page in the immediate
branch; in the timed branch EDX holds the destination's vptr. An EDX page
formal cannot be justified from the immediate branch alone. The
ordered interface evidence (in the decompilation notes, not yet published)
checks these local paths and all known holders.

The source uses integer transition counters; the retail timed body stores a
float duration, and the Process recheck (in the decompilation notes, not yet published)
records the retail float update/completion path. The former unqualified
“source-parity” label is too broad. This section is static instruction evidence,
not a retail or isolated execution of SetPage itself. The cheapest remaining
causality check is an original-code probe with callbacks that alter the active
page, followed by inspection of subsequent callback arguments and final fields.
Receiver bounds, nullability, callback reentrancy and exception behavior remain
unvalidated.

## Callers

The body makes four indirect calls, at `0x00466b12`, `0x00466b29`, `0x00466b3c` and `0x00466b8a`, in the
order described above. Its direct callers:

- Caller `CFrontEnd__HandleModalPanelButton` `0x0044dd60`, 2 sites.
- Caller `CFEPBEConfig__ButtonPressed` `0x00450090`, 2 sites.
- Caller `CFEPBriefing__ButtonPressed` `0x00451c20`, 2 sites.
- Caller `CFEPDebriefing__ButtonPressed` `0x004568a0`, one site.
- Caller `CFEPDemoMain__DoAction` `0x00457ee0`, one site.
- Caller `CFEPDevelopment__RefreshWorldListCore` `0x00458710`, one site.
- Caller `CFEPDevSelect__VFunc_3_00458a10` `0x00458a10`, one site.
- Caller `CFEPDevSelect__VFunc_2_00458e00` `0x00458e00`, 2 sites.
- Caller `CFEPMultiplayerStart__SubObj8848__Process` `0x00459b00`, one site.
- Caller `CFEPMultiplayerStart__SubObj8848__ButtonPressed` `0x00459c10`, 2 sites.
- Caller `CFEPLevelSelect__ButtonPressed` `0x004606b0`, 2 sites.
- Caller `CFEPLoadGame__ButtonPressed` `0x00461c60`, one site.
- Caller `CFEPLoadGame__DoLoad` `0x00461e20`, 2 sites.
- Caller `CFEPMain__DoAction` `0x004623e0`, 5 sites.
- Caller `CFEPMain__Process` `0x00462640`, 2 sites.
- Caller `CFEPSaveGame__ButtonPressed` `0x00464630`, one site.
- Caller `CFEPSaveGame__Process` `0x00464730`, 2 sites.
- Caller `CFEPSaveGame__CreateSave` `0x00464c50`, 3 sites.
- Caller `CFrontEnd__Init` `0x004662a0`, 4 sites.
- Caller `CFEPCredits__ButtonPressed` `0x0051a7f0`, one site.
- Caller `CFEPCredits__Process` `0x0051a820`, one site.
- Caller `CFEPDirectory__ButtonPressed` `0x0051aaf0`, 2 sites.
- Caller `CFEPDirectory__RefreshSaveFileList` `0x0051ad30`, one site.
- Caller `CFEPMultiplayerStart__SubObj4034_T3_0051b660` `0x0051b660`, one site.
- Caller `CFEPLanguageTest__ButtonPressed` `0x0051c090`, one site.
- Caller `CFEPMultiplayer__VFunc_3_0051ccb0` `0x0051ccb0`, 2 sites.
- Caller `CFEPMultiplayer__VFunc_2_0051d020` `0x0051d020`, one site.
- Caller `CFEPMultiplayerStart__ButtonPressed` `0x0051de60`, one site.
- Caller `CFEPOptions__SaveDefaultOptions` `0x0051f500`, 2 sites.
- Caller `CFEPOptions__Process` `0x0051f600`, one site.
- Caller `CFEPScreenPos__ButtonPressed` `0x0051fa00`, 2 sites.
- Caller `CFEPVirtualKeyboard__ButtonPressed` `0x00520370`, one site.
- Caller `CFEPVirtualKeyboard__HandleKeyToken` `0x00520cc0`, one site.
- Caller `CFEPWingmen__ButtonPressed` `0x00521d20`, one site.
