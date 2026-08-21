#!/usr/bin/env python3
"""Assemble the claude.ai upload zips for the writing skills.

claude.ai takes one skill per zip, with the skill folder at the zip root
(SKILL.md beside whatever it reads). A skill there cannot reach another
skill's files, so each zip carries its own copy of every document its
SKILL.md names.

Those copies are generated, never committed. `docs/` stays the single source
of truth, and a zip is rebuilt from it rather than kept in step by hand.

Which documents a skill gets is read out of the skill itself: every
`docs/<name>.md` its SKILL.md mentions, then every document those mention, to
a fixed point. Nothing here lists dependencies by hand, so adding a reference
to a SKILL.md is the whole of the change.

One thing is rewritten on the way out. A skill points at its documents with
`${CLAUDE_PLUGIN_ROOT}/docs/<name>.md`, which Claude Code expands to the
installed plugin directory. claude.ai has no such variable and would read the
path literally, so the generated copy drops the prefix and points at the
`docs/` folder sitting beside it. The skill under `skills/` is never touched.

Usage:  python scripts/build-claude-ai-skills.py
Output: dist/claude-ai/<skill>/  and  dist/claude-ai/<skill>.zip
"""

import re
import shutil
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
DOCS_DIR = REPO_ROOT / "docs"
OUT_DIR = REPO_ROOT / "dist" / "claude-ai"

# The writing half of Daikenja. The project-* skills and meeting-review need the
# ledger, which lives in a project working tree and has no claude.ai equivalent,
# so they are deliberately absent. setup-user's whole job is creating
# ~/.claude/daikenja/, which does not exist there either -- and it is what makes
# the Drive folder the others read. setup-project is absent for both reasons at
# once: it writes that config and seeds a ledger in a working tree. See
# docs/future-work.md.
SHIPPED = ["compose", "doc-review", "preflight", "remember-persona", "self-review", "thread"]

# A `docs/<name>.md` mention anywhere in the file, in prose or in a link.
DOC_REF = re.compile(r"docs/([a-z0-9-]+\.md)")

# Fenced code blocks (``` ... ```), stripped before DOC_REF is applied. A worked
# example can contain a plausible-looking docs/*.md path that is fictional --
# invented content for the example, not a real reference to resolve.
FENCED_CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)

# A `templates/<name>` mention. A skill that scaffolds a file the user does not
# have yet copies it from here, so the template travels with the skill.
TEMPLATE_REF = re.compile(r"templates/([a-z0-9-]+\.(?:md|yaml))")

LIMITATIONS_URL = "https://github.com/by-carlos/daikenja/blob/main/docs/future-work.md"

# Stated as fact in the shipped copy rather than detected at runtime. A skill
# asked to notice that a capability is missing is being asked to notice an
# absence, which is exactly what it fails to do -- so the surface is written
# into the file that only ever runs on that surface.
SURFACE_NOTE = f"""> **This is the claude.ai build of a Daikenja skill.** Settings come from the
> `daikenja` folder in your Google Drive, and there is no project ledger here --
> the ledger skills run only in Claude Code. Known limitations:
> <{LIMITATIONS_URL}>
"""

DISPATCH_NOTE = """>
> **Reviewers do not run as subagents here.** claude.ai has no dispatch, so
> every reviewer runs in this one context and each has read the ones before it.
> They are a checklist read carefully, not independent second opinions, and a
> run in Claude Code is meaningfully stronger. Say so in the `Reviewed:` line,
> and never write that cycle 2 *confirmed* anything.
"""

PERSONA_NOTE = """>
> **There is no local file to fall back to here.** `~/.claude/daikenja/` does
> not exist on claude.ai, and the filesystem this skill can reach is a sandbox
> that is thrown away when the session ends. Writing an entry there would report
> a success and lose the user's prose, so on this surface the local path is not
> a fallback -- it is a failure.
>
> `personas.md` means the file in the `daikenja` folder in Google Drive, written
> by the replace-and-verify sequence in `docs/config-drive.md`. If the
> connector is missing, the folder does not resolve, or the read-back after the
> write does not confirm, **do not claim a write**: print the exact entry and
> tell the user to paste it in themselves.
"""

# Skills whose behaviour actually changes without dispatch.
DISPATCHES = {"preflight"}

# Skills that write, and so must never fall back to the throwaway sandbox disk.
WRITES = {"remember-persona"}


def add_surface_note(text, skill):
    """Insert the surface preamble directly below the frontmatter block."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            note = SURFACE_NOTE
            if skill in DISPATCHES:
                note += DISPATCH_NOTE
            if skill in WRITES:
                note += PERSONA_NOTE
            return "".join(lines[: index + 1]) + "\n" + note + "".join(lines[index + 1 :])
    return None


def referenced_docs(text):
    """The doc file names a body of text mentions, as a set."""
    return set(DOC_REF.findall(FENCED_CODE_BLOCK.sub("", text)))


def resolve_docs(skill_md_text):
    """Every doc a skill needs, following doc-to-doc references to a fixed point."""
    wanted = referenced_docs(skill_md_text)
    seen = set()
    while wanted - seen:
        name = (wanted - seen).pop()
        seen.add(name)
        doc = DOCS_DIR / name
        if doc.is_file():
            wanted |= referenced_docs(doc.read_text(encoding="utf-8"))
    return sorted(seen)


def build(skill):
    src = SKILLS_DIR / skill / "SKILL.md"
    if not src.is_file():
        return f"{skill}: no SKILL.md at {src}"

    text = src.read_text(encoding="utf-8")
    dest = OUT_DIR / skill
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    # Point the document references at the copies placed beside SKILL.md.
    # Claude Code expands ${CLAUDE_PLUGIN_ROOT}; claude.ai does not, and would
    # read the unexpanded path as a literal file name.
    shipped = text.replace("${CLAUDE_PLUGIN_ROOT}/docs/", "docs/")
    shipped = shipped.replace("${CLAUDE_PLUGIN_ROOT}/templates/", "templates/")
    if "CLAUDE_PLUGIN_ROOT" in shipped:
        return (
            f"{skill}: SKILL.md still references CLAUDE_PLUGIN_ROOT outside "
            "docs/ after rewriting, which cannot resolve on claude.ai"
        )

    shipped = add_surface_note(shipped, skill)
    if shipped is None:
        return f"{skill}: SKILL.md has no frontmatter block to insert the surface note below"

    (dest / "SKILL.md").write_text(shipped, encoding="utf-8", newline="\n")

    carried = []
    for name in resolve_docs(text):
        doc = DOCS_DIR / name
        if not doc.is_file():
            return f"{skill}: SKILL.md references docs/{name}, which does not exist"
        (dest / "docs").mkdir(exist_ok=True)
        shutil.copyfile(doc, dest / "docs" / name)
        carried.append(name)

    for name in sorted(set(TEMPLATE_REF.findall(text))):
        template = REPO_ROOT / "templates" / name
        if not template.is_file():
            return f"{skill}: SKILL.md references templates/{name}, which does not exist"
        (dest / "templates").mkdir(exist_ok=True)
        shutil.copyfile(template, dest / "templates" / name)
        carried.append(f"templates/{name}")

    archive = OUT_DIR / f"{skill}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(dest.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(dest.parent))

    size_kb = archive.stat().st_size / 1024
    docs_note = ", ".join(carried) if carried else "no supporting docs"
    print(f"  {skill}.zip  ({size_kb:.1f} KB)  {docs_note}")
    return None


def main():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    print(f"Building {len(SHIPPED)} claude.ai skill zips into {OUT_DIR}:")
    errors = [err for err in (build(skill) for skill in SHIPPED) if err]

    if errors:
        print("\nBuild failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("\nUpload each zip at claude.ai > Settings > Customize > Skills.")
    print("Requires code execution enabled, on a Pro, Max, Team or Enterprise plan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
