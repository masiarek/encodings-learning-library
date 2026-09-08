#!/usr/bin/env python3
"""One string per behaviour: the corpus a text field should be tested against.

A hostile corpus is usually a pile -- a thousand strings, no organising idea,
and no way to tell whether the pile covers anything. This one is organised the
other way round: every entry is here because it breaks ONE assumption a
programmer holds, and the columns say which check catches it.

Everything printed below is either a code point, a character NAME, arithmetic
over a list written into this file, or the result of a NORMALIZATION -- and
Unicode's stability policies freeze the first two and the third for every
character already assigned. That is why these may be an answer key, where a
count of assigned code points may not.

Run:  python3 hard_strings_py.py
"""

import unicodedata as ud

BAR = "-" * 72


def cps(s):
    """A string as its code points, which is the only unambiguous picture."""
    return " ".join(f"{ord(c):04X}" for c in s)


def head(n, title):
    print(f"{n}. {title}")
    print(BAR)


def mark(flag):
    return "=" if flag else "-"


def nfkc_cf(s):
    """The caseless match a username field should be doing: fold, then fold again."""
    return ud.normalize("NFKC", ud.normalize("NFKC", s).casefold())


# ---------------------------------------------------------------- 1

head(1, "FOUR SPELLINGS OF ONE WORD, AND WHY THERE ARE EXACTLY FOUR")
SPELLINGS = [
    ("A", "r\u00e9sum\u00e9"),
    ("B", "r\u00e9sume\u0301"),
    ("C", "re\u0301sum\u00e9"),
    ("D", "re\u0301sume\u0301"),
]
print("   To a reader these are one word, four times. To Python they are four")
print("   different values, and nothing about the picture says which you have.")
print()
print(f"      {'':3} {'chars':>5} {'bytes':>5}   code points")
for label, s in SPELLINGS:
    print(f"      {label:3} {len(s):5} {len(s.encode()):5}   {cps(s)}")
print()
print("   The count is not a curiosity, it is arithmetic. Each accented letter")
print("   can be written one way or two, the choices are independent, so a word")
print("   with k of them has 2**k spellings -- all of which normalize to one:")
print()
print(f"      distinct values          {len({s for _, s in SPELLINGS})}")
print(f"      distinct after NFC       {len({ud.normalize('NFC', s) for _, s in SPELLINGS})}")
print(f"      distinct after NFD       {len({ud.normalize('NFD', s) for _, s in SPELLINGS})}")
print()
PANGRAM = "zażółć gęślą jaźń"
k = sum(1 for c in PANGRAM if ud.decomposition(c) and not ud.decomposition(c).startswith("<"))
print(f"      the library's Polish pangram, {len(PANGRAM)} characters, has {k} of them")
print(f"      so it has 2**{k} = {2 ** k} spellings, every one of them correct")
print()
print("   A dictionary keyed on a name therefore has as many slots for that")
print("   name as the name has accents, and the user gets a different one")
print("   depending on which keyboard, phone or paste they arrived through.")
print()

# ---------------------------------------------------------------- 2

head(2, "ONE PICTURE, MANY VALUES -- AND THE CHECK THAT MERGES EACH PAIR")
PAIRS = [
    ("caf\u00e9", "cafe\u0301", "composed against decomposed"),
    ("Å", "\u212b", "ANGSTROM SIGN against A WITH RING"),
    ("Ω", "\u2126", "OHM SIGN against GREEK CAPITAL OMEGA"),
    ("q\u0307\u0323", "q\u0323\u0307", "two marks, written in two orders"),
    ("ﬁle", "file", "the fi ligature"),
    ("½", "1\u20442", "a vulgar fraction"),
    ("10²", "102", "a superscript two"),
    ("ＡＢ", "AB", "fullwidth forms"),
    ("Ⅸ", "IX", "a Roman numeral"),
    ("straße", "STRASSE", "the German sharp s"),
    ("Σ", "ς", "Greek final sigma"),
    ("\u212a", "k", "KELVIN SIGN against the letter k"),
    ("I", "\u0131", "Turkish dotless i"),
    ("a", "\u0430", "Cyrillic a"),
    ("admin", "ad\u200bmin", "a zero-width space"),
    ("admin", "ad\u00admin", "a soft hyphen"),
]
CHECKS = [
    ("==", lambda a, b: a == b),
    ("NFC", lambda a, b: ud.normalize("NFC", a) == ud.normalize("NFC", b)),
    ("NFD", lambda a, b: ud.normalize("NFD", a) == ud.normalize("NFD", b)),
    ("NFKC", lambda a, b: ud.normalize("NFKC", a) == ud.normalize("NFKC", b)),
    ("cf", lambda a, b: a.casefold() == b.casefold()),
    ("cf+K", lambda a, b: nfkc_cf(a) == nfkc_cf(b)),
]
print(f"   {len(PAIRS)} pairs. Every one of them draws the same, or close enough that")
print("   no reader will query it, and every one is two different values. A '='")
print("   means that check calls them equal; a '-' means it does not.")
print()
header = "".join(f"{name:>5}" for name, _ in CHECKS)
print(f"      {'left':<20} {'right':<20}{header}   what it is")
merged = [0] * len(CHECKS)
for left, right, note in PAIRS:
    row = ""
    for i, (_, check) in enumerate(CHECKS):
        got = check(left, right)
        merged[i] += got
        row += f"{mark(got):>5}"
    print(f"      {ascii(left):<20} {ascii(right):<20}{row}   {note}")
print(f"      {'':<20} {'merged, of ' + str(len(PAIRS)):<20}"
      + "".join(f"{n:>5}" for n in merged))
print()
print("   Read it column by column and the checks separate into jobs.")
print()
print("   NFC and NFD merge the same four rows and no others, because they are")
print("   the CANONICAL forms: they merge spellings of one character and refuse")
print("   to merge anything else. Note row 4 -- two combining marks in two")
print("   orders -- which is not about composing at all. Canonical ordering")
print("   sorts marks by combining class, so both forms fix it and == does not.")
print()
print("   NFKC merges five more, and every one of those five is a DIFFERENT")
print("   character being flattened onto a letter it merely resembles. That is")
print("   why 10**2 becomes 102: the compatibility forms are a lossy fold, and")
print("   the loss is the point of them.")
print()
print("   The casefold() column is the surprise, and it is why it is worth")
print("   printing rather than reasoning about. It merges six, and only three")
print("   of those six are about letter case. Full case folding also folds the")
print("   ANGSTROM SIGN onto a-ring and the fi ligature onto two letters, so it")
print("   is not a pure case operation and never was -- it is the fold that")
print("   makes two strings the same KEY, whatever made them differ.")
print()
print("   Only the last column -- fold, casefold, fold again -- gets every")
print("   family at once, which is what an identifier comparison needs.")
print()
print("   And the last four rows are merged by nothing here, which is the")
print("   important part of the table. Two of them are two genuinely different")
print("   letters that history drew alike; two are a character you cannot see")
print("   at all. No normalization form will ever touch either kind, because")
print("   neither is a spelling of the other.")
print()

# ---------------------------------------------------------------- 3

head(3, "CASE MAPPING IS NOT A FOLD -- IT CHANGES LENGTH, IN BOTH DIRECTIONS")
CASED = ["ß", "ﬁ", "İ", "ẞ", "ǈ"]
print(f"      {'char':<10} {'upper()':<12} {'lower()':<12} {'casefold()':<12} name")
for c in CASED:
    print(f"      {ascii(c):<10} {ascii(c.upper()):<12} {ascii(c.lower()):<12} "
          f"{ascii(c.casefold()):<12} {ud.name(c)}")
print()
print("   Five things in that table are worth saying out loud.")
print()
print("   One character can uppercase to two, so upper() is not a per-character")
print("   substitution and a fixed-width column can overflow on a name it")
print("   accepted yesterday. LATIN CAPITAL LETTER I WITH DOT ABOVE does it in")
print("   the other direction: it LOWERCASES to two characters.")
print()
print("   Row four is the reason row one is not a typo. A capital sharp s does")
print("   exist, and it lowercases to the small one -- but upper() does not")
print("   produce it, because the two-letter answer is the one German readers")
print("   expect. So the pair is asymmetric on purpose.")
print()
print("   Case conversion does not round-trip, and each of the two fails in a")
print("   different direction -- which is why one example would have misled:")
print()
print(f"      {'char':<10} {'upper().lower()':<18} {'lower()':<14} agree?")
for c in ("ß", "İ"):
    print(f"      {ascii(c):<10} {ascii(c.upper().lower()):<18} {ascii(c.lower()):<14} "
          f"{c.upper().lower() == c.lower()}")
print()
print(f"      {'char':<10} {'lower().upper()':<18} {'upper()':<14} agree?")
for c in ("ß", "İ"):
    print(f"      {ascii(c):<10} {ascii(c.lower().upper()):<18} {ascii(c.upper()):<14} "
          f"{c.lower().upper() == c.upper()}")
print()
print("   And lower() is not casefold(). lower() is for display -- it answers")
print("   'how is this written in lower case'. casefold() is for comparison and")
print("   answers 'what do I hash', which is why it may produce a string nobody")
print("   would ever write, and why it is the one to compare with.")
print()
print("   The fifth row is the one people do not know is there: a TITLECASE")
print("   character, distinct from both its upper and its lower form, so the")
print("   mapping is three-way rather than two-way.")
print()
print("   What Python cannot show you here is the locale. str.upper() is")
print("   locale-independent by design, so 'i'.upper() is 'I' on every machine")
print("   in the world. Java, C#, ICU and a database collation are not, and in")
print("   a Turkish locale that same call returns a NON-ASCII character. The")
print("   page has the measurement; the point for the corpus is that the row")
print("   exists and this program is the wrong tool to find it with.")
print()

# ---------------------------------------------------------------- 4

head(4, "THE ONES YOU CANNOT SEE, AND WHICH OF THEM strip() TAKES")
INVISIBLE = [
    " ", "\u00a0", "\u3000", "\u2007",
    "\u200b", "\u200c", "\u200d", "\u00ad", "\u2060", "\ufeff",
]
print(f"      {'code point':<12} {'cat':<5} {'isspace':<9} {'stripped':<10} name")
for c in INVISIBLE:
    stripped = ("x" + c).strip() == "x"
    print(f"      U+{ord(c):04X}       {ud.category(c):<5} {str(c.isspace()):<9} "
          f"{('yes' if stripped else 'NO'):<10} {ud.name(c)}")
print()
print("   The break is between the two blocks and it is not where the eye puts")
print("   it. The first four are spaces: Unicode calls them whitespace, strip()")
print("   removes them, and a trimmed field is trimmed. The last six are format")
print("   characters -- Cf -- and every one of them is invisible, is not")
print("   whitespace to Python, and survives every trim in the standard library.")
print()
CLEAN, DIRTY = "admin", "ad\u200bmin"
print(f"      {ascii(CLEAN):<12} {ascii(DIRTY):<16} equal? {CLEAN == DIRTY}")
print(f"      len {len(CLEAN):<8} len {len(DIRTY):<12} and it is not the len that gets read")
print(f"      after strip()  {ascii(DIRTY.strip())}")
print(f"      after NFKC     {ascii(ud.normalize('NFKC', DIRTY))}")
print()
print("   Two usernames, one picture, one of them still there after every")
print("   cleaning step in the standard library. The fix is not a normalization")
print("   form; it is a rule that says which categories a name may contain.")
print()

# ---------------------------------------------------------------- 5

head(5, "NORMALIZATION THROWS THINGS AWAY, AND NFC DOES IT TOO")
LOSSY = [
    ("10²", "an exponent becomes a digit"),
    ("½", "a fraction becomes three characters"),
    ("Ⅸ", "a numeral becomes two letters"),
    ("㍿", "one character becomes four"),
]
print(f"      {'before':<14} {'NFKC after':<28} {'chars':<10} what was lost")
for s, note in LOSSY:
    after = ud.normalize("NFKC", s)
    print(f"      {ascii(s):<14} {ascii(after):<28} {len(s)} -> {len(after):<5} {note}")
print()
CHAMPION = "ﷺ"
print("   The champion expansion is an Arabic ligature this library does not")
print("   print, because a right-to-left character would reorder the row it")
print("   sits in and no page here teaches bidi. Its name and its numbers are")
print("   safe to give:")
print()
print(f"      U+FDFA   {ud.name(CHAMPION)}")
print(f"               NFKC turns {len(CHAMPION)} character into "
      f"{len(ud.normalize('NFKC', CHAMPION))}")
print()
print("   NFKC being lossy is well known. This is the one that is not:")
print()
COMPAT_HAN = "\ufa10"
print(f"      {ascii(COMPAT_HAN)}   {ud.name(COMPAT_HAN)}")
print(f"      NFC  -> {ascii(ud.normalize('NFC', COMPAT_HAN))}   "
      f"{ud.name(ud.normalize('NFC', COMPAT_HAN))}")
print()
print("   NFC -- the safe one, the one everybody recommends storing -- replaces")
print("   that character with a different one. It is a CJK compatibility")
print("   ideograph, and several of them are in Japanese personal names, which")
print("   is why 'just normalize on the way in' is a decision about somebody's")
print("   name and not a tidy-up.")
print()
print("   And normalizing the pieces is not normalizing the whole:")
print()
LEFT, RIGHT = "e", "\u0301"
joined = ud.normalize("NFC", LEFT) + ud.normalize("NFC", RIGHT)
whole = ud.normalize("NFC", LEFT + RIGHT)
print(f"      NFC({ascii(LEFT)}) + NFC({ascii(RIGHT)})   {ascii(joined):<12} {len(joined)} chars")
print(f"      NFC({ascii(LEFT)} + {ascii(RIGHT)})     {ascii(whole):<12} {len(whole)} chars")
print(f"      equal? {joined == whole}")
print()
print("   So a template that normalizes each field and then concatenates has")
print("   not produced normalized output, and a stream normalized chunk by")
print("   chunk is normalized nowhere except inside the chunks.")
print()

# ---------------------------------------------------------------- 6

head(6, "THE STRING YOUR ENCODER WILL REFUSE")
LONE = "\ud800"
print(f"      {ascii(LONE)}   len {len(LONE)}   {ud.category(LONE)}   a lone surrogate, in a str, legally")
try:
    LONE.encode()
except Exception as exc:
    print(f"      .encode()                 raises {type(exc).__name__}")
print(f"      .encode(errors='surrogatepass')  {LONE.encode('utf-8', 'surrogatepass').hex()}")
print()
print("   Python's str is a sequence of code points, and a surrogate is a code")
print("   point -- so it goes in, and only the encoder objects. That is the")
print("   shape of the whole family: the value is legal in memory, legal in")
print("   JSON, and not encodable, so it fails at the boundary rather than at")
print("   the assignment. Test the boundary, not the constructor.")
print()

# ---------------------------------------------------------------- 7

head(7, "THE CORPUS, AS ESCAPES YOU CAN PASTE")
print("   Every entry above, written the only way that survives a copy through")
print("   an editor, a ticket and a chat window. A bare combining mark or a")
print("   zero-width space does not.")
print()
CORPUS = [
    ("nfc_nfd", "cafe\u0301"),
    ("mark_order", "q\u0323\u0307"),
    ("singleton", "\u212b"),
    ("ligature", "ﬁle"),
    ("superscript", "10²"),
    ("fullwidth", "ＡＢ"),
    ("sharp_s", "straße"),
    ("final_sigma", "ς"),
    ("kelvin", "\u212a"),
    ("dotless_i", "\u0131"),
    ("dotted_I", "İ"),
    ("confusable", "\u0430"),
    ("zero_width", "ad\u200bmin"),
    ("soft_hyphen", "ad\u00admin"),
    ("nbsp", "a\u00a0b"),
    ("bom_inside", "a\ufeffb"),
    ("compat_han", "\ufa10"),
    ("expanding", "㍿"),
    ("lone_surrogate", "\ud800"),
]
for name, s in CORPUS:
    print(f"      {name:<16} = {ascii(s)}")
print()
print(f"   {len(CORPUS)} strings, one per behaviour. That is the whole list -- not")
print("   because nothing else is strange, but because everything else strange")
print(f"   is one of these {len(CORPUS)} wearing a different alphabet.")
