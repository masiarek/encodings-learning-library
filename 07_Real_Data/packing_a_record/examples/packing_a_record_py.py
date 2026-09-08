"""The layout lives in the format string, and the prefix you leave off is a trap.

`struct` is the shortest way in any language on this page to say what a binary
record looks like -- three field letters and a prefix -- and that compression is
the whole problem. The prefix is one character, it is optional, and leaving it
off does not mean "no opinion about byte order and padding". It means *this
machine's C compiler decides*, which is a different record on a different
machine and never raises anything.

Everything below that could differ between two machines is printed as a
comparison rather than as a number, for the reason `to_ne_bytes` is not printed
on the byte-order page: a recorded answer key must not depend on who ran it.

Run:  python3 packing_a_record_py.py
"""

import struct

RULE = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{RULE}\n")


def row(label, blob, note=""):
    print(f"   {label:<28} {blob.hex(' '):<47} {note}")


def cls(e):
    """The exception's class, never its message: the wording is CPython's."""
    return f"{type(e).__module__}.{type(e).__name__}"


# One order line from an interface. Three fields, three widths, no text yet --
# the name arrives in section 5, which is where this stops being a
# data-structures exercise and becomes an encodings one.
ID, QTY, PRICE = 4711, -3, 19.5

# ------------------------------------------------------------------ 1
head(1, "A RECORD IS SOME VALUES AND A LAYOUT NOBODY SENT WITH THEM")

wire = struct.pack(">Ihd", ID, QTY, PRICE)
print(f"   id    = {ID:<8} unsigned, 4 bytes   'I'")
print(f"   qty   = {QTY:<8} signed,   2 bytes   'h'")
print(f"   price = {PRICE:<8} float,    8 bytes   'd'")
print()
row("struct.pack('>Ihd', ...)", wire, f"{len(wire)} bytes")
print()
print("   Field by field, at the offsets the format string fixes:")
print(f"     0..4    {wire[0:4].hex(' '):<24} id")
print(f"     4..6    {wire[4:6].hex(' '):<24} qty, two's complement")
print(f"     6..14   {wire[6:14].hex(' '):<24} price, IEEE 754 binary64")
print()
print("   Nothing in those fourteen bytes says any of that. No header, no")
print("   field name, no length, no separator. The layout is an agreement")
print("   held somewhere else -- in a specification, in a comment, or, most")
print("   often, in the format string of whichever program wrote the file.")

# ------------------------------------------------------------------ 2
head(2, "THE BYTE ORDER IS THE FIRST CHARACTER OF THE STRING")

for prefix, note in (("<", "little-endian"),
                     (">", "big-endian"),
                     ("!", "network order -- the same bytes as '>'")):
    row(f"struct.pack('{prefix}Ihd', ...)",
        struct.pack(f"{prefix}Ihd", ID, QTY, PRICE), note)
print()
print(f"   '!Ihd' and '>Ihd' agree, byte for byte: "
      f"{struct.pack('!Ihd', ID, QTY, PRICE) == struct.pack('>Ihd', ID, QTY, PRICE)}")
print()
print("   Same three values, same three widths, two different files. Which")
print("   one is correct is not a property of the data and cannot be worked")
print("   out from it. It is a property of whoever you are sending it to.")

# ------------------------------------------------------------------ 3
head(3, "AND THE PREFIX YOU DID NOT WRITE IS NOT 'NO PREFIX'")

std = struct.calcsize("<Ihd")
print(f"   struct.calcsize('<Ihd')     {std}    4 + 2 + 8, and 14 on every machine")
print(f"   struct.calcsize('>Ihd')     {struct.calcsize('>Ihd')}    the order changes no width")
print(f"   struct.calcsize('!Ihd')     {struct.calcsize('!Ihd')}")
print(f"   struct.calcsize('=Ihd')     {struct.calcsize('=Ihd')}    native ORDER, standard sizes")
print("   struct.calcsize('Ihd')      -- deliberately not printed: with no")
print("                                  prefix the sizes and the padding are")
print("                                  your C compiler's, so the number is a")
print("                                  fact about this machine, not 'Ihd'")
print()
print(f"   Is the unprefixed format the same length as '<Ihd'?   "
      f"{struct.calcsize('Ihd') == std}")
print()
print("   That False is the whole section. 'Ihd' is not a shorter spelling of")
print("   '<Ihd' or of '>Ihd' -- it is a fourth format, and the bytes it adds")
print("   are ALIGNMENT PADDING: dead bytes the compiler inserts so each")
print("   field begins at an address its type is willing to start at.")
print()
print("   Padding is not the enemy. Invisible padding is. In standard mode you")
print("   can write it down, and then it sits in the string somebody reviews:")
print()
row("struct.pack('<Ihd', ...)", struct.pack("<Ihd", ID, QTY, PRICE),
    f"{struct.calcsize('<Ihd')} bytes, no padding")
row("struct.pack('<Ihxxd', ...)", struct.pack("<Ihxxd", ID, QTY, PRICE),
    f"{struct.calcsize('<Ihxxd')} bytes, two 'x' pads")
print()
print("   'x' is a pad byte you asked for: it writes a zero, unpacks to")
print("   nothing, and is visible in the format. The padding inside 'Ihd'")
print("   does the same job and is visible nowhere.")

# ------------------------------------------------------------------ 4
head(4, "THE WRONG ORDER IS SILENT; ONLY THE WRONG LENGTH IS LOUD")

be = struct.pack(">Ihd", ID, QTY, PRICE)
print(f"   written big-endian, read big-endian      {struct.unpack('>Ihd', be)}")
print(f"   written big-endian, read little-endian   {struct.unpack('<Ihd', be)}")
print()
print("   No exception, no warning, nothing in the data to check against.")
print("   4711 read backwards is a perfectly good unsigned integer and 19.5")
print("   read backwards is a perfectly good float, so every field survives")
print("   and every field is wrong. That is the failure this page exists for.")
print()
print("   The one mistake that does raise is a length mismatch, because a")
print("   format string knows exactly how many bytes it wants:")
try:
    struct.unpack("<Ihxxd", be)
except struct.error as e:
    print(f"     unpack('<Ihxxd', <14 bytes>)   {cls(e)}"
          f"   -- a 16-byte format cannot read 14 bytes")
print()
print("   Worth reading twice: the check that fires is on the TOTAL LENGTH,")
print("   never on the meaning. A record of the right length in the wrong")
print("   order passes every check `struct` has.")

# ------------------------------------------------------------------ 5
head(5, "THE NAME FIELD, WHERE THIS BECOMES A QUESTION ABOUT TEXT")

name = "Zażółć"
raw = name.encode("utf-8")
print(f"   name               {name!r}")
print(f"     len(name)         {len(name)}   characters")
print(f"     len(encoded)      {len(raw)}  bytes in UTF-8   {raw.hex(' ')}")
print()
try:
    struct.pack("<10s", name)
except struct.error as e:
    print(f"   struct.pack('<10s', name)       {cls(e)}")
print()
print("   Two things in that one line. 's' does not pack a string -- it packs")
print("   BYTES, and it will not encode for you, which is the right refusal:")
print("   it does not know which encoding the other end agreed to. And the")
print("   class is struct.error rather than TypeError, so a program guarding")
print("   its packs with `except TypeError` catches none of this.")
print()
print("   The encode step is yours:")
print()
row("struct.pack('<10s', raw)", struct.pack("<10s", raw), "10 bytes, exactly full")
print()
print("   Six characters into a ten-byte field, filled to the byte. That is a")
print("   coincidence of this word rather than a rule: 'Zażółć' is two ASCII")
print("   letters and four Polish ones, and each of the four costs two bytes.")
print("   The same field holds ten letters of an English name and five of a")
print("   Polish one. A field width is a BYTE budget.")

# ------------------------------------------------------------------ 6
head(6, "A BYTE BUDGET THAT 's' WILL QUIETLY SPEND FOR YOU")

nine = struct.pack("<9s", raw)
row("struct.pack('<9s', raw)", nine, "9 bytes -- one short")
print()
print("   No exception. 's' truncates on the right and says nothing, because")
print("   as far as `struct` is concerned it was handed bytes and asked for")
print("   nine of them. Ask what those nine bytes are:")
print()
try:
    nine.decode("utf-8")
except UnicodeDecodeError as e:
    print(f"     nine.decode('utf-8')            {cls(e)}")
print(f"     nine.decode('utf-8', 'replace')  {nine.decode('utf-8', 'replace')!r}")
print()
print("   The cut landed between the two bytes that spell 'ć', so the field")
print("   is not text any more. It is nine bytes of which the last is a lead")
print("   byte with nothing behind it -- valid UTF-8 up to position 8 and")
print("   then a promise the file does not keep.")
print()
print("   In a BINARY record the answer is not to truncate more carefully.")
print("   It is to refuse, before the pack, where you still know whose name")
print("   it was:")
print()
for candidate in ("Adam", "Zażółć", "Zażółći"):
    enc = candidate.encode("utf-8")
    print(f"     {candidate:<8} {len(candidate)} chars {len(enc):>3} bytes"
          f"   fits a 10-byte field: {len(enc) <= 10}")
print()
print("   Check the encoded length before you pack and raise at the boundary")
print("   the data entered, rather than shipping a field that is half a")
print("   character. Backing up to a character boundary is the right answer")
print("   for a fixed-width TEXT record, and that is a different lesson.")

# ------------------------------------------------------------------ 7
head(7, "THE ROUND TRIP, ONCE ALL FOUR DECISIONS ARE WRITTEN DOWN")

FMT = ">Ih10s"
packed = struct.pack(FMT, ID, QTY, raw)
row(f"struct.pack('{FMT}', ...)", packed, f"{struct.calcsize(FMT)} bytes")
back_id, back_qty, back_name = struct.unpack(FMT, packed)
print(f"   unpacked           id={back_id}  qty={back_qty}  name={back_name!r}")
print(f"     name.decode()    {back_name.decode('utf-8')!r}")
print()
print(f"   round trips: "
      f"{(back_id, back_qty, back_name.decode('utf-8')) == (ID, QTY, name)}")
print()
print("   Four decisions, all of them in that one string and the call around it:")
print("     >      byte order, named rather than inherited from the hardware")
print("     I h    widths, fixed by the standard rather than by the compiler")
print("     10s    a byte budget, checked by you before the pack")
print("     utf-8  an encoding, applied by you because 's' will not guess")
print()
print("   A record whose writer and reader agree on all four is portable.")
print("   A record missing any one of them works on the machine that wrote it.")
print()
