# Security

Status: active — how to report sensitive content in this repository
Last updated: 2026-11-06
Summary: how to report leaked private material or other sensitive content in this documentation repository, and what it contains.

## Reporting a problem

This repository holds Markdown and small TSV and JSON tables; its one script, `tools/check_docs.py`, is a standard-library documentation check that sends nothing anywhere. The problems
that matter here are sensitive content committed or posted by mistake: credentials, personal contact details, machine-local
paths, links into private repositories, or game files, decompiler output or disassembly with raw bytes that
[CONTRIBUTING.md](CONTRIBUTING.md) excludes.

Please report those privately, not in a public issue or pull request, through GitHub's **Report a vulnerability** form on
this repository's Security tab
(<https://github.com/dlprentice/onslaught-preservation/security/advisories/new>). Name the file and commit, describe
what it exposes, and leave the sensitive text itself out of the report. A maintainer reads reports there; no response
time is promised.

Documentation errors, wrong claims and broken links are not security problems: open a public
[issue](https://github.com/dlprentice/onslaught-preservation/issues) or pull request.

## Other repositories

Each public repository of the project has its own `SECURITY.md` and reporting form:
[Onslaught CE](https://github.com/dlprentice/onslaught-ce/security/policy),
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp/security/policy),
[onslaught-godot](https://github.com/dlprentice/onslaught-godot/security/policy) and
[Onslaught-Career-Editor](https://github.com/dlprentice/Onslaught-Career-Editor/security/policy). Report a problem in the
repository that owns the affected files.
