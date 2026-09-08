#!/usr/bin/env python3
"""Kata answer key: seven numbers for one two-character string.

Every number below is a count at a named layer of the model. None of them is
"the length of the string", and no two adjacent rows are answering the same
question -- which is the whole exercise.

Run:  python3 the_encoding_model_kata_py.py
"""

TEXT = "ż\U0001F600"  # U+017C, U+1F600


def units(text, codec, width):
    return len(text.encode(codec)) // width


rows = [
    ("code points", len(TEXT), "the CCS layer -- what Python's len() counts"),
    ("UTF-8 code units", units(TEXT, "utf-8", 1), "2 for ż, 4 for the emoji"),
    ("UTF-16 code units", units(TEXT, "utf-16be", 2), "1 for ż, a surrogate PAIR for the emoji"),
    ("UTF-32 code units", units(TEXT, "utf-32be", 4), "one unit per code point, always"),
    ("bytes, utf-16le", len(TEXT.encode("utf-16le")), "3 units x 2 bytes, no mark"),
    ("bytes, utf-16", len(TEXT.encode("utf-16")), "the compound scheme: the same 6, after a 2-byte mark"),
    ("bytes, utf-8-sig", len(TEXT.encode("utf-8-sig")), "6 + a 3-byte signature that marks nothing"),
]

print(f"TEXT = {TEXT!r}   (U+017C, U+1F600)\n")
for label, n, why in rows:
    print(f"   {label:20} {n:2}   {why}")

print("""
   Row 5 against row 6 is the form/scheme boundary in two numbers, and
   rows 2, 3 and 4 are one code point counted three ways.

   The last question has no row because the answer is that nothing
   moves: on a big-endian machine every count above is unchanged. Byte
   ORDER is a property of the scheme, and a count is not an order --
   which is why utf-16be and utf-16le never differ in length.""")
