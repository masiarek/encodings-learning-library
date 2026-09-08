"""Answer key: one bad byte, four languages, and what is left of the check.

Every language decodes UTF-8 by the same rules. The kata is about WHERE the
check happens and what remains of it in the type system afterwards.
"""
BAD = b"caf\xe9.txt"           # a Latin-1 é loose in a stream declared UTF-8

print(f"the bytes   {BAD.hex(' ')}   -- e9 is not a legal UTF-8 lead byte")
print()
print("PYTHON: THE CHECK IS AT THE DOOR, AND THEN IT IS OVER")
try:
    BAD.decode("utf-8")
except UnicodeDecodeError as e:
    print(f"   strict            UnicodeDecodeError at byte {e.start}")
print(f"   errors='replace'  {BAD.decode('utf-8', 'replace')!r}   lossy, and cannot be undone")
print(f"   errors='surrogateescape' {BAD.decode('utf-8', 'surrogateescape')!r}")
print(f"   ...and back       {BAD.decode('utf-8', 'surrogateescape').encode('utf-8', 'surrogateescape') == BAD}")
print("   Once decode() returns, the value is a str and the str type makes no")
print("   promise about where it came from. Nothing downstream can tell a")
print("   checked string from a repaired one -- which is why the error handler")
print("   is a POLICY DECISION and not a convenience.")
print()
print("RUST: THE CHECK IS AT THE DOOR AND THE TYPE REMEMBERS")
print("   String::from_utf8(v)        -> Result<String, FromUtf8Error>")
print("   String::from_utf8_lossy(v)  -> Cow<str>, U+FFFD substituted")
print("   str::from_utf8_unchecked    -> unsafe, and the word is the point")
print("   A &str is a PROOF that the bytes were checked. The check happens")
print("   once, at the same boundary Python checks at, and then it is carried")
print("   in the type -- so a function taking &str cannot be handed unchecked")
print("   bytes by accident, and no later code re-validates 'to be safe'.")
print()
print("C: THERE IS NO DOOR")
print("   char* is bytes. Nothing decodes, so nothing can refuse, and a")
print("   sequence like this travels to the far end of the program unexamined")
print("   -- where strlen counts 8, printf emits whatever the terminal makes of")
print("   it, and the first thing that notices is a person looking at output.")
print()
print("WHAT THE THREE HAVE IN COMMON, WHICH IS THE ACTUAL LESSON")
print("   All three agree these bytes are not UTF-8. The decoders are the same")
print("   algorithm. What differs is how much of that knowledge survives the")
print("   function call:")
print("       C       nothing was ever asked")
print("       Python  it was asked and the answer was discarded")
print("       Rust    it was asked and the answer is in the type")
print()
print("   So 'is this string valid' is a question you can only ask at a")
print("   boundary. One byte further in, the honest answer in two of the three")
print("   languages is: it depends who checked, and you cannot find out.")

assert BAD.decode("utf-8", "surrogateescape").encode("utf-8", "surrogateescape") == BAD
