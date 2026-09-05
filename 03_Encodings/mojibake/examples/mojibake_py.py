#!/usr/bin/env python3
"""Mojibake made on purpose, recognised, counted, and reversed.

Mojibake is not corruption. Every byte is exactly what the writer wrote; the
reader applied a different table. This program produces each of the common
patterns deliberately from known text, shows that the bytes never changed,
counts the layers when it happened twice, reverses the ones that can be
reversed, and shows the two that cannot -- because in those the byte really
was thrown away, and by which side.

Run:  python3 mojibake_py.py
"""

import unicodedata

BAR = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


def damage(text, wrong_table="latin_1"):
    """One round trip of the classic bug: written UTF-8, read under another table."""
    return text.encode("utf_8").decode(wrong_table)


def repair(text, wrong_table="latin_1"):
    """The inverse: put the characters back as bytes, read them as UTF-8."""
    return text.encode(wrong_table).decode("utf_8")


# ------------------------------------------------------------------ 1
head(1, "THE MECHANISM: THE BYTES DO NOT CHANGE")
true_text = "café"
raw = true_text.encode("utf_8")
seen = raw.decode("latin_1")
print(f"   the writer had      {true_text!r}")
print(f"   and wrote           {raw.hex(' ')}   (UTF-8)")
print(f"   the reader read     {raw.hex(' ')}   (the same bytes)")
print(f"   under Latin-1, so   {seen!r}")
print(f"   bytes identical:    {seen.encode('latin_1') == raw}")
print()
print("   Nothing was corrupted. The file is byte-for-byte what the writer")
print("   produced. Only the table was wrong, which is why the damage is")
print("   perfectly regular -- and therefore recognisable, and often reversible.")

# ------------------------------------------------------------------ 2
head(2, "THE RECOGNITION TABLE")
samples = [
    ("é", "latin_1", "an accented letter, read as Latin-1"),
    ("é", "cp1252", "the same, read as Windows-1252"),
    ("—", "cp1252", "an em dash -- the commonest one in the wild"),
    ("“", "cp1252", "a curly quote from a word processor"),
    ("”", "cp1252", "its closing partner -- see below"),
    ("\u00a0", "cp1252", "a non-breaking space: the lone Â people see"),
    ("łódź", "cp1252", "Polish, via a UTF-8 file read as 1252"),
]
print(f"   {'true text':<10} {'UTF-8 bytes':<24} {'seen as':<16} what it was")
for text, table, note in samples:
    try:
        seen = repr(damage(text, table))
    except UnicodeDecodeError as e:
        seen = f"<raises: {e.object[e.start]:#04x}>"
    print(f"   {text!r:<10} {text.encode('utf_8').hex(' '):<24} {seen:<16} {note}")
print()
print("   Every row is the same one bug. Once `Ã` or `â€` is a shape you")
print("   recognise, you are reading the writer's table off the screen.")
print()
holes = [b for b in range(256) if not bytes([b]).decode('cp1252', errors='ignore')]
print(f"   The row that raises is worth keeping: Windows-1252 leaves {len(holes)} byte")
print(f"   values undefined ({', '.join(f'{h:#04x}' for h in holes)}), so unlike Latin-1 it can")
print("   occasionally refuse. That is the whole of its advantage as a detector,")
print("   and 5 out of 256 is not much of one.")

# ------------------------------------------------------------------ 3
head(3, "DOUBLE ENCODING: COUNTING THE LAYERS")
s = "café"
for layer in range(4):
    print(f"   {layer} layer(s): {s!r:<24} {s.encode('utf_8').hex(' ')}")
    s = damage(s)
print()
print("   Each pass multiplies: one byte above 0x7f becomes two, then four.")
print("   'é' -> 'Ã©' -> 'Ã\\x83Â©'. The growth is the tell -- a file that got")
print("   longer every time it was copied has an interface applying the bug")
print("   on every hop.")

# ------------------------------------------------------------------ 4
head(4, "REVERSING IT, AND COUNTING BACK DOWN")
broken = damage(damage("café"))
print(f"   found in the data: {broken!r}")
layers = 0
while True:
    try:
        candidate = repair(broken)
    except (UnicodeDecodeError, UnicodeEncodeError):
        break
    broken, layers = candidate, layers + 1
    print(f"   after {layers} repair(s):  {broken!r}")
print()
print(f"   {layers} layers, and it stops on its own: the next repair raises,")
print("   which is the signal that the text underneath is now real. This works")
print("   because Latin-1 maps all 256 byte values -- so .encode('latin_1')")
print("   hands back exactly the bytes the wrong decode read, none lost.")

# ------------------------------------------------------------------ 5
head(5, "THE TWO THAT DO NOT REVERSE")
gone_on_write = "café".encode("ascii", errors="replace")
gone_on_read = b"caf\xe9".decode("utf_8", errors="replace")
print(f"   thrown away at WRITE time: 'café'.encode('ascii', errors='replace')")
print(f"     bytes on disk  {gone_on_write.hex(' ')}  -> {gone_on_write.decode('ascii')!r}")
print(f"   thrown away at READ time:  b'caf\\xe9'.decode('utf_8', errors='replace')")
print(f"     text in memory {gone_on_read!r}  U+{ord(gone_on_read[-1]):04X} {unicodedata.name(gone_on_read[-1])}")
print()
print("   '?' and U+FFFD are not encodings of 'é'. They are the record that a")
print("   character was discarded, and no table anywhere can bring it back. If")
print("   these are in the archive, the archive is the loss -- go upstream.")
print("   The difference matters when you are asked whether a file is fixable:")
print("   'Ã©' is a display of the right bytes and repairs; '?' and U+FFFD are")
print("   the right display of bytes that no longer say what they said.")

# ------------------------------------------------------------------ 6
head(6, "AND ONE THAT IS NOT AN ENCODING BUG AT ALL")
for ch in "字𝔊":
    print(f"   {ch!r}  U+{ord(ch):04X}  {unicodedata.name(ch)}")
    print(f"       decoded fine: {ch.encode('utf_8').hex(' ')} -> {ch.encode('utf_8').decode('utf_8')!r}")
print()
print("   If a character shows as a box and Python can still tell you its name,")
print("   the decode was correct and your font has no glyph. Tofu is a display")
print("   problem. Changing the encoding will not fix it, and trying is how a")
print("   working file gets damaged.")

# ------------------------------------------------------------------ 7
head(7, "NAMING THE CULPRIT FROM THE GARBAGE ALONE")
TABLES = ["latin_1", "cp1252", "cp1250", "iso8859_2", "cp850", "mac_roman"]

print("   Forwards first: one em dash, read under each table in turn.")
dash = "—"
for read_as in TABLES:
    print(f"     {read_as:<10} -> {dash.encode('utf_8').decode(read_as)!r}")
print()
print("   Six tables, five distinct shapes -- cp1252 and cp1250 agree here, so")
print("   the fingerprint names a FAMILY and only sometimes a single table.")
print("   The last row is the one people meet without knowing its name: an")
print("   em dash in a CSV that Excel opened on a Mac.")

print()
print("   Backwards is the useful direction. Given only the garbage, try")
print("   every table it could have been READ under, and re-read as UTF-8:")
SIGHTINGS = [
    ("Å‚Ã³dÅº", "a Polish name, in a report from a Windows box"),
    ("‚Äî", "an em dash, in a CSV double-clicked on a Mac"),
]
for observed, where in SIGHTINGS:
    print()
    print(f"   {observed!r}  -- {where}")
    for read_as in TABLES:
        try:
            guess = observed.encode(read_as).decode("utf_8")
        except UnicodeEncodeError as e:
            print(f"     read as {read_as:<10} no: {e.object[e.start]!r} is not in this table")
            continue
        except UnicodeDecodeError:
            print(f"     read as {read_as:<10} no: the bytes that gives are not UTF-8")
            continue
        names = ", ".join(unicodedata.name(c, "?") for c in guess if ord(c) > 0x7F)
        print(f"     read as {read_as:<10} -> {guess!r}   [{names}]")
print()
print("   Exactly one table produces a word, and it is a different table for")
print("   each sighting. That pair IS the bug report: the file was written")
print("   UTF-8 and read as that table, at whichever hop first shows the")
print("   damage. Note what the second one tells you for free -- mac_roman is")
print("   not a table anybody chooses, it is what a Mac reaches for when no")
print("   encoding was declared, so the garbage named the PLATFORM as well as")
print("   the table. Prove it with a hex dump of the original rather than")
print("   arguing about it -- the bytes have been right the whole time.")
