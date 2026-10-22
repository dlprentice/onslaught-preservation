# CBattleEngine__CountActiveWeapons

Status: active static contract
Last updated: 2026-10-22 (research-campaign records and decompiler-style code removed)
Summary: mode-selected active-weapon count re-derived from the main dispatcher and complete Jet/Walker callees.
Source File: `references/Onslaught/BattleEngine.cpp:3245-3251` at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. | Binary: BEA.exe.original.backup, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Specimen: `<maintainer evidence>/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x0040dc90`

The six-instruction, 31-byte body ends at `0x0040dcae`; raw-byte SHA-256
`72b3f37b257b58dc1a06d7ea45decbe34d7190f2ded07035e13e7ef5dcb64b8a`.
The name replaces the earlier analysis label `CBattleEngine__CountFlag9CBySelectionMode`;
the filename is kept for links.

A member returning an `int`: ECX is main; there are no stack arguments. State `+0x260 == 3` loads Jet from
`+0x57c` and tail-jumps to `CBattleEngineJetPart__CountActiveWeapons`
(`0x004129a0`). Every other value loads Walker from `+0x578` and tail-jumps to
`CBattleEngineWalkerPart__CountActiveWeapons` (`0x00414b70`). The selected
callee's EAX is returned unchanged.

The Jet callee counts list entries whose weapon active DWORD at `+0x9c` is
nonzero. It uses a local iterator, leaving the shared cursor unchanged; an empty
list yields zero. It counts active entries, not all weapons or admitted shots.
The Walker count identity was separately re-derived in its preceding audit.

Complete bytes, source and actual receiver/callee links settle the earlier identity and
component questions. They do not prove corrupt-list safety,
lifetime, overflow under arbitrary authored state or player-facing behavior.
No execution of these two count helpers is claimed here.

Evidence: MEASURED — nine-row manifest (archived research record, not published),
complete packets under `<maintainer evidence>/test-runs/re-audit-20260926/jet/` and
readbacks under `<maintainer evidence>/…/re-audit-20260926/jet-helper-identities/`.
Cheapest falsifier: compare the branch, receiver offsets and each count callee's
full active-DWORD test against the pristine bytes. A controlled runtime check
would additionally need valid owned lists and observable mode changes.
