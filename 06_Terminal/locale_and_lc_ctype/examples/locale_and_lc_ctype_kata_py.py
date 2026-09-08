"""Answer key: six variables, one that matters here, and the language that opted out.

This key prints no locale NAME and reads no environment: the available locales
differ per machine and the runner pins LC_ALL=C, so anything measured from the
environment would be a fact about the runner. What is printed is the shape of
the system and Python's documented position in it.
"""
import locale
import sys

print("THE SIX CATEGORIES, AND WHAT EACH ONE DECIDES")
CATS = [
    ("LC_CTYPE", "what a CHARACTER is: case, class, the multibyte encoding"),
    ("LC_COLLATE", "what ORDER strings sort in"),
    ("LC_NUMERIC", "the decimal separator -- comma or point"),
    ("LC_TIME", "date and time formatting, and the first day of the week"),
    ("LC_MONETARY", "the currency symbol and where it goes"),
    ("LC_MESSAGES", "the language of a program's own output"),
]
for name, what in CATS:
    print(f"   {name:<13} {what}")
print()
print("   They are INDEPENDENT. LANG sets a default for all six, LC_ALL")
print("   overrides all six, and any single one can be set on its own -- so a")
print("   session sorting in Polish while formatting numbers in English is a")
print("   normal configuration, not a broken one.")
print(f"   Python's list, straight from the module: "
      f"{sorted(n for n in dir(locale) if n.startswith('LC_'))}")
print()
print("WHY LC_CTYPE IS THE ONE THIS LIBRARY CARES ABOUT")
print("   It decides what a tool means by 'a character', which decides:")
print("     * whether grep's . matches one byte or one character")
print("     * whether tr, cut -c and wc -m count bytes or characters")
print("     * whether a tool refuses an invalid sequence or skips the line")
print("   In the C locale a character IS a byte, which is why LC_ALL=C is the")
print("   escape hatch for searching -- and why it is the wrong answer for")
print("   anything that REARRANGES text, such as rev.")
print()
print("AND PYTHON, SINCE 3.7, DOES NOT ASK")
print(f"   sys.getdefaultencoding()      {sys.getdefaultencoding()!r}   always, everywhere")
print("   str is code points and never bytes, so LC_CTYPE cannot change what a")
print("   character means inside the language. What the locale COULD still")
print("   affect is the boundary -- the default encoding for open() and for")
print("   stdio -- and PEP 538/540 made even that predictable: UTF-8 mode, on")
print("   by default in a POSIX locale since 3.7, so a container with no")
print("   locales behaves like a workstation with all of them.")
print()
print("   The practical consequence is worth stating plainly. A pipeline of")
print("   shell tools changes behaviour when LC_ALL changes; the Python script")
print("   in the middle of that pipeline does not. If the two disagree about")
print("   how many characters a line has, they are not both misconfigured --")
print("   one of them is asking the environment and the other never does.")
print()
print("   locale.getpreferredencoding(False) still reports the boundary")
print("   default, and it is the one call whose answer legitimately differs")
print("   per machine -- which is exactly why it is not printed here.")

assert sys.getdefaultencoding() == "utf-8"
assert "LC_CTYPE" in dir(locale)
