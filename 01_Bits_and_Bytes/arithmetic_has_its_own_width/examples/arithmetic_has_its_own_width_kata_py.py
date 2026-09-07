"""Answer key: three expressions, and only one of them fits back in the byte.

The kata asks for each expression twice -- as arithmetic, and as what survives
being stored back into eight bits. Python is the right language to answer in
because its integers never overflow, so the two columns can be printed side by
side and the difference is visible rather than inferred.
"""

CASES = [("200 + 100", 200 + 100), ("255 << 2", 255 << 2), ("1 << 9", 1 << 9), ("60 + 5", 60 + 5)]

print(f"{'expression':<12} {'arithmetic':>10} {'stored in a byte':>17}   fits?")
for label, wide in CASES:
    stored = wide & 0xFF
    print(f"{label:<12} {wide:>10} {stored:>17}   {'yes' if stored == wide else 'NO -- lost ' + str(wide - stored)}")

print()
print("Only 60 + 5 comes back. The other three are not wrong arithmetic: 300,")
print("1020 and 512 are the right answers, and Python, the shell's $(( )) and")
print("C's int all produce them. What differs is the BOX you put the answer in.")
print()
print("The masking is what a fixed-width type does for you, and where it")
print("happens is the whole lesson:")
print("  * Python  -- never. int grows; you only lose bits if you write & 0xFF.")
print("  * Rust    -- at the operator. 255u8 << 2 is 252 in release and a panic")
print("               in debug, because the type is eight bits all the way")
print("               through. There is no wide intermediate to look at.")
print("  * C       -- at the STORE. The operands are promoted to int, so the")
print("               expression really is 1020, and the truncation happens")
print("               silently when it lands back in a uint8_t.")
print()
print("That is why the same source line gives three answers, and why 'it")
print("overflowed' is not a useful sentence until you say where.")

assert (255 << 2) & 0xFF == 252
assert (1 << 9) & 0xFF == 0, "512 masks to zero -- the whole value is gone"
