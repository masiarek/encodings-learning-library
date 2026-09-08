"""Answer key: two spellings, four forms, and the three places it bites."""
import unicodedata as ud

NFC, NFD = "café", "café"

print("TWO STRINGS THAT DRAW THE SAME")
for label, s in [("NFC", NFC), ("NFD", NFD)]:
    print(f"   {label}  {s}  len {len(s)}  bytes {len(s.encode())}  "
          f"{' '.join('%04X' % ord(c) for c in s)}")
print(f"   equal? {NFC == NFD}     hash equal? {hash(NFC) == hash(NFD)}")
print()
print("THE FOUR FORMS")
print(f"   {'form':<6} {'café':<10} {'ﬁle':<8} {'2⁵':<6} what it does")
for form in ["NFC", "NFD", "NFKC", "NFKD"]:
    a, b, c = (ud.normalize(form, x) for x in (NFD, "ﬁle", "2⁵"))
    kind = "composes" if form in ("NFC", "NFKC") else "decomposes"
    compat = "and folds compatibility spellings" if "K" in form else "canonical only"
    print(f"   {form:<6} {a:<10} {b:<8} {c:<6} {kind}, {compat}")
print()
print("   The K forms are LOSSY on purpose: 2⁵ becomes 25 and the ligature")
print("   becomes two letters. That is right for a search index and wrong for")
print("   anything you will display back to the person who typed it.")
print()
print("THE THREE PLACES IT BITES")
print(f"   1. comparison   NFC == NFD is {NFC == NFD}")
d = {NFC: 1}
print(f"   2. dict/set     {{NFC: 1}}.get(NFD) -> {d.get(NFD)}   (the key is not there)")
print(f"   3. length       {len(NFC)} vs {len(NFD)} code points for one four-letter word")
print("   A dict lookup that misses is the worst of the three, because nothing")
print("   raises -- the key is simply not there, and the two keys print the")
print("   same in the traceback.")
print()
print("WHERE THE TWO SPELLINGS COME FROM")
print("   Not from carelessness. A Mac's filesystem has historically handed")
print("   back decomposed names, most keyboards and most Windows software")
print("   produce composed ones, and both are correct Unicode. So a filename")
print("   that made a round trip through macOS and a filename typed on Windows")
print("   can be the same word and different strings.")
print()
print("THE RULE")
print("   Normalize at the BOUNDARY -- once, on the way in -- and store one")
print("   form. Normalizing to compare is free; normalizing in place is an")
print("   edit to somebody's data, and NFKC in particular cannot be undone.")

assert NFC != NFD and ud.normalize("NFC", NFD) == NFC
assert ud.normalize("NFKC", "2⁵") == "25"
