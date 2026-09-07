"""Answer key: four line-shaped questions, and Python's answer to each.

The kata is about how many lines a string has, which sounds like one question
and is four.
"""
S = "a\tb\r\nc\rd\ne\x0bf"

print(f"the string   {S!r}")
print(f"len          {len(S)}   characters, every control included")
print()
print(f"S.split('\\n')       -> {S.split(chr(10))}")
print(f"S.splitlines()      -> {S.splitlines()}")
print(f"len(splitlines())   -> {len(S.splitlines())}")
print()
print("split('\\n') cuts on ONE byte and gives 3 pieces. splitlines() cuts on")
print(f"{len('\\r\\n\\v\\f\\x1c\\x1d\\x1e\\x85\\u2028\\u2029')} + 1 different things -- CR, LF, CRLF as one, plus VT, FF, the")
print("three file separators, NEL, and Unicode's own LINE and PARAGRAPH")
print("SEPARATOR -- and gives more. Same string, two correct answers, and the")
print("difference is a parser differential inside one language.")
print()
print("THE FOUR CONTROLS THE PAGE IS ABOUT")
for ch, why in [("\t", "moves to the next tab stop -- a layout instruction, not spaces"),
                ("\n", "ends a line on Unix; one byte, 0x0a"),
                ("\r", "returns the carriage; on a terminal the NEXT text overwrites this line"),
                ("\x00", "ends a C string -- see below")]:
    print(f"   {ch.encode('unicode_escape').decode():<6} U+{ord(ch):04X}  {why}")
print()
print("AND THE NUL")
n = "a\x00b"
print(f"   {n!r}   Python len = {len(n)}")
print(f"   utf-8 bytes = {n.encode().hex()}   -- three bytes, perfectly valid")
print("   C strlen would say 1. The byte is not removed and not rejected; the")
print("   next layer simply stops reading there, which is why text that crosses")
print("   into C comes back shorter with nothing raised anywhere.")

assert len(S.splitlines()) > len(S.split("\n"))
assert len("a\x00b".encode()) == 3
