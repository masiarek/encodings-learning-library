"""Answer key: one run of bits, cut four ways.

The kata asks for the output length of each scheme before running it. The
arithmetic is the whole family: how many bits fit in one printable symbol.
"""
import base64

DATA = b"cafe!"                     # 5 bytes = 40 bits

print(f"input   {DATA!r}   {len(DATA)} bytes = {len(DATA) * 8} bits")
print()
rows = [
    ("base16 (hex)", 4, base64.b16encode(DATA)),
    ("base32", 5, base64.b32encode(DATA)),
    ("base64", 6, base64.b64encode(DATA)),
    ("base85", 0, base64.b85encode(DATA)),
]
print(f"{'scheme':<14} {'bits/symbol':>11} {'output':<18} {'len':>4} {'growth':>7}")
for name, bits, out in rows:
    b = str(bits) if bits else "~6.4"
    print(f"{name:<14} {b:>11} {out.decode():<18} {len(out):>4} {len(out)/len(DATA):>6.2f}x")
print()
print("The growth is forced, not chosen: 8 bits of input have to be carried by")
print("symbols worth 4, 5 or 6 bits, so the ratios are 8/4, 8/5 and 8/6 --")
print("2x, 1.6x and 1.333x. Nothing is compressed and nothing is encrypted;")
print("the bits are re-cut into smaller pieces.")
print()
print("Read the base64 row again, though: 1.60x, not 1.333x. Those ratios are")
print("what you get on a WHOLE number of groups, and 5 bytes is not one --")
print("base64's group is 3 bytes, so 5 bytes is two groups with the second one")
print("mostly empty, and the padding is charged to the length. The ratio")
print("arrives as the input grows:")
for n in (3, 5, 30, 300, 3000):
    out = len(base64.b64encode(bytes(n)))
    print(f"   {n:>5} bytes -> {out:>5} characters   {out/n:.3f}x")
print("   Only the multiples of 3 sit exactly on 4/3. Everything else pays for")
print("   a partial group, and on a short field that overhead is most of the")
print("   difference between the schemes.")
print()
print("THE PADDING IS ARITHMETIC TOO")
for n in range(1, 4):
    out = base64.b64encode(DATA[:n]).decode()
    print(f"   {n} byte(s) = {n*8:2d} bits -> {out:<8} {out.count('=')} '=' character(s)")
print("   base64's unit is 3 bytes (24 bits = four 6-bit symbols). An input")
print("   that is not a multiple of 3 leaves a partial group, and '=' says how")
print("   many bytes the last group really carried. It is a length statement,")
print("   not data -- which is why some formats drop it and pass the length")
print("   along some other way.")
print()
print("AND NONE OF IT IS ABOUT TEXT")
print(f"   base64 of raw bytes: {base64.b64encode(bytes([0, 255, 128])).decode()}")
print("   The input was not text and there was no charset anywhere. Base64")
print("   takes bits. If you hand it a string you must encode that string")
print("   first, and THAT step is where the charset lives -- which is why")
print("   'base64 encoded' is never a complete description of a field.")

assert base64.b64encode(b"cafe!") == b"Y2FmZSE="
assert base64.b64decode(base64.b64encode(DATA)) == DATA
