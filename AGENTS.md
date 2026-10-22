# Onslaught preservation: agent guide

Status: active — the single instruction file for this repository; `CLAUDE.md` only points here
Last updated: 2026-10-22 (public related projects are linked by URL)
Summary: what this repository is, the document header convention, and the evidence and content rules for edits.

## What this is

Documentation of how *Battle Engine Aquila* (2003) works: formats, saves, mechanics, levels, engine and platforms.
Markdown and small TSV/JSON tables only; no code, no app, no build. [`README.md`](README.md) is the front page,
[`INDEX.md`](INDEX.md) the front door to the findings, and each folder's `README.md` lists what it holds.

## Document headers

Every new or edited `.md` starts, after its title, with:

```text
Status: <state> — <what the document is>
Last updated: YYYY-MM-DD (<what changed>)
Summary: <one or two sentences>
```

`Date:` may stand in for `Last updated:` on a dated finding. A finding that quotes a retail address adds a
`Specimen:` line naming the file and its SHA-256. Headers carry no volatile counts. Keep heading text stable: other
documents link to its anchors.

## Evidence rule

- Every behaviour claim cites a controlled runtime capture, a byte comparison against a named specimen, a focused
  test, or a pinned source file and line (`references/Onslaught/<file>:<line>` means Stuart's source at the commit
  named in the README).
- Never quote decompiler output or paste retail bytes. Disassembly is described in words or as mnemonics without the
  byte column; a patch document may give only the patch site's original and patched bytes.
- Static evidence establishes identities and structures; only controlled runtime evidence establishes causality and
  values. Unknowns are open questions with the cheapest falsifier.

## Content rules

- No machine paths, home directories, drive letters or private repository paths. Private receipts are written
  `<maintainer evidence>/…`.
- No links to private repositories. Link the public related projects (listed in the README) by full URL.
- No game files, screenshots, string dumps or links to disc images (see [`CONTRIBUTING.md`](CONTRIBUTING.md)).
- Relative links between documents; check them after moving or renaming a file.
- Licences are mapped per path in [`REUSE.toml`](REUSE.toml); a new folder of quoted source needs its own annotation.
