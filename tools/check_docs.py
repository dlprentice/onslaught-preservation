#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Check this documentation repository before a pull request (standard library only).

    python3 tools/check_docs.py              # links, anchors, content rules over every tracked Markdown file
    python3 tools/check_docs.py --changed    # also require headers on documents your branch adds or edits
    python3 tools/check_docs.py --changed --base upstream/main   # compare with another Git ref (default: origin/main)
    python3 tools/check_docs.py --self-test  # prove the checks catch what they claim to catch

What it checks, from CONTRIBUTING.md:
  * every relative link resolves to a tracked file or directory, and every heading anchor exists
    (GitHub's anchor rules, approximated);
  * no machine-local path (home directories, drive letters) and no link to a repository of this project that is not on the public list;
  * with --changed (templates under .github/ excepted): a document added since the base branch starts with Status:, Last updated: (or Date:) and
    Summary: (or Verdict:); an edited document that already has any of these fields has all of them.

It does not judge the evidence in a finding, and it cannot tell whether a quoted byte or code fragment is allowed:
read CONTRIBUTING.md for that. Exit status 0 means no problem found, 1 means a problem was found, 2 means the check
could not run (for example, outside a Git checkout).
"""
from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from pathlib import Path

PUBLIC_REPOS = {"onslaught-career-editor", "onslaught-ce", "onslaught-decomp", "onslaught-godot", "onslaught-preservation",
                "onslaught", "ayaresourceextractor", "dlprentice"}
MACHINE_PATH = re.compile(r"(?:/home/[a-z_][a-z0-9_-]*/|/Users/[A-Za-z0-9_.-]+/|\b[A-Za-z]:\\(?:Users|Projects|Work)\\)")
HEADER_FIELDS = (("Status", ("Status",)), ("Last updated", ("Last updated", "Date")), ("Summary", ("Summary", "Verdict")))
LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|(?<!\!)\[[^\]]+\]:\s*(\S+)")
FENCE = re.compile(r"^\s*(```|~~~)")


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout


def slug(heading: str) -> str:
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = re.sub(r"[`*_~]", "", text).strip().lower()
    text = unicodedata.normalize("NFKC", text)
    out = []
    for ch in text:
        if ch.isalnum() or ch in "-_":
            out.append(ch)
        elif ch == " ":
            out.append("-")
    return "".join(out)


def prose_lines(text: str):
    """Yield (line number, line) outside fenced code blocks."""
    fenced = False
    for number, line in enumerate(text.split("\n"), 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            yield number, line


def anchors_of(text: str) -> set[str]:
    seen: dict[str, int] = {}
    found: set[str] = set()
    for _, line in prose_lines(text):
        match = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if match:
            base = slug(match.group(1))
            count = seen.get(base, 0)
            seen[base] = count + 1
            found.add(base if count == 0 else f"{base}-{count}")
        for explicit in re.findall(r'<a\s+(?:name|id)="([^"]+)"', line):
            found.add(explicit)
    return found


def check_links(root: Path, files: list[str], texts: dict[str, str]) -> list[str]:
    problems = []
    tracked = set(git(root, "ls-files", "--cached", "--others", "--exclude-standard").split("\n"))
    directories = {str(Path(f).parent) for f in tracked if "/" in f}
    anchor_cache: dict[str, set[str]] = {}
    for name in files:
        for number, line in prose_lines(texts[name]):
            line = re.sub(r"`[^`]*`", "", line)
            for found in LINK.finditer(line):
                target = found.group(1) or found.group(2)
                target = target.strip("<>")
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("//"):
                    continue
                path_part, _, fragment = target.partition("#")
                if path_part:
                    resolved = (Path(name).parent / path_part).as_posix()
                    resolved = str(Path(*Path(resolved).parts)) if resolved else resolved
                    parts: list[str] = []
                    for piece in resolved.split("/"):
                        if piece == "..":
                            if parts:
                                parts.pop()
                        elif piece not in ("", "."):
                            parts.append(piece)
                    resolved = "/".join(parts)
                    if resolved not in tracked and resolved not in directories and resolved != "":
                        problems.append(f"{name}:{number}: link target not found: {target}")
                        continue
                else:
                    resolved = name
                if fragment and resolved.endswith(".md"):
                    if resolved not in anchor_cache:
                        anchor_cache[resolved] = anchors_of(texts.get(resolved) or (root / resolved).read_text(encoding="utf-8"))
                    if fragment.lower() not in anchor_cache[resolved]:
                        problems.append(f"{name}:{number}: no heading anchor #{fragment} in {resolved}")
    return problems


def check_content(files: list[str], texts: dict[str, str]) -> list[str]:
    problems = []
    for name in files:
        for number, line in enumerate(texts[name].split("\n"), 1):
            if MACHINE_PATH.search(line):
                problems.append(f"{name}:{number}: machine-local path (use <maintainer evidence>/… for a private receipt)")
            for repo in re.findall(r"github\.com/dlprentice/([A-Za-z0-9_.-]+)", line):
                if repo.lower().removesuffix(".git") not in PUBLIC_REPOS:
                    problems.append(f"{name}:{number}: link to a repository that is not a listed public repository")
    return problems


def header_fields(text: str) -> set[str]:
    head = "\n".join(text.split("\n")[:60])
    head = head.split("\n## ")[0]
    present = set()
    for label, spellings in HEADER_FIELDS:
        for spelling in spellings:
            if re.search(rf"^[>\-\s*]*\**{spelling}:\**\s*\S", head, re.M):
                present.add(label)
    return present


def check_headers(root: Path, base: str, texts: dict[str, str]) -> list[str]:
    problems = []
    try:
        added = set(git(root, "diff", "--name-only", "--diff-filter=A", f"{base}...HEAD").split())
        touched = set(git(root, "diff", "--name-only", "--diff-filter=AM", f"{base}...HEAD").split())
    except subprocess.CalledProcessError:
        print(f"check_docs: cannot compare with {base} (fetch it, or pass --base REF)", file=sys.stderr)
        raise SystemExit(2)
    for line in git(root, "status", "--porcelain").split("\n"):
        if line.strip():
            path = line[3:].strip()
            touched.add(path)
            if line.startswith(("A ", "??")):
                added.add(path)
    for name in sorted(touched):
        if not name.endswith(".md") or name not in texts or name.startswith(".github/"):
            continue
        present = header_fields(texts[name])
        if name in added or present:
            missing = [label for label, _ in HEADER_FIELDS if label not in present]
            if missing and (name in added or len(present) < len(HEADER_FIELDS)):
                problems.append(f"{name}: header lacks {', '.join(missing)}")
    return problems


def run(root: Path, changed: bool, base: str) -> int:
    try:
        files = [f for f in git(root, "ls-files", "--cached", "--others", "--exclude-standard", "*.md").split("\n") if f]
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("check_docs: not a Git checkout; nothing was checked.", file=sys.stderr)
        return 2
    texts = {f: (root / f).read_text(encoding="utf-8") for f in files if (root / f).exists()}
    files = [f for f in files if f in texts]
    problems = check_links(root, files, texts) + check_content(files, texts)
    if changed:
        problems += check_headers(root, base, texts)
    for problem in problems:
        print(problem)
    print(f"check_docs: {len(files)} Markdown files, {len(problems)} problem(s).")
    return 1 if problems else 0


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        (root / "a.md").write_text("# Title\n\nStatus: x\n\n## Real Heading\n\nsee [b](b.md#there) [c](b.md#missing) "
                                   "[d](gone.md) [e](#real-heading) [f](#nope) [g](https://example.org/x)\n"
                                   "`[h](ignored.md)`\n```\n[i](ignored.md)\n```\n", encoding="utf-8")
        (root / "b.md").write_text("# B\n\n## There\n\n/home/someone/work and https://github.com/dlprentice/hidden-repo/blob/main/y\n",
                                   encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        texts = {f: (root / f).read_text(encoding="utf-8") for f in ("a.md", "b.md")}
        found = check_links(root, ["a.md", "b.md"], texts) + check_content(["a.md", "b.md"], texts)
        expected = ["a.md:7: no heading anchor #missing in b.md", "a.md:7: link target not found: gone.md",
                    "a.md:7: no heading anchor #nope in a.md", "b.md:5: machine-local path (use <maintainer evidence>/… for a private receipt)",
                    "b.md:5: link to a repository that is not a listed public repository"]
        failures = [e for e in expected if e not in found]
        extra = [f for f in found if f not in expected]
        if failures or extra or header_fields(texts["a.md"]) != {"Status"}:
            print("SELF-TEST FAIL", failures, extra)
            return 1
        # --base: the ref is read from the command line, and --changed compares with exactly that ref.
        parsed = [parse_base([]), parse_base(["--changed", "--base", "upstream/main"]), parse_base(["--base=fork/x"])]
        if parsed != ["origin/main", "upstream/main", "fork/x"]:
            print("SELF-TEST FAIL --base parsing", parsed)
            return 1
        git_env = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@example.org"]
        subprocess.run(git_env + ["commit", "-q", "-m", "base"], check=True)
        subprocess.run(git_env + ["branch", "upstream-main"], check=True)
        (root / "c.md").write_text("# C\n\nno header here\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "c.md"], check=True)
        subprocess.run(git_env + ["commit", "-q", "-m", "add c"], check=True)
        texts["c.md"] = (root / "c.md").read_text(encoding="utf-8")
        flagged = check_headers(root, "upstream-main", texts)
        if "c.md: header lacks Status, Last updated, Summary" not in flagged:
            print("SELF-TEST FAIL --changed against another ref", flagged)
            return 1
        if any(f.startswith("c.md") for f in check_headers(root, "HEAD", texts)):
            print("SELF-TEST FAIL --changed against HEAD should see nothing new", check_headers(root, "HEAD", texts))
            return 1
    print("SELF-TEST PASS")
    return 0


def fail_base() -> None:
    print("check_docs: --base needs a Git ref, for example --base upstream/main", file=sys.stderr)
    raise SystemExit(2)


def parse_base(argv: list[str]) -> str:
    """The ref --changed compares with: `--base REF` or `--base=REF`; origin/main when absent."""
    base = "origin/main"
    for i, arg in enumerate(argv):
        if arg.startswith("--base="):
            base = arg[len("--base="):]
        elif arg == "--base":
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                fail_base()
            base = argv[i + 1]
    if not base:
        fail_base()
    return base


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    base = parse_base(argv)
    root = Path(__file__).resolve().parent.parent
    return run(root, "--changed" in argv, base)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
