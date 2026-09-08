#!/usr/bin/env python3
"""Case mapping is a function on STRINGS, not a table of one character per character.

Three separate things break the one-in-one-out assumption, and they break it in
three different ways:

    LENGTH    'ß'.upper() is 'SS'   -- one character in, two out
    POSITION  'Σ'.lower() depends on what is on either side of it
    LOCALE    'i'.upper() is 'I' -- unless the text is Turkish, and Python
              will not ask

Run:  python3 case_is_not_per_character_py.py
"""

import re
import unicodedata


def cps(s: str) -> str:
    """The code points of a string, so a glyph cannot hide a difference."""
    return " ".join(f"{ord(c):04X}" for c in s)


def rule(title: str) -> None:
    print(title)
    print("-" * 72)


def main() -> None:
    # ------------------------------------------------------------------
    rule("1. LENGTH: ONE CHARACTER IN, TWO CHARACTERS OUT")
    sharp = "ß"  # LATIN SMALL LETTER SHARP S -- the cast's case specialist
    print(f"   {sharp!r}  {unicodedata.name(sharp)}")
    print()
    print(f"   {'operation':<22} {'result':<10} {'chars':>5} {'bytes':>6}  code points")
    for label, value in [
        ("the character", sharp),
        (".upper()", sharp.upper()),
        (".casefold()", sharp.casefold()),
        (".capitalize()", sharp.capitalize()),
        (".title()", sharp.title()),
    ]:
        print(f"   {label:<22} {value!r:<10} {len(value):>5} "
              f"{len(value.encode()):>6}  {cps(value)}")
    print()
    print("   So a buffer sized for the input is too small for the output, and")
    print("   `for c in s: out.append(c.upper())` is not a mistake a type system")
    print("   catches -- it type-checks, and it is wrong for German.")
    print()
    print("   And it does not come back:")
    print(f"     {sharp!r}.upper().lower() -> {sharp.upper().lower()!r}   "
          f"same as the input? {sharp.upper().lower() == sharp}")
    print("   Case mapping is not invertible. There was one sharp s and there")
    print("   are now two esses, and nothing records which esses used to be one.")
    print()

    # ------------------------------------------------------------------
    rule("2. POSITION: THE SAME CHARACTER, TWO LOWERCASE FORMS")
    print("   Greek sigma is written differently at the end of a word:")
    print(f"     U+03A3 {unicodedata.name(chr(0x03A3))}")
    print(f"     U+03C3 {unicodedata.name(chr(0x03C3))}")
    print(f"     U+03C2 {unicodedata.name(chr(0x03C2))}")
    print()
    print("   One uppercase letter, so `.lower()` has to decide by looking around it.")
    print()
    print(f"   {'input':<14} {'lower()':<14} {'final form?':<12} why")
    for text, why in [
        ("ΟΔΟΣ", "at the end of a word"),
        ("ΟΔΟΣ Μ", "before a space: still the end"),
        ("ΟΔΟΣ.", "before a full stop: still the end"),
        ("ΟΔΟΣΑ", "a letter follows, so NOT the end"),
        ("Σ", "nothing precedes it, so not a final anything"),
        ("ΑΣ", "one letter is enough to make it final"),
    ]:
        low = text.lower()
        mark = "yes  U+03C2" if "ς" in low else "no   U+03C3"
        print(f"   {text!r:<14} {low!r:<14} {mark:<12} {why}")
    print()
    print("   Read row 4 against row 1. The sigma is the same character in the")
    print("   same word; one letter after it changes what it lowercases to. No")
    print("   per-character table can express that, because the answer is not a")
    print("   property of the character.")
    print()

    # ------------------------------------------------------------------
    rule("3. AND THE TWO OPERATIONS DISAGREE ON PURPOSE")
    word = "ΟΔΟΣ"
    print(f"   {word!r:<10} .lower()    -> {word.lower()!r:<10} {cps(word.lower())}")
    print(f"   {word!r:<10} .casefold() -> {word.casefold()!r:<10} {cps(word.casefold())}")
    print()
    print("   .lower() gives the FINAL sigma; .casefold() gives the plain one.")
    print("   That is not an inconsistency, it is the two jobs:")
    print()
    print("     .lower()    is for text a person will READ -- keep the")
    print("                 distinction Greek spelling makes")
    print("     .casefold() is for text a program will COMPARE -- destroy every")
    print("                 distinction that must not separate two equal strings")
    print()
    print("   The proof that they are different questions:")
    a, b = "οδος", "οδοσ"
    print(f"     {a!r} == {b!r}                     -> {a == b}")
    print(f"     {a!r}.casefold() == {b!r}.casefold() -> {a.casefold() == b.casefold()}")
    print("   Two spellings of one Greek word. Only one of the two questions")
    print("   answers `the same word` -- and it is not the one called `lower`.")
    print()
    print("   And a third function answers a third way. A regex told to ignore")
    print("   case compares ONE character with ONE character, so the length axis")
    print("   from section 1 is invisible to it:")
    for pat, s in (("ß", "SS"), ("SS", "ß")):
        hit = re.fullmatch(pat, s, re.IGNORECASE) is not None
        print(f"     {f're.fullmatch({pat!r}, {s!r}, re.IGNORECASE)':<40} -> {hit}")
    print(f"     {repr('ß') + '.casefold() == ' + repr('SS') + '.casefold()':<40} -> "
          f"{'ß'.casefold() == 'SS'.casefold()}")
    print("   casefold() calls them equal and the matcher cannot, in either")
    print("   direction: a comparison made one character at a time has no way")
    print("   to say that one character equals two.")
    print()

    # ------------------------------------------------------------------
    rule("4. LOCALE: THE ANSWER DEPENDS ON A LANGUAGE PYTHON NEVER ASKED FOR")
    print("   Turkish has two i's, and they case in pairs that cross the")
    print("   Latin ones:")
    print()
    print(f"   {'char':<6} {'code pt':<9} {'name':<40} {'upper()':<10} lower()")
    for ch in "iIİı":
        print(f"   {ch!r:<6} U+{ord(ch):04X}    {unicodedata.name(ch):<40} "
              f"{ch.upper()!r:<10} {ch.lower()!r}")
    print()
    print("   In Turkish, `i` uppercases to U+0130 (dotted) and `I` lowercases")
    print("   to U+0131 (dotless). The table above does neither. Python's answer")
    print("   is the language-neutral one, and it is wrong for Turkish text --")
    print("   correctly wrong, because it was never told the text was Turkish.")
    print()
    print("   That refusal is total, and it is the design. `str.upper()` reads")
    print("   no environment variable, and setting one changes nothing:")
    print()
    print("     LC_ALL=tr_TR.UTF-8 python3 -c \"print('i'.upper())\"   ->  'I'")
    print()
    print("   The standard library HAS locale-sensitive text operations -- they")
    print("   are in `locale`, and they are about sorting:")
    import locale
    ops = sorted(n for n in ("strcoll", "strxfrm") if hasattr(locale, n))
    print(f"     locale.{', locale.'.join(ops)}   <- collation, locale-sensitive")
    print("     str.upper, str.lower              <- casing, locale-INDEPENDENT")
    print()
    print("   So the language will sort your text the way your country does and")
    print("   refuses to case it that way. The asymmetry is deliberate: a wrong")
    print("   sort order is visible, and a wrong case fold silently merges two")
    print("   identifiers or splits one.")
    print()
    print("   The length trap is here too, in a mapping nobody expects:")
    dotted = "İ"
    print(f"     {dotted!r}.lower() -> {dotted.lower()!r}   {len(dotted)} char in, "
          f"{len(dotted.lower())} out   {cps(dotted.lower())}")
    print("   U+0307 is a COMBINING DOT ABOVE. Lowercasing grew the string, and")
    print("   the second character is a mark that renders on top of the first.")
    print()

    # ------------------------------------------------------------------
    rule("5. EVERY ANSWER ABOVE IS A BET, AND HERE IS THE SIZE OF IT")
    print("   Every mapping on this page came from `str`, which reads whichever")
    print("   Unicode table this interpreter was built with. So each one is a")
    print("   fact about a machine, and this library's rule is that such facts")
    print("   do not become answer keys.")
    print()
    print("   The usual escape is the frozen table Python ships beside the live")
    print("   one -- `unicodedata.ucd_3_2_0`, sealed at Unicode 3.2 in 2002. Ask")
    print("   it for a normalization and the answer cannot vary by machine:")
    frozen = unicodedata.ucd_3_2_0
    for s in ("café", "ﬁ"):
        print(f"     {s!r:8} NFKC  frozen {frozen.normalize('NFKC', s)!r:8} "
              f"live {unicodedata.normalize('NFKC', s)!r}")
    print()
    print("   That escape is not available here, and the reason is the finding:")
    cased = [n for n in dir(frozen)
             if any(w in n.lower() for w in ("case", "upper", "lower", "fold"))]
    print(f"     functions on the frozen table that concern case:  {len(cased)}")
    print()
    print("   It carries name, category, combining class, decomposition,")
    print("   normalize, bidirectional, east_asian_width and more -- and not one")
    print("   case mapping among them. Case lives on `str`, and `str` has exactly")
    print("   one table: the current one.")
    print()
    print("   So this page records `ß`.upper() == 'SS', the two sigmas and the")
    print("   four Turkish i's as keys knowing it cannot prove them stable from")
    print("   inside Python. The bet is that these particular entries are load-")
    print("   bearing in every text stack on earth and will not move. If one ever")
    print("   does, this page's key goes red on the next run -- which is the")
    print("   correct outcome, and the reason the bet is worth making out loud")
    print("   rather than by saying nothing.")


if __name__ == "__main__":
    main()
