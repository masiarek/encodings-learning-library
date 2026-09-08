"""A fixed-width field is measured in BYTES, and a cut in the wrong place
stops the file being text.

The bug this page is about does not fail every time, which is why it ships. A
naive `value.encode()[:width]` is correct for every ASCII value it was tested
on, correct for most Polish ones too, and produces a file no decoder will read
for the rest. Section 2 counts exactly how often, for one real string.

Nothing here reads a locale, a library or a platform. The answers are
arithmetic over UTF-8's own structure.

Run:  python3 fixed_width_byte_fields_py.py
"""

WIDTH = 10
# CAST.md's Polish pangram: every diacritic the language has, in one line.
VALUE = "zażółć gęślą jaźń"
RAW = VALUE.encode("utf-8")


def hexs(b):
    return " ".join(f"{x:02x}" for x in b)


def decodes(b):
    try:
        b.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def truncate_chars(text, width):
    """Longest prefix of `text` whose UTF-8 form fits in `width` bytes."""
    kept, used = [], 0
    for ch in text:
        n = len(ch.encode("utf-8"))
        if used + n > width:
            break
        kept.append(ch)
        used += n
    return "".join(kept)


def truncate_bytes(raw, width):
    """The same cut, made on the buffer: back up while the FIRST DROPPED
    byte is a continuation byte (10xxxxxx), because that means the cut
    landed inside a sequence rather than between two."""
    n = min(width, len(raw))
    while 0 < n < len(raw) and raw[n] & 0b1100_0000 == 0b1000_0000:
        n -= 1
    return raw[:n]


print("1. THE FIELD IS BYTES; THE VALUE IS CHARACTERS")
print("-" * 70)
print(f"   the value            {VALUE!r}")
print(f"   len(value)           {len(VALUE)} characters")
print(f"   len(value.encode())  {len(RAW)} bytes")
print(f"   bytes per character  {''.join(str(len(c.encode())) for c in VALUE)}")
print()
print(f"   So one CHAR({WIDTH}) field, counted in bytes, holds either:")
print(f"     {WIDTH:2d} ASCII letters   {'a' * WIDTH!r}   {len(('a' * WIDTH).encode())} bytes")
print(f"     {WIDTH // 2:2d} Polish letters  {'żółćę'!r}        {len('żółćę'.encode())} bytes")
print("   Same field, half the letters, and the type name says neither.")
print()

print("2. THE NAIVE CUT IS RIGHT MOST OF THE TIME, WHICH IS WHY IT SHIPS")
print("-" * 70)
safe = [n for n in range(1, len(RAW) + 1) if decodes(RAW[:n])]
split = [n for n in range(1, len(RAW) + 1) if not decodes(RAW[:n])]
print(f"   value.encode()[:n], for every n from 1 to {len(RAW)}:")
print("     " + " ".join(f"{n:2d}" for n in range(1, len(RAW) + 1)))
print("     " + " ".join(" ." if n in safe else " X" for n in range(1, len(RAW) + 1)))
print(f"   decodes: {len(safe)}     splits a character: {len(split)}")
print(f"   the widths that split it: {split}")
print()
print(f"   The {len(safe)} safe widths are not a coincidence: a prefix decodes exactly")
print(f"   when it ends on a character boundary, and this value has {len(VALUE)}")
print(f"   characters. Safe widths = characters; the other {len(split)} are the gaps")
print("   inside multi-byte sequences, one per byte a character has past")
print("   its first.")
print()
print(f"   Width {WIDTH} is {'a clean cut' if WIDTH in safe else 'a split character'} for THIS value. The width decides")
print("   whether the code is correct, and the width is in somebody else's")
print("   specification. That is the whole shape of the bug: it is a")
print("   property of the data, so testing with your own data proves nothing.")
print()

print("3. WHAT A SPLIT SEQUENCE LOOKS LIKE AS BYTES")
print("-" * 70)
bad_n = split[0]
PAD = 21  # 3 spaces of indent + an 18-column label field
print(f"   {f'cut at {bad_n} bytes':<18}{hexs(RAW[:bad_n])}")
print(f"   {'one byte later':<18}{hexs(RAW[:bad_n + 1])}")
print(f"{' ' * (PAD + 3 * bad_n)}^^ the byte the cut left behind")
print()
lead = RAW[bad_n - 1]
promised = 2 if lead >> 5 == 0b110 else 3 if lead >> 4 == 0b1110 else 4
print(f"   The last byte kept is 0x{lead:02x}, which is {lead:08b} in binary.")
print("   A UTF-8 leading byte states its own length in its high bits:")
print("   110xxxxx promises two bytes, 1110xxxx three, 11110xxx four.")
print(f"   This one promises {promised} and the field ends after 1.")
print()
print("   So the sequence is not WRONG about its length; it is INCOMPLETE,")
print("   which is a different failure and the one a decoder can name to the")
print("   exact byte. That precision is the feature -- a cut in a code page")
print("   with no structure produces a different letter and says nothing.")
print()

print("4. WHAT EACH READER DOES WITH THE HALF CHARACTER")
print("-" * 70)
cut = RAW[:bad_n]
try:
    cut.decode("utf-8")
except UnicodeDecodeError as exc:
    print(f"   .decode()                    {type(exc).__name__}")
    print(f"     .start .end                {exc.start} {exc.end}   -- byte offsets, not characters")
    print(f"     the bytes it names         {hexs(cut[exc.start:exc.end])}")
print()
for handler in ("replace", "ignore", "backslashreplace", "surrogateescape"):
    got = cut.decode("utf-8", errors=handler)
    try:
        back = got.encode("utf-8", errors=handler)
    except UnicodeEncodeError as exc:
        back = None
    trip = "holds" if back == cut else "is LOST"
    print(f"   errors={handler!r:18s} {got!r}")
    print(f"     {len(got)} characters; re-encoding gives {'-' if back is None else len(back)} bytes, round trip {trip}")
print()
print("   Only surrogateescape survives the round trip. It parks each stray")
print("   byte in an unpaired surrogate and hands the same byte back on the")
print("   way out, so a value you cannot read is still a value you can")
print("   forward. 'replace' and 'ignore' both destroy the byte, and they")
print("   destroy a different NUMBER of them, so neither length is the")
print("   original -- which is why neither belongs in a pipeline that")
print("   re-emits the record.")
print()

print("5. CUTTING IN THE RIGHT PLACE")
print("-" * 70)
w = split[4]
print("   Five spellings of 'fit this value into the field', at width")
print(f"   {w}, where the naive one is wrong:")
print()
a = VALUE[:w].encode("utf-8")
b = RAW[:w]
c = RAW[:w].decode("utf-8", errors="ignore").encode("utf-8")
d = truncate_chars(VALUE, w).encode("utf-8")
e = truncate_bytes(RAW, w)
L = 34
print(f"   {f'value[:{w}].encode()':<{L}}{len(a):2d} bytes  {'fits' if len(a) <= w else 'OVERFLOWS the field'}")
print(f"   {f'value.encode()[:{w}]':<{L}}{len(b):2d} bytes  {'decodes' if decodes(b) else 'does NOT decode'}")
print(f"   {f'...[:{w}].decode(ignore).encode()':<{L}}{len(c):2d} bytes  decodes, and hides a real error")
print(f"   {'loop over characters':<{L}}{len(d):2d} bytes  decodes  {d.decode()!r}")
print(f"   {'back up off continuation bytes':<{L}}{len(e):2d} bytes  decodes  {e.decode()!r}")
print()
print("   The first counts the wrong unit and can overflow the field by up")
print("   to three bytes per character. The second is the bug. The third is")
print("   the tempting fix and the dangerous one: errors='ignore' cannot")
print("   tell a character YOU cut in half from bytes that arrived broken,")
print("   so it silences the truncation and the corruption with one word.")
print("   The last two are the same decision made in the two units, and")
print("   they agree byte for byte -- the loop is clearer, the back-up is")
print("   what you write when all you have is the buffer.")
print()

print("6. PADDING IS PART OF THE WIDTH, AND THE PAD IS AN ENCODED CHARACTER")
print("-" * 70)
short = "żółw"
print(f"   value {short!r}   {len(short)} characters, {len(short.encode())} bytes")
print(f"   ljust({WIDTH}) then encode   {len(short.ljust(WIDTH).encode()):2d} bytes   padded in CHARACTERS, overflows")
print(f"   encode then pad to {WIDTH}   {len(short.encode().ljust(WIDTH)):2d} bytes   padded in BYTES, correct")
print(f"     {hexs(short.encode().ljust(WIDTH))}")
print()
print("   The pad is a character too, so it is encoded like one -- and in a")
print("   two-byte encoding a field cannot be padded with single 0x20 bytes:")
u16 = short.encode("utf-16-be")
print(f"     {short!r} as UTF-16BE   {hexs(u16)}   ({len(u16)} bytes)")
for n in (2, 3, 4):
    v = u16 + b" " * n
    try:
        got = repr(v.decode("utf-16-be"))
    except UnicodeDecodeError as exc:
        got = type(exc).__name__
    print(f"     + {n} ASCII spaces      {hexs(v[len(u16):])}  ->  {got}")
print()
print("   Two spaces are not two spaces: 0x20 0x20 is one UTF-16 code unit,")
print("   U+2020, which is a DAGGER. An odd number of them leaves the field")
print("   an odd number of bytes long and no decoder will read it at all.")
print("   The correct pad is the space ENCODED -- 00 20 per slot:")
print(f"     + 2 encoded spaces    {hexs(b'\x00 ' * 2)}  ->  {(u16 + b'\x00 ' * 2).decode('utf-16-be')!r}")
print()
print("   In UTF-8 a space is one byte, so this particular mistake cannot")
print("   happen -- which is exactly why nobody thinks about it until the")
print("   field on the other side of the interface is UTF-16.")
