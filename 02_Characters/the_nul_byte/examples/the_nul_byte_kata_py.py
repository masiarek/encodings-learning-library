"""Answer key: five doors, and which of them a NUL walks through.

The kata's claim to test is the page's: U+0000 is an ordinary character that
encodes to one ordinary byte and passes every validator -- and almost nothing
that carries text will carry it.
"""
import re

S = "a\x00b"

print(f"the string     {S!r}   len {len(S)}")
print(f"utf-8          {S.encode().hex()}   three bytes")
print(f"round trip     {S.encode().decode() == S}   -- valid UTF-8, in and out")
print()
print("FIVE DOORS")

def door(label, fn):
    try:
        fn()
        print(f"   {label:<26} accepted")
    except (ValueError, TypeError) as e:
        print(f"   {label:<26} {type(e).__name__} -- refused")

door("str.encode('utf-8')", lambda: S.encode())
door("int('1\\x002')", lambda: int("1\x002"))
door("open(name)", lambda: open(S))
door("re.compile", lambda: re.compile(S))
door("'a\\x00b'.split()", lambda: S.split())
print()
print("The encoder does not care -- U+0000 is assigned, and its UTF-8 form is")
print("the single byte 00, which every validator accepts because there is")
print("nothing invalid about it. Python's own str carries it without comment.")
print()
print("The refusals are all at BOUNDARIES, and every one of them is refusing on")
print("behalf of something else: a filename crosses into a C API where 00 ends")
print("the string, so Python raises rather than silently truncating -- which is")
print("the good behaviour and the reason you meet a ValueError instead of a")
print("file called 'a'.")
print()
print("WHY IT IS ALSO THE SEPARATOR YOU CAN TRUST")
names = ["one two", "three\nfour", "five'six"]
joined = "\x00".join(names)
print(f"   {names}")
print(f"   joined with NUL, split back: {joined.split(chr(0))}")
print("   Every other separator can occur inside a filename -- space, newline,")
print("   quote, tab. NUL cannot, because the kernel's own API cannot express")
print("   it. That is exactly why find -print0 and xargs -0 exist: the one byte")
print("   that is guaranteed absent from the data is the one safe delimiter.")

assert S.encode() == b"a\x00b"
assert "\x00".join(names).split("\x00") == names
