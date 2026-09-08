"""Alphabetical order is locale data, and `sorted()` has none of it.

This program deliberately does NOT ask the machine for a human locale. Which
locales exist differs between a Mac, a CI runner and a container -- a bare
ubuntu:24.04 offers exactly three, none of them a human language -- and
`locale.setlocale` raises rather than falling back, so an example that asked
for `pl_PL.UTF-8` would be a page that only works where it was written. The
three-locale comparison this page is really about is on the page, in a dated
fence, measured on named builds.

What is left is everything that does not depend on the machine: what code point
order actually is, what asking for a locale does when it fails, and why the two
tricks people reach for instead of a locale -- stripping accents, and sorting
the normalized form -- are one locale's answer hard-coded, badly.

Run:  python3 sorting_and_collation_py.py
"""

import functools
import locale
import unicodedata

# Polish words chosen so that every ordering rule below disagrees with another.
NAMES = ["Zebra", "Łódź", "Osa", "Óda", "Ćma", "Cma", "Żuk", "Zuk", "Świt", "Swit"]

# The Polish alphabet, in the order a Polish speaker recites it. This is the
# data `sorted()` does not have, and shipping it for every language is what
# CLDR and ICU are.
PL_ALPHABET = "aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźż"


def show(label, seq):
    print(f"   {label:<26}{' '.join(seq)}")


print("1. CODE POINT ORDER IS NOT ALPHABETICAL ORDER IN ANY LANGUAGE")
print("-" * 70)
show("sorted(names)", sorted(NAMES))
print()
print("   Read the tail: every accented word is behind every unaccented one,")
print("   in a block. That is not a near miss, it is a different principle.")
print()
def block(cp):
    """Named from the range, not looked up: these three boundaries are the
    three eras this section is about."""
    if cp < 0x80:
        return "ASCII, 1963"
    if cp < 0x100:
        return "Latin-1 Supplement, 1987"
    return "Latin Extended-A, 1991"


for word in ("Zebra", "Óda", "Ćma", "Łódź", "Żuk"):
    ch = word[0]
    print(f"     {ch}  U+{ord(ch):04X}  {ord(ch):>5}   {block(ord(ch))}")
print()
print("   Three blocks, three eras. 'Z' is in ASCII, which fixed its 128")
print("   numbers in the 1960s. 'Ó' is in the Latin-1 supplement, the second")
print("   half of an 8-bit table from the 1980s. 'Ł', 'Ć' and 'Ż' are in")
print("   Latin Extended-A, a block Unicode added in 1991 for the languages")
print("   the first two had no room for.")
print()
print("   So 'Ł' is U+0141 and 'Z' is U+005A because of when each letter got")
print("   a number, not because of anything about the letters. A code point")
print("   is an index into a table nobody ever sorted; sorting by it is")
print("   sorting by the history of the standard.")
print()

print("2. ASKING FOR A LOCALE IS A CALL THAT CAN FAIL, AND IT DOES NOT FALL BACK")
print("-" * 70)
print(f"   LC_COLLATE at the start        {locale.setlocale(locale.LC_COLLATE)!r}")
try:
    locale.setlocale(locale.LC_COLLATE, "xx_XX.UTF-8")
    print("   asked for a locale nobody has  it worked?!")
except locale.Error as exc:
    print(f"   asked for a locale nobody has  {type(exc).__module__}.{type(exc).__name__}")
print(f"   LC_COLLATE afterwards          {locale.setlocale(locale.LC_COLLATE)!r}")
print()
print("   It raised, and it changed nothing. There is no quiet fallback to a")
print("   near-enough locale, and there is no way to ask 'do you have one for")
print("   Polish?' other than trying it -- so a program that wants a specific")
print("   ordering has to handle NOT GETTING IT, on every machine it will run")
print("   on. A container is the likely place to find out: a stock")
print("   ubuntu:24.04 image ships C, C.utf8 and POSIX, and no human language")
print("   at all, so this call fails there for every locale you would want.")
print()
print("   Two more things about the call, both of which surprise people:")
print("     * it is PROCESS-GLOBAL state, not an argument. Setting it in one")
print("       thread changes the sort in every other one.")
print("     * LC_COLLATE is not LC_CTYPE. Setting the character type to a")
print("       UTF-8 locale says nothing about ordering, and the wrong one of")
print("       the six is the usual reason 'I set the locale' did not work.")
print()

print("3. THE TWO SPELLINGS, AND WHAT THE C LOCALE MEANS BY 'COLLATE'")
print("-" * 70)
by_key = sorted(NAMES, key=locale.strxfrm)
by_cmp = sorted(NAMES, key=functools.cmp_to_key(locale.strcoll))
show("key=locale.strxfrm", by_key)
show("cmp_to_key(strcoll)", by_cmp)
show("sorted(names)", sorted(NAMES))
print()
print(f"   the two collation spellings agree with each other   {by_key == by_cmp}")
print(f"   ...and with plain code point order                  {by_key == sorted(NAMES)}")
print()
print("   Both are the real thing: strxfrm turns a string into a sort KEY so")
print("   the transformation happens once per element, strcoll compares two")
print("   strings and costs a comparison every time. Prefer strxfrm for a")
print("   sort and strcoll for a one-off test.")
print()
print("   And here they change nothing, because this process is in the C")
print("   locale, where collation IS code point order. That is not a broken")
print("   configuration -- it is the default in every container, cron job and")
print("   CI runner, which means the production answer to 'sort these names'")
print("   is usually the one at the top of section 1.")
print()

print("4. STRIPPING THE ACCENTS IS NOT COLLATION -- IT IS ONE LOCALE'S ANSWER")
print("-" * 70)


def strip_marks(s):
    """The trick: decompose, then drop the combining marks."""
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if not unicodedata.combining(c))


show("key=strip_marks", sorted(NAMES, key=strip_marks))
print()
print("   Look at the first two. 'Ćma' and 'Cma' are DIFFERENT WORDS and the")
print(f"   trick gives them the same key ({strip_marks('Ćma')!r} == {strip_marks('Cma')!r}), so it cannot")
print("   order them at all -- Python's sort is stable, so what you get back")
print("   is the order they arrived in. Shuffle the input and the output")
print("   changes. A collation has to be a total order over the strings it")
print("   is given; this is not one, and nothing reports that.")
print()
polish_letters = "ąćęłńóśźż"
decomposes = [c for c in polish_letters if len(unicodedata.normalize("NFD", c)) > 1]
stays = [c for c in polish_letters if len(unicodedata.normalize("NFD", c)) == 1]
print(f"   Polish's nine special letters   {' '.join(polish_letters)}")
print(f"   NFD decomposes                  {' '.join(decomposes)}   ({len(decomposes)} of {len(polish_letters)})")
print(f"   NFD leaves alone                {' '.join(stays)}   ({len(stays)} of {len(polish_letters)})")
print()
print("   That is the flaw, and it is silent. Eight of the nine come apart")
print("   into a base letter and a combining mark, so the trick files them")
print("   next to their base letter. 'ł' does not: U+0142 is a letter with a")
print("   stroke THROUGH it, and a stroke is not a combining mark, so there")
print("   is nothing to strip and 'Łódź' stays out at the end where the code")
print("   points put it. Same word list, same trick, two different rules")
print("   applied depending on how Unicode happened to encode each letter.")
print()
print("   It is worth being precise about what the trick gets right, too:")
print("   filing 'ó' next to 'o' IS the correct answer -- in English. In")
print("   Polish 'ó' is a LETTER, with its own place after 'o', so a Polish")
print("   list sorts 'Osa' before 'Óda' and an English one the other way")
print("   round. The trick cannot express that, because it has thrown the")
print("   distinction away before the comparison starts.")
print()
print("   Which is the general point: an accent is not noise on a letter.")
print("   Whether it is noise is a fact about the LANGUAGE, and it is the")
print("   fact a locale carries.")
print()

print("5. WHAT A COLLATION ACTUALLY IS: LEVELS, OVER AN ALPHABET YOU DECLARE")
print("-" * 70)
RANK = {ch: i for i, ch in enumerate(PL_ALPHABET)}


def pl_key(s):
    """A toy Polish collation: primary = position in the Polish alphabet,
    secondary = case. Real ones have three or four levels and a lot more
    data; this one has the shape and none of the coverage."""
    low = s.lower()
    primary = tuple(RANK.get(c, len(RANK)) for c in low)
    secondary = tuple(0 if c.islower() else 1 for c in s)
    return (primary, secondary)


show("key=pl_key (toy Polish)", sorted(NAMES, key=pl_key))
show("key=strip_marks", sorted(NAMES, key=strip_marks))
show("sorted(names)", sorted(NAMES))
print()
print("   The toy gets Polish right for this list -- 'Cma' then 'Ćma', 'Osa'")
print("   then 'Óda', 'Swit' then 'Świt', 'Zuk' then 'Żuk', and 'Łódź' up")
print("   between 'l' and 'm' where it belongs -- and it does it with thirty")
print("   lines and ONE STRING: the alphabet, written out in order. That")
print("   string is the entire difference between this and sorted().")
print()
print("   Two levels is also the shape of the real thing. Compare base")
print("   letters first; if they tie, compare accents; if they still tie,")
print("   compare case. That is why two locales can both look 'right' and")
print("   still disagree -- they are not disagreeing about the levels, they")
print("   are disagreeing about which differences belong on which level.")
print()
print("   What the toy has no room for is the rest of the data, and the")
print("   omissions are not exotic:")
print("     * contractions -- Czech sorts 'ch' as ONE letter, after 'h', so")
print("       'chata' comes after 'hrad'; a per-character rank cannot say it")
print("     * expansions -- German 'ß' compares as 'ss', one character")
print("       weighing as two")
print("     * variable weighting -- whether a space or a hyphen counts at all")
print("       before the letters have been compared. Nobody thinks about that")
print("       one, and it is the rule that moved in glibc 2.28.")
