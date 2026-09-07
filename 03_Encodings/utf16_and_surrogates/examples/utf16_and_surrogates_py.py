#!/usr/bin/env python3
"""The surrogate pair: the arithmetic, the reserved block, and the ceiling it set.

UTF-8 lets you ignore the difference between a code point and a code unit,
because it never asks you to think in units at all. UTF-16 cannot: above
U+FFFF one character is written as *two* units, and every "length" argument
in this library comes back to that. This program does the pair arithmetic by
hand, checks it against Python's own encoder, and then shows the two things
that follow from it — 2,048 code points that can never be characters, and the
reason Unicode stops where it does.

Run:  python3 utf16_and_surrogates_py.py
"""

import unicodedata

BAR = "-" * 72
CAST = "Aéż€日ಠ😀"


def cols(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def pad(s, width):
    return s + " " * max(0, width - cols(s))


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


# ------------------------------------------------------------------ 1
head(1, "CODE POINT VS CODE UNIT: THE DISTINCTION UTF-8 LETS YOU IGNORE")
print(f"   {'char':<6} {'code point':<12} {'utf-8':>7} {'utf-16':>8} {'utf-32':>8}")
print(f"   {'':<6} {'':<12} {'bytes':>7} {'units':>8} {'units':>8}")
for ch in CAST:
    u8 = len(ch.encode("utf_8"))
    u16 = len(ch.encode("utf_16_be")) // 2
    u32 = len(ch.encode("utf_32_be")) // 4
    print(f"   {pad(ch, 6)} {'U+%04X' % ord(ch):<12} {u8:>7} {u16:>8} {u32:>8}")
print()
print("   Every row is ONE code point. UTF-32 always agrees; UTF-8 varies but")
print("   never asks you to count units; UTF-16 is the only one where a single")
print("   character can be two of the things the language calls a character.")

# ------------------------------------------------------------------ 2
head(2, "THE ARITHMETIC: ONE CODE POINT INTO TWO UNITS")
cp = 0x1F600
print(f"   Encoding U+{cp:04X} ({chr(cp)}) as a surrogate pair, step by step:")
print()
shifted = cp - 0x10000
hi = 0xD800 + (shifted >> 10)
lo = 0xDC00 + (shifted & 0x3FF)
print(f"     subtract the BMP   {cp:#07x} - 0x10000 = {shifted:#07x}   ({shifted.bit_length()} bits, max 20)")
print(f"     top 10 bits        {shifted:#07x} >> 10    = {shifted >> 10:#05x}")
print(f"     bottom 10 bits     {shifted:#07x} &  0x3FF = {shifted & 0x3FF:#05x}")
print(f"     high surrogate     0xD800 + {shifted >> 10:#05x}  = 0x{hi:04X}")
print(f"     low  surrogate     0xDC00 + {shifted & 0x3FF:#05x}  = 0x{lo:04X}")
print()
mine = f"{hi:04X}{lo:04X}"
theirs = chr(cp).encode("utf_16_be").hex().upper()
print(f"     by hand            {mine}")
print(f"     Python's encoder   {theirs}")
print(f"     agree              {mine == theirs}")
print()
back = 0x10000 + ((hi - 0xD800) << 10) + (lo - 0xDC00)
print(f"   And back again: 0x10000 + ((0x{hi:04X}-0xD800) << 10) + (0x{lo:04X}-0xDC00) = U+{back:04X}")

# ------------------------------------------------------------------ 3
head(3, "THE 2,048 CODE POINTS THAT CAN NEVER BE CHARACTERS")
n_hi = 0xDBFF - 0xD800 + 1
n_lo = 0xDFFF - 0xDC00 + 1
print(f"     high surrogates  U+D800..U+DBFF   {n_hi:>5}")
print(f"     low  surrogates  U+DC00..U+DFFF   {n_lo:>5}")
print(f"     reserved total                    {n_hi + n_lo:>5}")
print()
print("   They are permanently unassigned so that UTF-16 is unambiguous: a unit")
print("   in D800-DBFF always means 'a pair starts here', and nothing else can.")
print("   The cost is that they leak into every format that grew up around")
print("   UTF-16 and must then be refused elsewhere:")
lone = "\ud83d"
for label, fn in [
    ("lone.encode('utf-8')", lambda: lone.encode("utf_8")),
    ("lone.encode('utf-8', 'surrogatepass')", lambda: lone.encode("utf_8", "surrogatepass").hex(" ")),
    ("lone.encode('utf-16-be')", lambda: lone.encode("utf_16_be").hex(" ")),
]:
    try:
        print(f"     {label:<40} -> {fn()}")
    except UnicodeEncodeError as e:
        print(f"     {label:<40} -> UnicodeEncodeError: {e.reason}")
print()
print("   UTF-8 refuses, correctly — a surrogate is not a character, so there is")
print("   nothing to encode. UTF-16 hands it back happily, because in UTF-16 it")
print("   is just a unit. That asymmetry is the whole bug class.")

# ------------------------------------------------------------------ 4
head(4, "AND WHY UNICODE STOPS AT U+10FFFF")
supp = (0x3FF + 1) * (0x3FF + 1)
print(f"     a high surrogate carries 10 bits  -> {0x3FF + 1:>7} values")
print(f"     a low  surrogate carries 10 bits  -> {0x3FF + 1:>7} values")
print(f"     so the pair addresses                {supp:>7} code points")
print(f"     which is exactly                     {supp // 0x10000:>7} planes of 65,536")
print(f"     plus the BMP itself                  {1:>7} plane")
print(f"     total                                {(supp + 0x10000):>7} = {hex(supp + 0x10000)}")
print()
import sys
print(f"   The last code point is therefore U+{supp + 0x10000 - 1:04X}, and sys.maxunicode agrees:")
print(f"   {hex(sys.maxunicode)}. That ceiling is not a decision about how many characters")
print("   the world needs — it is the largest number two 16-bit surrogates can")
print("   address. UTF-8 as originally designed ran to six bytes and U+7FFFFFFF;")
print("   it was cut back to match what UTF-16 could reach.")

# ------------------------------------------------------------------ 5
head(5, "UTF-32: THE ONE WITH NO SURROGATES, AND ALMOST NO USERS")
s = "A😀"
for enc in ("utf_8", "utf_16_be", "utf_32_be"):
    b = s.encode(enc)
    print(f"     {enc:<10} {len(b):>2} bytes   {b.hex(' ')}")
print()
print(f"   In UTF-32 every character is one unit — len(s) == {len(s)} matches the unit")
print("   count exactly, and there is no pair to split. It costs four bytes for")
print("   an 'A' and carries a byte order, which is why it is a fine in-memory")
print("   representation and almost never a file.")
