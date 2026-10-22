# Contributing

Status: active — how contributions are accepted
Last updated: 2026-10-22
Summary: the licence contributions come in under, the evidence a finding needs, and the material this repository
never accepts.

## Licence: inbound = outbound

By opening a pull request you agree that your contribution is licensed under the same terms as the file it changes:
Creative Commons Attribution-ShareAlike 4.0 International ([`LICENSE`](LICENSE)), plus GPL-3.0-only for the notes in
`engine/source/` and MIT for the `formats/aya-resource-extractor-*` notes, as [`REUSE.toml`](REUSE.toml) records.
Only contribute text you wrote or may license on those terms. Credit for substantial contributions goes in
[`history/attribution.md`](history/attribution.md).

## What a finding needs

- A header: `Status:`, `Last updated:` (or `Date:`) and `Summary:` in the first lines of every new or edited
  document. A finding that quotes a retail address also names its specimen in a `Specimen:` line with the file's
  SHA-256.
- Evidence for every behaviour claim: a controlled runtime capture, a byte comparison against a named retail file,
  a focused test, or a pinned source file and line. A plausible name or a tool's opinion proves nothing. Write
  unknowns as open questions, with the cheapest check that would settle them.
- Describe what the code does in your own words. Cite function names and addresses; do not paste code.
- Relative links between documents, and no paths from your own machine.

## Never commit

- Game files of any kind: executables, DLLs, archives, levels, textures, models, audio, video, saves, or anything
  converted from them. Screenshots of the game are not accepted either.
- Decompiler output (pseudo-C, decompiled function bodies) from any tool.
- Disassembly listings with raw instruction bytes. A patch document may give the few original and patched bytes of
  the patch site itself; it does not reproduce surrounding code.
- Wholesale dumps of the game's strings or data tables.
- Debugger logs, traces or captures that contain retail bytes.
- Credentials, personal contact details or machine-specific paths.
- Links to disc images or other copies of the game.
