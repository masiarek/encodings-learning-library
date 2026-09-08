#!/usr/bin/env python3
"""Python normalizes your variable names, and does it silently.

Every other page in this chapter is about text your program HANDLES. This one
is about text your program is WRITTEN IN -- and Python applies a Unicode
normalization form to it before the compiler ever sees a name, which means two
identifiers you typed differently can be one variable, and two you typed to
look identical can be two.

PEP 3131 fixed the form as NFKC in 2007, so everything below is the same on
every Python 3 there has ever been.

Run:  python3 unicode_in_identifiers_py.py
"""

import unicodedata

BAR = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


def define(source):
    """Run one assignment and report which name actually got bound."""
    ns = {}
    exec(source, ns)
    return sorted(k for k in ns if not k.startswith("__"))


# ------------------------------------------------------------------ 1
head(1, "AN IDENTIFIER DOES NOT HAVE TO BE ASCII")
żółw = 4
print(f"   żółw = 4   ->   {żółw}")
print()
print("   Legal since Python 3.0. The rule is Unicode's own, not Python's:")
print("   a name starts with an XID_Start character and continues with")
print("   XID_Continue, which is UAX #31 and is what most languages that")
print("   allow this use. The boolean comes first below because a CJK")
print("   character is two columns wide and would break the alignment:")
print()
for candidate in ("żółw", "café", "日本語", "_x", "ﬁle", "\N{MATHEMATICAL ITALIC SMALL A}", "2fast", "a-b"):
    print(f"      isidentifier() {str(candidate.isidentifier()):<6} {candidate!r}")

# ------------------------------------------------------------------ 2
head(2, "AND PYTHON NORMALIZES IT BEFORE BINDING IT")
for source, typed in (
    ("\N{MATHEMATICAL ITALIC SMALL A} = 1", "\N{MATHEMATICAL ITALIC SMALL A}"),
    ("\N{LATIN SMALL LIGATURE FI}le = 2", "\N{LATIN SMALL LIGATURE FI}le"),
    ("\N{ROMAN NUMERAL ONE} = 3", "\N{ROMAN NUMERAL ONE}"),
):
    bound = define(source)
    print(f"   typed {typed!r:<10} ({' '.join('U+%04X' % ord(c) for c in typed)})")
    print(f"      bound as {bound}")
print()
print("   Nothing you typed is what the namespace holds. The compiler")
print("   applies NFKC to every identifier, so a mathematical italic letter")
print("   becomes an ordinary one and a ligature becomes two letters --")
print("   which is NFKC -- normalization's aggressive form -- doing exactly")
print("   what it says on the tin, in a place nobody expects to find it.")

# ------------------------------------------------------------------ 3
head(3, "SO TWO SPELLINGS CAN BE ONE VARIABLE")
ns = {}
exec("\N{LATIN SMALL LIGATURE FI}le = 'assigned through the ligature'", ns)
print(f"   exec(\"ﬁle = ...\")  then  ns['file']  ->  {ns['file']!r}")
print()
exec("file = 'reassigned through ASCII'", ns)
print(f"   exec(\"file = ...\")  then  is 'ﬁle' a key?  {'\N{LATIN SMALL LIGATURE FI}le' in ns}")
print(f"                             ns['file'] ->  {ns['file']!r}")
print()
print("   One variable, two spellings, and the ligature spelling is not even")
print("   a key. A reader who greps the file for `file` finds one of the two")
print("   assignments; a reader who greps for the ligature finds the other.")

# ------------------------------------------------------------------ 4
head(4, "AND THE LOOK-ALIKE IT DOES *NOT* MERGE")
latin, cyrillic = "a", "а"
ns = {}
exec(f"{latin} = 'latin'", ns)
exec(f"{cyrillic} = 'cyrillic'", ns)
print(f"   after binding both spellings of `a`:")
print(f"      names in the namespace   {sorted(k for k in ns if not k.startswith('__'))}")
print(f"      how many                 {len([k for k in ns if not k.startswith('__')])}")
for name in (latin, cyrillic):
    print(f"      U+{ord(name):04X} {unicodedata.name(name):<28} -> {ns[name]!r}")
print()
print(f"   NFKC('а') == 'a'   {unicodedata.normalize('NFKC', cyrillic) == latin}")
print()
print("   TWO variables, rendered identically, and Python said nothing at")
print("   all. This is the same rule as the previous page: NFKC merges what")
print("   Unicode declared COMPATIBILITY-equivalent -- ligatures, italic")
print("   letters, Roman numerals -- and never merges two letters that are")
print("   merely drawn alike, because they are different letters.")
print()
print("   Put sections 3 and 4 together and the shape is uncomfortable:")
print("   normalization SURPRISES you where the characters are related, and")
print("   ABANDONS you where they are not. The first costs you an afternoon")
print("   of confusion; the second is the one that gets into a code review.")

# ------------------------------------------------------------------ 5
head(5, "WHAT THIS MEANS FOR A DIFF")
print("   Two assignments that no reviewer can tell apart:")
print()
print("       total = compute()      # ASCII a")
print("       tоtal = compute()      # U+043E CYRILLIC SMALL LETTER O")
print()
same_shape = "total", "t\N{CYRILLIC SMALL LETTER O}tal"
for name in same_shape:
    print(f"      {name!r:<10} {' '.join('U+%04X' % ord(c) for c in name)}")
print(f"      equal?   {same_shape[0] == same_shape[1]}")
print()
print("   Python will bind both, run both, and warn about neither. The")
print("   defence is not a language feature here -- it is a linter, a")
print("   pre-commit hook, or a rule that identifiers stay ASCII and the")
print("   other languages live in the strings.")

# ------------------------------------------------------------------ 6
head(6, "THE REPL SESSION THAT LOOKS LIKE A BROKEN INTERPRETER")
CYR_A = "\N{CYRILLIC SMALL LETTER A}"
ns = {}
exec("value = 3", ns)
exec(f"v{CYR_A}lue = 4", ns)
print("   Typed at a prompt, one line after another:")
print()
print("       >>> value = 3")
print("       >>> value = 4          # the `a` here is U+0430, not U+0061")
print("       >>> value")
print(f"       {ns['value']}")
print()
print("   The second assignment did not overwrite the first, so reading the")
print("   name back gives the value you set TWO lines ago. Nothing is wrong")
print("   with the interpreter and nothing was shadowed: there are two names")
print("   in the namespace and they are the same picture.")
print()
print(f"      names bound   {sorted(k for k in ns if not k.startswith('__'))!r}")
print(f"      as code points")
for name in sorted(k for k in ns if not k.startswith("__")):
    print("         %-24s %s  -> %s" % (
        " ".join("U+%04X" % ord(c) for c in name), "", ns[name]))
print()
print("   And the one-line version of the same fact, which is the thing to")
print("   reach for when a name will not resolve and the spelling looks")
print("   right:")
print()
print("       >>> ord('a')")
print("       %d" % ord("a"))
print("       >>> ord('a')          # pasted from somewhere else")
print("       %d" % ord(CYR_A))
print()
print("   97 is U+0061 %s." % unicodedata.name("a"))
print("   1072 is U+0430 %s." % unicodedata.name(CYR_A))
print("   ord() is the whole diagnosis, and it fits on one line.")

head(7, "AND THE CHARACTERS THAT CANNOT GET IN AT ALL")
print("   The letter that slips through is an ORDINARY, ASSIGNED, VISIBLE")
print("   one. The reserved code points are refused at the door:")
print()
print("   code point  %-44s %-15s %s" % ("what it is", "isidentifier()", "exec"))
for cp, label in [
    (0x0430, "CYRILLIC SMALL LETTER A -- a real letter"),
    (0x00E9, "LATIN SMALL LETTER E WITH ACUTE"),
    (0xE000, "a private-use code point"),
    (0xFFFE, "a noncharacter"),
    (0x0378, "unassigned -- may be a letter one day"),
]:
    name = "val" + chr(cp) + "ue"
    try:
        exec(name + " = 1", {})
        verdict = "bound"
    except SyntaxError:
        verdict = "SyntaxError"
    print("   U+%-9s %-44s %-15s %s" % (
        "%04X" % cp, label, name.isidentifier(), verdict))
print()
print("   Python rejects the last three with the same message -- `invalid")
print("   non-printable character` -- because none of them carries")
print("   XID_Continue, and a code point with no properties cannot be part")
print("   of a name. Which is the reassuring half and also the point: the")
print("   dangerous character in an identifier is never the exotic one. It")
print("   is a real letter from a real alphabet that happens to be drawn")
print("   the same as yours.")
