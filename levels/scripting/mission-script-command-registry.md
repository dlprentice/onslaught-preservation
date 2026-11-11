# The Mission script-command registry, recovered from shipped data

Status: active, bounded static registry recovery; boundary and metadata disposition updated
Last updated: 2026-11-11 (pointers to the signatures table, the corrections page and the natives overview; earlier, 2026-11-06: retraction history removed, Git keeps it; renaming state stated once; tiers defined)
Evidence: MEASURED — abstract interpretation of the stores in
`ScriptCommandRegistry__InitBuiltins` against the pristine specimen,
reconstructing the record array at `0x0064CE20` and reading its name/handler
pairs, joined to the function names of the time; UNKNOWN — every
handler signature, argument contract, side effect and runtime behaviour, none of
which this recovery addresses.
Summary: 144 script commands are paired one-to-one with 144 unique handler
addresses by the game's own data, and every handler resolves to a known function.
This proves registry vocabulary only, not C++ symbols, signatures or semantics.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

What the registry leaves open is partly answered elsewhere: [the declared signatures table](mission-script-command-signatures.tsv) and
[the corrections page](mission-script-registry-corrections.md) give each command's declared arguments and what 34 of them
do, and [the natives overview](native-behaviour.md) describes what 33 natives do.

## Prior art — corrected 2026-08-12, this recovery was less novel than first written

**This document originally presented the registry as a new recovery. That was wrong.** The registry was already tracked:

- The earlier function catalogue (archived research record, not published) carries
  **Appendix A: complete 144-entry MissionScript native registry**, with 144
  numbered rows already naming `GetRealHealth`, `GetInitialHealth`,
  `SpawnersEmpty`, `EnableWeapon` and `SetSpeed`.
- `IScript.cpp.md` (in the decompilation notes, not yet published) already states that
  `ScriptCommandRegistry__InitBuiltins` initialises 144 contiguous `0x40`-byte
  descriptor slots at base `0x0064CE20`, already binds the `Pause` row to
  `0x00537C70` from direct stores, and already declines to promote that name.

The prior-art check found `<maintainer evidence>/msl/natives.json`, but the earlier catalogue
was not checked before the first write.

What this document still contributes, and what the earlier work did not have:

- the handler pointers **resolved against the dated 2026-08-12 name table**,
  which identifies the original 54 slots whose handlers carried default names;
- the refutation and alignment checks below;
- the 23-row adjudication, which finds that five handlers documented as
  `IScript__PlaySound*` in `functions/IScript.cpp.md` (in the decompilation notes, not yet published) queue localized messages;
  the downstream message-box path can then start voice or fall back to text.

Read the structure section below as reproduction and extension of tracked
evidence, not as first recovery.

## Structure

`ScriptCommandRegistry__InitBuiltins @ 0x0052FF30` (13,429 bytes) populates a
record array at `0x0064CE20` using `mov [absolute], reg` and
`mov [absolute], imm` stores, holding shared constants in registers across long
runs. Interpreting those stores abstractly — tracking `mov reg, imm`,
`xor reg, reg`, and clearing on `call` — reconstructs the table with **zero
stores left on an untracked register**.

| Property | Value |
| --- | --- |
| Record stride | `0x40` |
| Command-name pointer | record `+0x00` |
| Handler function pointer | record `+0x30` |
| Records recovered | 144, terminating cleanly at index 144 |
| Unique handler pointers | 144 |
| Handlers resolving to a saved function entry | 144 |
| Callable handler entries absent from the current function census | 0 |
| Handlers without a descriptive name | 0 |
| Handlers on SetSpeed's no-op handler | 1 |

The 144 count independently matches the 144-slot native table reached from the
opposite direction by the compiled-script work (unpublished, not in this repository), which indexes this table with a
`CALL` operand masked to `& 0xff`.

The `isFunctionEntry` column in the TSV is undated and reads `False` for 34 rows, the number that the Boundary section below says was added to the function inventory later. Read that column as the state before that addition; the table above is the current census.

## Two independent channels agree on three names

The same day, the
PC-native source-coordinate instrument (archived research record, not published)
singled out `0x005359D0`, `0x00535A30` and `0x00535A90` as unnamed functions
carrying exact `IScript.cpp` coordinates at lines 1158, 1173 and 1188. The
registry assigns those same three handlers the commands `GetRealHealth`,
`GetInitialHealth` and `SpawnersEmpty`.

Unlike the PC/Xbox coordinate pair — which share a signal and must not be cited
as mutual corroboration — these two channels are genuinely independent: one reads
debug-allocator arguments, the other reads a registrar's stores.

## Refutation, and why the 54 names required a separate promotion

Three checks were run before any renaming was contemplated.

**Second read agrees on 143 of 144 rows — passed.** An earlier read of the same
table, by a different author and method, agrees on every index/name pair it covers. It
shares this recovery's source, so it is not independent evidence, but it validates
the stride and name-offset arithmetic. The row it leaves out is not named here; the open question is which row that is and why it was left out, and the cheapest check is to diff the second read's index list against the 144 TSV rows.

**Table alignment — passed.** This is the check able to detect a wrong base or
stride. Commands `GetX`, `GetY`, `GetZ` occupy consecutive indices 57, 58, 59 and
land in exact order on `IScript__GetVectorX`, `IScript__GetVectorY`,
`IScript__GetVectorZ`; `SetX`, `SetY`, `SetZ` occupy 60, 61, 62. An off-by-N
stride or wrong base would scatter or reverse those families. It does neither.

**Agreement with pre-existing names — 55 testable, 32 agree, 23 disagree.** Most
of the 23 are cases where the existing name is a descriptive placeholder
and the registry supplies the game's actual command:
`IScript__SetThingValueViaVFunc198_FromArg` is registered as `EnableWeapon`,
`IScript__CheckValueInRange` as `IsNumberBetween`, `IScript__GetVectorLength` as
`Magnitude`. Superseding those is what this registry is for. That count therefore
does not by itself indicate an extraction error — but it does mean **23 existing
names require per-row adjudication before anything is renamed**, because each is
either a name the registry should supersede or a sign that one of the two is
wrong.

The sharpest was `GetVariable` against
`IScript__GetWorldTextSlotTimerValue`. The adjudication below resolves the
apparent conflict: `GetVariable` is the script-facing wrapper vocabulary, while
the narrower world-timer name remains the visible callee mechanism.

**Posture: the recovered pairing and all 23 disagreements are adjudicated.** The
54 unnamed handlers and 21 superseded names are renamed, and the two pan-camera rows
keep their Tier-1 names. Renaming changes the names, not the evidence grade of any handler.

## The 23 adjudications, resolved

They fall into three classes, and only one is a rename candidate.

Two kinds of name are compared. A **Tier-1** name is a self-identity that the shipped binary carries for a function, here the C++ name in the game's own error text. A **Tier-2** name is the script-facing command name that the shipped registry carries for a slot. Under the naming convention used for the renames, a Tier-1 name is kept, and a Tier-2 command name replaces a descriptive placeholder.

**Class 1 — the existing name is the real C++ identity; do not rename (2).**
Indices 114 and 115 are registered `Goto3PointPanCamera` and
`Goto4PointPanCamera`, while their function names are `IScript__Create3PointPanCamera`
and `IScript__Create4PointPanCamera`. Their bodies carry the shipped strings
`FATAL ERROR: null thing passed to 'Create3PointPanCamera'` and its 4-point
counterpart. The game's own error text names the C++ function `Create…`; the
registry names the script command `Goto…`. Both are right about different things,
and adopting the registry string here would destroy a shipped-symbol identity.
This proves from the binary — not from caution — that a registry string is a
script-facing command name rather than a C++ symbol.

**Class 2 — the registry vocabulary superseded five descriptive names (5).**
Before the renaming, five handlers named `IScript__PlaySound*` called no sound
routine directly. Their callees are `CText__GetStringById`, `CMessage__ctor_base` and
`CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`: they build a localized
message and queue it. The two `…Wait` variants add `CEventManager__GetNextFreeEvent`
and `CScheduledEvent__Set`.

The queued message does reach audio. `Insert…SortedAndMaybeAdvance` calls
`CMessageBox__VFunc_0_004B81D0`, which calls `CMessageBox__StartVoiceOrFallbackTextReveal`,
which calls `CText__GetAudioNameById` and `CBinkOpenThread__StartAsync`. A message
carries a voice line, and the message box starts it when the queue advances, so
`PlaySound` is a defensible description of the **effect**. The queue is not script-only:
`CUnit__ApplyDamage` and `CUnit__TriggerEffect` also insert queued messages. The
paragraphs in this class cover the immediate call layer only.

| Idx | Registry command | Earlier name (2026-08-12) |
| ---: | --- | --- |
| 17 | `AddMessage` | `IScript__PlaySound` |
| 28 | `PlayCharMessage` | `IScript__PlaySoundWithCallback` |
| 36 | `PlayCharMessageWait` | `IScript__PlaySoundWithFade` |
| 90 | `PlayPCharMessage` | `IScript__PlaySoundWithPriority` |
| 91 | `PlayPCharMessageWait` | `IScript__PlaySoundWithFadeAndPriority` |

The suffixes on current evidence:

| Suffix | Status | Evidence |
| --- | --- | --- |
| `WithCallback` | unsupported | nothing in `PlayCharMessage` registers a callback |
| `WithFade` | wrong | the two variants it names are the `Wait` forms, which schedule through `CEventManager__GetNextFreeEvent` |
| `WithPriority` | plausibly right | argument seven (`this+0x2C`) is caller-varied on the `PChar` forms and fixed at ten on the others; see the seven-slot map below |
| `WithFadeAndPriority` | split | its `Fade` part is wrong, as for `WithFade`; its `Priority` part is plausibly right, as for `WithPriority` |

The correction is therefore the five-row replacement with the registry's script-facing vocabulary. It does not claim that every old suffix described an absent mechanism. Under the naming convention, `WithPriority` still loses to the shipped Tier-2 command names.

### `CMessage__ctor_base` recovered — and it settles the voice question

`0x004B6E50`, 191 bytes, `ret 0x1c` — **seven stack arguments** plus `this`.
Each is stored to a fixed field, and two are decisive:

| Arg slot | Stored to | Role |
| --- | --- | --- |
| `[esp+0x24]` | `this+0x18` | — |
| `[esp+0x28]` | `this+0x0C` | **the wide message text** — also passed to `WcsLen` |
| `[esp+0x2C]` | `this+0x10` | — |
| `[esp+0x30]` | `this+0x20` | — |
| `[esp+0x34]` | — | **optional audio reader**: if non-zero, `CGenericActiveReader__SetReader` runs and `this+0x38` is set to 1 |
| `[esp+0x38]` | `this+0x28` | — |
| `[esp+0x3C]` | `this+0x2C` | — |

Two facts follow, and both rest on stores rather than on inferred call windows:

1. **A message carries an optional voice stream directly.** Argument five is a
   reader handle; when supplied, the constructor installs it and raises a
   has-voice flag at `this+0x38`. This is the concrete mechanism behind the
   Class 2 audio reach described above: the audio is attached at construction,
   not looked up later.
2. **Display duration is computed from text length.**
   `this+0x14 = WcsLen(text) * [0x005DC6AC] + [0x005D8604]` — a linear reveal
   time. Those two shipped floats are the cheapest next measurement.

Mapping which slots each native fills was then attempted with call boundaries
honoured — each intervening `call` consuming its own callee-popped pushes, named
callees giving an exact count from their `ret imm`. It reaches **three of the
seven** before hitting an indirect virtual call whose consumption cannot be
resolved, and stops there rather than guessing:

| Native | Ctor args 1–3 |
| --- | --- |
| `AddMessage` | **`0x0089C328`**, `ebx`, `eax` |
| `PlayCharMessage` | `ebx`, `ebp`, `eax` |
| `PlayPCharMessage` | `ebx`, `ebp`, `eax` |
| `PlayCharMessageWait` | `ecx`, `eax`, `eax` |
| `PlayPCharMessageWait` | `ecx`, `eax`, `eax` |

Three things follow. `AddMessage` alone passes a **fixed global** as argument
one where every `…CharMessage` form passes a register — the clearest structural
distinction found so far. The plain and `Wait` forms have visibly different
argument shapes. And **`Char` and `PChar` are indistinguishable across all three
resolved arguments**, so whatever separates them lies in arguments four to seven,
which were not reached.

That partial map was the state until the indirect targets were resolved rather
than assumed. Reading the boxed-value vtables directly:

| Vtable | Installs in IScript.cpp | Slot `+0x30` | Arity |
| --- | ---: | --- | --- |
| `0x005E4EA4` | 15× | `CFloatDataType__VFunc_12_0052F290` | `ret 0` |
| `0x005E4D50` | 12× | `SharedVFunc__ReturnZero_00405930` | `ret 0` |
| `0x005E4B4C` | 8× | `SharedVFunc__ReturnZero_00405930` | `ret 0` |
| `0x005E4DF8` | 7× | `SharedVFunc__ReturnZero_00405930` | `ret 0` |
| `0x005E4AF8` | 5× | `SharedVFunc__ReturnField04_0052F540` | `ret 0` |

**Every one takes zero stack arguments**, so the indirect `call [reg+0x30]` that
halted the walk consumes nothing and the backward scan can safely pass it. The
blocker was arity, and the arity is zero, as read from the vtables.

It also identifies the boxed type: vtable `0x005E4EA4` is **`CFloatDataType`**,
and it is the vtable the three characterized health natives install at `+0x00` of
their allocated 0x18-byte return box. So `GetRealHealth`, `GetInitialHealth` and
`SpawnersEmpty` return a **boxed float**, and `+0x30`/`+0x34` are its
zero-argument accessors — consistent with health being a float and with
`SpawnersEmpty` returning a float-encoded boolean.

### The seven-slot map, complete

With getter arity resolved the walk completes for all five. Arguments are pushed
right-to-left, so argument one is the last push and lands at `this+0x18`;
argument seven is the first push and lands at `this+0x2C`.

| Native | 1 | 2 (text) | 3 | 4 | 5 (audio) | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `AddMessage` | **`0x89C328`** | `ebx` | `eax` | `eax` | `ebp` | `eax` | **`0xA`** |
| `PlayCharMessage` | `ebx` | `ebp` | `eax` | `edx` | `edi` | **`0`** | **`0xA`** |
| `PlayCharMessageWait` | `ecx` | `eax` | `eax` | `ecx` | `edi` | `esi` | **`0xA`** |
| `PlayPCharMessage` | `ebx` | `ebp` | `eax` | `eax` | `edi` | **`0`** | **`edx`** |
| `PlayPCharMessageWait` | `ecx` | `eax` | `eax` | `eax` | `edx` | `edi` | **`ecx`** |

Three axes fall out, each on a single slot:

- **Argument 7 → `this+0x2C` is the `P` axis.** The two `PChar` forms pass a
  script-supplied register; the other three hardcode `0xA`. So `P` marks a
  caller-varied numeric parameter where the rest use a fixed ten.
- **Argument 6 → `this+0x28` is the `Wait` axis.** Both plain forms pass literal
  `0`; both `Wait` forms pass a register, alongside their
  `CEventManager__GetNextFreeEvent` scheduling.
- **Argument 1 separates `AddMessage`**, which alone passes the fixed global
  `0x0089C328` where every `…CharMessage` form passes a script value.

**Every one of the five passes a register in argument five**, the audio-reader
slot — so all five can carry a voice line, which closes the Class 2 question from
the store side.

Consequences for the three suffixes. `WithPriority` marks a real difference in the call: a
caller-varied numeric at `this+0x2C` against a fixed ten, which is what a priority would
look like. That it is a priority is a reading, so its status stays plausible rather than
measured. `WithFade` is **wrong**: that axis is argument six's scheduling handle, which is
`Wait`. `WithCallback` is **unsupported**: what distinguishes `PlayCharMessage` from
`AddMessage` is argument one's source, not any callback.

The mechanism evidence is complete for all five handlers. Their names are the registry's
script-facing vocabulary under the naming convention defined above; that choice is a
convention, not a measurement.

**Class 3 — descriptive placeholder the registry supersedes (16).** `GetX/GetY/
GetZ` over `GetVectorX/Y/Z`, `Magnitude` over `GetVectorLength`,
`IsNumberBetween` over `CheckValueInRange`, `EnableWeapon`/`DisableWeapon` over
`SetThingValueViaVFunc198/19C_FromArg`, and similar. `GetVariable` wraps
`CWorld__GetWorldTextSlotTimerValue`, so only the wrapper is at issue and the
callee keeps its name.

Consequently a blanket replacement of all 23 differing descriptive labels
would have been wrong: 21 lose to the registry vocabulary, while the two pan-
camera rows retain stronger shipped Tier-1 self-identities. The 54 previously
unnamed handlers have no such conflict. The renaming keeps script-facing
names distinct from recovered C++ identities.

## A named dormant capability

Exactly one handler is SetSpeed's no-op handler, and its command is **`SetSpeed`**. The
mission language can call it. The handler body does nothing in the static reading; its
runtime effect has not been measured. The cheapest falsifier is a mission script that
calls `SetSpeed` and observes no effect.

## Boundary

A registry string is the **script-facing command name for that slot**. It is not
a recovered C++ symbol, and mapping it onto the existing `IScript__<Command>`
convention would be a well-supported naming choice rather than a proven identity.
This recovery establishes no handler signature, argument contract, write set,
failure behaviour or runtime semantics; the separate work on `SetPos`
and `UnsetObjective` shows what a real contract for one of these costs.

The 34 formerly unresolved handlers were independently established as
additional callable entries. The strict initializer reproduces all 144 pointer
stores; each of the 34 entries decodes to a bounded, RET-reaching CFG in
executable `.text`; their exact reachable byte sets are pairwise disjoint and
intersect none of the 8,136 previously known function bodies; and neither decoded
direct branches nor an all-byte direct-branch over-approximation targets an
interior. Two byte-identical replays and the exact rows are preserved under
`<maintainer evidence>/mission-registry-missing-functions-20260813-v1/`. The 34 were then added
to the function inventory without changing any existing entry. This establishes boundaries and the
8,170 lower bound only—not original names, signatures, semantics, or a final inventory ceiling. The
later 34-function static-contract addendum (in the decompilation notes, not yet published) supplies
bounded instruction-visible envelopes and per-row falsifiers; it does not turn registry vocabulary into
C++ symbols or add runtime evidence.

The discovery receipts are kept by the maintainer under `<maintainer evidence>/mission-native-registry-20260812-v1/`;
the recovered pairing is
[`mission-script-command-registry.tsv`](mission-script-command-registry.tsv).
