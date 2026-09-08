#!/usr/bin/env python3
"""PRECIS: the framework that replaced stringprep, and inverted its question.

stringprep (RFC 3454) lists what is FORBIDDEN, in tables pinned to Unicode 3.2.
PRECIS (RFC 8264) derives what is ALLOWED from Unicode properties, so it never
has to be reissued when the standard grows. Both decisions have a price, and
this program is about what each one bought.

The two profiles that matter are both in RFC 8265, and they are for two things
people wrongly assume are the same kind of string:

    UsernameCaseMapped   a login name   -- fold it hard, so two people cannot
                                          register names nobody can tell apart
    OpaqueString         a password     -- touch it as little as possible, and
                                          NEVER fold case

Run:  python3 precis_after_stringprep_py.py
"""

import unicodedata

# ----------------------------------------------------------------------
# One transcribed table, and it is the honest half of this program.
#
# PRECIS's `Additional Mapping Rule` for passwords maps every non-ASCII SPACE
# to U+0020, and `space` there means the Unicode general category Zs. Asking
# this interpreter for that category would put its Unicode version into the
# answer key -- and section 5 is about what happens when it does. So the list
# is written down here, from the modern table, and section 5 shows the cost of
# writing one down.
# ----------------------------------------------------------------------
NON_ASCII_SPACES = (
    "\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006"
    "\u2007\u2008\u2009\u200a\u202f\u205f\u3000"
)

# And the same reasoning one step further. IdentifierClass admits a character
# if it is a letter or a digit, which is a question about its general category
# -- the lookup this library will not put in an answer key. So the categories
# of exactly the characters this page uses are transcribed here. Anything not
# on the list is refused rather than guessed at, which keeps the program from
# quietly accepting a character nobody checked.
CATEGORY = {
    **{c: "Ll" for c in "abcdefghijklmnopqrstuvwxyz"},
    **{c: "Lu" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
    **{c: "Nd" for c in "0123456789"},
    "\u00df": "Ll", "\u00e9": "Ll", "\u017c": "Ll", "\uff41": "Ll",   # U+00DF U+00E9 U+017C U+FF41
    "\u0301": "Mn",                                # COMBINING ACUTE ACCENT
    " ": "Zs",                                     # U+0020 SPACE
    "\u00a0": "Zs",                                # NO-BREAK SPACE
    "\u200b": "Cf",                                # ZERO WIDTH SPACE -- section 5
    "\U0001F511": "So",                           # KEY: a symbol, not a letter
    "-": "Pd", "_": "Pc", "!": "Po",
}

LETTERS_DIGITS = {"Ll", "Lu", "Lo", "Lt", "Lm", "Nd"}


class Disallowed(Exception):
    """A profile returns a string or an error, never both."""


class Untranscribed(Exception):
    """This program was asked about a character its table does not cover."""


def category(c: str) -> str:
    try:
        return CATEGORY[c]
    except KeyError:
        raise Untranscribed(f"U+{ord(c):04X} is not in this program's table") from None


# ---------------------------------------------------------------- the rules
def width_map(s: str) -> str:
    """Rule 1: fullwidth and halfwidth forms become their plain equivalents."""
    out = []
    for c in s:
        d = unicodedata.decomposition(c)
        if d.startswith("<wide>") or d.startswith("<narrow>"):
            out.append(chr(int(d.split()[1], 16)))
        else:
            out.append(c)
    return "".join(out)


def map_spaces(s: str) -> str:
    """Rule 2, for OpaqueString only: any non-ASCII space becomes U+0020."""
    return "".join(" " if c in NON_ASCII_SPACES else c for c in s)


def username_case_mapped(s: str) -> str:
    """RFC 8265 section 3.3 -- the five rules, in the order the RFC fixes."""
    s = width_map(s)                              # 1. width mapping
    #                                               2. additional mapping: none
    s = s.casefold()                              # 3. case mapping: casefold
    s = unicodedata.normalize("NFC", s)           # 4. normalization: NFC
    #                                               5. directionality: Bidi Rule
    for c in s:                                   # and then the CLASS check
        if category(c) not in LETTERS_DIGITS:
            raise Disallowed(f"IdentifierClass: U+{ord(c):04X} is {category(c)}")
    return s


def opaque_string(s: str) -> str:
    """RFC 8265 section 4.2 -- the same five slots, four of them different."""
    #                                               1. width mapping: NONE
    s = map_spaces(s)                             # 2. additional: Zs -> U+0020
    #                                               3. case mapping: NONE
    s = unicodedata.normalize("NFC", s)           # 4. normalization: NFC
    #                                               5. directionality: NONE
    if s == "":
        raise Disallowed("FreeformClass: an empty password is not a password")
    for c in s:                                   # FreeformClass: much wider
        if category(c).startswith("C") and c not in " ":
            raise Disallowed(f"FreeformClass: U+{ord(c):04X} is {category(c)}")
    return s


def run(fn, s: str) -> str:
    try:
        return repr(fn(s))
    except (Disallowed, Untranscribed) as e:
        return f"error: {e}"


def cps(s: str) -> str:
    if len(s) > 12:
        return f"({len(s)} code points)"
    return " ".join(f"{ord(c):04X}" for c in s)


def rule(title: str) -> None:
    print(title)
    print("-" * 72)


def main() -> None:
    # ------------------------------------------------------------------
    rule("1. THE INVERSION")
    print("   stringprep, 2002:  here are the tables of what is FORBIDDEN")
    print("   PRECIS,     2015:  here is how to DERIVE what is allowed")
    print()
    print("   The consequence is a maintenance one, and it is the whole reason")
    print("   the framework was replaced. A list of the forbidden has to be")
    print("   reissued every time Unicode grows; a derivation does not. RFC 3454")
    print("   was obsoleted by 7564, obsoleted by 8264, in thirteen years.")
    print()
    print("   PRECIS defines two string classes, and the difference is not")
    print("   severity -- it is what the string is FOR:")
    print()
    print("     IdentifierClass  letters and digits, and almost nothing else.")
    print("                      NO spaces. For things that get compared.")
    print("     FreeformClass    letters, digits, spaces, punctuation, symbols,")
    print("                      emoji. For things a person composes.")
    print()

    # ------------------------------------------------------------------
    rule("2. UsernameCaseMapped -- FOLD IT HARD")
    print("   Five rules, and RFC 8264 fixes the order:")
    print("     1 width mapping   2 additional mapping   3 case mapping")
    print("     4 normalization   5 directionality")
    print()
    print(f"   {'input':<20} {'prepared':<16} code points")
    for s in ["Straße", "STRASSE", "ａdmin", "ADMIN", "café", "cafe\u0301",
              "Ada Lovelace", "🔑🔑🔑"]:
        got = run(username_case_mapped, s)
        try:
            out = cps(username_case_mapped(s))
        except (Disallowed, Untranscribed):
            out = ""
        print(f"   {s!r:<20} {got:<16} {out}".rstrip())
    print()
    print("   Rows 1 and 2 land on the same prepared string, because casefold")
    print("   turns sharp s into two esses. So `Straße` and `STRASSE` are ONE")
    print("   username, and the second person to arrive is told the name is")
    print("   taken. RFC 8265 knows this and accepts it: two names nobody can")
    print("   tell apart must not both be registrable.")
    print()
    print("   Rows 5 and 6 are the same word typed two ways -- one composed,")
    print("   one with a combining acute. NFC reconciles them, which is rule 4")
    print("   doing the only job it has.")
    print()
    print("   Rows 7 and 8 are the CLASS, not the rules. A space is not a")
    print("   letter or a digit and neither is a key emoji, so IdentifierClass")
    print("   refuses both -- and a profile returns a string or an error, never")
    print("   both. Note that nothing was silently dropped: PRECIS does not")
    print("   sanitise a username, it declines to have one.")
    print()

    # ------------------------------------------------------------------
    rule("3. OpaqueString -- TOUCH IT AS LITTLE AS POSSIBLE")
    print(f"   {'input':<26} {'prepared':<26} code points")
    for s in ["paßwort", "PAßWORT", "correct horse battery staple",
              "my\u00a0password", "cafe\u0301", "ａdmin", "🔑🔑🔑",
              "pass\u200bword"]:
        got = run(opaque_string, s)
        try:
            out = cps(opaque_string(s))
        except (Disallowed, Untranscribed):
            out = ""
        print(f"   {s!r:<26} {got:<26} {out}".rstrip())
    print()
    print("   Four differences from the profile above, and every one of them is")
    print("   a decision about what a password IS:")
    print()
    print("     no case mapping   rows 1 and 2 stay two different passwords.")
    print("                       Folding case would shrink the keyspace, and")
    print("                       hand an attacker collisions for free.")
    print("     spaces allowed    row 3 is a passphrase. FreeformClass exists")
    print("                       so that four words can be a password.")
    print("     spaces MAPPED     row 4 was typed with a NO-BREAK SPACE, and")
    print("                       comes out with an ordinary one -- so a user")
    print("                       whose keyboard or phone inserted U+00A0 can")
    print("                       still log in tomorrow from a machine that")
    print("                       inserts U+0020.")
    print("     no width mapping  row 6's fullwidth `a` is NOT folded to `a`.")
    print("                       The username profile folds it; the password")
    print("                       profile keeps every bit the user typed.")
    print()
    print("   Rows 7 and 8 are the class doing its job in both directions. A")
    print("   password may be three key emoji, because FreeformClass admits")
    print("   symbols -- and may NOT contain a ZERO WIDTH SPACE, because that")
    print("   is a format character, and a password with an invisible character")
    print("   in it is one the user can never retype. Section 5 is about how")
    print("   close those two verdicts are to each other.")
    print()
    print("   Row 5 shows the one rule both profiles share, and it is the one")
    print("   with no free option. NFC is applied to passwords too -- because")
    print("   the alternative is a password that works on the keyboard it was")
    print("   set on and silently never works anywhere else.")
    print()

    # ------------------------------------------------------------------
    rule("4. THE SAME STRING, THROUGH BOTH")
    print(f"   {'input':<32} {'as a username':<24} {'as a password'}")
    for s in ["Straße", "ａdmin", "correct horse battery staple", "cafe\u0301", "🔑🔑🔑"]:
        u = run(username_case_mapped, s)
        u = "error: IdentifierClass" if u.startswith("error:") else u
        print(f"   {s!r:<32} {u:<24} {run(opaque_string, s)}".rstrip())
    print()
    print("   One framework, one document, two answers per row. `Preparing a")
    print("   string` made the case that preparation is a policy question; this")
    print("   is that argument with the policies written out side by side.")
    print()

    # ------------------------------------------------------------------
    rule("5. WHAT PRECIS TOOK BACK WHEN IT UNPINNED THE TABLE")
    print("   stringprep froze Unicode 3.2 so a registered name could never")
    print("   change meaning. The cost was that it can never accept a character")
    print("   invented after 2002. PRECIS derives from the LIVE table instead,")
    print("   so it grows -- and inherits the problem the freeze was there to")
    print("   solve. A property PRECIS reads can move.")
    print()
    print("   Here is one that did, and Python ships both tables to prove it:")
    zwsp = "\u200b"
    frozen = unicodedata.ucd_3_2_0
    print()
    print(f"   U+200B ZERO WIDTH SPACE")
    print(f"     general category in the frozen 2002 table:  {frozen.category(zwsp)!r}")
    print()
    print("   `Zs` is the category PRECIS's Additional Mapping Rule means by")
    print("   `space`. Read under a 2002 table, a ZERO WIDTH SPACE in a password")
    print("   IS a space and gets MAPPED to U+0020. It has since been")
    print("   reclassified as a format character, so a modern table puts it in")
    print("   `Cf` and PRECIS DISALLOWS it instead -- which is the verdict the")
    print("   last row of section 3 printed.")
    print()
    print("   This program can prove the two endpoints and deliberately does not")
    print("   name the version in between: the frozen table is shipped and so is")
    print("   printable, and the release that moved the character is a fact this")
    print("   program has no way to check.")
    print()
    print("   Same character, same rule, same RFC: mapped on one machine and")
    print("   refused on another, decided by nothing but which Unicode the")
    print("   implementation was built against.")
    print()
    print("   This program does not print what YOUR table says, because that")
    print("   would be a fact about your machine rather than about text -- and")
    print("   the frozen answer above is printable precisely because it is")
    print("   frozen. Run it yourself:")
    print()
    print("     python3 -c \"import unicodedata as u; print(u.category('\\u200b'))\"")
    print()
    print("   That is the honest shape of the trade, and neither side of it is")
    print("   a mistake. stringprep bought determinism with a permanent freeze:")
    print("   a name registered in 2003 means the same thing forever, and no")
    print("   character invented since may ever be registered. PRECIS bought")
    print("   growth with a version number -- your users can have the alphabet")
    print("   they actually write in, and `is this string allowed` is now a")
    print("   question about which Unicode your server was built against.")


if __name__ == "__main__":
    main()
