# Contributing

Status: active — how contributions are accepted
Last updated: 2026-11-11 (how to compare against this repository's main from a fork; the findings rule stated)
Summary: where each kind of work belongs, how to propose and check a documentation change, the licence contributions
come in under, the evidence a finding needs, and the material this repository never accepts.

## Where to contribute

This repository holds the documentation of how the game works: file formats, saves, mechanics, levels and engine. It is
edited directly: the maintainer reviews and merges pull requests here, and no response time is promised. Everyone
contributes by fork and pull request; no invitation, collaborator access or private repository is needed. The short map:

- Playing Onslaught CE, its bugs, Linux and Windows issues, the launcher and updates (Internet multiplayer is planned,
  not in this version yet):
  [onslaught-ce](https://github.com/dlprentice/onslaught-ce) (generated; open issues and pull requests there as usual).
- The one rule for findings: documentation of behaviour, formats and mechanics lives here; a function's identity, its
  naming and whether it matches the retail code go to onslaught-decomp.
- The byte-matching decompilation (functions, tools, matching notes):
  [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) (generated; matching work needs your own copy of the
  game plus the compiler and SDK inputs its guide names). This repository uses its function names.
- The Godot rebuild: [onslaught-godot](https://github.com/dlprentice/onslaught-godot).
- The Companion (saves, backups, settings, lore, music) and the program's goals and plan:
  [Onslaught-Career-Editor](https://github.com/dlprentice/Onslaught-Career-Editor). Its `reverse-engineering/` tree is a
  frozen copy of this repository's documents: corrections to game findings come here, not there.
- The [Onslaught](https://github.com/dlprentice/Onslaught) and
  [AYAResourceExtractor](https://github.com/dlprentice/AYAResourceExtractor) forks are pinned references, not
  contribution targets.

The full map, with how each repository takes pull requests, is
[Where to contribute](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/CONTRIBUTING.md#where-to-contribute).
Security problems and leaked private material go through [SECURITY.md](SECURITY.md).
Questions and ideas: https://github.com/dlprentice/onslaught-ce/discussions.

## Your first hour

What you need depends on what you change. There is no application to build and no hosted CI, so the checks below are yours
to run and report in the pull request. They need Git and Python 3 (standard library only), and no game files.

| You are changing | You need | Run before the pull request |
| --- | --- | --- |
| A typo, a wording fix or a broken link | Git, Python 3 and a text editor | `git diff --check` and `python3 tools/check_docs.py` |
| A document's explanation of something already measured | The above | The same, and cite the evidence the document already rests on |
| A new document, or a changed claim | The above | The same with `python3 tools/check_docs.py --changed`, which also requires a header on what your branch adds or edits |
| A new or changed measurement | Your own licensed copy of *Battle Engine Aquila*, and the tool you measured with | The same, plus the evidence and specimen rules below |

`python3 tools/check_docs.py` checks every relative link and heading anchor in the tracked Markdown files and rejects
machine-local paths and links to project repositories that are not public. `python3 tools/check_docs.py --self-test` shows that its checks
catch what they claim to. It does not judge evidence, and it cannot tell whether a quoted byte or code fragment is
allowed: that is the review of your `git diff` below.

`--changed` compares your branch with `origin/main`. In a fork, `origin` is your fork, whose `main` may be behind or
ahead of this repository's. To compare with this repository's `main`, add it as a second remote and name it:

```text
git remote add upstream https://github.com/dlprentice/onslaught-preservation.git
git fetch upstream
python3 tools/check_docs.py --changed --base upstream/main
```

`--base` takes any Git ref (a remote branch, a local branch or a commit). If the ref does not exist the script says so
and exits with status 2; it never falls back to `origin/main`.

Steps:

1. Fork [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation), clone your fork and create a
   branch from `main`: `git switch -c my-change`.
2. Use [`INDEX.md`](INDEX.md) to find the document that owns the subject; keep the finding there and update its folder index
   or [`QUICK-REFERENCE.md`](QUICK-REFERENCE.md) if needed. Keep existing heading text stable when possible, because other
   documents link to its anchors.
3. Make one focused edit, following the header and evidence rules below.
4. Run `git diff --check` and `python3 tools/check_docs.py --changed` (from a fork, add `--base upstream/main` as above), and read `git diff`. Check that external source
   links identify the intended file and revision, and that nothing in the diff is excluded under "Never commit".
5. Commit the scoped files, push the branch to your fork and open a pull request against `main`. The
   [pull request form](.github/pull_request_template.md) asks for what changed, the evidence and the checks you ran or
   could not run.

Commit messages describe the change itself. Leave out session or chat links, private paths and anything copied from the
game; keep any `Co-Authored-By` trailer for someone who wrote part of the change.

For a new measured finding, describe the specimen and its SHA-256, the setup and steps, the observed result,
and the limits of the claim in your own words. Link public evidence at an exact revision where possible.
If the underlying receipt contains material prohibited below, state that the receipt is unavailable publicly
and include only the permitted description and identifying hash; do not attach the receipt to an issue or PR.
An unavailable receipt limits what another contributor can independently verify.

## Licence: inbound = outbound

By opening a pull request you agree that your contribution is licensed under the same terms as the file it changes:
Creative Commons Attribution-ShareAlike 4.0 International ([`LICENSE`](LICENSE)), plus GPL-3.0-only for the notes in
`engine/source/` and for the check script in `tools/`, and MIT for the `formats/aya-resource-extractor-*` notes, as
[`REUSE.toml`](REUSE.toml) records.
Only contribute text you wrote or may license on those terms. Credit for substantial contributions goes in
[`history/attribution.md`](history/attribution.md).

## What a finding needs

- A header: `Status:`, `Last updated:` (or `Date:`) and `Summary:` (or `Verdict:`) in the first lines of every new
  document and of every older document whose claims you change. A typo or link fix to an older document that has no
  header does not need one. A finding that quotes a retail address also has an `Evidence:` line (`MEASURED`, `SOURCE`,
  `INFERRED` or `UNKNOWN`, as the README's "How to read a finding" defines) and names its specimen in a `Specimen:` line
  with the file's SHA-256.
- Evidence for every behaviour claim: a controlled runtime capture, a byte comparison against a named retail file,
  a focused test, or a pinned source file and line. A plausible name or a tool's opinion proves nothing. Write
  unknowns as open questions, with the cheapest check that would settle them.
- Describe what the code does in your own words. Cite function names and addresses; do not paste code. Quotations of
  Stuart Gillam's published source belong in the notes under `engine/source/` (GPL-3.0-only) and the
  `formats/aya-resource-extractor-*` notes (MIT), whose licences [`REUSE.toml`](REUSE.toml) records; a few older documents
  elsewhere carry short fragments of that source with their file and line, and new quotations go in those notes. A new
  folder of quoted source needs its own annotation. Decompiler output is never quoted, anywhere.
- Relative links between documents, no paths from your own machine, and no links to private repositories. Link the
  related public projects by their full URL.

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
