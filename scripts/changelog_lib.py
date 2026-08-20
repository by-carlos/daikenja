"""Shared CHANGELOG.md section-boundary helper for the release scripts."""

import re

HEADING_RE = re.compile(r"^## \[", re.MULTILINE)


def section_body(text, body_start):
    """Return the trimmed body of the section that starts at body_start.

    body_start is the offset right after a `## [...]` heading line; the
    section runs up to the next `## [...]` heading or end of file.
    """
    next_heading = HEADING_RE.search(text, body_start)
    body_end = next_heading.start() if next_heading else len(text)
    return text[body_start:body_end].strip("\n")
