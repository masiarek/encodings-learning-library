#!/usr/bin/env python3
"""One line of text, walked through six eras of how text was numbered.

Every era is still in your working life somewhere: the case bit is ASCII's,
the mainframe extract is EBCDIC's, the "almost right" quote is a code page's,
and the surrogate pair is the 16-bit assumption that broke in 1996.

Run:  python3 from_telegraph_to_unicode_py.py
"""

import unicodedata

BAR = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


def pad(s, width):
    """Left-justify by TERMINAL columns, not characters.

    CJK characters occupy two columns, so ljust() — which counts characters —
    leaves a table that is correct and looks crooked.
    """
    cols = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    return s + " " * max(0, width - cols)


# ---------------------------------------------------------------- 1874
head(1, "FIVE BITS (1874): THE ARITHMETIC THAT FORCED A SHIFT KEY")
needed = 26 + 10 + len(" .,:?'-()/+=")
print(f"   patterns in 5 bits : 2**5 = {2**5}")
print(f"   letters + digits + a little punctuation : {needed}")
print(f"   enough? {2**5 >= needed}")
print("   The fix was a MODE, not more bits: one code said 'letters follow',")
print("   another said 'figures follow', so 32 patterns carried 62 meanings.")
print("   Shift state is the oldest idea in this library — and the oldest bug:")
print("   a lost shift code turns the rest of the message into gibberish.")

# ---------------------------------------------------------------- 1963
head(2, "SEVEN BITS (ASCII, 1963/1967): 128 AGREED, 128 UNCLAIMED")
print(f"   patterns in 7 bits : {2**7}      patterns in 8 : {2**8}")
for ch in "Az0":
    b = ch.encode("ascii")[0]
    print(f"   {ch!r:5} -> {b:3d}  0x{b:02X}  {b:08b}   top bit {b >> 7}")
print("   Every ASCII byte has its top bit 0. The other 128 patterns belonged")
print("   to nobody, and that vacancy is the whole of the next forty years.")

# ---------------------------------------------------------------- 1964
head(3, "EBCDIC (IBM, 1964): THE OTHER NUMBERING, STILL SHIPPING")
print("   IBM's System/360 came out a year after ASCII with its own table,")
print("   inherited from punched cards. It does not even agree about 'A'.")
for ch in "A a 0 space".split():
    c = " " if ch == "space" else ch
    print(f"   {ch:6} ASCII 0x{c.encode('ascii')[0]:02X}    EBCDIC 0x{c.encode('cp037')[0]:02X}")
print()
print("   The alphabet is not contiguous — punched-card rows left two gaps:")
print("     ", " ".join(f"{c}=0x{c.encode('cp037')[0]:02X}" for c in "HIJKQRS"))
print("   so 'B' - 'A' == 1 but 'J' - 'I' == 8. Loops over letter codes break.")
print()
print("   And the sort order is inverted at every level:")
words = ["Zoe", "apple", "3rd", "Alpha"]
print("     by ASCII byte  :", sorted(words, key=lambda s: s.encode("ascii")))
print("     by EBCDIC byte :", sorted(words, key=lambda s: s.encode("cp037")))
print("   digits-then-caps-then-lower, versus lower-then-caps-then-digits.")
print("   Reading an EBCDIC file as ASCII is not mojibake, it is nonsense:")
print(f"     0x41, which is 'A' in ASCII, is {b'\x41'.decode('cp037')!r} in EBCDIC —"
      f" {unicodedata.name(b'\x41'.decode('cp037'))}, not a letter at all.")

# ---------------------------------------------------------------- 1987
head(4, "CODE PAGES (1980s): EVERYBODY CLAIMED THE TOP HALF")
print("   The same byte, 0xE9, decoded under the tables that were shipping:")
seen = []
for cp, note in [
    ("latin_1", "Western Europe, ISO 8859-1"),
    ("cp1252", "Windows Western"),
    ("iso8859_2", "Central Europe, ISO 8859-2"),
    ("cp1250", "Windows Central Europe"),
    ("cp437", "the original IBM PC"),
    ("cp850", "PC Western Europe"),
    ("koi8_r", "Russian"),
    ("mac_roman", "classic Mac OS"),
    ("cp037", "EBCDIC"),
]:
    ch = bytes([0xE9]).decode(cp)
    seen.append(ch)
    print(f"     0xE9 under {cp:10} -> {ch!r:6}  ({note})")
print(f"   {len(seen)} tables, {len(set(seen))} answers, and the file says which one it used: nowhere.")
print()
print("   They were also INCOMPLETE, which is the part people forget.")
print("   No 8-bit table holds Polish and Greek and Japanese at once:")
for cp in ["latin_1", "cp1250", "iso8859_2"]:
    try:
        "Łódź καλημέρα".encode(cp)
        print(f"     'Łódź καλημέρα' in {cp:10} -> encoded")
    except UnicodeEncodeError as e:
        print(f"     'Łódź καλημέρα' in {cp:10} -> UnicodeEncodeError on {e.object[e.start]!r}")

# ---------------------------------------------------------------- 1980s
head(5, "DOUBLE BYTES (1980s): ASIA NEVER FIT IN 256 AT ALL")
jp = "日本語"
for cp in ["shift_jis", "euc_jp", "iso2022_jp", "utf_8"]:
    enc = jp.encode(cp)
    print(f"   {pad(jp, 5)} in {cp:11} -> {enc.hex(' '):38} ({len(enc)} bytes)")
print("   Three legacy encodings, three different byte strings for the same")
print("   three characters. And look at iso2022_jp: 1b 24 42 is an ESCAPE that")
print("   switches the reader into Japanese and 1b 28 42 switches it back — the")
print("   1874 shift code again, 110 years later, with the same failure mode.")
print("   In shift_jis and euc_jp a byte in the middle of a file could be the")
print("   second half of a character, so you could not scan backwards or split.")
try:
    jp.encode("gb2312")
except UnicodeEncodeError as e:
    print(f"   Even inside one region they disagreed: gb2312 cannot hold {e.object[e.start]!r}.")

# ---------------------------------------------------------------- 1991
head(6, "UNICODE (1991): NUMBER THE CHARACTERS ONCE, FOR EVERYONE")
for ch in "Aé語😀":
    print(f"   {pad(repr(ch), 5)} U+{ord(ch):04X}  {ord(ch):>7d}   {unicodedata.name(ch)}")
print("   That number is the CODE POINT. Note what has not been said yet:")
print("   nothing at all about how many bytes it takes. That is chapter 3.")

# ---------------------------------------------------------------- 1996
head(7, "1996: THE 16-BIT ASSUMPTION BROKE")
print(f"   16 bits holds {2**16:,} characters. In 1991 that looked like plenty,")
print("   so Windows NT, Java and JavaScript all built 16-bit characters in.")
print(f"   Unicode 2.0 (1996) raised the ceiling to U+10FFFF = {0x10FFFF + 1:,} slots,")
print("   and paid for it with SURROGATES: two 16-bit units for one character.")


def utf16_units(s):
    return len(s.encode("utf_16_le")) // 2


for s in ["café", "Łódź", "日本語", "😀"]:
    print(
        f"   {pad(s, 9)} code points {len(s):2}   UTF-16 units {utf16_units(s):2}"
        f"   UTF-8 bytes {len(s.encode('utf_8')):2}"
    )
print(f"   '😀' as UTF-16 is {'😀'.encode('utf_16_be').hex(' ')}: the surrogate pair D83D DE00.")
print("   Python counts characters, so len('😀') == 1. Java and JavaScript count")
print("   UTF-16 units, so their .length is 2. Same string, two answers, forever.")

# ---------------------------------------------------------------- 1992
head(8, "UTF-8 (1992, WON BY 2008): THE ONE THAT KEPT ASCII WORKING")
for s in ["Hi", "café", "日本語", "😀"]:
    print(f"   {pad(s, 9)} -> {s.encode('utf_8').hex(' ')}")
print("   Look at 'Hi': an ASCII file is already a UTF-8 file, byte for byte.")
print("   Nothing else on this page could say that, which is why it won.")

# ---------------------------------------------------------------- today
head(9, "THE SCARS YOU STILL STEP ON")
print(f"   ASCII's layout   : chr(ord('a') ^ 0x20) == {chr(ord('a') ^ 0x20)!r}   (upper/lower is one bit)")
print(f"   the teletype     : Windows still ends a line with {b'\r\n'!r}")
print(f"   Latin-1's luck   : it is the only table where byte == code point,")
print(f"                      so bytes -> latin-1 -> bytes round-trips: "
      f"{bytes(range(256)).decode('latin-1').encode('latin-1') == bytes(range(256))}")
print(f"   the 16-bit era   : len('😀') == {len('😀')} here, .length == {utf16_units('😀')} in JS")
nfc, nfd = unicodedata.normalize("NFC", "é"), unicodedata.normalize("NFD", "é")
print(f"   two spellings    : 'é' is {nfc.encode().hex(' ')} composed or "
      f"{nfd.encode().hex(' ')} decomposed,")
print(f"                      and nfc == nfd is {nfc == nfd} until you normalize")
print(f"   bytes vs letters : len('Łódź') == {len('Łódź')}, "
      f"len('Łódź'.encode()) == {len('Łódź'.encode())} — a CHAR(4) column is not enough")
