"""Is this damaged text repairable? Answer that BEFORE reaching for a repair.

The repair itself is one line. Knowing whether it can work is the skill, and
it is decidable from the table that was wrongly applied plus the way the
damage was recorded -- neither of which requires touching the data.
"""

import itertools

UTF8 = "utf-8"
LATIN1 = "latin-1"
CP1252 = "cp1252"


def try_repair(damaged, table):
    """Undo a wrong decode: put the characters back as bytes, read them as UTF-8.

    Returns (text, verdict). On any failure the INPUT is returned unchanged,
    so calling this can never leave the data worse than it was found.
    """
    try:
        raw = damaged.encode(table)
    except UnicodeEncodeError as exc:
        return damaged, f"cannot re-encode under {table}: {exc.reason}"
    try:
        candidate = raw.decode(UTF8)
    except UnicodeDecodeError:
        return damaged, "re-encoded, but the bytes are not UTF-8"
    if candidate == damaged:
        return damaged, "round trip is a no-op -- nothing to repair"
    return candidate, "repaired"


print("1. THE DECIDING QUESTION")
print("-" * 72)
print("   Mojibake is a function that was applied to your bytes. A function")
print("   can be undone when it threw nothing away. So the question is not")
print("   'how do I repair this' but:")
print()
print("      Did the wrong step DISCARD any byte, or merely MISREAD it?")
print()
print("   Misread bytes are all still there and the damage is reversible.")
print("   Discarded bytes are gone, and no amount of cleverness returns")
print("   them. Sections 2 to 4 work out which case you are in.")
print()

print("2. WHY LATIN-1 ALWAYS REVERSES -- BY EXHAUSTION, NOT BY REPUTATION")
print("-" * 72)
survived = 0
for b in range(256):
    if bytes([b]).decode(LATIN1).encode(LATIN1) == bytes([b]):
        survived += 1
print(f"   bytes that survive .decode('latin-1').encode('latin-1'): {survived} of 256")
print()
print("   Latin-1 maps byte N to code point N for all 256 values, so the")
print("   decode is a total, one-to-one function and the encode is exactly")
print("   its inverse. A reader using Latin-1 cannot fail and cannot drop")
print("   anything -- so every byte of the original file is still sitting")
print("   inside the wrong-looking string, and .encode('latin-1') hands the")
print("   file back byte for byte.")
print()
print("   That is why Latin-1 is the right tool for UNDOING mojibake and the")
print("   wrong tool for DETECTING anything: it accepts every file on earth.")
print()

print("3. WHY CP1252 DOES NOT ALWAYS REVERSE")
print("-" * 72)
holes = []
for b in range(256):
    try:
        bytes([b]).decode(CP1252)
    except UnicodeDecodeError:
        holes.append(b)
print("   cp1252 leaves five byte values unassigned:")
print("      " + " ".join(f"0x{b:02X}" for b in holes))
print()
print("   Those five are all legal UTF-8 CONTINUATION bytes, so they appear")
print("   inside ordinary characters. Any character whose UTF-8 encoding")
print("   contains one cannot survive a cp1252 round trip. Below U+0800")
print("   that is 150 characters, and these are the everyday ones:")
print()
lost = []
for cp in range(0x20, 0x800):
    raw = chr(cp).encode(UTF8)
    if set(raw) & set(holes):
        lost.append((cp, raw))
for cp, raw in lost:
    # the Latin-1 supplement and Latin Extended-A: the letters of western
    # and central European languages, rather than the phonetic extensions
    if 0x00C0 < cp < 0x0180 and chr(cp).isprintable():
        print(f"      U+{cp:04X}  {chr(cp)}   {raw.hex(' ')}")
print()
print("   So the repair that fails is not an exotic corner: it is a Spanish")
print("   or Icelandic capital, or a Polish L-with-stroke.")
print()

print("4. ONE STRING, FOUR WAYS OF GOING WRONG")
print("-" * 72)
original = "\N{LATIN CAPITAL LETTER L WITH STROKE}\N{LATIN SMALL LETTER O WITH ACUTE}d\N{LATIN SMALL LETTER Z WITH ACUTE}"
raw = original.encode(UTF8)
print(f"   original           {original!r}")
print(f"   correct UTF-8      {raw.hex(' ')}")
print()

print("   (a) READ AS LATIN-1 -- every byte misread, none discarded")
damaged = raw.decode(LATIN1)
print(f"       looks like     {ascii(damaged)}")
fixed, verdict = try_repair(damaged, LATIN1)
print(f"       repair         {verdict}: {fixed!r}")
print(f"       identical to the original? {fixed == original}")
print()

print("   (b) READ AS CP1252 -- the decode cannot even complete")
try:
    raw.decode(CP1252)
    print("       unexpectedly decoded")
except UnicodeDecodeError as exc:
    print(f"       {type(exc).__name__}: byte 0x{raw[exc.start]:02X} at offset {exc.start}")
print("       A strict cp1252 reader REFUSES this file. That is the good")
print("       outcome -- it is the reader telling you the label is wrong")
print("       before anything is written down.")
print()

print("   (c) READ AS CP1252 BY A LENIENT READER -- the byte survives, the")
print("       repair does not")
lenient = "".join(
    chr(b) if b in holes else bytes([b]).decode(CP1252) for b in raw
)
print(f"       looks like     {ascii(lenient)}")
fixed, verdict = try_repair(lenient, CP1252)
print(f"       repair         {verdict}")
print(f"       unchanged?     {fixed == lenient}")
print("       Many readers outside Python map the five holes to the C1")
print("       controls rather than refusing. The text then looks repairable")
print("       and is not, because Python's cp1252 ENCODER has no entry to")
print("       write those characters back to. The guard returns the input.")
print()

print("   (d) WRITTEN WITH A REPLACEMENT -- the byte is genuinely gone")
for policy in ("replace", "ignore", "xmlcharrefreplace"):
    lossy = original.encode(LATIN1, errors=policy)
    back = lossy.decode(LATIN1)
    print(f"       errors={policy:<18} -> {back!r}")
print("       These happened at WRITE time, in the sending system, and no")
print("       byte of the original reached the file. 'replace' wrote 0x3F,")
print("       the ASCII question mark; 'ignore' wrote nothing at all. Only")
print("       xmlcharrefreplace is reversible, because it wrote the code")
print("       point down in ASCII instead of throwing it away.")
print()

print("5. THE GUARD, AND WHY IT IS THE WHOLE POINT")
print("-" * 72)
print("   try_repair() returns the INPUT unchanged whenever the round trip")
print("   fails, so running it on text that was never damaged is a no-op:")
print()
for sample in ("already fine", original, "caf\N{LATIN SMALL LETTER E WITH ACUTE}"):
    fixed, verdict = try_repair(sample, LATIN1)
    print(f"      {sample!r:<20} -> {verdict:<38} {'unchanged' if fixed == sample else 'CHANGED'}")
print()
print("   That property is what lets you run a repair over a whole column")
print("   without first sorting the good rows from the bad ones.")
print()

print("6. THE GUARD'S LIMIT: A SUCCESSFUL ROUND TRIP IS NOT A PROOF")
print("-" * 72)
innocent = "\N{LATIN CAPITAL LETTER A WITH TILDE}\N{COPYRIGHT SIGN}"
fixed, verdict = try_repair(innocent, LATIN1)
print(f"   {innocent!r} is a legitimate two-character string.")
print(f"   try_repair says: {verdict} -> {fixed!r}")
print("   Correct text, silently changed. The guard proves the bytes form")
print("   valid UTF-8; it cannot prove they were MEANT to.")
print()
print("   How often can that happen? Count every string of length N drawn")
print("   from Latin-1's printable top half, and ask how many are valid")
print("   UTF-8 by accident:")
print()
top = bytes(range(0xA0, 0x100))
for n in (1, 2, 3):
    accidental = 0
    total = 0
    for combo in itertools.product(top, repeat=n):
        total += 1
        try:
            bytes(combo).decode(UTF8)
            accidental += 1
        except UnicodeDecodeError:
            pass
    print(f"      length {n}: {accidental:>6} of {total:>6} = {accidental / total:7.3%}")
print()
print("   Length 1 is impossible -- one high byte is never valid UTF-8 on")
print("   its own. Then the rate falls away as every extra character has to")
print("   keep fitting the UTF-8 grammar. The practical reading: the guard")
print("   is safe on a sentence and genuinely risky on a two-character")
print("   field, which is exactly the sort of column an interface has.")
print("   On a short field, check the whole column instead of each value.")
print()

print("7. COUNTING THE LAYERS BEFORE REPAIRING THEM")
print("-" * 72)
text = "\N{LATIN SMALL LETTER E WITH ACUTE}"
hops = 3
for layer in range(hops + 1):
    print(f"   after {layer} bad hop(s): {ascii(text):<26} {len(text)} chars")
    if layer < hops:
        text = text.encode(UTF8).decode(LATIN1)
print()
print("   Each hop turns one high byte into two, so the string grows and a")
print("   column that keeps overflowing is often this. Repair by looping")
print("   try_repair until the verdict stops being 'repaired':")
print()
rounds = 0
while True:
    fixed, verdict = try_repair(text, LATIN1)
    if verdict != "repaired":
        break
    text = fixed
    rounds += 1
print(f"   stopped after {rounds} repair(s): {text!r}")
print(f"   the ladder above took {hops} hops, and the loop undid {rounds} -- "
      f"{'they agree' if rounds == hops else 'THEY DISAGREE'}")
print("   The loop terminates because the last step is a UTF-8 DECODE, and")
print("   repaired text fails it. A shell pipeline has no such stop -- see")
print("   the mojibake page for iconv cheerfully taking one hop too many.")
