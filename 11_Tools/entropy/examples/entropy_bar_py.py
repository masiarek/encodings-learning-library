"""Entropy is a histogram: Ghidra's overview score, computed on chunks chosen by hand.

Ghidra's Entropy overview bar cuts a program's bytes into chunks -- 1024 by
default -- counts how often each of the 256 byte values occurs in a chunk, and
turns the counts into one number from 0.0 to 8.0, which it paints as a colour
down the right edge of the Listing. This program does the same arithmetic on
chunks built in memory, so the answer key is the same on every machine, and
then applies Ghidra 12.1.3's own constants -- the seven named ranges, the
palette quantisation, the log table -- to see where those chunks land. Nothing
here runs Ghidra: what the page says Ghidra does is read off its source at the
12.1.3 tag and linked from the page.

Run:  python3 entropy_bar_py.py
"""
import codecs
import hashlib
import math
import zlib
from collections import Counter

# A chunk of real prose, because the score needs a whole chunk of natural text
# and the cast (CAST.md) has words rather than paragraphs. The opening of the
# Declaration of Independence, 1776: public domain, and pure ASCII, so its
# UTF-8, Latin-1 and Windows-1252 spellings are the same bytes.
PROSE = (
    "When in the Course of human events, it becomes necessary for one people "
    "to dissolve the political bands which have connected them with another, "
    "and to assume among the powers of the earth, the separate and equal "
    "station to which the Laws of Nature and of Nature's God entitle them, a "
    "decent respect to the opinions of mankind requires that they should "
    "declare the causes which impel them to the separation. We hold these "
    "truths to be self-evident, that all men are created equal, that they are "
    "endowed by their Creator with certain unalienable Rights, that among "
    "these are Life, Liberty and the pursuit of Happiness. That to secure "
    "these rights, Governments are instituted among Men, deriving their just "
    "powers from the consent of the governed, That whenever any Form of "
    "Government becomes destructive of these ends, it is the Right of the "
    "People to alter or to abolish it, and to institute new Government, "
    "laying its foundation on such principles and organizing its powers in "
    "such form, as to them shall seem most likely to effect their Safety and "
    "Happiness. Prudence, indeed, will dictate that Governments long "
    "established should not be changed for light and transient causes; and "
    "accordingly all experience hath shewn, that mankind are more disposed to "
    "suffer, while evils are sufferable, than to right themselves by "
    "abolishing the forms to which they are accustomed. But when a long train "
    "of abuses and usurpations, pursuing invariably the same Object evinces a "
    "design to reduce them under absolute Despotism, it is their right, it is "
    "their duty, to throw off such Government, and to provide new Guards for "
    "their future security. Such has been the patient sufferance of these "
    "Colonies; and such is now the necessity which constrains them to alter "
    "their former Systems of Government. The history of the present King of "
    "Great Britain is a history of repeated injuries and usurpations, all "
    "having in direct object the establishment of an absolute Tyranny over "
    "these States. To prove this, let Facts be submitted to a candid world."
)

CHUNK = 1024                                    # EntropyChunkSize.LARGE, the default


def entropy(chunk: bytes) -> float:
    """-sum p(x) log2 p(x) over the byte histogram: 0.0 for one value, 8.0 for all 256 equally."""
    n = len(chunk)
    return 0.0 - sum(c / n * math.log2(c / n) for c in Counter(chunk).values())   # 0.0 -, not -sum: no -0.00


def values(chunk: bytes) -> int:
    return len(set(chunk))


# The seven named ranges of EntropyKnot.java, Ghidra 12.1.3: option label, name
# shown in the tooltip and legend, centre, and half-width.
KNOTS = {
    "x86":        ("x86 code",      5.94,   0.4),
    "arm":        ("ARM code",      5.1252, 0.51),
    "thumb":      ("THUMB code",    6.2953, 0.5),
    "powerpc":    ("PowerPC code",  5.6674, 0.52),
    "ascii":      ("ASCII strings", 4.7,    0.5),
    "compressed": ("Compressed",    8.0,    0.5),
    "utf16":      ("Unicode UTF16", 3.21,   0.2),
}
DEFAULT_SLOTS = ["compressed", "x86", "ascii", "utf16"]   # Entropy Range 1..4; Range 5 is None


def palette_index(score: float) -> int:
    """EntropyOverviewColorService.quantizeChunk: floor(score / 8 * 256), at most 255."""
    return min(math.floor(score / 8.0 * 256.0), 255)


def band(name: str) -> tuple[int, int]:
    """The palette indexes a named range claims, both ends inclusive.

    EntropyOverviewOptionsManager.addPaletteKnot floors centre and half-width
    onto the 256-entry palette; OverviewPalette.addKnot mirrors the start
    about the centre for the end; KnotRecord.contains is start <= i <= end.
    """
    _, centre, width = KNOTS[name]
    point = min(math.floor(32.0 * centre), 255)
    start = max(point - math.floor(32.0 * width), 0)
    end = min(2 * (point - start) + 1 + start, 256)
    return start, end


def tooltip_name(score: float, slots=DEFAULT_SLOTS) -> str:
    """getKnotName: the first configured slot whose band contains the palette index, else nothing."""
    i = palette_index(score)
    for name in slots:
        start, end = band(name)
        if start <= i <= end:
            return name
    return "-"


def band_text(name: str) -> str:
    start, end = band(name)
    return f"{start / 32:.2f} to {(end + 1) / 32:.2f}"


def section(n: int, title: str) -> None:
    print(f"{n}. {title}")
    print("-" * 72)


section(1, "THE SCORE, ON CHUNKS BUILT BY HAND")
rows = [
    ("1024 bytes of 00", bytes(1024)),
    ("512 x 'a', then 512 x 'b'", b"a" * 512 + b"b" * 512),
    ("'abcd' x 256", b"abcd" * 256),
    ("512 x 'a', 256 x 'b', 256 x 'c'", b"a" * 512 + b"b" * 256 + b"c" * 256),
    ("every byte value, four times over", bytes(range(256)) * 4),
]
print(f"   {'chunk':<36} {'values':>6}   {'score':>5}   2^score")
for label, chunk in rows:
    h = entropy(chunk)
    print(f"   {label:<36} {values(chunk):>6}   {h:5.2f}   {2 ** h:7.2f}")
print()
print("   The fourth row, written out: p(a) = 1/2, p(b) = p(c) = 1/4, so")
print("   H = -(1/2)log2(1/2) - 2 x (1/4)log2(1/4) = 0.5 + 1.0 = 1.5 bits.")
print("   Read 2^H as how many EQUALLY likely values would spread this much:")
print("   one value is 0 bits, two are 1 bit, all 256 are 8 bits, and the")
print("   1.5-bit chunk is spread like 2.83 equally likely values.")
print()

section(2, "ONE PARAGRAPH OF ENGLISH, SIX ENCODINGS, THE FIRST 1024 BYTES OF EACH")
print(f"   {'encoding':<9} {'values':>6}   {'score':>5}   log2(values)   Ghidra's name for it")
samples: dict[str, bytes] = {}
for enc in ["utf-8", "cp037", "utf-16le", "utf-16be", "utf-32le", "utf-32be"]:
    chunk = PROSE.encode(enc)[:CHUNK]
    samples[enc] = chunk
    h = entropy(chunk)
    print(f"   {enc:<9} {values(chunk):>6}   {h:5.2f}   {math.log2(values(chunk)):12.2f}   {tooltip_name(h)}")
print()
print("   Where the encoding itself caps the score. A fraction f of every")
print("   chunk is one fixed byte, and the rest is spread over at most k values:")


def cap(fixed: float, k: int) -> float:
    rest = 1.0 - fixed
    return (0.0 if fixed == 0 else -fixed * math.log2(fixed)) + rest * math.log2(k / rest)


for label, fixed, k in [
    ("ASCII: bit 7 is never set, so 128 values at most", 0.0, 128),
    ("UTF-16 of ASCII: every other byte is 00", 0.5, 128),
    ("UTF-32 of ASCII: three bytes in four are 00", 0.75, 128),
    ("any byte at all", 0.0, 256),
]:
    print(f"   {label:<52} cap {cap(fixed, k):4.2f}")
print()
print("   English is well under its cap in every encoding -- letters are not")
print("   equally likely -- but the caps are why the encodings sort into")
print("   Ghidra's bands: the same paragraph is 'ascii' in UTF-8 and in")
print("   EBCDIC, 'utf16' in either byte order, and below every named range")
print("   in UTF-32.")
print()

section(3, "ORDER, REPETITION AND A SUBSTITUTION ARE INVISIBLE TO IT")
chunk = samples["utf-8"]
rows = [
    ("as written", chunk),
    ("the same bytes, sorted", bytes(sorted(chunk))),
    ("the same bytes, reversed", chunk[::-1]),
    ("the same 1024 bytes twice over", chunk * 2),
    ("ROT13", codecs.encode(PROSE, "rot13").encode("ascii")[:CHUNK]),
    ("EBCDIC (cp037)", samples["cp037"]),
]
for label, data in rows:
    print(f"   {label:<34} {len(data):>5} bytes   {entropy(data):5.2f}")
print()
print("   Six inputs, one score. The histogram is the whole input: the order")
print("   of the bytes never enters the sum, a chunk repeated has the same")
print("   proportions, and a one-to-one substitution of values -- ROT13, or")
print("   ASCII to EBCDIC -- moves the bars of the histogram without changing")
print("   their heights. So 'ascii' is Ghidra's name for a text-shaped")
print("   histogram, and an EBCDIC string table earns it too.")
print()

section(4, "WHAT SCORES 8.0, AND WHETHER IT WOULD COMPRESS")
counter = bytes(range(256)) * 4
chain, block = bytearray(), b""
while len(chain) < CHUNK:                       # SHA-256 chained on itself: fixed, and spread like noise
    block = hashlib.sha256(block + b"entropy").digest()
    chain += block
chain = bytes(chain[:CHUNK])
samples["counter"], samples["chain"] = counter, chain
print(f"   {'chunk':<40} {'score':>5}   name         zlib -9 shrinks it below a third")
for label, data in [
    ("00 01 02 .. ff, four times over", counter),
    ("1024 bytes of chained SHA-256", chain),
]:
    h = entropy(data)
    shrinks = len(zlib.compress(data, 9)) < len(data) / 3
    print(f"   {label:<40} {h:5.2f}   {tooltip_name(h):<12} {shrinks}")
print()
print("   The counter scores a perfect 8.0 and compresses to a fraction; the")
print("   hash chain scores less -- 1024 draws over 256 values leave the")
print("   histogram bumpy -- and does not compress at all. Entropy measures")
print("   how evenly the values are spread, not whether the bytes carry")
print("   information, so 'compressed' is Ghidra's name for a flat histogram:")
print("   compressed data has one, encrypted data has one, and so does a")
print("   table that walks through every value.")
print()

section(5, "WHERE EACH CHUNK LANDS, IN THE DEFAULT PALETTE")
print("   Ghidra's four default ranges, in slot order, as integer bands of")
print("   the 256-entry palette (the Rust example derives them):")
for name in DEFAULT_SLOTS:
    start, end = band(name)
    print(f"   {KNOTS[name][0]:<14} {name:<11} index {start:>3} to {end:>3}   score {band_text(name)}")
print()
print(f"   {'chunk':<28} {'score':>5}   index   tooltip prints   name")
for label, data in [
    ("English, UTF-8", samples["utf-8"]),
    ("English, UTF-16LE", samples["utf-16le"]),
    ("English, UTF-32LE", samples["utf-32le"]),
    ("'abcd' x 256", b"abcd" * 256),
    ("chained SHA-256", chain),
    ("00 01 02 .. ff, x 4", counter),
]:
    h = entropy(data)
    i = palette_index(h)
    print(f"   {label:<28} {h:5.2f}   {i:>5}   {i * 8.0 / 255:14.4f}   {tooltip_name(h)}")
print()
print("   The tooltip does not print the score. Ghidra keeps floor(score x 32)")
print("   as a palette index and prints index x 8 / 255 -- 256 steps in, 255")
print("   steps out -- so every number it shows is a little high, by up to")
print("   1/32 plus 0.4%. Its format is #0.0, which hides all of that.")
print()

section(6, "THE LAST CHUNK OF A MEMORY BLOCK IS SCORED AGAINST A FULL ONE")


def ghidra_index(chunk: bytes, chunk_size: int = CHUNK) -> int:
    """quantizeChunk over computeHistogram(bytesRead): each count is divided by
    the CHUNK SIZE (buildLogTable), not by the number of bytes actually read."""
    total = 0.0
    for c in Counter(chunk).values():
        p = c / chunk_size
        total += -p * math.log2(p)
    return min(math.floor(total / 8.0 * 256.0), 255)


print(f"   {'chunk read from the block':<38} {'true':>5}   ghidra index   tooltip   name")
for label, data in [
    ("every value x 4 (1024 bytes)", counter),
    ("every value x 2 (512 bytes)", bytes(range(256)) * 2),
    ("every value x 1 (256 bytes)", bytes(range(256))),
    ("English, UTF-8 (1024 bytes)", samples["utf-8"]),
    ("English, UTF-8 (512 bytes)", samples["utf-8"][:512]),
]:
    i = ghidra_index(data)
    print(f"   {label:<38} {entropy(data):5.2f}   {i:>12}   {i * 8.0 / 255:7.2f}   {tooltip_name(i * 8.0 / 256)}")
print()
print("   Chunks are cut from the start of each memory block, so a block whose")
print("   length is not a multiple of the chunk size ends in a short one, and")
print("   the short one is scored with its counts divided by 1024 rather than")
print("   by the bytes it has. A 512-byte tail of perfectly flat data scores")
print("   4.5 instead of 8.0 -- and 4.5 is inside the 'ascii' band, which is")
print("   what the tooltip would then call it. Read off the 12.1.3 source, not")
print("   run through Ghidra; the page links the three methods involved.")
print()

section(7, "CHUNK SIZE: THE OPTION TRADES DETAIL FOR STEADINESS")
text = PROSE.encode("ascii")
print(f"   the paragraph is {len(text)} bytes; full chunks only")
print(f"   {'chunk size':>10}   chunks   {'lowest':>6}   {'highest':>7}   spread   all in the 'ascii' band")
for size in [1024, 512, 256]:
    scores = [entropy(text[i:i + size]) for i in range(0, len(text) - size + 1, size)]
    lo, hi = min(scores), max(scores)
    inside = all(tooltip_name(s) == "ascii" for s in scores)
    print(f"   {size:>10}   {len(scores):>6}   {lo:6.2f}   {hi:7.2f}   {hi - lo:6.2f}   {inside}")
print()
print("   Smaller chunks draw finer detail down the bar and score less")
print("   steadily, because a histogram of 256 buckets filled from 256 bytes")
print("   is mostly empty buckets. The same paragraph, cut finer, spreads")
print("   over a wider range of scores.")
