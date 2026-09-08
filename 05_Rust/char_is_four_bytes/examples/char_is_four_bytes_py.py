"""Python has no character type — and pays for the width Rust charges per char.

Run:  python3 char_is_four_bytes_py.py
"""

import sys

CAST = [("U+0041", "A"), ("U+00E9", "é"), ("U+20AC", "€"), ("U+1F600", "\U0001F600")]


def width_of(s: str) -> int:
    """Bytes this string spends per character, measured as a DIFFERENCE.

    getsizeof(s + 'a'*101) - getsizeof(s + 'a'*100) grows by exactly one
    character's worth, so the object header, the interning and every other
    version-specific overhead cancel out and only PEP 393's width is left.
    Appending ASCII never widens a string, so the answer belongs to `s`.
    A bare getsizeof() would be a number about this CPython build.
    """
    return sys.getsizeof(s + "a" * 101) - sys.getsizeof(s + "a" * 100)


print("1. THERE IS NO CHARACTER TYPE TO ASK ABOUT")
s = "café"
print(f"   s = {s!r}")
print(f"   s[3]        {s[3]!r}   type = {type(s[3]).__name__}   len = {len(s[3])}")
print(f"   s[3][0]     {s[3][0]!r}   type = {type(s[3][0]).__name__}   len = {len(s[3][0])}")
print("   Indexing a str gives a str of length 1, which indexes to itself, forever.")
print("   Rust's char is a separate type with a separate size. Python's is a one-character")
print("   string, so `size_of::<char>()` has no Python question to be the answer to.")
print()

print("2. WHAT PYTHON HAS INSTEAD, AND IT IS THE SAME NUMBER FROM THE OTHER END")
print(f"   {'code pt':<9} {'ord()':>8} {'utf-8':>7} {'bytes/char':>11}   glyph")
for label, ch in CAST:
    print(f"   {label:<9} {ord(ch):>8} {len(ch.encode()):>7} {width_of(ch):>11}   {ch}")
print("   The last column is PEP 393: a str picks ONE width for all of its characters —")
print("   1, 2 or 4 bytes — from its widest member. Rust spends 4 bytes on every char and")
print("   1 to 4 inside a String; Python spends 1 to 4 per string and the same for every")
print("   character in it. Same three widths, opposite thing held fixed.")
print()

print("3. SO ONE CHARACTER CAN QUADRUPLE A STRING")
plain = "a" * 1000
mixed = "a" * 999 + "\U0001F600"
for label, text in [("'a' * 1000", plain), ("'a' * 999 + '\\U0001F600'", mixed)]:
    w = width_of(text)
    print(f"   {label:<24} len = {len(text)}   {w} byte/char   {len(text) * w:>5} bytes of text")
print(f"   Same length, {width_of(mixed) // width_of(plain)}x the text. ONE character forced the whole string up to")
print("   4 bytes each — there is no mixed-width str. UTF-8 would have spent 1003 bytes")
print("   on it; the in-memory form is not UTF-8 and was never trying to be.")
print("   (Measured as a per-character difference. A bare sys.getsizeof would add a")
print("   header whose size is a fact about this CPython build, not about the text.)")
print()

print("4. THE HOLE RUST LEAVES IN char, PYTHON DOES NOT LEAVE IN str")
for n in (0xD7FF, 0xD800, 0xDFFF, 0xE000, 0x10FFFF):
    ch = chr(n)
    try:
        enc = ch.encode("utf-8").hex(" ")
    except UnicodeEncodeError as exc:
        enc = f"{type(exc).__name__}"
    print(f"   chr(0x{n:06X})   len = {len(ch)}   .encode('utf-8') -> {enc}")
print("   Every one of those is a str Python will build, index, slice, sort and use as a")
print("   dict key. Two of them cannot be encoded to UTF-8 at all — so the check Rust")
print("   makes at char::from_u32 is one Python makes at .encode(), and only there.")
print("   That gap is the room PEP 383's surrogateescape lives in.")
print()

print("5. AND NO INDEX INTO A PYTHON STRING IS EVER A BYTE INDEX")
print(f"   s = {s!r}")
print(f"   len(s)              {len(s)}   <- characters")
print(f"   len(s.encode())     {len(s.encode())}   <- bytes; Rust's len() is THIS number")
print(f"   s[3]                {s[3]!r}")
print(f"   s.encode()[3]       {s.encode()[3]}   <- an int, and only half of the character")
print("   Rust has char_indices() because its two counts are both needed. Python does not,")
print("   because you can only ever have the first one — which is friendlier right up to")
print("   the moment you have to write the byte offset into a fixed-width record.")
