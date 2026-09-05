# Mojibake round trip

**Level:** 201 · for anyone repairing data

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** When a file was written as UTF-8 and read as Latin-1, the damage is reversible byte for byte — `s.encode('latin-1').decode('utf-8')` — and when it was written with `?` in place of the character, the data is gone and no amount of cleverness gets it back.

## What the finished page has to answer

- The reversible case: why Latin-1 is the one table that round-trips every byte, so the original bytes are still there inside the wrong string
- The CP1252 variant: the same trick with `cp1252`, and the five bytes it cannot round-trip (`0x81 0x8D 0x8F 0x90 0x9D`) that make it fail one time in fifty
- Double and triple encoding: repairing in layers, and the test that tells you when to stop
- The irreversible cases: `?`, `U+FFFD`, and `ignore` — each a byte thrown away at write time
- A repair function with a guard: it returns the input unchanged when the round trip does not produce valid UTF-8, so it can never make things worse

## The example it will run

Python: damage `'Zażółć gęślą jaźń'` four ways, repair the reversible three, and show the irreversible one staying broken.

## See also

- [Mojibake](../../03_Encodings/mojibake/README.md)
- [SAP code pages](../sap_code_pages/README.md)
