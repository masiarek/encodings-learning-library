"""Answer key: rot13 twice, and the letter it will not touch.

The kata asks for three things: the output, what applying it again does, and
what happens to a letter ASCII never met.
"""
import codecs

def rot13_ascii(s: str) -> str:
    out = []
    for c in s:
        if "a" <= c <= "z":
            out.append(chr((ord(c) - ord("a") + 13) % 26 + ord("a")))
        elif "A" <= c <= "Z":
            out.append(chr((ord(c) - ord("A") + 13) % 26 + ord("A")))
        else:
            out.append(c)
    return "".join(out)

MSG = "Attack at dawn, żółw!"
once = rot13_ascii(MSG)
twice = rot13_ascii(once)

print(f"plain    {MSG!r}")
print(f"rot13    {once!r}")
print(f"rot13^2  {twice!r}   -- back to the start")
print()
print("Applying it twice returns the input, because 13 + 13 = 26 and the")
print("alphabet is 26 long. That is not a property of encryption, it is a")
print("property of half. The shift is in the name, so the keyspace has one")
print("element and there is nothing to guess.")
print()
print("THE LETTERS IT LEFT ALONE -- and the one it did not")
print(f"   {'w'!r} U+0077  -> {rot13_ascii('w')!r}   ASCII, so it rotates like any other letter")
for c in "żół":
    print(f"   {c!r} U+{ord(c):04X}  unchanged -- outside a..z and A..Z")
print()
print("The two things that make rot13 feel elegant are facts about ASCII's")
print("layout, not about rotation:")
print("  * it is ONE SUM, because the 26 letters are contiguous. In a table")
print("    where they are not, the same idea needs a lookup.")
print("  * the byte count never moves, because every ASCII letter is one byte")
print("    and stays one byte.")
print()
print("Rotate past ASCII and you lose both. Add 13 to the code point instead:")
for c in "żół":
    print(f"   {c!r} + 13 = {chr(ord(c) + 13)!r}   "
          f"{len(c.encode()):d} byte(s) -> {len(chr(ord(c) + 13).encode()):d}")
print("   Not letters, not a rotation, and nothing came back round -- because")
print("   there is no 26-long run to come round in.")
print()
print(f"Python's own codec agrees on the ASCII part: {codecs.encode('Attack', 'rot13')!r}")

assert rot13_ascii(rot13_ascii(MSG)) == MSG
assert rot13_ascii("ż") == "ż"
