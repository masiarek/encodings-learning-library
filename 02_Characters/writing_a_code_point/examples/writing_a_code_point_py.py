#!/usr/bin/env python3
"""One character, five spellings -- and Python's own rule for choosing one.

A code point is a number. This program is about writing that number down:
in a source file, where a parser reads it, and on a screen, where a person
does. Python offers three escape forms and they are not interchangeable --
two have a FIXED width and the third takes a name instead of a number.

The last section is the half nobody writes down: repr() chooses a spelling
too, and its rule is the one worth copying.

Nothing here is a Unicode-table lookup that could differ between versions.
EURO SIGN has been U+20AC under that name since 1998; the widths and the
syntax errors belong to the language, not to the table.

Run:  python3 writing_a_code_point_py.py
"""

import unicodedata
import warnings

BAR = "-" * 72
BS = chr(92)   # one backslash, built rather than typed, so nothing below
Q = chr(34)    # has to be escaped twice on its way to the screen
EURO = chr(0x20AC)


def head(n, title):
    print("\n" + str(n) + ". " + title + "\n" + BAR)


def literal(body):
    """A source-code string literal, as text: literal('\\u20ac') -> "\\u20ac" """
    return Q + body + Q


def verdict(src):
    """Compile a literal without running it, and report what Python said."""
    try:
        compile(src, "<demo>", "eval")
        return "compiles"
    except SyntaxError as exc:
        # The tail of the message is the reason; the prefix is bookkeeping.
        return exc.msg.rsplit(": ", 1)[-1]


head(1, "FIVE SPELLINGS, ONE CHARACTER")
for src, what in [
    (literal(EURO), "the character itself, pasted in"),
    (literal(BS + "u20ac"), "the four-digit escape"),
    (literal(BS + "N{EURO SIGN}"), "by name"),
    ("chr(0x20AC)", "from the number, at run time"),
    ("chr(8364)", "the same number in decimal"),
]:
    print("   " + src.ljust(22) + what)

five = {EURO, eval(literal(BS + "u20ac")), eval(literal(BS + "N{EURO SIGN}")),
        chr(0x20AC), chr(8364)}
print()
print("   distinct strings among those five: " + str(len(five)))
print("   the one they all are: " + repr(EURO) + "  U+" + format(ord(EURO), "04X")
      + "  " + unicodedata.name(EURO))
print()
print("   Five spellings, one string. Nothing survives into the running")
print("   program except the number -- so the choice between them is a")
print("   message to the next person who reads the file, not to Python.")

head(2, "THE WIDTH IS PART OF THE ESCAPE")
print("   The two numeric escapes have FIXED widths. There is no closing")
print("   delimiter, so the width is the only thing telling the parser where")
print("   the escape stops.")
print()
for body in ["x2", "xe9", "u20a", "u20ac", "U0001F60", "U0001F600"]:
    src = literal(BS + body)
    print("   " + (BS + body).ljust(14) + verdict(src))
print()
print("   Exactly 2 digits after " + BS + "x, 4 after " + BS + "u, 8 after "
      + BS + "U. Rust writes the same character with braces instead of a")
print("   width -- and that spelling is not Python:")
print()
print("   " + (BS + "u{20AC}").ljust(14) + verdict(literal(BS + "u{20AC}")))
print()
print("   Every one of those failures is a SyntaxError, raised before the")
print("   line can run. An escape is not a function call; it is spelling,")
print("   and the parser is the one doing the reading.")

head(3, "THE THIRD FORM TAKES A NAME, AND IT IS CHECKED TOO")
print("   " + literal(BS + "N{EURO SIGN}").ljust(26) + "-> "
      + repr(eval(literal(BS + "N{EURO SIGN}"))))
print("   " + literal(BS + "N{euro sign}").ljust(26) + "-> "
      + repr(eval(literal(BS + "N{euro sign}"))) + "    (names are case-insensitive)")
print("   " + literal(BS + "N{NOT A REAL NAME}").ljust(26) + "-> "
      + verdict(literal(BS + "N{NOT A REAL NAME}")))
print()
print("   A misspelt name is a SyntaxError, so " + BS + "N{...} is the one escape")
print("   that cannot be quietly wrong. A misspelt NUMBER is a different")
print("   character that compiles perfectly:")
print()
for cp in (0x20AC, 0x20AD, 0x20BC):
    print("      U+" + format(cp, "04X") + "  " + chr(cp) + "  "
          + unicodedata.name(chr(cp)))
print()
print("   One digit apart, and nothing in a code review would show it. That")
print("   is the argument for the name form wherever a reader has to check")
print("   the intent rather than the value.")

head(4, "THE SAME ESCAPE MEANS SOMETHING ELSE IN A BYTES LITERAL")
print("   " + BS + "x is the escape both kinds of literal share, and it does")
print("   not mean the same thing in each:")
print()
as_str = eval(literal(BS + "xe9"))
as_bytes = eval("b" + literal(BS + "xe9"))
print("   " + literal(BS + "xe9").ljust(12) + repr(as_str).ljust(12)
      + str(len(as_str)) + " character   -- a CODE POINT below 256")
print("   b" + literal(BS + "xe9").ljust(11) + repr(as_bytes).ljust(12)
      + str(len(as_bytes)) + " byte        -- a BYTE")
print()
print("   And the two spellings a str has that bytes does not:")
print()
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    not_escape = eval("b" + literal(BS + "u20ac"))
    warned = [w.category.__name__ for w in caught]
raw = eval("r" + literal(BS + "u20ac"))
print("   b" + literal(BS + "u20ac").ljust(11) + repr(not_escape).ljust(12)
      + str(len(not_escape)) + " bytes       -- not an escape at all")
print("   r" + literal(BS + "u20ac").ljust(11) + repr(raw).ljust(12)
      + str(len(raw)) + " characters  -- raw: the backslash is data")
print()
print("   A bytes literal has no " + BS + "u, " + BS + "U or " + BS + "N, because")
print("   a byte is not a code point and there would be nothing for them to")
print("   mean. So the backslash is read as data and you get six bytes -- a")
print("   silent six-fold difference in length from the str you meant. Python")
print("   is in the middle of taking that away: compiling that literal")
print("   raises a warning (" + str(len(warned)) + " here) whose text says such sequences")
print("   will not work in the future. Which CATEGORY of warning depends on")
print("   your Python version, so this program counts them and the page")
print("   names one, with a date.")

head(5, "PRINTING IS A CHOICE OF SPELLING TOO")
sample = "caf" + chr(0xE9) + " " + EURO + " " + chr(0x0CA0)
print("   str()    " + sample)
print("   repr()   " + repr(sample))
print("   ascii()  " + ascii(sample))
print()
print("   ascii() escapes everything above 127 and picks the shortest form")
print("   per character -- two widths in one line, " + BS + "xe9 for the")
print("   e-acute and " + BS + "u0ca0 for the Kannada letter.")
print()
print("   repr() is the interesting one, because it escapes SOME characters")
print("   and not others. The rule is str.isprintable():")
print()
print("   " + "code point".ljust(12) + "printable".ljust(12) + "repr()".ljust(14) + "name")
for cp, label in [
    (0x0041, "LATIN CAPITAL LETTER A"),
    (0x20AC, "EURO SIGN"),
    (0x0CA0, "KANNADA LETTER TTHA"),
    (0x00A0, "NO-BREAK SPACE"),
    (0x0009, "<a control: TAB has no name>"),
    (0x202E, "RIGHT-TO-LEFT OVERRIDE"),
]:
    c = chr(cp)
    print("   U+" + format(cp, "04X").ljust(10) + str(c.isprintable()).ljust(12)
          + repr(c).ljust(14) + label)
print()
print("   A character that draws something is printed as itself; one that")
print("   draws nothing is printed as an escape. That is the rule you want")
print("   for a log line, an error message or a test failure, and it is why")
print("   repr() rather than str() is the right way to print a value you did")
print("   not write yourself.")
print()
print("   Read the last row again. Printed raw, that character reorders the")
print("   line it lands in -- including this one. repr() will not do that to")
print("   you, and neither will this program: every invisible character above")
print("   reached the screen as an escape.")
