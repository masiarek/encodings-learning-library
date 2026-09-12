#!/usr/bin/env python3
"""Which of the dialog's settings can change what an operation writes.

Three questions for each of the twenty operations, answered by trying inputs
rather than by reasoning about them:

  sign     Signed Byte against Unsigned Byte, on all 256 byte values
  endian   Big Endian against Little Endian, on all 65,536 two-byte
           Unsigned Shorts, and on 65,536 four-byte Unsigned Ints
  width    Unsigned Short against Unsigned Byte, over the same two bytes,
           on all 65,536 of them

Every operand is one both sides of a comparison can hold. A "yes" needs one
input that differs, and the first one found is printed. A "no" means every
input tried agreed -- which for the Short and Byte columns is every input
there is, and for the Int column is a deterministic sample of 65,536 out of
4,294,967,296.

The formulas are the manual's C notation under C's rules, with two choices C
leaves open made the way every compiler this library runs makes them: a result
that does not fit keeps its low bits, and >> on a negative signed value copies
the sign bit. The Block Shift rows read the manual's sentence as "the values,
in order, each most significant bit first"; that reading is not measured, and
nothing says what a signed Block Shift Right fills with, so that cell is "?".

Run:  python3 which_settings_matter_py.py
"""


def signed_value(pattern, bits):
    return pattern - (1 << bits) if pattern >> (bits - 1) else pattern


def c_div(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def c_mod(a, b):
    return a - b * c_div(a, b)


def rotate_left(pattern, count, bits):
    count %= bits
    return (pattern << count | pattern >> (bits - count)) & ((1 << bits) - 1)


def swap_bytes(pattern, bits):
    return int.from_bytes(pattern.to_bytes(bits // 8, "little"), "big")


# name, which operands it takes, formula(value, bit pattern, operand, bits)
OPERATIONS = [
    ("Assign", "any", lambda v, u, k, b: k),
    ("Add", "any", lambda v, u, k, b: v + k),
    ("Subtract", "any", lambda v, u, k, b: v - k),
    ("Multiply", "any", lambda v, u, k, b: v * k),
    ("Divide", "nonzero", lambda v, u, k, b: c_div(v, k)),
    ("Negate", "none", lambda v, u, k, b: -v),
    ("Modulus", "nonzero", lambda v, u, k, b: c_mod(v, k)),
    ("Set Minimum", "any", lambda v, u, k, b: max(v, k)),
    ("Set Maximum", "any", lambda v, u, k, b: min(v, k)),
    ("Swap Bytes", "none", lambda v, u, k, b: swap_bytes(u, b)),
    ("Binary And", "any", lambda v, u, k, b: v & k),
    ("Binary Or", "any", lambda v, u, k, b: v | k),
    ("Binary Xor", "any", lambda v, u, k, b: v ^ k),
    ("Binary Invert", "none", lambda v, u, k, b: ~v),
    ("Shift Left", "count", lambda v, u, k, b: v << k),
    ("Shift Right", "count", lambda v, u, k, b: v >> k),
    ("Block Shift Left", "block", None),
    ("Block Shift Right", "block", None),
    ("Rotate Left", "count", lambda v, u, k, b: rotate_left(u, k, b)),
    ("Rotate Right", "count", lambda v, u, k, b: rotate_left(u, b - k % b, b)),
]

# Operands for one byte signed against unsigned: everything both can hold.
SIGN_OPERANDS = {"any": range(128), "nonzero": range(1, 128), "none": (0,),
                 "count": range(8), "block": range(8)}
# Operands for the endian and width columns, all of which a byte can hold.
WIDE_OPERANDS = {"any": (1, 2, 3, 5, 0x10, 0x7F, 0xFF), "nonzero": (1, 2, 3, 5, 0x10, 0x7F, 0xFF),
                 "none": (0,), "count": (1, 3, 4, 7), "block": (1, 3, 4, 7)}


def run(operation, data, bits, signed, endian, operand):
    """The bytes the dialog writes over `data`, cut into values of `bits`."""
    name, _, formula = operation
    width = bits // 8
    patterns = [int.from_bytes(data[i:i + width], endian)
                for i in range(0, len(data), width)]
    mask = (1 << bits) - 1
    if formula is None:  # a Block Shift: the values, in order, as one number
        total = bits * len(patterns)
        block = 0
        for pattern in patterns:
            block = block << bits | pattern
        if name.endswith("Left"):
            block = (block << operand) & ((1 << total) - 1)
        else:
            block >>= operand
        results = [(block >> bits * (len(patterns) - 1 - i)) & mask
                   for i in range(len(patterns))]
    else:
        results = []
        for pattern in patterns:
            value = signed_value(pattern, bits) if signed else pattern
            results.append(formula(value, pattern, operand, bits) & mask)
    return b"".join(r.to_bytes(width, endian) for r in results)


def first_difference(operation, inputs, operands, left, right):
    """The first (input, operand) the two settings disagree on, or None."""
    for data in inputs:
        for operand in operands:
            a = run(operation, data, *left, operand)
            b = run(operation, data, *right, operand)
            if a != b:
                return data, operand, a, b
    return None


BYTES = [bytes([v]) for v in range(256)]
SHORTS = [v.to_bytes(2, "big") for v in range(65536)]
# Four bytes per input: a Short, then the same Short spread by a fixed odd
# multiplier -- deterministic, so the column is the same on every run.
INTS = [v.to_bytes(2, "big") + ((v * 40503) & 0xFFFF).to_bytes(2, "big")
        for v in range(65536)]


def verdict(found):
    return "yes" if found else "no"


def main():
    print("1. WHICH SETTINGS CAN CHANGE THE BYTES AN OPERATION WRITES")
    print("-" * 72)
    print("   sign: Signed against Unsigned Byte. endian: Big against Little,")
    print("   as a Short and as an Int. width: Short against Byte, same bytes.")
    print()
    print(f"     {'operation':<19} {'sign':<6} {'endian Short':<14} {'endian Int':<12} width")
    witnesses = []
    table = {}
    for operation in OPERATIONS:
        name, takes, _ = operation
        if name == "Block Shift Right":
            sign = "?"
        else:
            found = first_difference(operation, BYTES, SIGN_OPERANDS[takes],
                                     (8, False, "little"), (8, True, "little"))
            sign = verdict(found)
            if found:
                witnesses.append((name, found))
        operands = WIDE_OPERANDS[takes]
        short = verdict(first_difference(operation, SHORTS, operands,
                                         (16, False, "little"), (16, False, "big")))
        wide = verdict(first_difference(operation, INTS, operands,
                                        (32, False, "little"), (32, False, "big")))
        width = verdict(first_difference(operation, SHORTS, operands,
                                         (8, False, "little"), (16, False, "little")))
        table[name] = (sign, short, wide, width)
        print(f"     {name:<19} {sign:<6} {short:<14} {wide:<12} {width}")
    print()

    print("2. THE FIRST INPUT ON WHICH SIGNED AND UNSIGNED DISAGREE")
    print("-" * 72)
    print("   One byte, one operand, the byte each setting writes:")
    print()
    for name, (data, operand, unsigned, signed) in witnesses:
        shown = "" if name == "Negate" else f" {operand}"
        print(f"     {name + shown:<20} on {data.hex()}   Unsigned {unsigned.hex()}   Signed {signed.hex()}")
    print()

    print("3. WHAT THE TABLE SAYS, COUNTED")
    print("-" * 72)
    untouched = [n for n, cells in table.items() if all(c == "no" for c in cells)]
    endian_free = [n for n, (_, s, i, _) in table.items() if s == "no" and i == "no"]
    short_only = [n for n, (_, s, i, _) in table.items() if s == "no" and i == "yes"]
    sign_free = [n for n, cells in table.items() if cells[0] == "no"]
    print(f"   no setting changes it:             {', '.join(untouched)}")
    print(f"   the Endian toggle cannot change:   {', '.join(endian_free)}")
    print(f"   ...on a Short, but can on an Int:  {', '.join(short_only)}")
    print(f"   signed or unsigned is the same:    {len(sign_free)} of {len(table)}")


if __name__ == "__main__":
    main()
