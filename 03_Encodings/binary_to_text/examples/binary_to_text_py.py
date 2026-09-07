#!/usr/bin/env python3
"""Base64 by hand, then the four questions the reference tables never ask.

A binary-to-text encoding re-cuts a run of bits into pieces small enough that
every piece has a printable character to stand for it. That is the whole idea,
and base64 is the one everybody meets: 24 bits in, four 6-bit slices out.

Run:  python3 binary_to_text_py.py
"""

import base64
import binascii
import gzip
import zlib

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

RULE = "-" * 72


def say(title: str) -> None:
    print(f"\n{title}\n{RULE}")


say("1. TWENTY-FOUR BITS IN, FOUR CHARACTERS OUT")

word = "café"
raw = word.encode("utf-8")
print(f"   {'the text':<22} {word!r}   {len(word)} characters")
print(f"   {'its UTF-8 bytes':<22} {raw.hex(' ')}   {len(raw)} bytes")
print()

for start in range(0, len(raw), 3):
    chunk = raw[start : start + 3]
    padded = chunk + b"\x00" * (3 - len(chunk))
    bits = "".join(f"{b:08b}" for b in padded)
    slices = [bits[i : i + 6] for i in range(0, 24, 6)]
    kept = len(chunk) + 1  # 3 bytes -> 4 chars, 2 -> 3, 1 -> 2
    print(f"   quantum {start // 3 + 1}: {chunk.hex(' ')}" + ("" if len(chunk) == 3 else "   (short)"))
    print(f"     {' '.join(f'{b:08b}' for b in padded):<29} the bytes in binary")
    print(f"     {' '.join(slices):<29} the same 24 bits, re-cut into sixes")
    print(f"     {' '.join(f'{int(s, 2):>6}' for s in slices):<29} each six bits as a number, 0-63")
    out = [ALPHABET[int(s, 2)] for s in slices[:kept]] + ["="] * (4 - kept)
    print(f"     {' '.join(f'{c:>6}' for c in out):<29} ALPHABET[n], then padding")
    print()

by_hand = ""
for start in range(0, len(raw), 3):
    chunk = raw[start : start + 3]
    padded = chunk + b"\x00" * (3 - len(chunk))
    bits = "".join(f"{b:08b}" for b in padded)
    kept = len(chunk) + 1
    by_hand += "".join(ALPHABET[int(bits[i : i + 6], 2)] for i in range(0, kept * 6, 6))
    by_hand += "=" * (4 - kept)

print(f"   {'by hand':<22} {by_hand}")
print(f"   {'base64.b64encode':<22} {base64.b64encode(raw).decode()}")
print(f"   {'the same string?':<22} {by_hand == base64.b64encode(raw).decode()}")
print()
print("   Nothing above looked at a character. It looked at bits, in groups")
print("   of six, because 2**6 == 64 and there are more than 64 printable")
print("   ASCII characters to spend. That is the entire mechanism, and every")
print("   other scheme in the family is the same trick at a different width.")

say("2. SO BASE64 HAS NO CHARSET -- IT ENCODES BYTES")

for name in ("utf-8", "iso-8859-1"):
    b = word.encode(name)
    print(f"   'café' as {name:<11} {b.hex(' '):<16} -> {base64.b64encode(b).decode()}")
print()
print("   One word, two byte strings, two base64 strings, both perfectly")
print("   valid and neither carrying the faintest hint of which is which.")
print('   "base64 of this text" is not defined until somebody says which')
print("   encoding made the bytes -- the same missing statement that makes")
print("   percent-encoding guessable, one layer down.")
print()
print("   And it never fails. Encode anything, including bytes that are not")
print("   text at all:")
broken = b"\xc3\x28\xff"
print(f"     {broken.hex(' '):<16} -> {base64.b64encode(broken).decode():<9} (not valid UTF-8, encodes fine)")
try:
    broken.decode("utf-8")
except UnicodeDecodeError as exc:
    print(f"     the same bytes .decode('utf-8') -> UnicodeDecodeError: {exc.reason}")

say("3. PADDING IS THE LENGTH, WRITTEN DOWN")

print(f"   {'bytes in':>8}  {'base64 out':<12} {'chars':>5} {'pads':>5}   4 * ceil(n/3)")
for n in range(1, 8):
    enc = base64.b64encode(b"a" * n).decode()
    print(f"   {n:>8}  {enc:<12} {len(enc):>5} {enc.count('='):>5}   {4 * -(-n // 3):>12}")
print()
print("   The output length depends only on the input length, so a decoder")
print("   can size its buffer before reading a byte. The '=' is not a")
print("   separator and carries no data: it says how many of the last")
print("   quantum's bytes were real -- one '=' means two, two means one.")
print()
print("   Which is why the padding is droppable when the length is known")
print("   another way. A JWT is three base64url fields split on '.', so the")
print("   lengths are already there and RFC 7515 tells you to strip it:")
tok = base64.urlsafe_b64encode(b'{"alg":"none"}').decode()
print(f"     {'with padding':<20} {tok}")
print(f"     {'as a JWT sends it':<20} {tok.rstrip('=')}")
print("   Python will not decode the stripped form -- b64decode wants a")
print("   multiple of four -- so putting the padding back is the first line")
print("   of every JWT library:")
stripped = tok.rstrip("=")
try:
    base64.urlsafe_b64decode(stripped)
except binascii.Error as exc:
    print(f"     b64decode(stripped)          -> binascii.Error: {exc}")
restored = stripped + "=" * (-len(stripped) % 4)
print(f"     s + '=' * (-len(s) % 4)      -> {base64.urlsafe_b64decode(restored)!r}")

say("4. TWO SPELLINGS, ONE PAYLOAD -- AND validate=True DOES NOT CARE")

print("   One byte, 0x41, needs 8 bits. Two base64 characters carry 12.")
print("   The 4 bits left over are supposed to be zero, and nothing in the")
print("   decoder makes them be:")
print()
spellings = [
    "Q" + c + "==" for c in ALPHABET if base64.b64decode("Q" + c + "==") == b"A"
]
print(f"   {'canonical':<14} {spellings[0]}  -> {base64.b64decode(spellings[0])!r}")
print(f"   {'also decodes':<14} {spellings[1]}  -> {base64.b64decode(spellings[1])!r}")
print(f"   {'and so does':<14} {spellings[-1]}  -> {base64.b64decode(spellings[-1])!r}")
print(f"   {'distinct spellings of that one byte:':<38} {len(spellings)}")
print()
print("   validate=True sounds like the fix. It is not -- it validates the")
print("   ALPHABET, not the arithmetic:")
print(f"     b64decode('{spellings[1]}', validate=True) -> {base64.b64decode(spellings[1], validate=True)!r}")
try:
    base64.b64decode("SGVs bG8=", validate=True)
except binascii.Error as exc:
    print(f"     b64decode('SGVs bG8=', validate=True) -> binascii.Error: {exc}")
print(f"     b64decode('SGVs bG8=')                -> {base64.b64decode('SGVs bG8=')!r}   (space skipped)")
print()
print("   So base64 is NOT canonical: decode is many-to-one. Any check that")
print("   compares the TEXT -- a signature over the encoded form, a cache")
print("   key, a deduplication table, an allow-list -- can be defeated by")
print("   respelling it. Compare the bytes you decoded, never the string.")
print("   The only way to know a string is canonical is to re-encode what")
print("   you decoded and require the two to match:")
for s in (spellings[0], spellings[1]):
    again = base64.b64encode(base64.b64decode(s)).decode()
    print(f"     {s} -> decode -> encode -> {again}   canonical: {again == s}")

say("5. THE LINE THE TABLES DO NOT DRAW: DOES THE BASE DIVIDE A POWER OF TWO?")

print("   Every scheme so far cut the bits into equal pieces, because 64,")
print("   32 and 16 are powers of two and a whole number of bits fits:")
print()
print(f"   {'scheme':<10} {'bits/char':>9}   {'quantum':<20} {'café ->'}")
for label, fn, bits, quantum in (
    ("Base16", base64.b16encode, 4, "1 byte  -> 2 chars"),
    ("Base32", base64.b32encode, 5, "5 bytes -> 8 chars"),
    ("Base64", base64.b64encode, 6, "3 bytes -> 4 chars"),
    ("Ascii85", base64.a85encode, None, "4 bytes -> 5 chars"),
):
    b = f"{bits}" if bits else "~6.4"
    print(f"   {label:<10} {b:>9}   {quantum:<20} {fn(raw).decode()}")
print()
print("   Ascii85 is the odd one: 85 is not a power of two, but 85**5 just")
print("   exceeds 256**4, so it still has a fixed quantum -- four bytes in,")
print("   five characters out, a base-85 number per group.")
print()
print("   Base58 and Base62 have no quantum at all. There is no group size")
print("   that works, so the encoder reads the WHOLE input as one enormous")
print("   integer and divides it down. Three consequences follow, and none")
print("   of them is an efficiency percentage:")
print()

B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode(data: bytes) -> str:
    n = int.from_bytes(data, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = B58[r] + out
    return out


print(f"   {'base58 of café':<26} {b58encode(raw)}")
print("     (a) You cannot start until the last byte has arrived, and you")
print("         cannot decode the front without the back: no streaming, no")
print("         seeking, no fixed output length.")
print("     (b) The arithmetic is quadratic. Doubling the input roughly")
print("         quadruples the work, which is why nobody base58s a file.")
print("     (c) A leading zero byte is not a digit, it is nothing:")
for data, note in ((b"\x00\x00\x41", "two leading zeros"), (b"\x41", "no leading zeros")):
    n = int.from_bytes(data, "big")
    print(f"         {data.hex(' '):<10} -> int {n:<4} -> base58 {b58encode(data)!r:<6} ({note})")
print("         Base58Check patches this by hand, writing one '1' per")
print("         leading zero byte -- a rule bolted on outside the maths.")
print()
print("   That is the split worth carrying: a power-of-two base is a")
print("   re-cutting of bits and runs in one pass; anything else is")
print("   arbitrary-precision division over the whole message. The two are")
print("   not neighbours on a scale of efficiency. They are different")
print("   algorithms, and the choice is made for humans -- Base58 drops")
print(f"   {'0OIl'!r} so a person can copy an address off a screen.")

say("6. WHAT IT COSTS, AND THE ORDER TO DO IT IN")

payload = ("date,name,amount\n" + "".join(
    f"2026-09-0{i % 9 + 1},café {i},{i * 37}\n" for i in range(200)
)).encode("utf-8")

enc_only = len(base64.b64encode(payload))
gz_then_b64 = len(base64.b64encode(gzip.compress(payload, mtime=0)))
b64_then_gz = len(gzip.compress(base64.b64encode(payload), mtime=0))

print(f"   {'the payload (a small CSV)':<30} {len(payload):>7} bytes")
print(f"   {'base64 of it':<30} {enc_only:>7} bytes   {enc_only / len(payload):.2f}x")
print()
print("   Four characters per three bytes is 4/3, so base64 costs 33% more")
print("   and always exactly that -- the '75% efficiency' in the reference")
print("   tables is the same number upside down (6 bits carried per 8 sent).")
print("   That number is arithmetic on the length, which is why it is")
print("   printed above and the next two are not.")
print()

smaller, larger = sorted((gz_then_b64, b64_then_gz))
gap_pct = round((larger - smaller) / smaller * 20) * 5
print("   Now compress as well, both ways round:")
print(f"     {'smaller':<22} {'gzip, then base64' if gz_then_b64 < b64_then_gz else 'base64, then gzip'}")
print(f"     {'the other one is':<22} about {gap_pct}% bigger")
print(f"     {'both are under':<22} {round(larger / len(payload) * 5) * 20}% of the raw payload")
print()
print("   The two byte counts themselves are deliberately not recorded")
print("   here: they are the output of whichever zlib the machine was")
print("   built against, so they belong in a dated line on the page and")
print("   not in an answer key. The ORDER is the lesson, and it is stable.")
print()
print("   Compress first. gzip works on the bytes; once they are base64 the")
print("   repeats it looks for have been smeared across a 4-character")
print("   period and it recovers fewer of them. The gap is not enormous")
print("   here, and on a payload that compresses badly it can vanish or")
print("   invert -- so measure yours rather than quoting the rule.")
print()
print("   And the thing base64 does not buy, which is worth saying out")
print("   loud because a decade of code review says otherwise:")
secret = base64.b64encode(b"hunter2").decode()
print(f"     b64decode('{secret}') -> {base64.b64decode(secret)!r}")
print("   It is not encryption, it is not obfuscation, and it is not a")
print("   checksum. It is a public, reversible rewriting whose only job is")
print("   to survive a channel that will not carry arbitrary bytes.")
print(f"   crc32 of the payload, for contrast: {zlib.crc32(payload):#010x} -- that one detects damage.")
