#!/usr/bin/env python3
"""The same one-liner, in the language that does not need a subprocess.

The shell version puts a character beside its bytes by running three programs.
Python asks the string itself, which is worth seeing side by side: the shell's
`xxd -p` and Python's `.encode().hex()` are the same operation.
"""

print("1. THE ONE-LINER")
ch = "ż"
print(f"   {ch} = {ch.encode('utf-8').hex()}")
print("   .encode('utf-8') is the step the shell does not show you: a str has no")
print("   bytes until you name an encoding. xxd -p only ever saw the result.")

print()
print("2. THE TABLE")
print(f"   {'char':<6} {'bytes':<6} {'hex':<14} {'code point':<10} name")
for ch in ("A", "ż", "€", "😀"):
    data = ch.encode("utf-8")
    print(f"   {ch:<6} {len(data):<6} {data.hex(' '):<14} U+{ord(ch):04X}     "
          f"{__import__('unicodedata').name(ch)}")
print("   The last two columns are the ones no terminal tool gives you for free:")
print("   the code point is the character's NUMBER, the hex is its UTF-8 SPELLING,")
print("   and confusing the two is the single most common mistake in this subject.")

print()
print("3. THE REVERSE GEAR")
raw = bytes.fromhex("c5bc")
print(f"   bytes.fromhex('c5bc')          -> {raw!r}")
print(f"   bytes.fromhex('c5bc').decode() -> {raw.decode('utf-8')!r}")
print("   Python's pair for xxd -p and xxd -r -p, and it fails loudly on bad input")
print("   where the shell would hand you a broken file and say nothing.")

print()
print("4. WHY THE HEX IS NOT THE CODE POINT")
for ch in ("A", "ż", "€"):
    print(f"   {ch}  U+{ord(ch):04X}  ->  {ch.encode('utf-8').hex(' ')}")
print("   For 'A' they look identical (41 and U+0041) and that coincidence is why")
print("   ASCII hides the distinction for a whole career. For 'ż' the number is")
print("   U+017C and the bytes are C5 BC — nothing about one is readable in the other.")
