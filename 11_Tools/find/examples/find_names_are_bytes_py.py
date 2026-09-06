#!/usr/bin/env python3
"""Filenames in Python: a str you can compare, over bytes you cannot control.

`find -name` compares bytes and says so by failing. Python hands you `str`, which
looks like it has solved the problem and has not: two strings that draw the same
word can still be unequal, and the filesystem is where they come from.
"""

import os
import tempfile
import unicodedata

NFC = "żółw"                    # ż ó ł w   — four characters
NFD = "żółw"                  # z+dot, o+acute, ł, w — six


def show(label: str, value: object) -> None:
    print(f"   {label:<40} {value}")


print("1. TWO STRINGS, ONE WORD, AND == SAYS NO")
show("NFC", f"{NFC!r}  len={len(NFC)}")
show("NFD", f"{NFD!r}  len={len(NFD)}")
show("they look the same on screen", f"{NFC}  {NFD}")
show("NFC == NFD", NFC == NFD)
show("as UTF-8, NFC", NFC.encode().hex())
show("as UTF-8, NFD", NFD.encode().hex())
print("   Four characters against six, seven bytes against nine. Python is not")
print("   wrong to say False — they are different sequences of code points. It")
print("   is the same answer find gives, arrived at one level up.")

print()
print("2. THE FIX IS normalize(), AND IT HAS TO BE APPLIED TO BOTH SIDES")
show("normalize('NFC', NFD) == NFC", unicodedata.normalize("NFC", NFD) == NFC)
show("normalize('NFD', NFC) == NFD", unicodedata.normalize("NFD", NFC) == NFD)
show("casefold() alone is not enough", NFC.casefold() == NFD.casefold())
print("   Pick one form, put every name through it, then compare. Which form")
print("   does not matter; that everything agrees does. This is the only")
print("   comparison on this page that answers the question a human asked.")

print()
print("3. WHAT THE FILESYSTEM GAVE BACK")
with tempfile.TemporaryDirectory() as d:
    with open(os.path.join(d, NFC), "w") as fh:
        fh.write("turtle\n")
    (got,) = os.listdir(d)
    show("we asked for", NFC.encode().hex())
    show("listdir returned", got.encode().hex())
    show("unchanged?", got == NFC)
    show("the NFD spelling is in listdir?", NFD in os.listdir(d))
    show("...after normalising both", any(
        unicodedata.normalize("NFC", n) == unicodedata.normalize("NFC", NFD)
        for n in os.listdir(d)))
print("   The bytes came back as they went in — both of the machines this")
print("   library is tested on store the name they are given. What differs is")
print("   what happens when you then ASK for the other spelling, and that is on")
print("   the page: one of the two filesystems will hand you the same file.")

print()
print("4. A FILENAME IS BYTES, AND PYTHON SAYS SO WHEN PUSHED")
raw = b"caf\xe9.txt"                            # a Latin-1 name, not valid UTF-8
name = os.fsdecode(raw)
show("the bytes", raw.hex())
show("os.fsdecode(raw)", repr(name))
show("round trips to the same bytes", os.fsencode(name) == raw)
show("len() of that name", len(name))
show("is it printable?", name.isprintable())
print("   \\udce9 is a lone surrogate — the surrogateescape trick, which parks an")
print("   undecodable byte in a code point that can never come from real text, so")
print("   the name survives a trip through str and back. It is why os.listdir()")
print("   can hand you every file on a Linux box, including the ones nobody can")
print("   name. print() on it raises UnicodeEncodeError; that is the cost.")

print()
print("5. THE RULE")
print("   Compare filenames after normalizing BOTH sides, never by retyping a")
print("   name you read off a screen — and when you pass names to another")
print("   program, pass the bytes you were given rather than a spelling of them.")
print("   In the shell that is find -print0 | xargs -0; in Python it is passing")
print("   the listdir/os.scandir entry itself, not a string you rebuilt.")
