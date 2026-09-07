#!/usr/bin/env python3
"""Four things called Base32, and the one difference that is not cosmetic.

A binary-to-text scheme has two independent parts: how the bits are cut, and
which symbols stand for the pieces. Sibling page `binary_to_text` is about the
first. This one is about the second, at the one width where the family has four
competing answers -- and about the entry in that list that is not a base32
encoding of bytes at all.

Everything here is a table lookup or arithmetic. Nothing is read out of a
Unicode table, nothing is random, and nothing asks the machine a question.

Run:  python3 base32_alphabets_py.py
"""

import base64
import itertools

# The four symbol sets, verbatim from their specifications.
RFC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"  # RFC 4648 section 6
HEX = "0123456789ABCDEFGHIJKLMNOPQRSTUV"  # RFC 4648 section 7, "base32hex"
CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # crockford.com/base32.html
ZBASE32 = "ybndrfg8ejkmcpqxot1uwisza345h769"  # Zimmermann/Wilcox-O'Hearn

RULE = "-" * 72


def say(title: str) -> None:
    print(f"\n{title}\n{RULE}")


def rename(encoded: str, alphabet: str) -> str:
    """RFC 4648 base32 text, with every symbol swapped for another set's."""
    return encoded.translate(str.maketrans(RFC, alphabet))


def crockford_chunks(raw: bytes) -> str:
    """Crockford's symbols over RFC 4648's packing -- what tools print."""
    return rename(base64.b32encode(raw).decode().rstrip("="), CROCKFORD)


def crockford_number(raw: bytes, width: int | None = None) -> str:
    """Crockford's own reading: the bytes as ONE number, in base 32."""
    n = int.from_bytes(raw, "big")
    out = ""
    while n:
        n, digit = divmod(n, 32)
        out = CROCKFORD[digit] + out
    return out.rjust(width, "0") if width else (out or "0")


say("1. THE SAME FORTY-FOUR BYTES, FOUR TIMES")

pangram = "The quick brown fox jumps over the lazy dog."
raw = pangram.encode("ascii")
padded = base64.b32encode(raw).decode()
bare = padded.rstrip("=")

print(f"   {'the text':<18} {pangram!r}")
print(f"   {'its bytes':<18} {len(raw)} = {len(raw) * 8} bits, which is {len(raw) * 8 / 5:.1f} five-bit pieces")
print()
print(f"   {'RFC 4648':<18} {bare}")
print(f"   {'base32hex':<18} {rename(bare, HEX)}")
print(f"   {'Crockford':<18} {rename(bare, CROCKFORD)}")
print(f"   {'z-base-32':<18} {rename(bare, ZBASE32)}")
print()
print(f"   Four strings of {len(bare)} characters, no two alike, one input. A dropdown")
print("   that offers all four calls them all Base32, and a reader is left to")
print("   assume they are four encodings. They are one encoding written in")
print("   four alphabets, and the four differ in nothing else -- with one")
print("   caveat and one outright exception, in sections 6 and 4.")
print()
print("   The caveat is z-base-32. Its specification is written over BITS,")
print("   not bytes: an encoder that knows the exact bit length may stop")
print("   short. The line above is its octet-mode reading, which is the one")
print("   a tool handed a byte string can give -- and in octet mode it is")
print("   exactly the rename it looks like.")
print()
print(f"   {'padded  ':<18} {padded}   {len(padded)} characters")
print(f"   {'unpadded':<18} {bare}   {len(bare)} characters")
print()
print("   RFC 4648 pads to a multiple of 8 characters; Crockford and z-base-32")
print("   define no padding at all. So the '=' is a fifth difference, and the")
print(f"   character count alone -- {len(bare)}, not {len(padded)} -- tells you the padding is off.")


say("2. THREE OF THE FOUR ARE ONE str.translate AWAY")

sample = base64.b32encode(b"cat").decode().rstrip("=")
print(f"   {'RFC 4648 of ' + repr(b'cat'):<34} {sample}")
for name, alphabet in (("base32hex", HEX), ("Crockford", CROCKFORD), ("z-base-32", ZBASE32)):
    print(f"   {'.translate(RFC -> ' + name + ')':<34} {rename(sample, alphabet)}")
print()
back = rename(sample, CROCKFORD).translate(str.maketrans(CROCKFORD, RFC))
print(f"   {'and straight back again':<34} {back}   recovered: {back == sample}")
print()
print("   A rename is invertible and loses nothing, because no bit moved. The")
print("   bytes were cut into five-bit pieces once; each scheme then writes")
print("   the SAME pieces with a different set of thirty-two symbols. That is")
print("   why one `tr` in a shell pipe converts between them -- see the")
print("   terminal section on the page.")


say("3. THE ORDER OF THE THIRTY-TWO SYMBOLS IS A FEATURE, NOT A STYLE")

print("   RFC 4648 gives a reason for base32hex, and it is a property of the")
print("   ordering alone: 'encoded data maintains its sort order when the")
print("   encoded data is compared bit-wise' (section 7).")
print()
print("   Tested over every two-byte string -- all 65,536 of them:")

pairs = [bytes([a, b]) for a in range(256) for b in range(256)]
by_raw = list(range(len(pairs)))
std = [base64.b32encode(p).decode() for p in pairs]
hexed = [base64.b32hexencode(p).decode() for p in pairs]
std_ok = sorted(by_raw, key=lambda i: std[i]) == by_raw
hex_ok = sorted(by_raw, key=lambda i: hexed[i]) == by_raw
print()
print(f"   {'sorting the base32 text == sorting the bytes':<48} {std_ok}")
print(f"   {'sorting the base32hex text == sorting the bytes':<48} {hex_ok}")

for i in range(len(pairs) - 1):
    if (std[i] < std[i + 1]) is not (pairs[i] < pairs[i + 1]):
        print()
        print("   the first place standard base32 gets it wrong:")
        print(f"     {pairs[i].hex():<8} -> {std[i]}")
        print(f"     {pairs[i + 1].hex():<8} -> {std[i + 1]}      but {pairs[i].hex()} < {pairs[i + 1].hex()}")
        break

print()
print("   The cause is ASCII, not base32. Standard base32 spells value 0 as")
print("   'A' and value 26 as '2', and '2' sorts BEFORE 'A', so the text order")
print("   and the byte order disagree the moment a value crosses 26.")
print("   base32hex spells 0..31 as 0-9 then A-V, which is already ascending")
print("   in ASCII, so the two orders can never disagree.")
print()
print("   That is worth a database index, and it is invisible on any table")
print("   that lists these schemes by bits-per-character.")


say("4. CROCKFORD'S BASE32 IS A NOTATION FOR NUMBERS")

print("   Its specification opens: 'Base 32 is a textual 32-symbol notation")
print("   for expressing NUMBERS' -- not byte strings. And on a short value it")
print("   says: 'zero-extend the number to make its bit-length a multiple of")
print("   5'. A number is zero-extended at the HIGH end. RFC 4648 pads the")
print("   LOW end of the last group. Same bits, opposite ends.")
print()

demo = b"Hi"
bits = f"{int.from_bytes(demo, 'big'):0{len(demo) * 8}b}"
gap = (-len(bits)) % 5
right = bits + "0" * gap
left = "0" * gap + bits
grp = lambda s: " ".join(s[i:i + 5] for i in range(0, len(s), 5))
print(f"   {'the bytes':<24} {demo!r}  =  {demo.hex()}  =  {bits}")
print(f"   {'RFC 4648: pad the right':<24} {grp(right)}   -> {crockford_chunks(demo)}")
print(f"   {'Crockford: extend left':<24} {grp(left)}    -> {crockford_number(demo, len(right) // 5)}")
print()
print("   Two strings. Both are 'Crockford's Base32 of these two bytes'. A")
print("   converter that shows you an alphabet dropdown gives you the first;")
print("   ULID, which specifies Crockford's Base32 for a 128-bit number,")
print("   is built on the second.")
print()
print("   The two readings agree exactly when there is nothing to extend --")
print("   when the bit count is already a multiple of 5, i.e. when the byte")
print("   count is a multiple of 5. Checked, by length:")
print()

SYMS = (0x00, 0x01, 0x5A, 0x80, 0xFF)


def nth_case(index: int, length: int) -> bytes:
    """The index-th string over SYMS, addressed directly rather than counted to."""
    out = bytearray(length)
    for position in range(length - 1, -1, -1):
        index, digit = divmod(index, len(SYMS))
        out[position] = SYMS[digit]
    return bytes(out)


print(f"   {'bytes':>6} {'% 5':>4} {'tested':>8} {'agreed':>8}   verdict")
for length in range(1, 16):
    if length <= 2:
        cases = [bytes(t) for t in itertools.product(range(256), repeat=length)]
    else:
        total = len(SYMS) ** length
        stride = max(1, total // 4096)
        cases = [nth_case(i, length) for i in range(0, total, stride)]
    width = (length * 8 + 4) // 5
    agree = sum(1 for c in cases if crockford_chunks(c) == crockford_number(c, width))
    verdict = "all of them" if agree == len(cases) else "only the all-zero string"
    print(f"   {length:>6} {length % 5:>4} {len(cases):>8} {agree:>8}   {verdict}")
print()
print("   Lengths 1 and 2 are exhaustive -- every one of the 256 and the")
print("   65,536; the rest sweep a fixed five-byte symbol set. The pattern is")
print("   not a sample artefact, it is the arithmetic above: a value that is")
print("   not a whole number of five-bit pieces has no agreed spelling, and")
print("   the one string that survives every length is the one made of")
print("   zeros, where it makes no difference which end you extend.")


say("5. AND A NUMBER HAS NO LEADING ZEROS")

for value in (b"\x00\x00\x41", b"\x00\x41", b"\x41"):
    print(f"   {value.hex():<10} chunks {crockford_chunks(value):<6}   as a number {crockford_number(value)}")
print()
print("   Three different byte strings; one number, 65. The chunked reading")
print("   keeps the length because it is encoding BYTES; the number reading")
print("   cannot, because 065 and 65 are the same number. Any format that")
print("   uses the number reading has to declare a width, and ULID does:")
print()
print(f"   {'ULID':<22} 128 bits, canonically 26 characters")
print(f"   {'26 x 5':<22} {26 * 5} bits -- {26 * 5 - 128} more than the value has")
print(f"   {'its two fields':<22} 48-bit time in 10 chars ({10 * 5} bits), 80-bit random in 16 ({16 * 5} bits)")
print()
print("   80 is a multiple of 5 and 48 is not, which is why only the")
print("   timestamp half needs the zero-extension at all.")


say("6. WHICH LETTERS ARE MISSING, AND WHAT A DECODER DOES ABOUT IT")

alnum = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
print(f"   {'Crockford':<12} drops {' '.join(sorted(alnum - set(CROCKFORD)))}")
print(f"   {'z-base-32':<12} drops {' '.join(sorted(set('0123456789abcdefghijklmnopqrstuvwxyz') - set(ZBASE32)))}")
print()
print("   Crockford's reasons are I and L looking like 1, O looking like 0,")
print("   and U 'to reduce the chance of accidental obscenity'. z-base-32")
print("   drops a different four (0, l, v, 2) and then PERMUTES the rest, so")
print("   that the symbols a person meets most often are the ones easiest to")
print("   read and say. Neither list is about bits. Both are about a human")
print("   reading a code off a screen and typing it somewhere else.")
print()
print("   The standard alphabet made no such allowance, so its decoders have")
print("   to. Python's has carried the repair since the module was written:")
print()

encoded = base64.b32encode(b"cat").decode()
typo = encoded.replace("I", "1").replace("O", "0")
print(f"   {'b32encode(' + repr(b'cat') + ')':<44} {encoded}")
print(f"   {'lower case, casefold=True':<44} {base64.b32decode(encoded.lower(), casefold=True)!r}")
print(f"   {'someone typed 1 for I and 0 for O':<44} {typo}")
print(f"   {'b32decode(..., casefold=True, map01=' + repr(b'I') + ')':<44} {base64.b32decode(typo, casefold=True, map01=b'I')!r}")
print()
print("   map01 has to be told which letter the digit 1 meant, because in the")
print("   standard alphabet both I and L are live symbols with different")
print("   values -- the ambiguity Crockford's alphabet removes by not having")
print("   them. A repair at the decoder is a strictly weaker fix than an")
print("   alphabet that cannot be mistyped.")
