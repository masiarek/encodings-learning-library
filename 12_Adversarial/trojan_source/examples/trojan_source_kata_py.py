"""Answer key: two readers of one file, and the one with no access to the bytes."""
import unicodedata as ud

RLO, PDI, LRI = "‮", "⁩", "⁦"
src = f'if access_level != "user{RLO}{PDI} {LRI}// Check if admin{PDI} {LRI}":'

print("THE LINE, AS CODE POINTS")
print(f"   length {len(src)} characters, {len(src.encode())} bytes")
bidi = [(i, c) for i, c in enumerate(src) if ud.category(c) == "Cf"]
print(f"   invisible format characters at index {[i for i, _ in bidi]}:")
for i, c in bidi:
    print(f"      {i:>3}  U+{ord(c):04X}  {ud.name(c)}")
print()
print("   Every one of those has General_Category Cf -- FORMAT. They have no")
print("   width, no glyph and no effect on what the parser reads. They change")
print("   only the ORDER a renderer draws the surrounding text in.")
print()
print("THE TWO READERS")
print("   the compiler   reads the ordered list of code points, in order, and")
print("                  ignores Cf characters entirely")
print("   the reviewer   reads a RENDERING, produced by a bidi algorithm that")
print("                  is doing exactly what those characters ask")
print("   Both are correct. They are given different objects.")
print()
print("WHY THE REVIEWER IS THE VULNERABLE ONE")
print("   Every other reader in the pipeline sees the bytes: the compiler, the")
print("   linter, the test suite, git's own hashing. The code reviewer is the")
print("   only participant whose input is a picture -- and a picture is the one")
print("   representation the attacker gets to choose.")
print()
print("THE DETECTION, WHICH IS THREE LINES")
def scan(text):
    return [(i, "U+%04X" % ord(c), ud.name(c, "?")) for i, c in enumerate(text)
            if ud.category(c) == "Cf"]
print("   [c for c in text if unicodedata.category(c) == 'Cf']")
print(f"   -> {len(scan(src))} hits on this line, 0 on ordinary source")
print("   That is a whole-repo grep, it has no false-negative story to worry")
print("   about, and it belongs in CI rather than in a reviewer's eyes. GitHub,")
print("   rustc and gcc all added warnings for exactly this after CVE-2021-42574.")
print()
print("THE GENERAL LESSON")
print("   Any time a human approves something on the strength of a rendering,")
print("   the rendering is part of the trust boundary. Source review, a diff, a")
print("   signed document, a URL in an address bar -- the question is always")
print("   whether the thing the person SAW is the thing that will ACT.")

assert any(ud.category(c) == "Cf" for c in src)
assert len(scan(src)) == 5
