#!/usr/bin/env python3
"""Kata answers for Where the standard library stops.

Six jobs. For each one the question is not "can Python do it" but "can the
STANDARD LIBRARY finish it" -- and the answer key is what the standard library
actually returns, so a prediction can be checked against it.

Run:  python3 where_the_stdlib_stops_kata_py.py
"""

import locale
import unicodedata as ud

ZWJ = "\N{ZERO WIDTH JOINER}"
FAMILY = "👨" + ZWJ + "👩" + ZWJ + "👧" + ZWJ + "👦"

print("1. 'cafÃ©' arrived; get 'café' back")
print(f"   'cafÃ©'.encode('cp1252').decode('utf-8') -> {'cafÃ©'.encode('cp1252').decode('utf-8')!r}")
print("   YES, standard library. Two calls; the skill is knowing to name cp1252.")
print()

print("2. How many characters does a user see in the family emoji?")
print(f"   len(FAMILY) = {len(FAMILY)}   a user sees 1")
print("   NO. Nothing in the standard library implements UAX #29; the regex module's")
print("   \\X, uniseg or grapheme.")
print()

print("3. Is 'Straße' the same word as 'STRASSE', ignoring case?")
print(f"   lower() == lower():       {'Straße'.lower() == 'STRASSE'.lower()}")
print(f"   casefold() == casefold(): {'Straße'.casefold() == 'STRASSE'.casefold()}")
print("   YES, standard library -- but only the second call. lower() is not a fold.")
print()

print("4. Which code page is b'caf\\xe9'?")
tables = ["latin-1", "cp1252", "iso-8859-2", "cp1250", "iso-8859-15", "cp1251", "koi8-r", "mac_roman"]
readings = {t: b"caf\xe9".decode(t) for t in tables}
for t in tables:
    print(f"   {t:12} -> {readings[t]!r}")
print(f"   {len(set(readings.values()))} different readings from {len(tables)} tables, every one of them valid.")
print("   NOBODY -- not the standard library, not a detector. One byte carries no")
print("   statistics. The answer is whoever wrote the file.")
print()

print("5. Make 'Łódź' safe for an ASCII URL slug")
out = "".join(c for c in ud.normalize("NFKD", "Łódź") if not ud.combining(c))
print(f"   NFKD, drop the marks -> {out!r}   isascii(): {out.isascii()}")
print("   NO. ł has no decomposition to strip. anyascii or Unidecode say 'Lodz'.")
print()

print("6. Sort ['łódź', 'lód', 'zebra'] the way a Polish dictionary does")
words = ["łódź", "lód", "zebra"]
locale.setlocale(locale.LC_COLLATE, "C")
print(f"   sorted()            -> {sorted(words)}")
print(f"   key=locale.strxfrm  -> {sorted(words, key=locale.strxfrm)}   (C locale, as CI runs)")
print("   NO. With no locale set, strxfrm is byte order and puts ł after z. pyuca")
print("   gets close (lód, łódź, zebra, by treating ł as an l) and ICU with locale")
print("   pl gets it right, for the right reason.")
print()

print("Score: 2 of 6 the standard library finishes, 1 nobody can, 3 need a library.")
