#!/usr/bin/env python3
"""What one str costs, and why the widest character in it sets the price.

Nothing here prints a byte total, and that is deliberate. sys.getsizeof is a
CPython number: not in the language, different between versions, different
between builds. What IS stable is the SHAPE -- that the cost per character is
a step function of the widest code point in the string, that the steps sit at
U+0100 and U+10000, and that the step does not move when the string gets
longer. Every line below prints a shape: a slope, a ratio, a threshold, or a
True. The actual byte counts are on the page, in a fence naming the
interpreter that produced them.

Run:  python3 str_in_memory_py.py
"""

import codecs
import sys

RULE = "-" * 72
W = 34


def width(ch):
    """Bytes per character for a string made of `ch`, measured as a slope.

    Two strings one character apart, same kind: the difference is the buffer's
    stride and nothing else. A str is immutable and exactly sized, so there is
    no over-allocation to confuse the subtraction -- which is why this is a
    measurement rather than an estimate."""
    return sys.getsizeof(ch * 101) - sys.getsizeof(ch * 100)


def ask_for_a_c_string(s):
    """Make a C function ask for `s` as a const char *, and discard the answer.

    codecs.lookup() takes its argument through PyArg_ParseTuple's 's'
    converter, which is documented to cache the UTF-8 form on the str itself.
    There is no codec named after a row of e-acutes, so this always raises --
    and that is fine: the conversion happens before the lookup fails."""
    try:
        codecs.lookup(s)
    except LookupError:
        pass


def kind(s):
    """The buffer PEP 393 gave this string -- decided by its WIDEST character.

    max() over a str returns the character with the highest code point, which
    is the one that chose the buffer. Asking s[0] instead is the bug this
    whole page is about, in the helper that describes it."""
    stride = width(max(s))
    if stride == 1:
        return "ASCII" if max(s) < "\x80" else "latin-1"
    return {2: "UCS-2", 4: "UCS-4"}[stride]


CAST = [
    ("A", "U+0041"),
    ("é", "U+00E9"),
    ("ż", "U+017C"),
    ("\U0001f600", "U+1F600"),
]

print("1. ONE TYPE, THREE BUFFERS")
print(RULE)
print("   PEP 393 gives every str one of three storage widths, chosen when the")
print("   string is built and never mixed inside one string. The width is")
print("   measurable without knowing any byte total: build the same string one")
print("   character longer, and subtract.")
print()
print("     %-9s %-7s %-9s %s" % ("code pt", "bytes", "buffer", "escape"))
for ch, cp in CAST:
    print("     %-9s %-7d %-9s %s" % (cp, width(ch), kind(ch), ascii(ch).strip("'")))
print()
print("   Read the first two rows twice: both cost one byte per character. An")
print("   all-ASCII str is a smaller OBJECT than a Latin-1 one -- it needs no")
print("   separate UTF-8 pointer -- but that is a fixed header, paid once,")
print("   not a price per character.")
print()
print("     %-46s %s" % ("one U+0080 makes an ASCII string bigger:",
                         sys.getsizeof("A" * 99 + "\x80") > sys.getsizeof("A" * 100)))
print("     %-46s %s" % ("...but the stride is the same either way:",
                         width("A") == width("é")))
print()

print("2. WHERE THE STEPS ARE")
print(RULE)
print("   Check the stride either side of the two code points PEP 393 names,")
print("   and print only the boundaries where it actually changes.")
print()
for cp in (0x100, 0x10000):
    before, after = width(chr(cp - 1)), width(chr(cp))
    if before != after:
        print("     U+%04X -> U+%-6X %d byte%s -> %d bytes per character"
              % (cp - 1, cp, before, " " if before == 1 else "s", after))
print()
print("   Neither number is arbitrary. U+00FF is the last code point a single")
print("   byte can index, and U+FFFF the last one a 16-bit unit can hold -- so")
print("   these are the same two walls UTF-16 was built around, met from")
print("   inside a language that does not use UTF-16 at all.")
print()

print("3. THE WIDEST CHARACTER SETS THE PRICE, NOT THE AVERAGE")
print(RULE)
print("   A thousand ASCII characters, then that same thousand with ONE more")
print("   character on the end. The ratio is what the added character did to")
print("   the whole buffer:")
print()
base = "A" * 1000
b0 = sys.getsizeof(base)
print("     %-24s %-9s %s" % ("appended", "stride", "size against the ASCII string"))
for ch, cp in CAST[1:]:
    print("     %-24s %-9d x%.2f"
          % ("one " + cp, width(ch), sys.getsizeof(base + ch) / b0))
print()
print("   999 of those 1001 characters are still 'A'. In the last row they")
print("   are paying four bytes each because one character in the string is")
print("   not -- and no amount of ASCII around it brings the average back")
print("   down, because there is no average. There is one buffer.")
print()

print("4. THE STEP DOES NOT MOVE WHEN THE STRING GETS LONGER")
print(RULE)
print("   The same stride measured at three lengths. If the buffer were")
print("   amortised, rounded up, or allocated in blocks, these rows would")
print("   disagree with each other.")
print()
print("     %-12s %-10s %-10s %s" % ("length", "ASCII", "UCS-2", "UCS-4"))
for n in (10, 1000, 100000):
    row = [sys.getsizeof(c * (n + 1)) - sys.getsizeof(c * n)
           for c in ("A", "ż", "\U0001f600")]
    print("     %-12d %-10d %-10d %d" % (n, row[0], row[1], row[2]))
print()

print("5. THE SAME STRING, MEASURED TWICE")
print(RULE)
print("   A str can carry a cached UTF-8 copy of itself, filled the first time")
print("   a C function asks for the string as a const char *. codecs.lookup()")
print("   is one such function: to answer 'is there a codec with this name?'")
print("   it must first turn the name into a C string, and it is that")
print("   conversion -- not the answer, which here is always LookupError --")
print("   that leaves the cache behind.")
print()
print("   str.encode('utf-8') does NOT fill it. encode() builds a new bytes")
print("   object and hands it to you; the str is never asked to keep one.")
print()
print("     %-9s %-12s %-16s %s"
      % ("buffer", "grew after", "grew after", "utf-8 form"))
print("     %-9s %-12s %-16s %s"
      % ("", ".encode()", "codecs.lookup()", "IS the buffer"))
for ch, cp in CAST:
    a_str = "".join([ch] * 100)
    a0 = sys.getsizeof(a_str)
    a_str.encode("utf-8")
    grew_encode = sys.getsizeof(a_str) > a0

    b_str = "".join([ch] * 100)
    b1 = sys.getsizeof(b_str)
    ask_for_a_c_string(b_str)
    grew_lookup = sys.getsizeof(b_str) > b1

    print("     %-9s %-12s %-16s %s"
          % (kind(ch), grew_encode, grew_lookup,
             len(ch.encode("utf-8")) == width(ch) == 1))
print()
print("   The ASCII row is the one that explains the other three. For an")
print("   all-ASCII str the UTF-8 form IS the buffer, byte for byte, so there")
print("   is nothing to cache and the number can never move. Every other kind")
print("   can grow later, without the string having changed at all.")
print()

print("6. SO A NARROWER STRING CAN COST MORE THAN A WIDER ONE")
print(RULE)
print("   100 of U+00E9 (one byte each) against 100 of U+017C (two bytes")
print("   each). Fresh, the wider one is bigger, as you would expect. Ask a C")
print("   function for the narrow one as a C string, and the order reverses:")
print()
narrow = "".join(["é"] * 100)
wide = "".join(["ż"] * 100)
print("     %-46s %s" % ("fresh: U+00E9 x100 smaller than U+017C x100:",
                         sys.getsizeof(narrow) < sys.getsizeof(wide)))
ask_for_a_c_string(narrow)
print("     %-46s %s" % ("after codecs.lookup() on the narrow one:",
                         sys.getsizeof(narrow) < sys.getsizeof(wide)))
print()
print("   Neither string changed. Neither is wrong. This is the whole reason")
print("   a number out of sys.getsizeof belongs in a diagnostic and never in")
print("   an assertion.")
print()

print("7. NONE OF THIS IS A CORRECTNESS QUESTION")
print(RULE)
print("   The three buffers are invisible from Python. Same operations, same")
print("   answers, whichever one you happened to get:")
print()
mixed = "Aéż\U0001f600"
print("     s = 'A' + U+00E9 + U+017C + U+1F600")
print("     %-*s %d   (characters, not bytes)" % (W, "len(s)", len(mixed)))
print("     %-*s %s" % (W, "s[3]", ascii(mixed[3])))
print("     %-*s %s" % (W, "s[1:3]", ascii(mixed[1:3])))
print("     %-*s %s" % (W, "s[::-1] == ''.join(reversed(s))",
                        mixed[::-1] == "".join(reversed(mixed))))
print("     %-*s %s" % (W, "buffer of s", kind(mixed)))
print("     %-*s %d" % (W, "len(s.encode('utf-8'))", len(mixed.encode("utf-8"))))
print()
print("   len() and s[i] are O(1) here precisely BECAUSE the buffer has one")
print("   fixed stride: character i lives at offset i * stride, so there is")
print("   nothing to scan. That is the trade being made. Rust's String is")
print("   UTF-8 -- one representation, no upgrade, no quadrupling -- and pays")
print("   for it with byte indices and no O(1) nth character.")
