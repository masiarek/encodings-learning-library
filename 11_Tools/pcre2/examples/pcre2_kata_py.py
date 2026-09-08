"""Answer key: what the second engine buys, and what it costs.

rg -P is on neither runner, so the two engines' *rules* are demonstrated with
Python's re -- which, like ripgrep's default engine, has no grapheme support
and no backreferences-in-lookbehind, and so lands on the same side of every
line drawn here.
"""
import re

FLAG = "e\u0301"          # e + COMBINING ACUTE: one grapheme, two code points
print(f"the string   {FLAG!r}   draws as {FLAG}")
print(f"   code points {len(FLAG)}   bytes {len(FLAG.encode())}   graphemes 1")
print()
print("1. WHAT THE DEFAULT ENGINE CANNOT DO")
print(f"   re.match('.', s) matches {re.match('.', FLAG).group()!r} -- one CODE POINT, the bare e")
print("   There is no pattern in Python's re, and none in ripgrep's default")
print("   engine, that means 'one grapheme cluster'. \\X is the PCRE2 spelling")
print("   and it is the single strongest reason to reach for -P: it is the only")
print("   regex engine already on your machine that can match what a person")
print("   would call one character.")
print()
print("2. THE OTHER THINGS -P BUYS")
for what, why in [
    ("\\X", "one grapheme cluster -- the headline"),
    ("look-behind", "(?<=...) -- ripgrep's default engine has none at all"),
    ("backreferences", "\\1 inside the pattern"),
    ("\\p{...} with more properties", "PCRE2 ships its own Unicode tables"),
]:
    print(f"   {what:<28} {why}")
print()
print("3. WHAT IT COSTS, AND THIS IS THE PART THAT BITES")
print("   The default engine is a finite automaton: linear time, no backtracking,")
print("   and it REFUSES a pattern it cannot run in linear time -- with a")
print("   paragraph of advice naming the flag that would help.")
print("   PCRE2 backtracks. So the same pattern that was refused now runs, and")
print("   on adversarial input it can take exponential time.")
print()
print("   The failure that matters is quieter than that, though. rg -P on a")
print("   build without PCRE2 support, or on a pattern PCRE2 rejects, can")
print("   match NOTHING and say NOTHING -- no error, no advice, exit 1, which")
print("   is indistinguishable from 'the text is not there'. The default")
print("   engine's refusal is loud; -P's is not.")
print()
print("4. AND IT IS A SECOND UNICODE IMPLEMENTATION")
print("   PCRE2 has its own copy of the Unicode tables, on its own release")
print("   schedule, separate from ripgrep's and from your Python's. So")
print(r"   \p{Alphabetic} can legitimately disagree between rg and rg -P on the")
print("   same machine in the same second, and neither is out of date.")
print("   That is the same shape as every other 'whose table is this' problem")
print("   in this library, one level further in.")
print()
print("THE RULE")
print("   Reach for -P when you need \\X or a look-behind, and know that you")
print("   have swapped a linear engine that refuses for a backtracking one that")
print("   might silently do nothing. Check that your rg has it:  rg --pcre2-version")

assert len("e\u0301") == 2
assert re.match(".", "e\u0301").group() == "e"
