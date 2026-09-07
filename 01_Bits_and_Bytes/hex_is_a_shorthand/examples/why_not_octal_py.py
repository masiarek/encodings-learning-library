#!/usr/bin/env python3
"""Why hex and not octal: the base has to divide the field you are reading.

Run:  python3 why_not_octal_py.py
"""

LABEL = 14  # every row below starts its data in this column, so the columns line up


def row(label: str, data: str, note: str = "", width: int = 21) -> str:
    line = f"   {label:<{LABEL - 3}}{data}"
    return f"{line}{'':<{max(1, width - len(data))}}{note}" if note else line


def main() -> None:
    print("1. THE BASE HAS TO DIVIDE THE WORD")
    print("   one octal digit = 3 bits        one hex digit = 4 bits")
    print(f"   a byte is 8 bits:   8 / 4 = {8 // 4} exactly      8 / 3 = {8 / 3:.2f}  <- does not divide")
    print("   That one fact is the whole argument. Everything below is it, seen from somewhere.")
    print()

    print("2. SO THE LEADING OCTAL DIGIT OF A BYTE IS NOT A WHOLE DIGIT")
    print("   Split 255 the way each base splits it, and look at the group sizes:")
    print(row("hex", "1111 1111", "= 0xFF    4 + 4"))
    print(row("", "F    F"))
    print(row("octal", "11 111 111", "= 0o377   2 + 3 + 3"))
    print(row("", "3  7   7"))
    print(f"   Three octal digits would be 9 bits. A byte has 8, so the top digit is short one bit:")
    print(f"   it runs 0-3 and no further. 0o377 = {0o377} is the biggest byte; 0o400 = {0o400} is past it.")
    print("   Both hex digits are full digits, 0-F. Neither is a special case you have to remember.")
    print()

    print("3. TWO BYTES: HEX SHOWS THE SEAM, OCTAL HIDES IT")
    two = "é".encode("utf-8")
    n = int.from_bytes(two, "big")
    bits = format(n, "016b")
    print(f"   'é' in UTF-8 is {len(two)} bytes: {two.hex(' ')}")
    print(row("as bits", f"{bits[:8]} {bits[8:]}", "<- the gap is the byte boundary"))
    print(row("as hex", f"{two[0]:02x}{'':6} {two[1]:02x}", "<- two digits each, and the gap survives"))

    # Octal counts from the RIGHT, so the groups are laid out from the right too.
    cuts = [(max(0, 16 - 3 * (i + 1)), 16 - 3 * i) for i in range(6)][::-1]
    groups = [bits[a:b] for a, b in cuts]
    print(row("as octal", " ".join(groups), f"= 0o{n:o}"))

    straddle = next(i for i, (a, b) in enumerate(cuts) if a < 8 < b)
    column = LABEL + sum(len(g) + 1 for g in groups[:straddle])
    print(f"{'':<{column}}{'^' * len(groups[straddle])}")
    print(f"{'':<{column}}this digit ({groups[straddle]} = {format(n, 'o')[straddle]}) is part of BOTH bytes at once")
    print("   In hex no digit is ever shared, because 4 divides 8. That is the entire reason a hex dump")
    print("   can print bytes in a grid and an octal one cannot.")
    print()

    print("4. OCTAL IS NOT WRONG. IT FITS A THREE-BIT FIELD PERFECTLY")
    perm = 0o755
    pbits = format(perm, "09b")
    print(f"   Unix permissions are three rwx triples = 9 bits, and 9 / 3 = {9 // 3} exactly.")
    print(row("octal", f"{pbits[:3]} {pbits[3:6]} {pbits[6:]}", f"= 0o{perm:o}   one digit per triple"))
    print(row("", "7   5   5"))
    print(row("hex", f"{format(perm, '012b')[:4]} {format(perm, '012b')[4:8]} {format(perm, '012b')[8:]}", f"= 0x{perm:X}   no digit lines up"))
    print(row("", "1    E    D"))
    print("   Same nine bits. `0o755` says rwx r-x r-x out loud; `0x1ED` says nothing at all.")
    print("   So the base is not a matter of taste — it is whichever one divides the field you are reading.")
    print()

    print("5. WHICH IS WHY THE ANSWER CHANGED WHEN THE CHARACTER DID")
    for width, name in ((6, "6-bit character  (Fieldata, BCDIC, DEC SIXBIT)"), (8, "8-bit byte       (System/360 onward)")):
        print(f"   {name}")
        for base, size in (("octal", 3), ("hex", 4)):
            fit = "exactly" if width % size == 0 else "NOT evenly"
            print(f"      {base:<6} {width} / {size} = {width / size:>4.2f}   {fit}")
    print("   Two octal digits held one 6-bit character. Two hex digits hold one 8-bit byte.")
    print("   Same property, a different width — the notation followed the character, not the fashion.")


if __name__ == "__main__":
    main()
