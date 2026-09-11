#!/usr/bin/env python3
"""Four systems for naming a character you cannot type, and one that is a standard.

You have identified a character -- from a hex dump, from `uni`, from a bug
report -- and now you have to produce one. Nothing on your keyboard makes a
`ż`. Four naming systems answer that, and they are not the same table:

  Unicode Name    LATIN SMALL LETTER Z WITH DOT ABOVE   the standard
  X11 keysym      zabovedot                             keysymdef.h's; a Compose file writes U017C
  Vim digraph     z.                                    Ctrl-K z .
  HTML entity     &zdot;                                a document, not a keyboard

Only the first is a standard with a stability guarantee, and it is the only
one Python can use directly -- which is section 4.

The Compose lines in section 2 are copied verbatim from the standard
en_US.UTF-8 Compose file (libx11-data 2:1.8.7-1build1, Ubuntu 24.04), so the
parser here is reading the real syntax, not a simplification.

Run:  python3 typing_a_character_py.py
"""

import re
import unicodedata

BAR = "-" * 72


def head(n, title):
    print("\n" + str(n) + ". " + title + "\n" + BAR)


# Measured 2026-09-07; keysym column corrected 2026-09-10. The keysym column is
# X11's keysymdef.h itself: uni 2.9.0's %(keysym) looks the keysym NUMBER up as
# though it were the code point, so it is blank for both Polish letters (see
# 11_Tools/uni_help). The HTML column is from uni 2.9.0 (Unicode 17.0), and
# the digraph column from Vim 9.1's own digraph_getlist(1), which is the
# authority for it -- uni prints "A" for U+0041 where Vim's table has no
# digraph for it at all. A "-" below means that system has no name for the
# character.
NAMED = [
    (0x0041, "A", "", "&#x41;"),
    (0x00E9, "eacute", "e'", "&eacute;"),
    (0x00A0, "nobreakspace", "NS", "&nbsp;"),
    (0x0142, "lstroke", "l/", "&lstrok;"),
    (0x017C, "zabovedot", "z.", "&zdot;"),
    (0x20AC, "EuroSign", "=e", "&euro;"),
    (0x0CA0, "", "", "&#xca0;"),
]

# Verbatim from the standard en_US.UTF-8 Compose file.
COMPOSE_LINES = """\
<dead_acute> <e>			: "é"	eacute # LATIN SMALL LETTER E WITH ACUTE
<Multi_key> <acute> <e>			: "é"	eacute # LATIN SMALL LETTER E WITH ACUTE
<Multi_key> <e> <acute>			: "é"	eacute # LATIN SMALL LETTER E WITH ACUTE
<Multi_key> <apostrophe> <e>		: "é"	eacute # LATIN SMALL LETTER E WITH ACUTE
<Multi_key> <e> <apostrophe>		: "é"	eacute # LATIN SMALL LETTER E WITH ACUTE
<Multi_key> <C> <equal>			: "€"	EuroSign # EURO SIGN
<Multi_key> <equal> <C>			: "€"	EuroSign # EURO SIGN
<Multi_key> <c> <equal>			: "€"	EuroSign # EURO SIGN
<Multi_key> <equal> <c>			: "€"	EuroSign # EURO SIGN
<Multi_key> <E> <equal>			: "€"	EuroSign # EURO SIGN
<Multi_key> <equal> <E>			: "€"	EuroSign # EURO SIGN
<Multi_key> <e> <equal>			: "€"	EuroSign # EURO SIGN
<Multi_key> <equal> <e>			: "€"	EuroSign # EURO SIGN
<Multi_key> <Cyrillic_ES> <equal>	: "€"	EuroSign # EURO SIGN
<Multi_key> <equal> <Cyrillic_ES>	: "€"	EuroSign # EURO SIGN
<Multi_key> <Cyrillic_IE> <equal>	: "€"	EuroSign # EURO SIGN
<Multi_key> <equal> <Cyrillic_IE>	: "€"	EuroSign # EURO SIGN
<dead_currency> <e>			: "€"	EuroSign # EURO SIGN
<dead_stroke> <l>			: "ł"	U0142 # LATIN SMALL LETTER L WITH STROKE
<Multi_key> <slash> <l>			: "ł"	U0142 # LATIN SMALL LETTER L WITH STROKE
<Multi_key> <l> <slash>			: "ł"	U0142 # LATIN SMALL LETTER L WITH STROKE
<Multi_key> <KP_Divide> <l>		: "ł"	U0142 # LATIN SMALL LETTER L WITH STROKE
<dead_abovedot> <z>			: "ż"	U017C # LATIN SMALL LETTER Z WITH DOT ABOVE
<Multi_key> <period> <z>		: "ż"	U017C # LATIN SMALL LETTER Z WITH DOT ABOVE
<Multi_key> <z> <period>		: "ż"	U017C # LATIN SMALL LETTER Z WITH DOT ABOVE
<Multi_key> <space> <space>		: " "	nobreakspace # NO-BREAK SPACE
<Multi_key> <o> <c>			: "©"	copyright # COPYRIGHT SIGN
<Multi_key> <O> <C>			: "©"	copyright # COPYRIGHT SIGN
<Multi_key> <C> <O>			: "©"	copyright # COPYRIGHT SIGN
<Multi_key> <minus> <minus> <minus>	: "—"	U2014 # EM DASH
"""

SEQ = re.compile(r'^((?:<[^>]+>\s*)+):\s*"((?:[^"\\]|\\.)*)"\s*(\S*)')


def unescape(s):
    """The Compose file escapes only \\" and \\\\ inside its result string."""
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            out.append(s[i + 1])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def parse(text):
    rows = []
    for line in text.splitlines():
        m = SEQ.match(line)
        if m:
            keys = tuple(re.findall(r"<([^>]+)>", m.group(1)))
            rows.append((keys, unescape(m.group(2)), m.group(3)))
    return rows


head(1, "FOUR SYSTEMS NAME A CHARACTER, AND THEY ARE NOT ONE TABLE")
print("   " + "code point".ljust(12) + "Unicode Name".ljust(37)
      + "keysym".ljust(15) + "digraph".ljust(9) + "HTML")
for cp, keysym, digraph, html in NAMED:
    name = unicodedata.name(chr(cp), "<no Name: it is a control>")
    print("   U+" + format(cp, "04X").ljust(10) + name.ljust(37)
          + (keysym or "-").ljust(15) + (digraph or "-").ljust(9) + html)
print()
print("   Read down the two middle columns. The Polish letters have both:")
print("   X11 named them in its Latin-2 set, and a Polish keyboard layout")
print("   sends them. The Kannada letter has neither, which is what 'a script")
print("   nobody here has a keyboard for' means in practice. Only the Name")
print("   column is filled all the way down, and only the Name column is a")
print("   standard rather than one project's table.")

head(2, "A COMPOSE SEQUENCE IS A PATH, NOT A NAME")
rows = parse(COMPOSE_LINES)
print("   " + str(len(rows)) + " sequences, verbatim from the en_US.UTF-8 Compose file:")
print()
print("   " + "keys".ljust(42) + "gives".ljust(10) + "keysym")
for keys, value, keysym in rows:
    shown = " ".join(keys)
    cps = " ".join("U+" + format(ord(c), "04X") for c in value)
    print("   " + shown[:40].ljust(42) + cps.ljust(10) + keysym)
print()
euro = [k for k, v, _ in rows if v == chr(0x20AC)]
print("   The euro alone has " + str(len(euro)) + " of them in that file, and the reason is")
print("   that a compose sequence is not a name being looked up -- it is a PATH")
print("   through a tree, so the file can afford to list every path a person")
print("   might try. C= and =C and c= and =c and E= and e=, plus the Cyrillic")
print("   letters that look like C and E. Vim's table has exactly one: =e.")
print()
print("   Two rows are worth stopping on. <Multi_key> <space> <space> produces")
print("   U+00A0, so the most troublesome invisible character in this library")
print("   is two keystrokes that look exactly like typing a space twice. And")
print("   the em dash takes three keys after Multi_key, not two -- the length")
print("   is not fixed, which is what section 3 is about.")

head(3, "WHY IT NEEDS NO TERMINATOR")
seqs = {k for k, _, _ in rows}
extensions = [k for k in seqs if any(k[:i] in seqs for i in range(1, len(k)))]
lengths = sorted({len(k) for k in seqs})
print("   sequence lengths in this sample: " + str(lengths))
print("   sequences that EXTEND another complete sequence: " + str(len(extensions)))
print()
print("   That zero is the whole design. No complete sequence is a prefix of")
print("   another, so the moment the keys you have typed match a sequence, the")
print("   input method can commit -- there is no longer path it might still be")
print("   on, and you never press Enter to say you are done. It holds over the")
print("   whole file too, not just this sample; the page has the number.")
print()
print("   It is the same property that makes UTF-8 self-synchronising, one")
print("   layer up: a code that can be read left to right with no lookahead.")

head(4, "THE ONE YOUR PROGRAM CAN ACTUALLY USE")
print("   Compose needs X11. Digraphs need Vim. The Unicode Name needs")
print("   nothing at all, because it is in the standard library:")
print()
for name in ["EURO SIGN", "LATIN SMALL LETTER Z WITH DOT ABOVE",
             "NO-BREAK SPACE", "KANNADA LETTER TTHA"]:
    c = unicodedata.lookup(name)
    print("   lookup(" + repr(name) + ")")
    print("      -> U+" + format(ord(c), "04X") + "   " + repr(c))
print()
print("   And it round-trips: unicodedata.name(unicodedata.lookup(n)) == n for")
print("   every name above -> " + str(all(
    unicodedata.name(unicodedata.lookup(n)) == n
    for n in ["EURO SIGN", "LATIN SMALL LETTER Z WITH DOT ABOVE",
              "NO-BREAK SPACE", "KANNADA LETTER TTHA"])))
print()
print("   That round trip is a promise, not an observation: a character's Name")
print("   is frozen when the character is assigned and can never be changed,")
print("   typos included. Neither the keysym table nor the digraph table")
print("   promises anything of the sort. Vim has added digraphs over the")
print("   years, and uni's digraph column -- built from RFC 1345, the 1992")
print("   list those digraphs began as -- has none of the additions except")
print("   the euro sign.")

head(5, "WHATEVER YOU TYPED, THE BYTES ARE THE ANSWER")
composed = unicodedata.lookup("LATIN SMALL LETTER E WITH ACUTE")
decomposed = unicodedata.normalize("NFD", composed)
print("   two ways to end up with the same picture:")
print("      one code point   " + str(len(composed)) + "  "
      + " ".join("U+" + format(ord(c), "04X") for c in composed)
      + "        " + str(len(composed.encode())) + " bytes")
print("      two code points  " + str(len(decomposed)) + "  "
      + " ".join("U+" + format(ord(c), "04X") for c in decomposed)
      + "  " + str(len(decomposed.encode())) + " bytes")
print("      equal?           " + str(composed == decomposed))
print()
print("   A dead key, a compose sequence, a digraph and a paste from a web")
print("   page can each hand you either one, and they are the same picture at")
print("   every size. So the last step of typing a character you could not")
print("   type is checking what you actually got: `uni identify` prints one")
print("   row or two, and unicodedata.normalize settles it in a program.")
print()
print("   The Compose file can even produce the bare mark on its own --")
print("   <dead_acute> <nobreakspace> is U+0301 with nothing under it -- which")
print("   is the one route by which a hand-typed decomposed string is possible")
print("   rather than merely claimed.")
