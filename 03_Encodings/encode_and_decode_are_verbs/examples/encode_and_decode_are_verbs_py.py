#!/usr/bin/env python3
"""Two nouns, two verbs, and one argument that nothing checks for you.

Text and bytes are different things. `encode` turns text into bytes and
`decode` turns bytes back into text, and each one takes a table as an
argument. Nothing in the data says which table is right, so the argument is
the whole bug surface of this subject -- which is what the 3x3 grid in
section 2 is: one string, three tables, every combination of the two verbs.

Run:  python3 encode_and_decode_are_verbs_py.py
"""

BAR = "-" * 72
TEXT = "café"
TABLES = ["utf_8", "latin_1", "utf_16_le"]


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


def outcome(data, table):
    """Decode, and report either the text or the exception -- never the message.

    The class name, the reason and the offset are stable across CPython
    versions; the full str(e) is not, and an answer key must not depend on
    which python3 the runner happened to ship.
    """
    try:
        return repr(data.decode(table))
    except UnicodeDecodeError as e:
        return f"{type(e).__name__} at byte {e.start}: {e.reason}"


# ------------------------------------------------------------------ 1
head(1, "TWO NOUNS")
raw = TEXT.encode("utf_8")
print(f"   text  {TEXT!r:<14} type {type(TEXT).__name__:<5} len {len(TEXT)}  <- characters")
print(f"   bytes {raw!r:<14} type {type(raw).__name__:<5} len {len(raw)}  <- bytes")
print()
print("   Two different types holding the same message. len() answers a")
print("   different question on each, and they disagree the moment a")
print("   character needs more than one byte.")

# ------------------------------------------------------------------ 2
head(2, "TWO VERBS, AND THE ARGUMENT NOTHING CHECKS")
print(f"   {TEXT!r}.encode('utf_8')          -> {TEXT.encode('utf_8')!r}")
print(f"   {raw!r}.decode('utf_8')  -> {raw.decode('utf_8')!r}")
print()
print("   encode: text  -> bytes,  under a table")
print("   decode: bytes -> text,   under a table")
print()
print("   The table is an ARGUMENT. It is not a property of the bytes, it is")
print("   not stored with them, and no check anywhere confirms that the table")
print("   you passed is the table the writer used.")

# ------------------------------------------------------------------ 3
head(3, "THE 3x3 GRID: ONE STRING, THREE TABLES, BOTH VERBS")
encoded = {t: TEXT.encode(t) for t in TABLES}
for t in TABLES:
    print(f"   {TEXT!r}.encode({t!r:<11}) = {encoded[t].hex(' ')}")
print()
for written in TABLES:
    print(f"   bytes written as {written}:")
    for read in TABLES:
        mark = "  <- correct" if read == written else ""
        print(f"     read as {read:<10} {outcome(encoded[written], read)}{mark}")
    print()
print("   Three of the nine are right, and they are right for one reason only:")
print("   the reader was told the same table the writer used. Of the other six,")
print("   three raise and three do not -- and the three that do not are worse.")

# ------------------------------------------------------------------ 4
head(4, "WHY latin-1 CAN NEVER RAISE")
def decodes(data, table):
    try:
        data.decode(table)
        return True
    except UnicodeDecodeError:
        return False


singles = [bytes([b]) for b in range(256)]
for table in ("latin_1", "utf_8", "ascii"):
    ok = sum(1 for b in singles if decodes(b, table))
    print(f"   of the 256 one-byte inputs, {table:<8} decodes {ok:>3}")
print()
print("   latin-1 maps all 256 byte values to code points 0-255, so decoding")
print("   under it CANNOT fail. That makes it the right tool for carrying")
print("   arbitrary bytes through a str, and the wrong tool for detecting")
print("   anything at all: it answers 'fine' to every file you show it.")

# ------------------------------------------------------------------ 5
head(5, "THE TWO ERRORS, FIELD BY FIELD")
try:
    b"caf\xe9!".decode("utf_8")
except UnicodeDecodeError as e:
    print("   b'caf\\xe9!'.decode('utf_8')")
    print(f"     .encoding {e.encoding!r:<10} the table you passed")
    print(f"     .start    {e.start:<10} the byte it stopped on")
    print(f"     .object   {e.object[e.start:e.end]!r:<10} that byte")
    print(f"     .reason   {e.reason!r}")
print()
try:
    "café".encode("ascii")
except UnicodeEncodeError as e:
    print("   'café'.encode('ascii')")
    print(f"     .encoding {e.encoding!r:<10} the table you passed")
    print(f"     .start    {e.start:<10} the character it stopped on")
    print(f"     .object   {e.object[e.start:e.end]!r:<10} that character")
    print(f"     .reason   {e.reason!r}")
print()
print("   Both name the table, the position and the reason. Read the position")
print("   first: it tells you which character in the file to look at, and a")
print("   hex dump of that offset usually ends the argument.")

# ------------------------------------------------------------------ 6
head(6, "THE UNICODE SANDWICH, AND THE COST OF SKIPPING IT")
print("   decode at the edge coming in  ->  work in text  ->  encode at the edge going out")
print()
print("   Slicing text and slicing bytes are not the same operation:")
print(f"     {TEXT!r}[:4]            = {TEXT[:4]!r}")
print(f"     {raw!r}[:4]     = {raw[:4]!r}  <- half of a character")
print(f"       and decoding that:      {outcome(raw[:4], 'utf_8')}")
print()
print("   A four-CHARACTER field and a four-BYTE column are different sizes:")
print(f"     len({TEXT!r})          = {len(TEXT)} characters")
print(f"     len({TEXT!r}.encode()) = {len(raw)} bytes")
print()
print("   Every interface bug in chapter 7 is one of those two lines being")
print("   the one the program did not mean.")
