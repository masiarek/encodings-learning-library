"""Answer key: four code points read as addresses, and what each costs.

The kata is not a memory test. It asks you to read U+XXXX the way you read a
street address -- which block, then which house -- and then to say what the
address costs to write down in two encodings.
"""
import unicodedata as ud

def blocks(cp: int) -> str:
    for lo, hi, name in [(0x0000, 0x007F, "Basic Latin (ASCII)"),
                         (0x0080, 0x00FF, "Latin-1 Supplement"),
                         (0x0100, 0x017F, "Latin Extended-A"),
                         (0x4E00, 0x9FFF, "CJK Unified Ideographs"),
                         (0x1F600, 0x1F64F, "Emoticons")]:
        if lo <= cp <= hi:
            return f"{name}, house {cp - lo}"
    return "somewhere else"

for ch in "Aéż中😀":
    cp = ord(ch)
    plane = cp >> 16
    u8, u16 = ch.encode("utf-8"), ch.encode("utf-16-le")
    print(f"{ch}  U+{cp:04X}")
    print(f"   name        {ud.name(ch)}")
    print(f"   block       {blocks(cp)}")
    print(f"   plane       {plane}  ({'BMP' if plane == 0 else 'astral -- above U+FFFF'})")
    print(f"   utf-8       {u8.hex(' '):<12} {len(u8)} byte(s)")
    print(f"   utf-16      {u16.hex(' '):<12} {len(u16)} byte(s)"
          f"{'  -- a SURROGATE PAIR, two code units' if len(u16) > 2 else ''}")
    print()

print("Three things the addresses tell you before any arithmetic.")
print()
print("The number IS the character's identity, and the hex is only how it is")
print("written down: U+0041 and 65 are the same fact. The four digits are a")
print("convention, not a width -- U+1F600 needs five and is not a bigger KIND")
print("of thing, just a house further along.")
print()
print("The block is the useful half of the address. Latin-1 Supplement holds")
print("the accented letters of western Europe because it inherited a code")
print("page's layout; CJK Unified Ideographs is 20,000 houses on one street.")
print("Knowing the street tells you what a neighbour probably is.")
print()
print("And the cost is not the same question as the address. One character is")
print("1 to 4 bytes in UTF-8 and 2 or 4 in UTF-16, so 'how long is this text'")
print("has a different answer per encoding -- and U+1F600 is the case where")
print("UTF-16 needs two code units, which is where surrogates come from.")

assert len("😀".encode("utf-16-le")) == 4
assert ord("A") == 65
