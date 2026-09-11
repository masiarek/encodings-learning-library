"""Go's rune is an int32 -- and Python's decoder already knows what Go would say.

Python has no rune at all: ord() hands back a plain int and chr() a str of
length one. What it does have is a UTF-8 decoder that reports every mistake as
the byte offset where it starts and the offset where it ends -- and that one
report is enough to compute three different counts of U+FFFD: the one Python
writes, the one Go's `for range` loop writes, and the one Go's
strings.ToValidUTF8 writes.

Run:  python3 rune_is_an_int32_py.py
"""

import codecs
from collections import defaultdict
from itertools import product

REPLACEMENT = chr(0xFFFD)

# The decoder calls this once per mistake, with the mistake's start and end.
# It returns the same U+FFFD that errors='replace' would, so the decoded string
# is identical -- the only difference is that we kept notes.
_found: list[tuple[int, int]] = []


def _record(exc: UnicodeDecodeError) -> tuple[str, int]:
    _found.append((exc.start, exc.end))
    return (REPLACEMENT, exc.end)


codecs.register_error("rune_is_an_int32.record", _record)


def mistakes(data: bytes) -> list[tuple[int, int]]:
    """Every mistake the UTF-8 decoder reports in `data`, as (start, end)."""
    _found.clear()
    data.decode("utf-8", "rune_is_an_int32.record")
    return list(_found)


def per_run(found: list[tuple[int, int]]) -> int:
    """Mistakes that touch, end to start, are one run -- and get one marker."""
    return sum(1 for i, (start, _) in enumerate(found) if i == 0 or found[i - 1][1] != start)


def ranges(values: list[int]) -> str:
    """[0x80, 0x81, ..., 0xBF] -> '80-BF'."""
    values = sorted(values)
    spans, first, prev = [], values[0], values[0]
    for v in values[1:]:
        if v != prev + 1:
            spans.append((first, prev))
            first = v
        prev = v
    spans.append((first, prev))
    return " ".join(f"{a:02X}-{b:02X}" if a != b else f"{a:02X}" for a, b in spans)


print("1. HOW MANY VALUES EACH LANGUAGE WILL CALL ONE CHARACTER")
int32_values = 2**32
code_points = 0x10FFFF + 1
surrogates = 0xDFFF - 0xD800 + 1
scalar_values = code_points - surrogates
print(f"   Go       a rune is an int32          {int32_values:>13,}   every one of them")
print(f"   Python   chr() takes a code point    {code_points:>13,}   surrogates included")
print(f"   Rust     a char is a scalar value    {scalar_values:>13,}   surrogates refused")
print()
for label, value in [("-1", -1), ("0x41", 0x41), ("0xD800", 0xD800), ("0x110000", 0x110000)]:
    try:
        ch = chr(value)
    except ValueError as exc:
        print(f"   chr({label})".ljust(19) + type(exc).__name__)
        continue
    try:
        encoded = ch.encode("utf-8").hex(" ")
    except UnicodeEncodeError as exc:
        encoded = type(exc).__name__
    print(f"   chr({label})".ljust(19) + f"{ascii(ch):<10} .encode('utf-8') -> {encoded}")
print("   Python checks the RANGE at chr() and leaves the surrogates to .encode().")
print("   Rust checks both, at char::from_u32. A Go rune checks neither: it is an")
print(f"   int32, and {int32_values - scalar_values:,} int32 values are not a scalar value --")
print("   the only kind of number UTF-8 can write. -1, 0xD800 and 0x110000 are three")
print("   of them, and nothing in the type records which.")
print()

print("2. ONE U+FFFD PER MISTAKE, PER BYTE, OR PER RUN")
CASES = [
    (bytes.fromhex("c3"), "é cut after 1 of its 2 bytes"),
    (bytes.fromhex("e2 82"), "€ cut after 2 of its 3 bytes"),
    (bytes.fromhex("f0 9f 98"), "😀 cut after 3 of its 4 bytes"),
    (bytes.fromhex("ed a0 80"), "U+D800 in the shape of UTF-8"),
    (bytes.fromhex("f4 90 80 80"), "one past U+10FFFF, same shape"),
]
print(f"   {'bytes':<12} {'mistakes at':<16} {'per mistake':>11} {'per byte':>9} {'per run':>8}   what they are")
for data, what in CASES:
    found = mistakes(data)
    written = data.decode("utf-8", "replace").count(REPLACEMENT)
    assert written == len(found), (data, written, found)
    at = " ".join(f"{s}-{e}" for s, e in found)
    per_byte = sum(e - s for s, e in found)
    print(f"   {data.hex(' '):<12} {at:<16} {written:>11} {per_byte:>9} {per_run(found):>8}   {what}")
print()
print("   'mistakes at' is what Python's decoder reports: byte offsets, end excluded.")
print("   per mistake  is what Python writes -- counted, not computed.")
print("   per byte     is what Go's `for range` loop writes, and what")
print("                utf8.RuneCountInString counts as that many runes.")
print("   per run      is what Go's strings.ToValidUTF8 writes.")
print("   The last two are computed here from Python's own report; the page puts")
print("   them beside Go itself.")
print()
print("   One decoder, one report, three policies. Per mistake and per byte agree")
print("   whenever every mistake is one byte long, and part only when one is")
print("   longer -- which happens when a character starts correctly and is cut")
print("   short. The first three rows are that one accident at three lengths.")
print("   Per run parts from both whenever mistakes touch, and rows 4 and 5 are")
print("   nothing but touching one-byte mistakes.")
print()

print("3. EVERY INPUT OF ONE OR TWO BYTES")
checked = agree = differ = long_where_differ = long_where_agree = 0
parted: dict[int, list[int]] = defaultdict(list)
for n in (1, 2):
    for values in product(range(256), repeat=n):
        data = bytes(values)
        found = mistakes(data)
        is_long = any(e - s > 1 for s, e in found)
        checked += 1
        if len(found) == sum(e - s for s, e in found):
            agree += 1
            long_where_agree += is_long
        else:
            differ += 1
            long_where_differ += is_long
            parted[data[0]].append(data[1])
print(f"   inputs                                         {checked:>7,}")
print(f"   per mistake and per byte agree                 {agree:>7,}")
print(f"   they differ                                    {differ:>7,}")
print(f"   ...differing, with a mistake over one byte     {long_where_differ:>7,}   every one")
print(f"   ...agreeing, with a mistake over one byte      {long_where_agree:>7,}   none")
print()
print("   Which ones? The program was never given the UTF-8 table. It read these")
print("   ranges off the inputs where the two counts parted:")
rows: list[list] = []
for lead in sorted(parted):
    text = ranges(parted[lead])
    if rows and rows[-1][2] == text and rows[-1][1] == lead - 1:
        rows[-1][1] = lead
        rows[-1][3] += len(parted[lead])
    else:
        rows.append([lead, lead, text, len(parted[lead])])
for first, last, text, count in rows:
    leads = f"{first:02X}" if first == last else f"{first:02X}-{last:02X}"
    print(f"       lead {leads:<6} then {text:<6} {count:>5}")
print("   Every row is the first two bytes of a three- or four-byte character with")
print("   nothing after them. Note where ED and F4 stop: 9F and 8F. ED A0 would")
print("   begin a surrogate and F4 90 a number past U+10FFFF, so the decoder turns")
print("   the pair down at its second byte and reports the lead byte alone -- a")
print("   one-byte mistake, which is why the two counts agree there.")
