"""Build-time fixes that would otherwise cost a pinned plugin dependency.

Three jobs, all about the sidebar:

1. **Clean chapter labels.** MkDocs derives a section label from the folder name
   on disk, so `01_Bits_and_Bytes/` reads as "01 Bits And Bytes". The numeric prefix exists
   to set reading order in a file listing; it should not be visible in the nav.
   Only *prefixed* folders are relabelled — a lesson folder takes its label from
   its page's own H1, which is already written the way it should read.

2. **Order the sections.** `NAV_ORDER` states the intended reading order per
   folder, keyed by folder path, listing children by their on-disk name.

3. **Fix acronym labels.** A lesson folder's label is its folder name
   title-cased, so `utf8_by_hand` reads as "Utf8 by hand" and `pcre2` as
   "Pcre2". `LABEL_OVERRIDES` restores the page's own H1 casing.

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

# Lesson folders whose sidebar label the title-caser gets wrong, because the
# name holds an acronym: MkDocs turns `utf8_by_hand` into "Utf8 by hand". Each
# value is that page's own H1 casing, so the tree and the page agree. Keyed by
# on-disk folder name -- a folder name is a permanent URL, so the fix belongs
# here rather than in a rename. Like NAV_ORDER, an entry naming a folder that no
# longer exists is a silent no-op.
LABEL_OVERRIDES: dict[str, str] = {
    "utf8_by_hand": "UTF-8 by hand",
    "look_paste_tee_split": "look, paste, tee and split",
    "utf16_and_surrogates": "UTF-16 and surrogates",
    "byte_order_and_bom": "Byte order and the BOM",
    "bom_in_a_csv": "A BOM in a CSV",
    "crlf_vs_lf": "CRLF vs LF",
    "sap_code_pages": "SAP code pages",
    "writing_a_code_point": "Writing a code point",
    "typing_a_character": "Typing a character",
    "pcre2": "PCRE2",
    # 12_Adversarial: the folder names say what the page is ABOUT (and are
    # permanent URLs); the H1s say what it CLAIMS, which is what belongs in a
    # table of contents.
    "parser_differentials": "Two readers, one byte string",
    "canonicalize_then_check": "The check that ran too early",
    "collisions_by_design": "Two people, one account",
    "in_band_signals": "The byte that means something to somebody else",
    "trojan_source": "What you see is not what runs",
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
        "11_Tools",
        "12_Adversarial",
        "13_Documentation",
        "RIPGREP.md",
        "CAST.md",
        "GLOSSARY.md",
        "RESOURCES.md",
        "ROADMAP.md",
        "TODO.md",
        "TOPICS.md",
    ],
    # From one switch to one byte, then how to write a byte down, then how to
    # read a screenful of them.
    "01_Bits_and_Bytes": [
        "README.md",
        "a_byte_is_eight_bits",
        "counting_in_hex",
        "hex_is_a_shorthand",
        "reading_a_hex_dump",
        "grouping_is_a_choice",
        "hex_number_or_bytes",
    ],
    # A character is a number by agreement; the agreements got bigger.
    "02_Characters": [
        "README.md",
        "a_character_is_a_number",
        "rotation_is_not_encryption",
        "control_characters",
        "the_nul_byte",
        "code_pages",
        "unicode_code_points",
        "writing_a_code_point",
        "the_table_has_a_version",
        "preparing_a_string",
        "a_code_point_is_not_a_character",
        "confusables_and_scripts",
        "logical_and_visual_order",
        "unicode_in_identifiers",
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
        "escaping_into_ascii",
        "binary_to_text",
        "base32_alphabets",
    ],
    "04_Python": [
        "README.md",
        "str_vs_bytes",
        "encode_decode_and_errors",
        "opening_a_file",
        "normalization",
        "bytes_hex_and_int",
        "str_in_memory",
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
        "file_type_is_four_questions",
        "the_first_two_bytes",
        "terminal_hyperlinks",
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
    # The tools you already run over text every day, then the ones worth
    # installing. Ordered by how often the tool is reached for, not by depth.
    "11_Tools": [
        "README.md",
        "grep",
        "ripgrep",
        "pcre2",
        "decompress_then_decode",
        "find",
        "xargs",
        "sed",
        "awk",
        "cut",
        "tr_and_sort",
        "diff_and_cmp",
        "look_paste_tee_split",
        "hexdump",
        "xxd",
        "od",
        "uni",
        "typing_a_character",
        "worth_installing",
    ],
    # The five moves, ordered by where they sit in a pipeline: the decode, then
    # the check, then the identity it establishes, then what the value is
    # embedded in -- and last the reader who is a person.
    "12_Adversarial": [
        "README.md",
        "parser_differentials",
        "canonicalize_then_check",
        "collisions_by_design",
        "in_band_signals",
        "trojan_source",
    ],
    # What is installed, then how old it is, then what it leaves out --
    # inventory, provenance, gaps.
    "13_Documentation": [
        "README.md",
        "the_encoding_man_pages",
        "a_page_has_a_date",
        "what_the_page_does_not_say",
    ],
    "07_Real_Data": [
        "README.md",
        "sap_code_pages",
        "mojibake_round_trip",
        "bom_in_a_csv",
        "fixed_width_byte_fields",
        "windows_1252_vs_latin1",
        "crlf_vs_lf",
        "sorting_and_collation",
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
        if name in LABEL_OVERRIDES:
            child.title = LABEL_OVERRIDES[name]
        elif PREFIX.match(name):
            child.title = _label(name)

    items.sort(key=lambda c: _order_key(path, _on_disk_name(c, depth)))

    for child in items:
        if not _is_section(child):
            continue
        name = _on_disk_name(child, depth)
        _visit(child.children, f"{path}/{name}".lstrip("/"), depth + 1)


def _pages_in_nav_order(items: list) -> list:
    """Every page under `items`, depth-first, in the order the sidebar shows."""
    out = []
    for item in items:
        if item.is_page:
            out.append(item)
        elif item.is_section:
            out.extend(_pages_in_nav_order(item.children))
    return out


def on_nav(nav, config, files):
    """Relabel numbered chapters, apply NAV_ORDER, and re-chain prev/next."""
    _visit(nav.items, "", 0)

    # Sorting nav.items fixes the sidebar and nothing else. MkDocs computes
    # every page's previous_page/next_page inside get_navigation(), which runs
    # BEFORE this hook -- so without the re-chain below, the arrows at the foot
    # of a lesson walk the reader alphabetically while the sidebar beside them
    # reads in order. That was live on all 13 chapters until 2026-09-07: the
    # published 11_Tools/index.html said rel="next" -> awk where NAV_ORDER
    # says grep. For a library with a reading order, the arrow IS the order.
    #
    # This repeats mkdocs.structure.nav._add_previous_and_next_links rather
    # than calling it, because that function is private and this is four lines;
    # a pin bump should not be able to break the nav silently.
    ordered = _pages_in_nav_order(nav.items)
    # If MkDocs ever grows a nav item type the walk above does not descend
    # into, this is where it shows -- loudly, at build time, rather than as a
    # handful of pages quietly dropping out of the prev/next chain.
    # Compared by source path, not by identity: MkDocs' Page defines __eq__
    # without __hash__, so a Page cannot go in a set.
    walked = {page.file.src_uri for page in ordered}
    known = {page.file.src_uri for page in nav.pages}
    assert walked == known, (
        "_pages_in_nav_order is out of step with mkdocs.structure.nav: "
        f"missed {sorted(known - walked)}, invented {sorted(walked - known)}"
    )
    for i, page in enumerate(ordered):
        page.previous_page = ordered[i - 1] if i else None
        page.next_page = ordered[i + 1] if i + 1 < len(ordered) else None
    nav.pages[:] = ordered

    return nav
