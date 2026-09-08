#!/usr/bin/env python3
"""UTS #18 grades a regex engine. This one grades Python's `re` against it.

The report defines Level 1 as eight numbered requirements and Level 2 as seven
more, and says an implementation may claim any subset as long as it names what
it has. That turns "does it support Unicode" into something you can measure,
which is what this program does -- one section per requirement, each printing
the observation rather than an opinion.

Nothing here is version-dependent on purpose. Where a fact about the Unicode
table would have been the answer (how many decimal digits exist, how many
marks), the program prints the INVARIANT instead: how many of them the engine
disagrees with. That number is zero or it is not, whatever table you are on.

Run:  python3 what_a_regex_matches_py.py
"""

import re
import sys
import unicodedata as ud
import warnings

BAR = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


def cps(s):
    return " ".join(f"U+{ord(c):04X}" for c in s)


# The cast, plus two strings this page needs and the cast does not carry.
NFC = "café"                     # c a f e-acute
NFD = "café"               # c a f e + U+0301 COMBINING ACUTE ACCENT
HINDI = "हिन्दी"                     # the name of the language, in the language
DEVA_DIGITS = "१२३"              # DEVANAGARI ONE TWO THREE
FAMILY = "\U0001F468‍\U0001F469‍\U0001F467‍\U0001F466"

# One pass over the whole code point space, because three sections want a
# question answered about every character and the sweep is the slow part.
D_DISAGREES = MARK_IN_W = PC_IN_W = 0
CASE_CLASSES = {"i": [], "k": [], "s": []}
_is_d = re.compile(r"\d").fullmatch
_is_w = re.compile(r"\w").fullmatch
_caseless = [(_members, re.compile(_base, re.I).fullmatch)
             for _base, _members in CASE_CLASSES.items()]
for _cp in range(0x110000):
    _ch = chr(_cp)
    _gc = ud.category(_ch)
    if bool(_is_d(_ch)) != (_gc == "Nd"):
        D_DISAGREES += 1
    if _is_w(_ch):
        if _gc[0] == "M":
            MARK_IN_W += 1
        elif _gc == "Pc":
            PC_IN_W += 1
    for _members, _match in _caseless:
        if _match(_ch):
            _members.append(_ch)


# ----------------------------------------------------------------------------
head(1, "ONE API, TWO ENGINES, AND THE SWITCH IS THE TYPE")
print(f"   the digits {DEVA_DIGITS}   {cps(DEVA_DIGITS)}")
print()
print(f"   r'\\d+'  against the str                 {bool(re.fullmatch(r'\d+', DEVA_DIGITS))}")
print(f"   rb'\\d+' against the same bytes          {bool(re.fullmatch(rb'\d+', DEVA_DIGITS.encode()))}")
print(f"   r'\\d+'  against the str, with re.ASCII  {bool(re.fullmatch(r'\d+', DEVA_DIGITS, re.ASCII))}")
print(f"   int() on that str                       {int(DEVA_DIGITS)}")
try:
    re.compile(rb"\d+", re.UNICODE)
    print("   rb'\\d+' with re.UNICODE                 accepted")
except ValueError:
    print("   rb'\\d+' with re.UNICODE                 ValueError -- there is no such mode")
print()
print("   Same three characters, same pattern text, two answers. A `str`")
print("   pattern is Unicode-aware and a `bytes` pattern is ASCII-only, and")
print("   `re.ASCII` turns the first into the second. There is no flag that")
print("   turns the second into the first: the type IS the mode, and asking")
print("   for re.UNICODE on bytes is refused rather than ignored.")
print()
print("   Nothing here is careless. A byte string has no encoding attached, so")
print("   there is no table an engine could consult -- the refusal is the")
print("   honest answer. What it means in practice is that the same regex")
print("   moved from a decoded string to a raw pipe silently narrows to ASCII.")


# ----------------------------------------------------------------------------
head(2, "RL1.2 PROPERTIES -- THE ONE PYTHON DOES NOT HAVE AT ALL")
for pat in [r"\p{L}", r"\pL", r"\p{Script=Greek}", r"\p{Alphabetic}"]:
    try:
        re.compile(pat)
        verdict = "compiles"
    except re.error:
        verdict = "raises re.error"
    print(f"   re.compile(r'{pat}'){'':<{20 - len(pat)}}{verdict}")
print()
print("   RL1.2 asks for a minimal list of properties addressable from the")
print("   pattern: General_Category, Script and Script_Extensions, Alphabetic,")
print("   Uppercase, Lowercase, White_Space, Noncharacter_Code_Point,")
print("   Default_Ignorable_Code_Point, and ANY / ASCII / ASSIGNED.")
print()
print("   Python's `re` has no syntax for any of them. Not a partial list, not")
print("   an older list -- no \\p{...} at all, so RL1.2 is not partly met, and")
print("   nor is RL1.2a, which is written in terms of it. That is the single")
print("   largest thing on this page: the module every Python program reaches")
print("   for is below Level 1 by the standard's own first substantive test.")
print()
print("   The properties are still in the standard library, just not in the")
print("   regex engine -- `unicodedata.category`, `.name`, `.numeric` and the")
print("   `str.is*` methods reach some of them, one character at a time. The")
print("   third-party `regex` module is where \\p{...} lives in Python, and it")
print("   is not what `import re` gives you.")


# ----------------------------------------------------------------------------
head(3, "RL1.2a COMPATIBILITY PROPERTIES -- WHAT \\w AND \\d ARE SUPPOSED TO BE")
print("   Annex C of the report defines the two classes every engine ships:")
print()
print("       \\d   \\p{gc=Decimal_Number}")
print("       \\w   \\p{alpha} + \\p{gc=Mark} + \\p{digit}")
print("            + \\p{gc=Connector_Punctuation} + \\p{Join_Control}")
print()
print("   Three of those five terms are a general category -- Mark, Connector")
print("   Punctuation, and \\p{digit}, which Annex C says is gc=Decimal_Number --")
print("   so a sweep over every code point can check them with no table this")
print("   program does not already have. Counts of characters move with the")
print("   Unicode version and are not printed; disagreements are the claim.")

print()
print(f"   code points where \\d disagrees with gc=Nd        {D_DISAGREES}")
print(f"   marks (gc=M*) that \\w matches                    {MARK_IN_W}")
print(f"   connector punctuation (gc=Pc) that \\w matches    {PC_IN_W}")
print()
print("   So \\d is exactly right, and \\w holds not one Mark of the thousands")
print("   there are, and exactly one connector. That one is the underscore,")
print("   written into the engine as a literal rather than looked up:")
for name, ch in [("U+005F LOW LINE", "_"), ("U+203F UNDERTIE", "‿")]:
    print(f"       {name:<18} gc={ud.category(ch)}   \\w matches it: {bool(re.fullmatch(r'\w', ch))}")
print()
print("   And here is what the missing Mark costs, in a word chosen because")
print("   it is the name of a language, written in that language:")
print()
print(f"       {HINDI}   {cps(HINDI)}")
pieces = re.findall(r"\w+", HINDI)
for ch in HINDI:
    hit = "yes" if re.fullmatch(r"\w", ch) else "NO"
    print(f"       U+{ord(ch):04X}  gc={ud.category(ch)}   in \\w: {hit}")
print()
print(f"       re.findall(r'\\w+', ...) finds {len(pieces)} words: {' '.join(pieces)}")
print(f"       re.fullmatch(r'\\w+', ...)     {bool(re.fullmatch(r'\w+', HINDI))}")
print()
print("   Three of the six characters are marks -- two vowel signs and a")
print("   virama -- and \\w rejects all three, so one word comes apart into")
print("   three consonants. The pattern did not fail. It reported success,")
print("   three times, with a wrong answer each time, which is the shape this")
print("   whole library keeps meeting.")


# ----------------------------------------------------------------------------
head(4, "RL1.3 SUBTRACTION AND INTERSECTION -- COMPILES, MEANS SOMETHING ELSE")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    pat = re.compile(r"[\w&&\d]")
    print(f"   re.compile(r'[\\w&&\\d]')     compiles")
    print(f"   ...and it matches '&'       {bool(pat.fullmatch('&'))}")
    print(f"   ...and it matches 'a'       {bool(pat.fullmatch('a'))}")
print()
print("   RL1.3 wants union, intersection and set difference inside a")
print("   character class, so that [\\w&&\\d] means the characters that are both.")
print("   Python has no such operator, so the two ampersands are just two more")
print("   members of the class: the expression means \\w, or '&', or \\d. It")
print("   does not raise, it does not warn on the page, and it matches every")
print("   word character -- the opposite of an intersection.")
print()
print("   This is the failure mode worth remembering from the whole page. A")
print("   missing \\p{...} announces itself; a missing set operator quietly")
print("   turns a narrowing expression into a widening one.")


# ----------------------------------------------------------------------------
head(5, "RL1.4 SIMPLE WORD BOUNDARIES -- THE MARK IS NOT ITS OWN WORD")
print("   The requirement is two sentences: the word character class covers")
print("   Alphabetic plus the decimals plus ZWNJ and ZWJ, and -- separately --")
print("   nonspacing marks are never divided from their base characters.")
print()
print(f"   re.findall(r'\\b\\w+\\b', hindi)             {re.findall(r'\b\w+\b', HINDI)}")
print(f"   re.findall(r'\\b\\w+\\b', 'cafe'+U+0301)     {re.findall(r'\b\w+\b', NFD)}")
print()
print("   The second line is the sharper one, because the string is four")
print("   letters of ASCII and one accent. \\b puts the boundary after the `e`")
print("   and leaves the acute outside the word, so a pattern anchored on \\b")
print("   matches `cafe` and reports it as a whole word -- in a string whose")
print("   whole word is `café`. Nothing about that is visible in the output.")


# ----------------------------------------------------------------------------
head(6, "RL1.5 SIMPLE LOOSE MATCHES -- THE CLOSURE IS NOT UNICODE'S")
print("   Which characters does re.IGNORECASE consider equal to each letter,")
print("   and does str.casefold() -- Python's own full case folding -- agree?")
print()
for base, klass in CASE_CLASSES.items():
    folds = sorted({c.casefold() for c in klass})
    word = "class" if len(folds) == 1 else "classes"
    print(f"   re.I class of {base!r}: {' '.join(f'U+{ord(c):04X}' for c in klass)}")
    print(f"      casefold puts those in {len(folds)} {word}: "
          f"{' / '.join(cps(f) for f in folds)}")
print()
sharp = "ß"
print(f"   re.fullmatch('ss', sharp-s, re.I)   {bool(re.fullmatch('ss', sharp, re.I))}")
print(f"   sharp-s.casefold()                  {sharp.casefold()!r}")
print()
print("   Two different disagreements, in two directions.")
print()
print("   The sharp-s one is allowed and is the point of the word `simple` in")
print("   the requirement's title: Level 1 asks only for simple case folding,")
print("   where a match may not change length, so 'ss' is not required to")
print("   match it. casefold() does full folding and gives 'ss'. Both correct.")
print()
print("   The `i` one is not the same shape. Unicode's default simple folding")
print("   leaves U+0130 and U+0131 -- the Turkish dotted capital and dotless")
print("   small i -- in classes of their own, and only the Turkic tailoring")
print("   merges them with the ASCII pair. Python's re merges them always, in")
print("   every locale, because its case-insensitive matching closes over the")
print("   simple case MAPPINGS rather than over case FOLDING. Its own")
print("   casefold() splits the same four characters into three classes and")
print("   is the half that agrees with Unicode.")


# ----------------------------------------------------------------------------
head(7, "RL1.6 LINE BOUNDARIES -- ONE STANDARD LIBRARY, TWO ANSWERS")
print("   The report names seven newline characters plus the CR LF pair.")
print("   Python's own str.splitlines() knows them; Python's own re does not.")
print()
print(f"   {'character':<22} {'. matches it':<14} {'$ before it (re.M)':<20} {'splitlines'}")
seps = [("U+000A LINE FEED", "\n"), ("U+000B LINE TAB", "\v"),
        ("U+000C FORM FEED", "\f"), ("U+000D CARRIAGE RET", "\r"),
        ("U+0085 NEXT LINE", ""), ("U+2028 LINE SEP", " "),
        ("U+2029 PARA SEP", " ")]
for name, ch in seps:
    dot = bool(re.fullmatch(r".", ch))
    dollar = bool(re.search(r"a$", "a" + ch + "b", re.M))
    lines = len(("a" + ch + "b").splitlines())
    print(f"   {name:<22} {str(dot):<14} {str(dollar):<20} {lines}")
print()
print("   Read the last two columns together. `re` breaks a line at exactly")
print("   one of the seven; splitlines() breaks at all seven. So a file read")
print("   with .splitlines() and searched with a MULTILINE `$` is being cut")
print("   twice, by two functions from the same standard library that do not")
print("   agree about where a line ends -- and `.`, which is documented as")
print("   'any character except a newline', matches six of the seven.")


# ----------------------------------------------------------------------------
head(8, "RL1.1 AND RL1.7 -- THE TWO PYTHON PASSES OUTRIGHT")
print(f"   r'\\U0001F600' matches the emoji           "
      f"{bool(re.fullmatch(r'\U0001F600', chr(0x1F600)))}")
print(f"   r'[\\U0001F600-\\U0001F64F]' is ONE unit    "
      f"{bool(re.fullmatch(r'[\U0001F600-\U0001F64F]', chr(0x1F600)))}")
print(f"   r'\\N{{LATIN SMALL LETTER E WITH ACUTE}}'    "
      f"{bool(re.fullmatch(r'\N{LATIN SMALL LETTER E WITH ACUTE}', 'é'))}")
print(f"   len(one astral character)                {len(chr(0x1F600))}")
print()
print("   RL1.1 wants the code point's own hex digits to appear in the syntax,")
print("   which rules out spelling an astral character as a surrogate pair or")
print("   as its UTF-8 bytes. `\\U0001F600` contains 1F600, so it qualifies;")
print("   `\\N{...}` is a bonus the requirement does not ask for.")
print()
print("   RL1.7 wants a supplementary code point handled as one unit. Since")
print("   PEP 393 a Python str is a sequence of code points with no surrogate")
print("   pairs in it, so this one is free -- and it is not free in every")
print("   language: the same requirement is the whole of why a Java or")
print("   JavaScript engine has to say something about UTF-16.")


# ----------------------------------------------------------------------------
head(9, "THE SCORECARD FOR LEVEL 1")
rows = [
    ("RL1.1  Hex Notation", "yes", "\\U0001F600 and \\N{NAME}"),
    ("RL1.2  Properties", "NO", "no \\p{...} syntax exists"),
    ("RL1.2a Compatibility Properties", "NO", "\\w holds no Mark at all"),
    ("RL1.3  Subtraction and Intersection", "NO", "&& is two literal ampersands"),
    ("RL1.4  Simple Word Boundaries", "NO", "\\b divides a mark from its base"),
    ("RL1.5  Simple Loose Matches", "~", "closes over mappings, not folding"),
    ("RL1.6  Line Boundaries", "NO", "one separator of seven"),
    ("RL1.7  Supplementary Code Points", "yes", "a str is code points"),
]
for name, verdict, why in rows:
    print(f"   {name:<38} {verdict:<5} {why}")
print()
print("   Two clear passes, five clear failures, one that depends on how you")
print("   read `at least`. The report allows exactly this -- an implementation")
print("   may claim Level 1 except for named requirements -- so the useful")
print("   sentence is not 'Python's re does not support Unicode'. It is:")
print("   Level 1 except RL1.2, RL1.2a, RL1.3, RL1.4 and RL1.6.")
print()
print("   That sentence is checkable, and 'supports Unicode' is not.")


# ----------------------------------------------------------------------------
head(10, "LEVEL 2, RL2.1 -- CANONICAL EQUIVALENCE, AND WHAT THE FIX IS")
print(f"   composed    {NFC}   {cps(NFC)}")
print(f"   decomposed  {NFD}   {cps(NFD)}")
print(f"   the two strings are equal                    {NFC == NFD}")
print(f"   NFC(decomposed) == composed                  {ud.normalize('NFC', NFD) == NFC}")
print()
print(f"   re.search(composed, decomposed_text)         {bool(re.search(NFC, NFD))}")
print(f"   re.fullmatch(r'caf.', decomposed_text)       {bool(re.fullmatch(r'caf.', NFD))}")
print(f"   re.match(r'caf.', decomposed_text) grabs     {re.match(r'caf.', NFD).group()!r}")
print(f"   re.fullmatch(r'caf..', decomposed_text)      {bool(re.fullmatch(r'caf..', NFD))}")
print(f"   after ud.normalize('NFC', text)              "
      f"{bool(re.search(NFC, ud.normalize('NFC', NFD)))}")
print()
print("   The third line is the one to keep. `caf.` was written by somebody")
print("   who meant 'caf and one more character', and on the decomposed")
print("   spelling the dot takes the bare `e` and stops -- the accent is left")
print("   behind, outside the match, and the captured group is a word that is")
print("   not in the file. Nothing raised.")
print()
print("   RL2.1 is Level 2 because doing it inside the engine is genuinely")
print("   hard: canonical equivalence can reorder and merge characters, so a")
print("   pattern would have to match parts of characters. The report's own")
print("   advice is the last line above -- put the text in a known")
print("   normalization form, write the pattern for that form, and match code")
print("   point by code point as usual. Normalization is the fix. A cleverer")
print("   pattern is not, and the conformance clause says a system meets RL2.1")
print("   this way as long as it says so out loud.")


# ----------------------------------------------------------------------------
head(11, "LEVEL 2, RL2.2 -- '.' IS A CODE POINT, AND THAT IS BY DESIGN")
print(f"   the family emoji           {FAMILY}")
print(f"   UTF-8 bytes                {len(FAMILY.encode())}")
print(f"   code points                {len(FAMILY)}")
print(f"   what a person counts       1")
print(f"   re.findall(r'.', ...)      {len(re.findall(r'.', FAMILY))} matches")
first = re.match(r".", FAMILY).group()
print(f"   the first one is           {first}   U+{ord(first):04X}")
print()
try:
    re.compile(r"\X")
    print("   re has \\X                   yes")
except re.error:
    print("   re has \\X                   no -- re.error")
print()
print("   `.` matched one seventh of a family and handed back a man. That is")
print("   not a bug in `re`: the report says in as many words that an engine")
print("   may treat `.` as one code point and spell the grapheme cluster \\X,")
print("   and RL2.2 is the requirement to provide the second one. Python's re")
print("   provides neither \\X nor any other way to ask the question.")
print()
print("   The 25 bytes above become 26 in a file, once the newline is on the")
print("   end -- which is the number the PCRE2 page measured with wc -c.")

assert sys.maxunicode == 0x10FFFF
