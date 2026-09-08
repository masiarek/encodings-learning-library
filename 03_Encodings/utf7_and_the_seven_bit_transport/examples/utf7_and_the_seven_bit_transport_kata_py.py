#!/usr/bin/env python3
"""Answers to the kata on the UTF-7 page.

Five candidate byte strings, one encoder, and one question about width.
Everything here is arithmetic and a codec call; nothing is read out of the
Unicode character database and nothing is random.

Run:  python3 utf7_and_the_seven_bit_transport_kata_py.py
"""

import base64

RULE = "-" * 72
TARGET = "<script>"

CANDIDATES = [
    b"<script>",
    b"+ADw-script+AD4-",
    b"+ADw-script+AD4",
    b"+ADx-script+AD4-",
    b"+ADwAcwBjAHIAaQBwAHQAPg-",
]


def say(title: str) -> None:
    print(f"\n{title}\n{RULE}")


say("1. WHICH OF THE FIVE DECODE TO THE TAG")

for cand in CANDIDATES:
    try:
        got = cand.decode("utf-7")
        verdict = "YES" if got == TARGET else "no"
        detail = f"{got!r}"
    except UnicodeDecodeError as exc:
        # The class, not the codec's wording: a message is the interpreter's.
        verdict, detail = "no", f"{type(exc).__name__} -- non-zero padding bits"
    print(f"   {verdict:<4} {cand.decode('ascii'):<26} -> {detail}")
print()
print("   Four of the five, and the four are not near-misses of each other:")
print("     1  direct, no shift sequence at all")
print("     2  each bracket in its own run, explicitly shifted out")
print("     3  the same, with the last run ended by the end of the input")
print("     5  every character of the tag inside ONE run")
print("   The one that fails is 4, and it fails for a reason that has nothing")
print("   to do with angle brackets: 'ADx' carries the same 16 payload bits as")
print("   'ADw' plus two padding bits that are not zero, and RFC 2152 calls")
print("   that ill-formed. A rule about arithmetic, not about characters.")

say("2. WHAT THE ENCODER PRODUCES")

print(f"   {TARGET!r}.encode('utf-7')  ->  {TARGET.encode('utf-7')!r}")
print()
print("   One of the five, and it is the one with no shift sequence in it.")
print("   '<' and '>' are Set O in RFC 2152 -- OPTIONAL direct characters --")
print("   so passing them through is a legal choice this encoder makes and a")
print("   decoder is not allowed to make. That is the asymmetry: feeding your")
print("   own encoder's output back through your own filter tests one spelling")
print("   out of the family, and it is the spelling nobody attacks with.")

say("3. THE WIDTH QUESTION")

print("   code point   UTF-16BE          code units   UTF-7        width   char")
for ch in ("é", "€", "😀"):
    enc = ch.encode("utf-7")
    units = ch.encode("utf-16-be")
    n = len(units) // 2
    print(f"   {f'U+{ord(ch):04X}':<12} {units.hex(' '):<17} {n:<12}"
          f" {enc.decode():<12} {len(enc)} bytes  {ch}")
print()
print("   Five bytes for the two BMP characters and eight for the emoji, and")
print("   the arithmetic says why. A run carries UTF-16 code units: 16 bits")
print("   each, re-cut into 6-bit base64 symbols, so one unit needs ceil(16/6)")
print("   = 3 symbols and two units need ceil(32/6) = 6. Add the '+' and the")
print(f"   '-' and you get {1 + 3 + 1} and {1 + 6 + 1}.")
print()
print("   The trap in the question is the word 'character'. The emoji is one")
print("   character and one code point, and it is TWO code units -- so its run")
print("   is twice as long, exactly as it is in UTF-16 and for the same reason.")
print("   A 1997 mail-safe format inherits the surrogate pair whole.")

say("4. THE CHECK")

print("   Base64 of the UTF-16BE bytes, done by hand and compared:")
for ch in ("é", "😀"):
    by_hand = base64.b64encode(ch.encode("utf-16-be")).rstrip(b"=").decode()
    from_codec = ch.encode("utf-7").decode().strip("+-")
    print(f"   b64(UTF-16BE) = {by_hand:<8}   codec said {from_codec:<8}"
          f"   {'same' if by_hand == from_codec else 'DIFFERENT'}   {ch}")
print()
print("   Nothing in a UTF-7 run is a UTF-7 invention. It is Base64, over")
print("   UTF-16, with the padding removed -- two encodings this library has")
print("   already taught, stacked. The only thing UTF-7 adds is the shift, and")
print("   the shift is the part that turned out to be dangerous.")
