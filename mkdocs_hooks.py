"""Build-time fixes that would otherwise cost a pinned plugin dependency.

Two jobs, both about the sidebar:

1. **Clean chapter labels.** MkDocs derives a section label from the folder name
   on disk, so `01_Bits_and_Bytes/` reads as "01 Bits And Bytes". The numeric prefix exists
   to set reading order in a file listing; it should not be visible in the nav.
   Only *prefixed* folders are relabelled — a lesson folder takes its label from
   its page's own H1, which is already written the way it should read.

2. **Order the sections.** `NAV_ORDER` states the intended reading order per
   folder, keyed by folder path, listing children by their on-disk name.

Why order here rather than by renaming files: a filename is a permanent URL.
Renumbering `03_` to `04_` to insert a lesson would move every page after it and
break any link anyone saved. Ordering is presentation, so it belongs in the
presentation layer. Unlisted pages keep their alphabetical slot at the bottom, so
adding a page needs no edit here.

One structural note that is easy to get wrong: the top-level object MkDocs hands
`on_nav` is a `Navigation`, whose children live on `.items`. Only `Section` has
`.children`. A hook that reaches for `.children` at the top level silently does
nothing at all — the build still succeeds, and the sidebar is simply never
touched.
"""

from __future__ import annotations

import re

PREFIX = re.compile(r"^(\d+)[_-]")

# Words the naive title-caser gets wrong.
FIXUPS = {
    "Vs": "vs",
    "And": "and",
    "Or": "or",
    "The": "the",
    "To": "to",
    "A": "a",
    "In": "in",
    "Of": "of",
}

# Reading order per folder path. Children named by on-disk name; anything not
# listed sorts alphabetically after the listed ones.
NAV_ORDER: dict[str, list[str]] = {
    "": [
        "index.md",
        "00_Start_Here",
        "01_Bits_and_Bytes",
        "02_Characters",
        "03_Encodings",
        "04_Python",
        "05_Rust",
        "06_Terminal",
        "07_Real_Data",
        "08_Build_Your_Own",
        "09_History",
        "10_Best_Practices",
        "CAST.md",
        "GLOSSARY.md",
        "RESOURCES.md",
        "ROADMAP.md",
    ],
    # From one switch to one byte, then how to write a byte down, then how to
    # read a screenful of them.
    "01_Bits_and_Bytes": [
        "README.md",
        "a_byte_is_eight_bits",
        "hex_is_a_shorthand",
        "reading_a_hex_dump",
    ],
    # A character is a number by agreement; the agreements got bigger.
    "02_Characters": [
        "README.md",
        "a_character_is_a_number",
        "control_characters",
        "code_pages",
        "unicode_code_points",
        "the_table_has_a_version",
        "a_code_point_is_not_a_character",
    ],
    # The number is settled; now how to write it as bytes.
    "03_Encodings": [
        "README.md",
        "utf8_by_hand",
        "validation_is_a_boundary",
        "overlong_sequences",
        "utf16_and_surrogates",
        "byte_order_and_bom",
        "encode_and_decode_are_verbs",
        "mojibake",
    ],
    "04_Python": [
        "README.md",
        "str_vs_bytes",
        "encode_decode_and_errors",
        "opening_a_file",
        "normalization",
        "bytes_hex_and_int",
    ],
    "05_Rust": [
        "README.md",
        "string_is_bytes_that_promise_utf8",
        "char_is_four_bytes",
        "from_utf8_and_lossy",
        "slicing_by_byte",
    ],
    "06_Terminal": [
        "README.md",
        "printf_writes_bytes",
        "trailing_newline",
        "character_and_its_bytes",
        "inspecting_a_file",
        "iconv",
        "locale_and_lc_ctype",
        "file_guesses",
    ],
    "08_Build_Your_Own": [
        "README.md",
        "tribit",
    ],
    # The story, in the order it happened.
    "09_History": [
        "README.md",
        "from_telegraph_to_unicode",
        "why_utf8_won",
    ],
    # The universal rules first, then the two languages, then the wire.
    "10_Best_Practices": [
        "README.md",
        "utf8_everywhere",
        "rust_strings_in_practice",
        "python_text_in_practice",
        "interfaces_and_storage",
    ],
    "07_Real_Data": [
        "README.md",
        "sap_code_pages",
        "mojibake_round_trip",
        "bom_in_a_csv",
        "fixed_width_byte_fields",
        "windows_1252_vs_latin1",
        "crlf_vs_lf",
    ],
}


def _label(name: str) -> str:
    """Folder name on disk -> sidebar label."""
    words = PREFIX.sub("", name).replace("_", " ").replace("-", " ").split()
    out = [FIXUPS.get(w.capitalize(), w.capitalize()) for w in words]
    if out:
        out[0] = out[0][0].upper() + out[0][1:]
    return " ".join(out)


def _is_section(item) -> bool:
    return getattr(item, "children", None) is not None


def _first_src(item) -> str:
    """Source path of `item`, or of the first page anywhere beneath it."""
    page_file = getattr(item, "file", None)
    if page_file is not None:
        return page_file.src_uri
    for child in getattr(item, "children", None) or []:
        found = _first_src(child)
        if found:
            return found
    return ""


def _on_disk_name(item, depth: int) -> str:
    """The name NAV_ORDER lists this child by: a filename, or a folder segment."""
    src = _first_src(item)
    if not src:
        return (getattr(item, "title", "") or "").lower()
    parts = src.split("/")
    if not _is_section(item):
        return parts[-1]
    return parts[depth] if depth < len(parts) - 1 else parts[-1]


def _order_key(path: str, name: str) -> tuple[int, str]:
    listed = NAV_ORDER.get(path, [])
    if name in listed:
        return (listed.index(name), "")
    return (len(listed), name.lower())


def _visit(items: list, path: str, depth: int) -> None:
    for child in items:
        if not _is_section(child):
            continue
        name = _on_disk_name(child, depth)
        # Only a numbered chapter folder gets relabelled. A lesson folder's
        # section label already comes from its page H1, which is authored prose;
        # title-casing it here would turn "Significant figures" into
        # "Significant Figures" and fight the page it points at.
        if PREFIX.match(name):
            child.title = _label(name)

    items.sort(key=lambda c: _order_key(path, _on_disk_name(c, depth)))

    for child in items:
        if not _is_section(child):
            continue
        name = _on_disk_name(child, depth)
        _visit(child.children, f"{path}/{name}".lstrip("/"), depth + 1)


def on_nav(nav, config, files):
    """Relabel numbered chapters and apply NAV_ORDER, depth-first."""
    _visit(nav.items, "", 0)
    return nav
