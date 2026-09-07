"""Answer key: one byte, four tables, and where the agreement stops.

The kata gives you two bytes and four code pages. The first byte is the one
everybody has met; the second is the one that shows the tables are not layered.
"""
TABLES = ["cp1252", "latin-1", "cp1250", "mac-roman"]

for byte in (0x41, 0xE9, 0x80):
    print(f"byte {byte:#04x}")
    for t in TABLES:
        try:
            ch = bytes([byte]).decode(t)
            name = "U+%04X" % ord(ch)
            drawn = repr(ch) if ch.isprintable() else "(a control, nothing drawn)"
        except UnicodeDecodeError:
            name, drawn = "--", "REFUSED: undefined in this table"
        print(f"   {t:<10} {name:<8} {drawn}")
    print()

print("0x41 is A in all four, and in every code page there has ever been: the")
print("first 128 are ASCII by agreement and that is the only thing they share.")
print()
print("0xE9 is e-acute in three of the four and a different letter in the")
print("fourth. That is the dangerous shape -- not a refusal, not a mess, just a")
print("plausible wrong letter, which is why the wrong table reads like a typo")
print("rather than like a bug.")
print()
print("0x80 is the one that settles the 'is cp1252 a superset of Latin-1'")
print("question, and the answer is NO. In cp1252 it is the euro sign; in")
print("Latin-1 it is a C1 control character with nothing to draw. cp1252")
print("REPLACED Latin-1's top control block, so the two tables disagree about")
print("32 positions rather than one extending the other.")

assert bytes([0x80]).decode("cp1252") == "€"
assert ord(bytes([0x80]).decode("latin-1")) == 0x80
