#!/usr/bin/env python3
"""Why a dump's NAMED-character row is fiction, in the two dialects that print it.

`od -tx1` prints the file. `od -a` prints names, and the two implementations
disagree about what to name a byte above 127:

  GNU od   masks the high bit off and names the 7-bit remainder — c3 -> 'C'
  BSD od   asks isprint() in the current locale, which in a UTF-8 locale answers
           for U+0080..U+00FF, so c3 is 'Ã' (printable) and is emitted RAW; only
           the C1 controls 80..9f fall through to a hex number

Both rules are applied below as arithmetic, so this output is the same on every
machine — which the tools' own output is not. (`str.isprintable()` is a Unicode
table lookup, so it is in principle version-sensitive; every byte it is asked
about here is in U+0080..U+00FF, whose categories have not moved in decades.)

Run:  python3 inspecting_a_file_py.py
"""

import codecs

# od's own names for the 33 unprintable ASCII values (od says "nl", not "lf").
ASCII_NAMES = (
    "nul soh stx etx eot enq ack bel  bs  ht  nl  vt  ff  cr  so  si "
    "dle dc1 dc2 dc3 dc4 nak syn etb can  em sub esc  fs  gs  rs  us"
).split()

TEXT = "café: 1€"


def gnu_name(b: int) -> str:
    """GNU od -a: strip the high bit, then name the low seven."""
    low = b & 0x7F
    if low < 0x20:
        return ASCII_NAMES[low]
    if low == 0x20:
        return "sp"
    if low == 0x7F:
        return "del"
    return chr(low)


def bsd_name(b: int) -> str:
    """BSD od -a in a UTF-8 locale: isprint(b) answered over U+0080..U+00FF."""
    if b < 0x20:
        return ASCII_NAMES[b]
    if b == 0x20:
        return "sp"
    if b == 0x7F:
        return "del"
    if chr(b).isprintable():
        return chr(b)  # emitted as a RAW BYTE; the terminal draws it or gives up
    return f"{b:02x}"  # the only branch that tells you the truth


def owner(data: bytes, index: int, text: str) -> str:
    """Which character of the text does this byte belong to, and how far in."""
    start = 0
    for ch in text:
        width = len(ch.encode("utf-8"))
        if start <= index < start + width:
            part = "whole" if width == 1 else f"byte {index - start + 1} of {width}"
            return f"{ch!r} ({part})"
        start += width
    return "the newline"


def main() -> None:
    data = TEXT.encode("utf-8") + b"\n"

    print("1. ONE LINE OF TEXT, TWO DIFFERENT COUNTS")
    print(f"   text        {TEXT!r}")
    print(f"   characters  {len(TEXT) + 1} (with the newline)")
    print(f"   bytes       {len(data)}  <- this is the number ls -l and wc -c report")
    print(f"   hex         {data.hex(' ')}")
    print()

    print("2. WHERE EACH CHARACTER SITS IN THE BYTES")
    start = 0
    for ch in TEXT:
        raw = ch.encode("utf-8")
        span = f"{start}" if len(raw) == 1 else f"{start}..{start + len(raw) - 1}"
        print(f"   {ch!r:<6} U+{ord(ch):04X}  {len(raw)} byte(s)  offset {span:<6} {raw.hex(' ')}")
        start += len(raw)
    print()

    print("3. THE NAMED-CHARACTER ROW, BY BOTH RULES")
    print("   byte  hex   GNU od -a   BSD od -a (UTF-8 locale)   what the byte really is")
    for i, b in enumerate(data):
        bsd = bsd_name(b)
        drawn = bsd if b < 0x80 else ("raw byte (terminal: ?)" if bsd != f"{b:02x}" else "hex number")
        print(f"   {i:>4}  {b:02x}    {gnu_name(b):<11} {drawn:<24} {owner(data, i, TEXT)}")
    print()

    print("4. WHY ONE BYTE OF THE THREE-BYTE € PRINTS AS A NUMBER AND THE OTHERS DO NOT")
    for b in (0xE2, 0x82, 0xAC):
        cp = chr(b)
        print(f"   {b:02x} -> U+{b:04X} {'printable' if cp.isprintable() else 'a C1 CONTROL, not printable'}"
              f"  =>  BSD od prints {'the raw byte' if cp.isprintable() else 'the hex number ' + f'{b:02x}'}")
    print("   So in a dump of this file, exactly one of the three € bytes shows a number.")
    print("   That is a fact about isprint() and a locale. It is not a fact about the file.")
    print()

    print("5. THE SAME NINE CHARACTERS, RE-ENCODED (what iconv does)")
    for label, blob in (
        ("UTF-8", data),
        ("UTF-16BE, no BOM", (TEXT + "\n").encode("utf-16-be")),
        ("UTF-16BE + BOM", codecs.BOM_UTF16_BE + (TEXT + "\n").encode("utf-16-be")),
        ("UTF-16LE + BOM", codecs.BOM_UTF16_LE + (TEXT + "\n").encode("utf-16-le")),
    ):
        print(f"   {label:<18} {len(blob):>2} bytes  {blob.hex(' ')}")
    print("   Mostly-ASCII text costs MORE in UTF-16, and gains bytes that are 00.")
    print()

    print("6. WHEN UTF-16 IS THE SMALLER FILE (no newline; the text goes last, so nothing")
    print("   has to align after a wide glyph)")
    for s in (TEXT, "日本語"):
        u8 = s.encode("utf-8")
        u16 = s.encode("utf-16-be")
        verdict = "UTF-8 wins " if len(u8) < len(u16) else "UTF-16 wins"
        print(f"   {len(s)} chars   UTF-8 {len(u8):>2} bytes   UTF-16 {len(u16):>2} bytes   {verdict}   {s!r}")
    print("   Neither encoding is 'smaller'. It depends entirely on the text.")


if __name__ == "__main__":
    main()
