# Onslaught preservation: agent guide

Status: active — the single instruction file for this repository; `CLAUDE.md` only points here
Last updated: 2026-11-11 (the findings rule stated)
Summary: what this repository is, the document header convention, and the evidence and content rules for edits.

## What this is

Documentation of how *Battle Engine Aquila* (2003) works: formats, saves, mechanics, levels, engine and platforms.
Behaviour, format and mechanics documentation lives here; function identity, naming and matching go to
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp). Markdown and small TSV/JSON tables only; no app, no
build. The one script is `tools/check_docs.py`, a standard-library link, anchor, header and content check (`python3 tools/check_docs.py --self-test`, then `python3 tools/check_docs.py --changed`). [`README.md`](README.md) is the front page,
[`INDEX.md`](INDEX.md) the front door to the findings, and each folder's `README.md` lists what it holds.

People contributing by pull request start with [`CONTRIBUTING.md`](CONTRIBUTING.md#where-to-contribute), which also
carries the content and commit rules below that apply to them.

## Cross-project navigation

The [Onslaught Toolkit goal](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/GOAL.md#how-progress-is-measured)
defines progress, and its [program](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/PROGRAM.md#cross-project-progress-and-priorities)
owns the dated cross-project chart and queue. Check current product evidence and follow the maintainer's current direction (see the Toolkit's GOAL.md and PROGRAM.md);
preservation findings and their history stay in this repository.

## Document headers

Every new or edited `.md` starts, after its title, with:

```text
Status: <state> — <what the document is>
Last updated: YYYY-MM-DD (<what changed>)
Summary: <one or two sentences>
```

`Last updated:` is the date of the last substantive change to what the document claims; renames, link repairs and
bulk reformatting do not bump it, so a file's last commit can be newer than its header.
`Date:` may stand in for `Last updated:` on a dated finding. A finding that quotes a retail address adds a
`Specimen:` line naming the file and its SHA-256. Headers carry no volatile counts. Keep heading text stable: other
documents link to its anchors.

## Evidence rule

- Every behaviour claim cites a controlled runtime capture, a byte comparison against a named specimen, a focused
  test, or a pinned source file and line (`references/Onslaught/<file>:<line>` means Stuart's source at the commit
  named in the README). This repository has no `references/` folder: the README's
  [How to read a finding](README.md#how-to-read-a-finding) section links the pinned tree, and a document that cites
  it links that tree on first use.
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
- Commits here are public: keep the Co-Authored-By line, add no Claude-Session line, and describe the change itself, not which agent or role made it.
