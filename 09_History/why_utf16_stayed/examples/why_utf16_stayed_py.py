#!/usr/bin/env python3
"""Why the encoding that lost is still inside Java, JavaScript, Windows and SAP.

Sixteen bits looked like enough in 1991, and four platforms built their string
types out of them. Unicode outgrew sixteen bits in 1996. This program is the
promise, the thing the promise bought, the day it broke, and the bill — and
then section 5, which is the one that explains why none of them left.

Run:  python3 why_utf16_stayed_py.py
"""

import unicodedata

BAR = "-" * 72


def cols(s):
    """Terminal columns, not characters: CJK and emoji are two columns wide."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def pad(s, width):
    return s + " " * max(0, width - cols(s))


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


# ------------------------------------------------------------------ 1
head(1, "THE 1991 PROMISE: EVERY CHARACTER IN EXACTLY TWO BYTES")
print(f"   Sixteen bits hold {0xFFFF + 1:,} code points, and Unicode 1.0 needed")
print("   far fewer. So the encoding question had an obvious answer: one")
print("   character, one 16-bit unit, fixed width, forever.")
print()
print(f"   {'char':<6} {'code point':<12} {'utf-16-be':<12} units")
for ch in "Aéż€日ಠ":
    b = ch.encode("utf_16_be")
    print(f"   {pad(ch, 6)} {'U+%04X' % ord(ch):<12} {b.hex(' '):<12} {len(b) // 2}")
print()
print("   Six characters from four scripts, one unit each. That is UCS-2 — and")
print("   it is what Windows NT (1993), Java and JavaScript (both designed in")
print("   1995) and SAP's Unicode kernel were all built on.")

# ------------------------------------------------------------------ 2
head(2, "WHAT FIXED WIDTH BUYS: AN OFFSET IS JUST ARITHMETIC")
rec = "Kraków  PLN"
u16 = rec.encode("utf_16_le")
u8 = rec.encode("utf_8")
print(f"   A fixed-width record — city in 8 characters, then a 3-character code:")
print(f"     {rec!r}   {len(rec)} characters")
print(f"     utf-16-le : {len(u16)} bytes  = 2 x {len(rec)}")
print(f"     utf-8     : {len(u8)} bytes  = it depends")
print()
print("   'The code field' is characters 8..11. Under UTF-16 you reach it by")
print("   multiplying the offset by two, and nothing else:")
print(f"     rec[8:11]                       -> {rec[8:11]!r}")
print(f"     u16[16:22].decode('utf-16-le')  -> {u16[16:22].decode('utf_16_le')!r}")
print()
print("   The same multiply-by-N trick in UTF-8 cuts a character in half:")
print(f"     u8[:5]  -> {u8[:5]!r}   the first 5 BYTES")
try:
    u8[:5].decode("utf_8")
except UnicodeDecodeError as e:
    print(f"     u8[:5].decode('utf-8') raises: {e.reason}")
print(f"     u16[:10].decode('utf-16-le') -> {u16[:10].decode('utf_16_le')!r}   the first 5 CHARACTERS")

# ------------------------------------------------------------------ 3
head(3, "THE 1996 BREAK: THE PROMISE STOPS BEING TRUE")
planes = (0x10FFFF + 1) // (0xFFFF + 1)
print(f"   Unicode 2.0 (July 1996) widened the codespace to {0x10FFFF + 1:,} code")
print(f"   points — {planes} planes, not one — and invented the surrogate pair to")
print("   let a 16-bit encoding reach them. UCS-2 became UTF-16 that day, and")
print("   'fixed width' quietly became 'variable width'.")
print()
emoji = "😀"
b = emoji.encode("utf_16_be")
print(f"     {emoji}  U+{ord(emoji):04X}  utf-16-be {b.hex(' ')}  = {len(b) // 2} units, {len(b)} bytes")
print()
print("   So the identity section 2 was built on holds for some strings and not")
print("   others, and nothing in the type says which:")
print()
print(f"     {'string':<18} {'chars':>5} {'utf-16 bytes':>13}   2 x N ?")
for s in ["café", "Kraków  PLN", "日本語", "😀", "a😀b"]:
    n, nb = len(s), len(s.encode("utf_16_le"))
    print(f"     {pad(repr(s), 18)} {n:>5} {nb:>13}   {'holds' if nb == 2 * n else 'BREAKS'}")
print()
print("   And this is the length disagreement that outlived the decision:")
print(f"     len('{emoji}')                          = {len(emoji)}   Python counts code points")
print(f"     len('{emoji}'.encode('utf-16-le')) // 2 = {len(emoji.encode('utf_16_le')) // 2}   Java, JavaScript and ABAP")
print("                                              count 16-bit units")

# ------------------------------------------------------------------ 4
head(4, "THE BILL: TWO SPELLINGS, AND A SORT THAT IS NOT CODE-POINT ORDER")
print("   A 16-bit unit is two bytes, so it has an order, so a file needs a")
print("   mark to say which one it used:")
for enc in ("utf_16_be", "utf_16_le", "utf_16"):
    print(f"     {enc:<12} {'é'.encode(enc).hex(' ')}")
print("   The third one is not a third encoding — it is UTF-16 with a BOM in")
print("   front, which is the platform's order written down.")
print()
print("   And because lead surrogates sit at D800-DBFF, below the last ordinary")
print("   code points at E000-FFFF, sorting UTF-16 bytes is NOT sorting by code")
print("   point. The same five characters, three ways:")
chars = ["A", "é", "日", "�", "😀"]
orders = [
    ("by code point", sorted(chars, key=ord)),
    ("by utf-8 bytes", sorted(chars, key=lambda c: c.encode("utf_8"))),
    ("by utf-16-be bytes", sorted(chars, key=lambda c: c.encode("utf_16_be"))),
]
for label, got in orders:
    flag = "" if got == orders[0][1] else "   <- inverted"
    print(f"     {label:<20} {' '.join(got)}{flag}")

# ------------------------------------------------------------------ 5
head(5, "AND WHY NOBODY LEFT: THE OFFSETS LIVE IN THE CALLERS")


def field_bytes(text, start, stop, enc):
    """Where characters [start:stop) begin and end once encoded."""
    a = len(text[:start].encode(enc))
    return a, a + len(text[start:stop].encode(enc))


print("   The same 8-character city field, in two records that differ only in")
print("   their data:")
print()
print(f"     {'record':<15} {'utf-16-le':>12} {'utf-8':>12}")
for text in ("Kraków  PLN", "Gdansk  PLN"):
    a16, b16 = field_bytes(text, 8, 11, "utf_16_le")
    a8, b8 = field_bytes(text, 8, 11, "utf_8")
    print(f"     {text!r:<15} {f'{a16}..{b16}':>12} {f'{a8}..{b8}':>12}")
print()
print("   The UTF-16 offsets are the same in both because they are 2 x 8. The")
print("   UTF-8 offsets move, because 'ó' is two bytes and 'a' is one — so the")
print("   number belongs to the DATA, not to the layout.")
print()
print("   A structure definition cannot hold a number that moves. That is the")
print("   whole reason a language built on fixed-length fields could adopt")
print("   UCS-2 as a widening of an existing rule (1 char = 1 byte became")
print("   1 char = 2 bytes) and could not adopt UTF-8 as anything short of")
print("   rewriting every offset in every program that ever touched the record.")

# ------------------------------------------------------------------ 6
head(6, "AND IT REACHES THE DATABASE: CESU-8")


def cesu8(s):
    """UTF-8 applied to UTF-16's surrogate pairs, which is not the same thing."""
    out = bytearray()
    for ch in s:
        if ord(ch) > 0xFFFF:
            u16 = ch.encode("utf_16_be")
            for half in (u16[:2], u16[2:]):
                out += chr(int.from_bytes(half, "big")).encode("utf_8", "surrogatepass")
        else:
            out += ch.encode("utf_8")
    return bytes(out)


print("   SAP HANA does not store UTF-8. It stores CESU-8: every BMP character")
print("   exactly as UTF-8 would, and every character above U+FFFF as a surrogate")
print("   PAIR with each half then encoded separately.")
print()
print(f"     {'string':<10} {'utf-8':<26} cesu-8")
for s in ["café", emoji]:
    print(f"     {pad(repr(s), 10)} {s.encode('utf_8').hex(' '):<26} {cesu8(s).hex(' ')}")
print()
print(f"   Identical for 'café'. For {emoji} it is {len(emoji.encode('utf_8'))} bytes against {len(cesu8(emoji))} —")
print("   and the six are not valid UTF-8 at all:")
try:
    cesu8(emoji).decode("utf_8")
except UnicodeDecodeError as e:
    print(f"     cesu8('{emoji}').decode('utf-8') raises: {e.reason}")
print()
print("   So the length answer travels the whole stack unchanged. HANA's LENGTH()")
print("   counts that one character as 2, exactly as ABAP's strlen( ) and Java's")
print("   .length() do — because CESU-8 exists to keep UTF-16's unit semantics")
print("   inside something UTF-8-shaped. A 1991 decision, still being honoured by")
print("   an in-memory column store designed twenty years later.")
