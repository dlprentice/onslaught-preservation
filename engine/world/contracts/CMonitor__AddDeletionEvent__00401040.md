# CMonitor__AddDeletionEvent

Status: active static contract with bounded execution coverage
Last updated: 2026-10-22 (research-campaign records removed; findings unchanged)
Summary: `CMonitor__AddDeletionEvent` at `0x00401040` lazily creates the monitor's deletion set and adds a
reader cell at its head; two recordings show the lazy-allocation path and the insertion executing, but no
retained trace ties one call's receiver, argument and result together.
Evidence: MEASURED — exact pristine body, two hash-bound execution-coverage products, and two hash-bound
`CGenericActiveReader__SetReader` null-rebind call envelopes. No new replay, recording or native execution.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `Monitor.h` is absent from the pinned source drop; `activereader.h/.cpp` supplies architecture analogy only | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00401040`

## Identity

- Body `[0x00401040,0x004010bd]`, one range, 126 bytes, 39 instructions; raw pristine-body SHA-256
  `b9d3c4afa0c93e5eccdcfbdfabc974da517d24c4172fde6f3a65628127701017`.
- Interface: a member with the receiver in ECX and one stack argument, the reader cell at
  `[entry ESP+4]`; it returns nothing and ends at `0x004010bb` with `RET 0x4`.

## What the body does

- **Null set:** if `[this+4] == 0`, allocate `0x18` bytes through `CDXMemoryManager__Alloc` (`0x005490e0`;
  manager `0x009c3df0`, source-path string `Monitor.h` at `0x00622b80`, line 94), call `CSPtrSet__Init` at
  `0x0040108a`, and store the new set at `[this+4]` (`0x00401093`).
- **Common path:** load the argument (`0x0040109f`) and `[this+4]` (`0x004010a3`) and call
  `CSPtrSet__AddToHead` (`0x004010a7`), which stores the argument as the new wrapper's payload and links
  the wrapper as the set's head.
- **Allocation failure:** `0x00401091 XOR ESI,ESI` reaches the same store and insertion with a null set;
  what `AddToHead` then does is not established.

The body writes no global directly. The pinned source's `CGenericActiveReader` removes its previous
deletion event and adds one to the new monitor, and `ToReadDied()` nulls the pointer; with `Monitor.h` and
the event-delivery code absent, that is analogy, not proof for this retail function.

## Callees and callers

- Callees: `CDXMemoryManager__Alloc` (`0x005490e0`) on the null path, `CSPtrSet__Init` (`0x004e5840`) after
  a successful allocation, and `CSPtrSet__AddToHead` (`0x004e5a80`) on the common path.
- Direct callers in the whole image: `CGenericActiveReader__SetReader` at `0x0040102a`,
  `CThing3rdPersonCamera__ctor` at `0x00418f39`, and `CScriptEventNB__RegisterEventListener` at
  `0x00538a85`. Indirect or inlined equivalents are not covered.

## Runtime coverage (bounded)

### Two recordings reach the successful lazy path

The following independent recordings are hash-bound to copied runtime
`E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4`:

1. Level-512 opening trace, 6,031,409,152 bytes, SHA-256
   `3D3A118FE211EAD7B1E41055E4150DCFF576B6D0CC64879C52D1163BECA94808`.
   Recording receipt SHA-256
   `dec087c4445c67a1c83d94054329c6af3f07caff43696c8ff6775d9bcf19be23`;
   coverage JSONL SHA-256
   `e00382036da957b09007a3c5eba5e1b16c45c1e1aa2d09039453e859960099c8`.
2. Level-521 native take 4, 14,214,496,256 bytes, SHA-256
   `45AB04297F32BB27AC0C80E8ECB0B332E666A9955CAEA0763A83984AFFB74AC2`.
   Recording receipt SHA-256
   `c8e59da9db3f9fd4304d68dc667dc346e622d87c67fbff0fc17c4ec01fa86b98`;
   coverage JSONL SHA-256
   `26d0db3700590167abb26328520beecfdb145562fb9113bf46a48811d5b2ba66`.

Both coverage products contain exactly the same target ranges:
`[0x00401040,0x00401091)` and `[0x00401093,0x004010be)`, 81 + 43 = 124
executed bytes. Against the exact disassembly, that establishes execution in
each recording where the entry null check reaches the allocation body,
allocation returns non-null, `CSPtrSet__Init` executes, and the jump at
`0x0040108f` skips the failure XOR. It separately establishes execution of the
common insertion/return bytes. Byte-union coverage does not prove those bytes
belong to the same invocation. The only two body bytes not observed are
`[0x00401091,0x00401093)`, the allocation-failure `XOR ESI,ESI`.

Coverage is a byte-union, not a call envelope. It supplies no invocation count,
receiver, argument, branch association, before/after memory, inserted-node
payload, or return association. It cannot establish whether an initialized-set
invocation also occurred in either recording.

### Retained call-context controls do not target AddDeletionEvent

The retained call-context catalog reports 92 local-lab call-context products.
An exact target-row search for `entry_va:"0x401040"` finds zero; exact searches
also find no target row for `CMonitor__DeleteDeletionEvent @ 0x0042d9b0` or
`CSPtrSet__AddToHead @ 0x004e5a80`.

Two READY slices do target `CGenericActiveReader__SetReader @ 0x00401000` and
provide a useful can-fail control:

- Level 512: call-context SHA-256
  `6ae1206e2fd9c58b2178ed468e4366e8e5e57da2bb8e7400d0bd6a0e6b9b50d8`,
  receipt `c0968ff62894800623eddca81a1b3c6fd9bb27530ed59a4bac65a714fea4670c`.
  The one gap-free envelope calls from `0x004d8e2a`, enters with receiver
  `ECX=0x08228b38`, carries argument dword zero at `[ESP+4]`, and returns at
  `0x00401031` to `0x004d8e2f`.
- Level 521 take 4: call-context SHA-256
  `fd853be09bf7c8e1c5da358757d0484baaedf12bb635a4ff4abfef7a7bc0ec4e`,
  receipt `2c779a8431b255b657a345db7db6cc220836d82d8844b599602dd029a2631d17`.
  The one gap-free envelope has the same caller/return sites, receiver
  `ECX=0x07a0aa18`, and argument dword zero.

Those are two independent null-rebind envelopes. The static SetReader body
therefore skips its `AddDeletionEvent` call. The captures do not read the old
monitor/set or prove a successful removal, so they are a can-fail control for
registration only—not the requested DeleteDeletionEvent/removal readback.

## Open questions

- No retained trace has a call-to-return envelope for this function, so the runtime receiver and reader
  cell, the set pointer before and after, the already-initialised insertion branch, the inserted payload
  and the return are all unobserved.
- Allocation-failure consequences, duplicate registration, removal behaviour and concurrency are unknown.
- Cheapest falsifier: an offline replay of either recording that snapshots `ECX`, `[ESP+4]` and
  `[ECX+4]` at entry and the set head, count and payload after the store, after the insertion and at
  return, for both the lazy and the already-initialised branch, plus the same fields around
  `CMonitor__DeleteDeletionEvent` (`0x0042d9b0`) as a removal control.
