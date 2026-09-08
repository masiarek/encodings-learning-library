"""Kata solution: five damaged fields, sorted by whether a repair can work.

Each field is shown as the READER sees it. The task is to decide, for each,
whether the original text is still recoverable -- and to say what evidence
the decision rests on -- before running any repair.
"""

UTF8 = "utf-8"
LATIN1 = "latin-1"
CP1252 = "cp1252"

FIELDS = [
    ("A", "caf\N{LATIN CAPITAL LETTER A WITH TILDE}\N{COPYRIGHT SIGN}"),
    ("B", "caf?"),
    ("C", "caf\N{REPLACEMENT CHARACTER}"),
    (
        "D",
        "\N{LATIN CAPITAL LETTER A WITH RING ABOVE}\x81"
        "\N{LATIN CAPITAL LETTER A WITH TILDE}\N{SUPERSCRIPT THREE}d"
        "\N{LATIN CAPITAL LETTER A WITH RING ABOVE}\N{MASCULINE ORDINAL INDICATOR}",
    ),
    (
        "E",
        "caf\N{LATIN CAPITAL LETTER A WITH TILDE}"
        "\N{LATIN SMALL LETTER F WITH HOOK}\N{LATIN CAPITAL LETTER A WITH CIRCUMFLEX}"
        "\N{COPYRIGHT SIGN}",
    ),
]


def repair(text, table):
    """One hop back. Returns (text, ok). Never returns something worse."""
    try:
        raw = text.encode(table)
    except UnicodeEncodeError:
        return text, False
    try:
        out = raw.decode(UTF8)
    except UnicodeDecodeError:
        return text, False
    return (out, True) if out != text else (text, False)


def repair_fully(text, table):
    """Keep undoing hops until the guard refuses. Returns (text, hops)."""
    hops = 0
    while True:
        out, ok = repair(text, table)
        if not ok:
            return text, hops
        text, hops = out, hops + 1


print("THE FIVE FIELDS, AS THE READER SEES THEM")
print("-" * 72)
for name, text in FIELDS:
    print(f"   {name}   {ascii(text)}")
print()

print("THE EVIDENCE, BEFORE ANY REPAIR")
print("-" * 72)
print("   Three questions decide it, and none of them changes the data:")
print("     1. Is there a '?' or a U+FFFD? Then a byte was DISCARDED, and")
print("        by whom depends on which of the two it is.")
print("     2. Does the text re-encode under the table that was misapplied?")
print("     3. Do those bytes then decode as UTF-8?")
print()
for name, text in FIELDS:
    marks = []
    if "?" in text:
        marks.append("holds '?' (discarded on WRITE)")
    if "\N{REPLACEMENT CHARACTER}" in text:
        marks.append("holds U+FFFD (discarded on READ)")
    for table in (LATIN1, CP1252):
        try:
            text.encode(table)
            marks.append(f"re-encodes under {table}")
        except UnicodeEncodeError:
            marks.append(f"will NOT re-encode under {table}")
    print(f"   {name}   " + "; ".join(marks))
print()

print("THE VERDICTS")
print("-" * 72)
print(f"   {'':3} {'through latin-1':<28} through cp1252")
for name, text in FIELDS:
    cells = []
    for table in (LATIN1, CP1252):
        out, hops = repair_fully(text, table)
        cells.append(f"{ascii(out)} ({hops} hop)" if hops else "no repair possible")
    print(f"   {name}   {cells[0]:<28} {cells[1]}")
print()

print("READING THE TABLE")
print("-" * 72)
print("   A  repairs, one hop. Ordinary mojibake: UTF-8 read as a one-byte")
print("      table. Both columns agree, because the bytes involved (c3, a9)")
print("      sit outside 0x80-0x9F, where the two tables are identical.")
print()
print("   B  never repairs. The '?' is byte 0x3F, written by the SENDING")
print("      system when its table had no room for the character. Nothing")
print("      about the original survived the write, so no reader can undo it.")
print()
print("   C  never repairs. U+FFFD was written by the READING system when it")
print("      met a byte its table could not use. Same loss, opposite end of")
print("      the wire -- and that is the whole diagnostic value of telling")
print("      the two apart: B is the sender's logs, C is the receiver's.")
print()
print("   D  repairs through latin-1 and NOT through cp1252. This is the")
print("      case the page is about. The text contains U+0081, one of the")
print("      five code points cp1252 cannot write, so the re-encode fails")
print("      before a decode is ever attempted. Latin-1 has all 256 and")
print("      hands the bytes straight back.")
print()
print("   E  repairs through cp1252 in TWO hops, and not through latin-1 --")
print("      the exact mirror of D. The field went through the same broken")
print("      interface twice, and the reader on the far side was a Windows")
print("      one, so the second hop put an f-with-hook in the string. That")
print("      character lives at 0x83 in cp1252 and does not exist in")
print("      latin-1 at all, so the latin-1 re-encode fails.")
print()
print("      D and E together are the point: the table that repairs is the")
print("      table that BROKE it, and guessing wrong does not silently")
print("      half-work -- it refuses.")
print()
original_d, hops_d = repair_fully(FIELDS[3][1], LATIN1)
original_e, hops_e = repair_fully(FIELDS[4][1], CP1252)
print(f"   For the record, D was {original_d!r} ({hops_d} hop through latin-1)")
print(f"   and E was {original_e!r} ({hops_e} hops through cp1252).")
print()

print("THE ONE THAT IS NOT ON THE LIST")
print("-" * 72)
print("   Every verdict above assumed the fields are damaged. Field A was")
print("   read as 'caf' + A-tilde + copyright, and repaired to 'cafe-acute'")
print("   -- but that same string is one a person could legitimately have")
print("   typed, and the method cannot tell:")
innocent = "\N{LATIN CAPITAL LETTER A WITH TILDE}\N{COPYRIGHT SIGN}"
out, ok = repair(innocent, LATIN1)
print(f"      {innocent!r} -> repaired={ok} -> {out!r}")
print()
print("   Same two characters, same successful round trip, and no way to")
print("   know which was meant. The guard proves the bytes ARE valid UTF-8;")
print("   it cannot prove they were meant to be. So decide for the COLUMN")
print("   -- if most of it is damaged the odd innocent row is a price you")
print("   chose, and if only one row looks damaged, look at it by hand.")
