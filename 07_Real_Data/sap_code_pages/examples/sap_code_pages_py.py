"""SAP names encodings by number. So do IBM and Microsoft, and they disagree.

Everything printed here about EBCDIC and about Python's codecs is measured by
this program. Everything about SAP's OWN numbering is a claim to verify
against the system that will run your job -- the program says so where it
matters, because a wrong number here is a wrong interface.
"""

import codecs
import string


def _ok(name):
    """True when this Python has a codec by that name."""
    try:
        codecs.lookup(name)
    except LookupError:
        return False
    return True

# SAP's numbers, as this library has met them. NOT verified by this program:
# nothing in the standard library knows what SAP calls a table. Treat this as
# a starting point for a lookup on your own system, never as an answer.
SAP_TO_PYTHON = [
    ("1100", "latin-1", "ISO-8859-1, western European"),
    ("1160", "cp1252", "Windows-1252"),
    ("1401", "iso8859-2", "ISO-8859-2, central European"),
    ("4110", "utf-8", "UTF-8"),
    ("4102", "utf-16-be", "UTF-16, big-endian"),
    ("4103", "utf-16-le", "UTF-16, little-endian"),
]

print("1. THREE NUMBERING SYSTEMS, ALL SPELLED 'CODE PAGE N'")
print("-" * 72)
print("   SAP numbers its tables, IBM numbers its CCSIDs, and Microsoft")
print("   numbers its Windows code pages. The three schemes are unrelated,")
print("   and Python's codec names follow IBM and Microsoft:")
print()
for number in ("1100", "1160", "4110", "037", "1140", "1252"):
    name = f"cp{number}"
    try:
        codecs.lookup(name)
        verdict = "resolves"
    except LookupError:
        verdict = "LookupError -- no such codec"
    print(f"      codecs.lookup({name!r})".ljust(34) + verdict)
print()
print("   So SAP's numbers are not typeable into Python at all: cp1100 is")
print("   not a codec, while cp1252 and cp1140 are -- and cp1140 is IBM's")
print("   EBCDIC, nothing to do with any SAP number that looks like it.")
print("   You need a mapping, and it has to come from the system.")
print()
print("   A starting point, TO BE VERIFIED against your own system's")
print("   code-page table before you rely on any row:")
print()
print(f"      {'SAP':<6} {'Python codec':<14} what it is")
for sap, codec_name, what in SAP_TO_PYTHON:
    print(f"      {sap:<6} {codec_name:<14} {what}")
resolvable = sum(1 for _, codec_name, _ in SAP_TO_PYTHON
                 if codecs.lookup(codec_name))
print()
print(f"   The middle column IS checked: all {resolvable} of the {len(SAP_TO_PYTHON)} codecs named")
print("   above resolve in this Python. The left column is not, and cannot")
print("   be -- nothing on this machine knows what SAP calls its tables, so")
print("   those numbers are the one thing on this page you have to go and")
print("   look up yourself.")
print()

print("2. EBCDIC: THE ALPHABET IS IN THREE PIECES")
print("-" * 72)
print("   ASCII puts A-Z in one unbroken run, which is why 'c >= \"a\" and")
print("   c <= \"z\"' is a letter test in every language that grew up on it.")
print("   EBCDIC does not:")
print()
for name, letters in (("lowercase", string.ascii_lowercase), ("uppercase", string.ascii_uppercase)):
    coded = [(c, ord(c.encode("cp037"))) for c in letters]
    runs = [[coded[0]]]
    for previous, current in zip(coded, coded[1:]):
        if current[1] - previous[1] == 1:
            runs[-1].append(current)
        else:
            runs.append([current])
    print(f"      {name}:")
    for run in runs:
        first, last = run[0], run[-1]
        print(f"         {first[0]}-{last[0]}   0x{first[1]:02X}-0x{last[1]:02X}   {len(run)} letters")
print()
low, high = ord("a".encode("cp037")), ord("z".encode("cp037"))
span = high - low + 1
gaps = [b for b in range(low, high + 1)
        if bytes([b]).decode("cp037") not in string.ascii_lowercase]
print(f"      a is 0x{low:02X} and z is 0x{high:02X}, so the range spans {span} byte")
print(f"      values to hold 26 letters. {len(gaps)} of them are not letters.")
print()
print("   The three runs are 9, 9 and 8 long, and they line up with the")
print("   three zone punches of the 80-column card EBCDIC inherited from.")
print("   The gaps are where the card had nothing to encode.")
print()

print("3. WHAT THE GAPS ACTUALLY BREAK")
print("-" * 72)
print("   (a) the range test, which quietly admits punctuation:")
wrong = [bytes([b]).decode("cp037") for b in range(low, high + 1)
         if bytes([b]).decode("cp037") not in string.ascii_lowercase]
printable_wrong = [c for c in wrong if c.isprintable()]
print(f"       characters that pass 'between a and z' but are not letters:")
print(f"          {' '.join(printable_wrong)}")
print()
print("   (b) sort order, which is not a rearrangement of the ASCII one:")
sample = ["Zebra", "apple", "9lives", "Apple"]
for encoding in ("ascii", "cp037"):
    order = sorted(sample, key=lambda s: s.encode(encoding))
    print(f"       by {encoding:<6} bytes: {order}")
print()
print("       ASCII sorts digits, then capitals, then small letters.")
print("       EBCDIC sorts small letters, then capitals, then digits --")
print("       the reverse grouping, so a report sorted on the mainframe and")
print("       the same report sorted after transfer do not agree, and")
print("       neither is broken.")
print()

print("4. THE EURO TWINS: ONE BYTE APART")
print("-" * 72)
print("   When the euro arrived, IBM did not extend the EBCDIC tables --")
print("   it published a second number for each one, differing in a single")
print("   position. Python ships exactly one of those pairs:")
print()
pairs = [("cp037", "cp1140"), ("cp273", "cp1141"), ("cp277", "cp1142"),
         ("cp278", "cp1143"), ("cp280", "cp1144"), ("cp284", "cp1145"),
         ("cp285", "cp1146"), ("cp297", "cp1147"), ("cp500", "cp1148"),
         ("cp871", "cp1149")]
for old, new in pairs:
    missing = []
    for n in (old, new):
        try:
            codecs.lookup(n)
        except LookupError:
            missing.append(n)
    if missing:
        print(f"      {old:<7} / {new:<7} not comparable: "
              f"{', '.join(missing)} not in this Python")
        continue
    differences = [(b, bytes([b]).decode(old), bytes([b]).decode(new))
                   for b in range(256)
                   if bytes([b]).decode(old) != bytes([b]).decode(new)]
    detail = "; ".join(f"0x{b:02X} {a!r} -> {c!r}" for b, a, c in differences)
    print(f"      {old:<7} / {new:<7} {len(differences)} byte differs: {detail}")
print()
print("   One byte. 0x9F was the international currency sign in cp037 and")
print("   is the euro sign in cp1140, and everything else is identical --")
print("   so a file converted under the wrong one of the pair is correct in")
print("   every position except the currency symbol, which is the same")
print("   shape of bug as Windows-1252 against Latin-1, on a different")
print("   continent of computing.")
print()
comparable = sum(1 for old, new in pairs
                 if all(_ok(n) for n in (old, new)))
print(f"   Note what this program could NOT check: {len(pairs) - comparable} of the {len(pairs)} pairs.")
print("   Those CCSIDs are real and documented by IBM; they are simply not")
print("   in Python's standard library, so nothing here can confirm what")
print("   they contain. That is the difference between a number this page")
print("   measured and a number this page repeated -- the same difference as")
print("   the SAP column in section 1.")
print()

print("5. TWO EBCDIC VARIANTS THAT AGREE ON EVERY LETTER AND DIGIT")
print("-" * 72)
differences = [(b, bytes([b]).decode("cp037"), bytes([b]).decode("cp500"))
               for b in range(256)
               if bytes([b]).decode("cp037") != bytes([b]).decode("cp500")]
print(f"   cp037 (US/Canada) against cp500 (International): "
      f"{len(differences)} bytes differ")
print()
print(f"      {'byte':<6} {'cp037':<8} cp500")
for b, a, c in differences:
    print(f"      0x{b:02X}   {a!r:<8} {c!r}")
letters_and_digits = string.ascii_letters + string.digits
same = all(ch.encode("cp037") == ch.encode("cp500") for ch in letters_and_digits)
print()
print(f"   every letter and digit encodes identically in both: {same}")
print()
print("   The seven that move are brackets, the exclamation mark, the pipe,")
print("   the caret, the cent sign and the not sign -- which is to say, the")
print("   characters that are SYNTAX. Names and amounts survive the wrong")
print("   choice; a JSON payload, a shell script or an ABAP field symbol")
print("   does not. Same lesson as 1252 against Latin-1: the tables agree")
print("   about the text and disagree about the punctuation.")
print()

print("6. REPRODUCING AN INTERFACE'S MOJIBAKE, OUTSIDE THE SYSTEM")
print("-" * 72)
print("   The point of the mapping in section 1: once you know which table")
print("   each end used, the damage is reproducible in four lines here, and")
print("   you can show it to somebody without a logon.")
print()
original = "Za\N{LATIN SMALL LETTER Z WITH DOT ABOVE}\N{LATIN SMALL LETTER O WITH ACUTE}\N{LATIN SMALL LETTER L WITH STROKE}\N{LATIN SMALL LETTER C WITH ACUTE}"
written_as = "utf-8"
read_as = "latin-1"
raw = original.encode(written_as)
print(f"   the field                 {original!r}")
print(f"   written as UTF-8          {raw.hex(' ')}")
print(f"   read back as Latin-1      {ascii(raw.decode(read_as))}")
print()
print("   That is one line of Python standing in for a file written under")
print("   one code page and read under another. Reproduce it before you")
print("   argue about it: the reproduction is the evidence, and it is the")
print("   same evidence whichever system turns out to be misconfigured.")
print()
print("   And check every number in it against the system. Nothing in this")
print("   file knows your landscape -- a table name printed here is a")
print("   hypothesis about a configuration somebody else controls.")
