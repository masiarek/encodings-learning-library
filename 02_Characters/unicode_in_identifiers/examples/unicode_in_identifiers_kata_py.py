"""Answer key: three variable names that are one variable.

The kata asks which of these bind the same name, and what the language did
without being asked.
"""
import unicodedata as ud

ﬁle = 2                      # a LIGATURE, U+FB01, as the first character
print("source text:  \\ufb01le = 2        (the name starts with the ligature fi)")
print(f"then `file` -- typed with an ordinary f and i -- reads back as {file}")
print(f"and the two spellings are different STRINGS: {'\ufb01le' == 'file'}")
print("One assignment, one variable, two ways of typing its name.")
print()

NAMES = ["file", "ﬁle", "ﬀile", "ｆile", "𝐟ile"]
print(f"{'written':<8} {'NFKC':<8} {'identifier?':<12} code points")
for n in NAMES:
    k = ud.normalize("NFKC", n)
    print(f"{n:<8} {k:<8} {str(n.isidentifier()):<12} {' '.join('%04X' % ord(c) for c in n)}")

print()
folded = {}
for n in NAMES:
    folded.setdefault(ud.normalize("NFKC", n), []).append(n)
for k, v in folded.items():
    if len(v) > 1:
        print(f"   all of {v} are the identifier {k!r}")

print()
print("Python normalizes identifiers to NFKC before binding -- PEP 3131, and it")
print("is not optional. So five different pieces of source text are one name,")
print("and nothing warns you: no error, no lint, no visible difference at the")
print("point of use. A diff shows two lines that look identical.")
print()
print("Rust made the other choice. Identifiers are XID with NFC applied and")
print("mixed-script confusables are a WARNING, so the compiler preserves what")
print("you wrote and tells you when two names could be confused. Neither")
print("choice is wrong; they answer different questions.")
print()
print("It is IDNA2003 against IDNA2008 one floor down -- map-and-fold so that")
print("two spellings cannot both exist, versus preserve-and-refuse so that")
print("nothing is silently changed. Domain names had this argument first, and")
print("had to redesign twice; here it decides what your program is written in.")

assert ud.normalize("NFKC", "ﬁle") == "file"
assert "ﬁle".isidentifier()
