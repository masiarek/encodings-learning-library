"""Where the UTF-8 check happens in Python, and what is left of it afterwards.

Run:  python3 validation_is_a_boundary_py.py
"""


def bits(b):
    """One byte as the slide draws it: 1110.0010"""
    return f"{b >> 4:04b}.{b & 0x0F:04b}"


print("1. THE THREE SEQUENCES FROM THE SLIDE, DECODED")
for n, raw in enumerate([b"\x7d", b"\xc2\xa9", b"\xe2\x89\xa0"], start=1):
    text = raw.decode("utf-8")               # the check happens HERE, and only here
    drawn = " ".join(bits(b) for b in raw)
    hexed = " ".join(f"0x{b:02X}" for b in raw)
    print(f"   {n}: {drawn:<35} U+{ord(text):04X}: {hexed:<15} ({text})")
print("   1 lead byte + 0/1/2 continuation bytes; the payload bits concatenate, nothing else moves.")
print()

print("2. SIX WAYS TO BE INVALID, AND WHAT THE EXCEPTION KNOWS")
BAD = [
    (b"\x89",                 "lone continuation byte"),
    (b"\xe2\x89",             "truncated 3-byte sequence"),
    (b"\xc0\xaf",             "overlong '/' — two bytes for U+002F"),
    (b"\xe0\x80\xaf",       "overlong '/' — the three-byte way"),
    (b"\xed\xa0\x80",         "UTF-16 surrogate U+D800"),
    (b"\xf5\x80\x80\x80",     "above U+10FFFF"),
]
for raw, why in BAD:
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"   {raw.hex(' '):<12} start={e.start} end={e.end}  {e.reason:<26} {why}")
print("   start is how far the bytes were text; the reason names which rule broke.")
print("   Two of the reasons are the rule table talking. C0 is an 'invalid start byte' because")
print("   C0 and C1 can only ever begin an overlong form, so no second byte is needed to reject it.")
print("   ED is a fine start byte, so ED A0 fails one byte later: after ED the only legal")
print("   second bytes are 80..9F, and A0 is where the surrogates begin.")
print()

print("3. THE SAME BAD BYTES, FIVE ERROR HANDLERS")
raw = b"caf\xe9 au lait"                     # Latin-1 'e-acute' loose in a UTF-8 stream
for how in ["replace", "ignore", "backslashreplace", "surrogateescape"]:
    print(f"   {how:<17} -> {raw.decode('utf-8', errors=how)!r}")
try:
    raw.decode("utf-8")
except UnicodeDecodeError as e:
    print(f"   {'strict (default)':<17} -> raises at byte {e.start}")
print("   Only 'strict' preserves the fact that something was wrong. The rest are decisions.")
print()

print("4. AFTER THE BOUNDARY, PYTHON DOES NOT HOLD UTF-8 AT ALL")
text = b"\xe2\x89\xa0".decode("utf-8")
print(f"   text                  = {text!r}")
print(f"   len(text)             = {len(text)}   (code points)")
print(f"   len(text.encode())    = {len(text.encode('utf-8'))}   (UTF-8 bytes, rebuilt on demand)")
print("   A str is a sequence of code points. The UTF-8 was consumed at decode() and is gone;")
print("   every .encode() builds it again. Nothing in the object records that a check ever ran.")
print()

print("5. AND A str CAN HOLD WHAT UTF-8 CANNOT ENCODE")
lone = chr(0xD800)
print(f"   chr(0xD800)           = {lone!r}   <- built without complaint")
try:
    lone.encode("utf-8")
except UnicodeEncodeError as e:
    print(f"   .encode('utf-8')      -> UnicodeEncodeError: {e.reason}")
print(f"   chr(0x10FFFF)         = {chr(0x10FFFF)!r}   (the top of the range; chr(0x110000) is a ValueError)")
print("   So Python checks on the way IN and again on the way OUT, because between the two")
print("   the type allows a value no UTF-8 file can contain.")
