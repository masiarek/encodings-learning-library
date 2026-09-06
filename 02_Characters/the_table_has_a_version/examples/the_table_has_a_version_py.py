#!/usr/bin/env python3
"""Two Unicode tables live in one stdlib module. Only one of them is safe to
write down; the other is a fact about the machine that ran the program."""

import unicodedata

MODERN = unicodedata  # the table THIS interpreter was built with
FROZEN = unicodedata.ucd_3_2_0  # Unicode 3.2.0, sealed in 2002, identical everywhere

RULE = "-" * 72

# Four cast members, then four characters chosen for their dates: the uppercase
# of the cast's own eszett, an emoji, and two currency signs the world needed
# after the frozen table was sealed.
PROBES = [0x00E9, 0x017C, 0x20AC, 0x0CA0, 0x1E9E, 0x1F600, 0x20BD, 0x20BF]

print("1. ONE MODULE, TWO UNICODE TABLES")
print(RULE)
print("   unicodedata               the table this interpreter was built with")
print("   unicodedata.ucd_3_2_0     Unicode %s, sealed in 2002" % FROZEN.unidata_version)
print()
print("   The frozen one is here because IDNA and stringprep pinned their table")
print("   on purpose: a domain name must not change meaning when Unicode grows.")
print("   That makes it the one Unicode table whose answers are the same on")
print("   every machine under every Python -- which is why this program may")
print("   print them, and may not print the other one's.")
print()

print("2. THE SAME QUESTION, ASKED OF BOTH TABLES")
print(RULE)
print("   code point  char   name, from whichever table knows it   in 2002?")
missing = 0
for cp in PROBES:
    ch = chr(cp)
    old, new = FROZEN.name(ch, ""), MODERN.name(ch, "")
    missing += not old
    print("   %-11s %-6s %-37s %s" % ("U+%04X" % cp, ch, new, "yes" if old else "no"))
print()
print("   %d of the %d are missing from the 2002 table." % (missing, len(PROBES)))
print("   Nothing was ever removed from Unicode -- these had not arrived yet.")
print()

# One pass over the whole number line, answering two questions at once.
renamed = named = 0
for cp in range(0x110000):
    ch = chr(cp)
    new = MODERN.name(ch, "")
    named += bool(new)
    old = FROZEN.name(ch, "")
    renamed += bool(old) and old != new

print("3. GROWING IS THE ONLY THING THE TABLE EVER DID")
print(RULE)
print("   code points the 2002 table and this one name differently:  %d" % renamed)
print("   code points this table has names for, over 100,000:        %s" % (named > 100_000))
print()
print("   The zero is not luck. A Name is one of Unicode's stability guarantees:")
print("   once a code point is assigned, its name may never change and the code")
print("   point may never be reused. So a NAME is safe to put in an answer key.")
print("   The count beside it is not -- which is why it is printed as a question")
print("   with a stable answer rather than as a number.")
print()

print("4. AN OLD TABLE DOES NOT SAY \"I DO NOT KNOW\"")
print(RULE)
print("   the frozen 2002 table, asked about four very different code points:")
print()
print("   code point  category  name          what it actually is")
for cp, truth in (
    (0x1F600, "GRINNING FACE, real since 2010"),
    (0x1E9E, "CAPITAL SHARP S, real since 2008"),
    (0x0378, "genuinely unassigned, still is"),
    (0xFFFE, "a noncharacter -- never will be"),
):
    ch = chr(cp)
    try:
        FROZEN.name(ch)
        answer = "(a name)"
    except ValueError:
        answer = "ValueError"
    print("   %-11s %-9s %-13s %s" % ("U+%04X" % cp, FROZEN.category(ch), answer, truth))
print()
print("   Four different truths and one answer. Cn means UNASSIGNED, so on the")
print("   top two rows the table is not reporting a gap in its own knowledge --")
print("   it is making a false statement about Unicode, with no hedge in it.")
print()
print("   That is the whole hazard in a line. An out-of-date table does not")
print("   fail, and it does not say it is out of date. It answers confidently")
print("   and wrongly, the way od -a invents a letter for a byte it cannot")
print("   name -- and you cannot tell the four cases apart from the answer,")
print("   because the answer is the same.")
print()

print("5. THE VERSION IS THE ONE THING THIS PROGRAM WILL NOT PRINT")
print(RULE)
v = MODERN.unidata_version
print("   unicodedata.unidata_version is a %s in three parts:   %s" % (
    type(v).__name__, len(v.split(".")) == 3))
print("   and it is newer than the frozen table:               %s" % (
    int(v.split(".")[0]) > int(FROZEN.unidata_version.split(".")[0])))
print()
print("   The value itself -- '16.0.0', '17.0.0', whatever yours says -- is")
print("   deliberately absent. Recording it would put the machine that built")
print("   this page into the answer key, and the next machine would then fail")
print("   a check about nothing. Ask your own copy instead:")
print()
print("       python3 -c 'import unicodedata; print(unicodedata.unidata_version)'")
print()

print("6. WHAT SURVIVES THE VERSION, AND WHAT DOES NOT")
print(RULE)
print("   arithmetic -- true under every version ever published:")
print("      usable scalar values, 0x110000 minus 2,048 surrogates   %d" % (0x110000 - 2048))
print()
print("   guaranteed -- Unicode promises these never change:")
print("      the name of an assigned code point   %s" % MODERN.name("é"))
print("      the code point of that character     U+%04X" % ord("é"))
print()
print("   a lookup -- true today, in this table, on this machine:")
print("      how many code points are assigned")
print("      whether U+11DB0 is one of them")
print("      whether a character is alphabetic, uppercase, whitespace")
print()
print("   The first two groups belong in a test.")
print("   The third belongs in a sentence with a date on it.")
