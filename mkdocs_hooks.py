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

Two checks ride along at the bottom of the file, unrelated to the sidebar:
every TAB inside a fence has to reach the page's HTML, and no fence title may
hold a backtick, which GitHub cannot parse. Each has a comment block of its own
saying why.
"""

from __future__ import annotations

import logging
import pathlib
import re

# A child of the "mkdocs" logger, so `mkdocs build --strict` counts its warnings.
log = logging.getLogger("mkdocs.plugins.mkdocs_hooks")

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
    "which_end_comes_first": "The bytes do not say which end",
    "utf8_by_hand": "UTF-8 by hand",
    "look_paste_tee_split": "look, paste, tee and split",
    "utf16_and_surrogates": "UTF-16 and surrogates",
    "byte_order_and_bom": "Byte order and the BOM",
    "bom_in_a_csv": "A BOM in a CSV",
    "crlf_vs_lf": "CRLF vs LF",
    "sap_code_pages": "SAP code pages",
    "writing_a_code_point": "Writing a code point",
    "typing_a_character": "Typing a character",
    "uni_help": "uni -h, line by line",
    "pcre2": "PCRE2",
    "sh": "The shell has no string type",
    "surrogateescape": "surrogateescape",
    "what_a_regex_matches": '"Supports Unicode" is a level, not a yes',
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
        "14_Resources",
        "RIPGREP.md",
        "KATAS.md",
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
        "arithmetic_has_its_own_width",
        "which_end_comes_first",
        "which_base_did_you_mean",
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
        "noncharacters_and_private_use",
        "preparing_a_string",
        "precis_after_stringprep",
        "a_code_point_is_not_a_character",
        "case_is_not_per_character",
        "where_a_line_may_break",
        "confusables_and_scripts",
        "logical_and_visual_order",
        "unicode_in_identifiers",
        "what_a_regex_matches",
        "rune_is_an_int32",
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
        "the_encoding_model",
        "utf7_and_the_seven_bit_transport",
    ],
    "04_Python": [
        "README.md",
        "str_vs_bytes",
        "encode_decode_and_errors",
        "surrogateescape",
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
        "osstr_path_and_wtf8",
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
        "binary_or_text",
        "terminal_hyperlinks",
        "pipe_is_not_a_terminal",
    ],
    "08_Build_Your_Own": [
        "README.md",
        "tribit",
        "framing_a_format",
    ],
    # The story, in the order it happened.
    "09_History": [
        "README.md",
        "from_telegraph_to_unicode",
        "why_utf8_won",
        "why_utf16_stayed",
        "a_token_is_not_a_character",
    ],
    # The universal rules first, then the two languages, then the wire.
    "10_Best_Practices": [
        "README.md",
        "utf8_everywhere",
        "rust_strings_in_practice",
        "python_text_in_practice",
        "what_your_language_gives_you",
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
        "sh",
        "cut",
        "tr_and_sort",
        "diff_and_cmp",
        "look_paste_tee_split",
        "creating_and_writing_files",
        "hexdump",
        "xxd",
        "od",
        "strings",
        "uni",
        "uni_help",
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
    # Not a chapter of the course -- what you use once the reading is done.
    "14_Resources": [
        "README.md",
        "anki",
        "hard_strings",
    ],
    "07_Real_Data": [
        "README.md",
        "sap_code_pages",
        "mojibake_round_trip",
        "bom_in_a_csv",
        "fixed_width_byte_fields",
        "packing_a_record",
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


# ---------------------------------------------------------------------------
# Fenced TABs. Python-Markdown expands every TAB in a page to spaces --
# `expandtabs(4)`, in its NormalizeWhitespace preprocessor -- before any fence
# is parsed, so until 2026-09-10 no page on this site carried a TAB byte. That
# included output where the TAB is part of the format: the one before each path
# in the `git ls-files --eol` listing on 07_Real_Data/crlf_vs_lf, and the
# TAB-separated fields of the magic(5) excerpt on
# 06_Terminal/file_type_is_four_questions, arrived as spaces, while GitHub
# rendered the same Markdown with the TABs intact.
#
# The fix is one line of mkdocs.yml: `preserve_tabs: true` on
# pymdownx.superfences, which lifts fences out ahead of that pass. Upstream
# calls the option experimental, and losing it would break nothing a build
# reports, so this is the check: a page whose fences hold N TABs in its
# Markdown must hold at least N in its HTML, or the build warns and `--strict`
# fails.
#
# Only closed fences at the left margin are counted, which is where every
# fenced TAB in the library sits. The option also keeps the TABs in a fence
# nested in a list or a blockquote; not counting those means they can make the
# check pass but never fail. "At least N" rather than N because the homepage
# inlines README.md through pymdownx.snippets, and an inlined fence's TABs are
# in the HTML without being in `page.markdown`.
# ---------------------------------------------------------------------------

FENCE_OPEN = re.compile(r"`{3,}|~{3,}")


def _fenced_tabs(markdown: str) -> int:
    """TABs inside the closed fences that start at the left margin."""
    total = pending = 0
    fence = None
    for line in markdown.split("\n"):
        if fence is None:
            m = FENCE_OPEN.match(line)
            if m:
                fence, pending = m.group(), 0
        elif re.fullmatch(rf"{fence[0]}{{{len(fence)},}}\s*", line):
            total += pending
            fence = None
        else:
            pending += line.count("\t")
    return total


def on_page_content(html, page, config, files):
    """Warn when a page's HTML holds fewer TABs than its fences did."""
    want = _fenced_tabs(page.markdown)
    got = html.count("\t")
    if got < want:
        log.warning(
            "Fenced TABs lost: %s has %d inside its fences and %d in its "
            "HTML. Is `preserve_tabs: true` still set on pymdownx.superfences?",
            page.file.src_uri,
            want,
            got,
        )
    return html


# ---------------------------------------------------------------------------
# Backticks in a fence title. CommonMark forbids a backtick in the info string
# of a BACKTICK fence, so on github.com a line like
#
#     ```text title="Real output — `cargo test`"
#
# is not a fence at all. Measured 2026-09-10 with `gh api markdown`: the opener
# renders as the start of a paragraph, and the block's closing ``` opens a new
# code block that runs to the next bare fence line. That swallowed the lesson's
# next paragraph after 21 of 24 such fences, and on the Rust library's
# 15_First_Programs/rustc_without_cargo everything to the end of the page.
# pymdownx.superfences accepts the form, so neither the site nor `--strict`
# ever showed it. The 24 came out on 2026-09-10, 13 here and 11 in the Rust
# library ("Drop the backticks from fence titles, which GitHub cannot parse");
# this check is what stops the 25th.
#
# Fences are tracked the CommonMark way: one closes on the first later line of
# its own character, at least as long, with nothing after it but whitespace.
# So the bad form shown INSIDE a longer or a ~~~ fence, which is how a page
# about the rule has to show it, is content and passes. A ~~~ fence may hold a
# backtick in its info string, and passes; so does a four-backtick ````rust
# fence, which a line grep for a backtick after the fence cannot tell from the
# real thing. Leading indentation and `>` are skipped, because GitHub reads a
# fence in a list item or a blockquote by the same rule. And a line that only
# starts with a code span, ```` ``` ```` say, is a paragraph on both surfaces
# -- superfences cannot read it as a fence header either -- so it passes too.
#
# README.md is excluded from the build, because index.md inlines it through
# pymdownx.snippets, yet it is the first page github.com shows. So a file a
# page inlines is scanned as well, whole, and named by its own path.
# ---------------------------------------------------------------------------

FENCE_LINE = re.compile(r"(?P<fence>`{3,}|~{3,})(?P<info>.*)")
# A `--8<-- "path"` line, as pymdownx.snippets reads one. A `:section` or
# `:start:end` suffix picks part of the file; the whole file is scanned.
SNIPPET = re.compile(r"""[ \t]*-+8<-+[ \t]+(["'])(?P<path>.+?)\1""")
BACKTICK_TITLE = (
    "Fence title holds a backtick: %s. GitHub does not read a ``` line whose "
    "info string contains one as a fence, so the block's closing ``` "
    "swallows what follows. Name the code bare, or open the fence with ~~~."
)

# The check's own cases, run on every build rather than behind a flag nobody
# passes: a scan that stops catching its own example fails the build instead
# of passing everything quietly.
BACKTICK_TITLE_CASES = [
    ("the title it exists for", '```text title="a `b` c"\nx\n```', [1]),
    ("the same title on a ~~~ fence", '~~~text title="a `b` c"\nx\n~~~', []),
    ("a bare four-backtick fence", "````rust\nfn f() {}\n````", []),
    ("the title shown inside a longer fence",
     '````markdown\n```text title="a `b` c"\nx\n```\n````', []),
    ("the title shown inside a ~~~ fence",
     '~~~markdown\n```text title="a `b` c"\nx\n```\n~~~', []),
    ("the title behind a blockquote's >",
     '> ```text title="a `b` c"\n> x\n> ```', [1]),
    ("the title indented in a list item",
     '1. Step\n\n    ```text title="a `b` c"\n    x\n    ```', [3]),
    ("a line starting with a code span, then the title",
     '```` ``` ```` opens a fence.\n\n```text title="a `b` c"\nx\n```', [3]),
    ("a fence only a bare line closes, then the title",
     '```\n```rust\n```\n```text title="a `b` c"\nx\n```', [4]),
]


def _backtick_titles(markdown: str) -> list[int]:
    """Line numbers of top-level ``` openers whose info string holds a backtick."""
    # superfences' own header pattern, which decides whether the site opens a
    # fence on that line. Imported here, not at the top, so that importing this
    # file still needs nothing beyond the standard library.
    from pymdownx.superfences import RE_NESTED_FENCE_START

    hits: list[int] = []
    fence = None
    for n, line in enumerate(markdown.split("\n"), 1):
        body = line.lstrip(" \t>")
        if fence is None:
            m = FENCE_LINE.match(body)
            if not m:
                continue
            if m["fence"][0] == "`" and "`" in m["info"]:
                header = RE_NESTED_FENCE_START.match(body)
                if header is None or header["unrecognized"]:
                    continue  # not a fence on the site either: a code span
                hits.append(n)
            fence = m["fence"]
        elif re.fullmatch(rf"{fence[0]}{{{len(fence)},}}[ \t]*", body):
            fence = None
    return hits


def _lines_above(page, markdown: str) -> int:
    """Lines MkDocs took off the top of the file before handing the rest over
    as `markdown` -- front matter, and the blank lines after it."""
    try:
        source = page.file.content_string
    except (OSError, ValueError):
        return 0
    if not markdown or not source.endswith(markdown):
        return 0
    return source[: len(source) - len(markdown)].count("\n")


def on_pre_build(config):
    """Warn if the fence-title scan has stopped passing its own cases."""
    for label, text, want in BACKTICK_TITLE_CASES:
        got = _backtick_titles(text)
        if got != want:
            log.warning(
                "The fence-title check is broken: on %s it reports lines %s, "
                "expected %s.",
                label,
                got,
                want,
            )


def on_page_markdown(markdown, page, config, files):
    """Warn once per fence title holding a backtick, here or in what it inlines."""
    src = page.file.src_uri
    skipped = _lines_above(page, markdown)
    for n in _backtick_titles(markdown):
        log.warning(BACKTICK_TITLE, f"{src}:{n + skipped}")
    inlined = {
        m["path"].split(":", 1)[0]
        for m in map(SNIPPET.fullmatch, markdown.split("\n"))
        if m
    }
    for rel in sorted(inlined):
        path = pathlib.Path(config["docs_dir"], rel)
        if path.is_file():
            for n in _backtick_titles(path.read_text(encoding="utf-8-sig")):
                log.warning(BACKTICK_TITLE, f"{rel}:{n}, inlined into {src}")
    return markdown
