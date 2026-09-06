#!/usr/bin/env python3
"""The last byte of a text file, from Python.

The shell shows what the byte does to tools. Python shows the sharper half:
the line-splitter you reach for by default cannot see the difference at all,
and the one that can is the one nobody uses.
"""

NO_NL = "ż"
WITH_NL = "ż\n"

print("1. TWO STRINGS, ONE CHARACTER, ONE BYTE APART")
for name, text in (("no_nl  ", NO_NL), ("with_nl", WITH_NL)):
    print(f"   {name}  {text.encode('utf-8').hex(' '):<12}  {len(text.encode('utf-8'))} bytes")
print("   The letter is two bytes (C5 BC). The newline is the third.")

print()
print("2. splitlines() CANNOT SEE THE DIFFERENCE")
print(f"   {NO_NL!r:<8}.splitlines()  -> {NO_NL.splitlines()}")
print(f"   {WITH_NL!r:<8}.splitlines()  -> {WITH_NL.splitlines()}")
print("   Identical. splitlines() treats a newline as a TERMINATOR: it closes the")
print("   line before it and does not open one after it. That is the right answer")
print("   for reading a file, and it is why the difference never reaches your code.")

print()
print("3. split('\\n') CAN — BECAUSE IT ASKS A DIFFERENT QUESTION")
print(f"   {NO_NL!r:<8}.split(chr(10))  -> {NO_NL.split(chr(10))}")
print(f"   {WITH_NL!r:<8}.split(chr(10))  -> {WITH_NL.split(chr(10))}")
print("   split() treats it as a SEPARATOR, so a trailing one opens an empty last")
print("   field. Neither function is wrong; they answer 'what are the lines?' and")
print("   'what is between the newlines?', and only the second is a byte question.")

print()
print("4. THE TEST TO WRITE, AND THE ONE THAT LIES")
for name, text in (("no_nl  ", NO_NL), ("with_nl", WITH_NL)):
    data = text.encode("utf-8")
    print(f"   {name}  endswith(b'\\n') -> {str(data.endswith(chr(10).encode())):<5}"
          f"  len(splitlines()) -> {len(text.splitlines())}"
          f"  count('\\n') -> {text.count(chr(10))}")
print("   Ask the bytes. Counting lines cannot tell you, because both files have")
print("   exactly one line — that is what section 2 just proved.")

print()
print("5. WRITING IT: WHICH CALL ADDS THE BYTE")
print("   print(x, file=f)      adds it   (end='\\n' is the default)")
print("   print(x, file=f, end='')  does not")
print("   f.write(x)            does not — write() writes exactly what you gave it")
print("   f.writelines(lines)   does not — the name promises a newline it never adds")
print("   The shell's pair is the same pair: echo adds it, printf does not.")

print()
print("6. READING A FILE THAT LACKS IT")
import io

handle = io.StringIO(WITH_NL + NO_NL)          # two records, the second unterminated
lines = handle.readlines()
print(f"   the file: {(WITH_NL + NO_NL)!r}")
print(f"   readlines() -> {lines}")
print("   Every element ends in a newline except the last, so code that strips a")
print("   fixed number of characters off the end damages exactly one row — the")
print("   last. Use .rstrip(chr(10)), or splitlines(), and never [:-1].")
