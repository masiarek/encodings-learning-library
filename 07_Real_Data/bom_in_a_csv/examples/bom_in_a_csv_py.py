#!/usr/bin/env python3
"""The three bytes in front of a CSV header, and the lookup that fails silently.

Excel writes EF BB BF at the front of a UTF-8 CSV, and reads one correctly
only if it is there. So the same three bytes are the fix for one audience and
the bug for the other, and the whole skill is knowing which audience a given
file has. This program shows the failing lookup, the one-word fix, and -- in
section 4 -- why Excel wants the signature in the first place.

Everything runs in memory: no file is written, so the bytes shown are the
bytes discussed.

Run:  python3 bom_in_a_csv_py.py
"""

import csv
import io

BAR = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


def rows(raw: bytes, encoding: str):
    """Read CSV bytes the way open(..., encoding=...) would."""
    stream = io.TextIOWrapper(io.BytesIO(raw), encoding=encoding, newline="")
    reader = csv.DictReader(stream)
    return reader, list(reader)


# What Excel writes when you Save As "CSV UTF-8".
EXCEL = "﻿id,name\n1,Ada\n2,Ben\n".encode("utf-8")
CLEAN = "id,name\n1,Ada\n2,Ben\n".encode("utf-8")

# ------------------------------------------------------------------ 1
head(1, "WHAT ARRIVED")
print(f"   {'from Excel':<14} {EXCEL[:12].hex(' ')} ...")
print(f"   {'from a script':<14} {CLEAN[:12].hex(' ')} ...")
print()
print("   The first three bytes are the difference, and on screen there is no")
print("   difference at all -- both files show 'id,name' on line 1. This is")
print("   the entire bug: the evidence is invisible in every tool that shows")
print("   you text, and obvious in the one that shows you bytes.")

# ------------------------------------------------------------------ 2
head(2, "READ AS PLAIN utf-8: THE LOOKUP THAT FAILS")
reader, data = rows(EXCEL, "utf-8")
print(f"   reader.fieldnames   {reader.fieldnames}")
print(f"   first row           {data[0]}")
print()
first_key = reader.fieldnames[0]
print(f"   the header, printed  '{first_key}'      <- looks exactly like 'id'")
print(f"   the header, repr     {first_key!r}")
print(f"   len()                {len(first_key)}   <- three characters, not two")
print(f"   == 'id'              {first_key == 'id'}")
try:
    data[0]["id"]
except KeyError as e:
    print(f"   row['id']            KeyError: {e}")
print()
print("   Read that pair of lines again. print() shows 'id' and the lookup on")
print("   'id' raises, because U+FEFF is zero width -- it takes up no space on")
print("   screen and one place in the string. A colleague who pastes the")
print("   header into a chat message pastes something that looks right.")

# ------------------------------------------------------------------ 3
head(3, "READ AS utf-8-sig: THE WHOLE FIX")
for label, raw in (("from Excel   ", EXCEL), ("from a script", CLEAN)):
    reader, data = rows(raw, "utf-8-sig")
    print(f"   {label}  fieldnames={reader.fieldnames}   row['id']={data[0]['id']!r}")
print()
print("   One word in the open() call, and note the second line: utf-8-sig on")
print("   a file that never had a signature does nothing at all. There is no")
print("   penalty for being wrong about which kind of file you were sent, so")
print("   for a CSV of unknown origin it is simply the correct reader.")

# ------------------------------------------------------------------ 4
head(4, "AND WHY EXCEL WANTED IT: THE OTHER DIRECTION")
dash_row = "id,note\n1,before—after\n"
raw = dash_row.encode("utf-8")
print(f"   your script writes this row     {dash_row.splitlines()[1]!r}")
print(f"   in UTF-8, that is               {dash_row.splitlines()[1].encode('utf-8').hex(' ')}")
print(f"   and the em dash is              {'—'.encode('utf-8').hex(' ')}   (U+2014)")
print()
print("   Now Excel opens it by double-click with no signature to go on, and")
print("   falls back to the machine's legacy code page:")
for table, where in (("mac_roman", "Excel on a Mac"), ("cp1252", "Excel on Windows")):
    print(f"     read as {table:<10} ({where:<17}) -> {raw.decode(table).splitlines()[1]!r}")
print(f"     read as {'utf_8_sig':<10} ({'told the truth':<17}) -> "
      f"{(chr(0xFEFF) + dash_row).encode('utf-8').decode('utf_8_sig').splitlines()[1]!r}")
print()
print("   Same file, three readings. The two guesses are mojibake, and they")
print("   are DIFFERENT mojibake -- so the garbage in the bug report tells you")
print("   which desk it was opened on before you have asked. Writing the")
print("   signature removes the guess, which is the only reason to write one.")

# ------------------------------------------------------------------ 5
head(5, "SO: WHO READS THIS FILE?")
print("   for a human, in Excel        -> write 'utf-8-sig'.")
print("     the file's job is to be double-clicked; nothing parses it; the")
print("     three bytes buy a correct guess and cost nothing.")
print()
print("   for a program, by exact bytes -> write 'utf-8'.")
print("     a header match, a ^-anchored grep, a diff, a JSON step downstream:")
print("     the mark is content and every one of those fails silently.")
print()
print("   unknown, or both              -> write 'utf-8', read 'utf-8-sig'.")
print("     the forgiving reader costs nothing and covers files you did not")
print("     write. This is the default worth reaching for.")
print()
print("   One more, easy to forget once the signature is in:")
joined = EXCEL + EXCEL
print(f"     two signed CSVs concatenated: {joined[:20].hex(' ')} ...")
print(f"     ..and at the join:            ... {joined[20:32].hex(' ')}")
print("     The second signature is in the middle of the file now, where it")
print("     is not a signature -- it is an invisible character in a data row.")
print("     Concatenating CSVs is common; strip on read, then join.")
