# CBattleEngine__EnableWeapon

Status: active static contract
Last updated: 2026-10-22 (research-campaign records and decompiler-style code removed)
Summary: source identity and ordered Walker/Jet byte-string forwarding re-derived from pristine instructions; failure and runtime limits remain open.
Source File: `references/Onslaught/BattleEngine.cpp:3229-3234` at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. | Binary: BEA.exe.original.backup, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — complete pristine bodies and actual caller/argument transport, compared with the pinned source; static identity and structure only.
Specimen: `<maintainer evidence>/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x0040dc30`

## Identity and interface

The complete 37-byte body has raw-byte SHA-256
`fa72dd3ff85e273d09fc380eeac638fd7559c07bded84a94d796a390eb92f839`. It is `CBattleEngine__EnableWeapon`;
earlier analysis called it `CBattleEngine__EnableVolumeEntryGroupsByName`, and the filename is kept for links.

A member returning nothing that takes the weapon name (`char *`). The receiver is ECX; the single pointer occupies the first four-byte stack slot;
`RET 4` balances that argument. The `char *` type is supported by the byte comparisons in
the complete callees; it does not establish an arbitrary character encoding or ownership.

## Behavior and limits

Always call Walker `0x00414970` using main `+0x578`, then Jet
`0x004127a0` using main `+0x57c`, forwarding the same name pointer.
There is no mode gate. The Jet helper walks its shared list cursor, compares the byte-string name
case-sensitively against the weapon profile name and sets each matching active
DWORD at `+0x9c` to one.

The wrapper adds no pointer validation, transaction or rollback. No claim is made
about corrupt strings/lists, concurrent mutations or failure recovery. The
September recheck is static; the absence of a recorded execution is not
evidence that the function is dormant.

## Evidence and falsifier

Complete body/source/caller packets: `<maintainer evidence>/test-runs/re-audit-20260926/jet/`.
Exact manifest (archived research record, not published)
and readbacks: `<maintainer evidence>/…/re-audit-20260926/jet-helper-identities/`.
See the [weapon-store contract](../battle-engine-weapon-stores.md#september-27-jet-recheck).
Compare the complete body,
call order, forwarded stack slot and both callees' byte-string comparisons to
falsify this contract. Runtime failure behavior needs a controlled experiment on
owned copies; no game or save was written for this recheck.
