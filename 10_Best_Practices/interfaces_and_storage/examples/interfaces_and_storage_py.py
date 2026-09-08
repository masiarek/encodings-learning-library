"""One name, six channels, and the one question each channel answers differently.

Every wire format has exactly one place where the encoding is declared, and the
whole job is knowing where that place is -- because two of the six below have
nowhere to put it at all, and for those the answer lives in a document rather
than in the file.

The value is a Polish city name rather than a CAST.md string because this page
is about a RECORD crossing an interface, and because 'Łódź' carries both kinds
of Polish letter: 'ó' and 'ź' decompose under NFD, 'Ł' does not.

Everything here is stdlib -- json, csv, urllib.parse, codecs -- and none of it
touches the network, the clock or a locale.

Run:  python3 interfaces_and_storage_py.py
"""

import csv
import io
import json
import unicodedata
import urllib.parse

CITY = "Łódź"


def hexs(b):
    return " ".join(f"{x:02x}" for x in b)


print("1. ONE NAME, EIGHT ROWS, AND HOW MANY DIFFERENT SIZES")
print("-" * 72)
utf8 = CITY.encode("utf-8")
json_ascii = json.dumps({"city": CITY}).encode("utf-8")
json_raw = json.dumps({"city": CITY}, ensure_ascii=False).encode("utf-8")

buf = io.StringIO(newline="")
csv.writer(buf, lineterminator="\n").writerow(["city", CITY])
csv_plain = buf.getvalue().encode("utf-8")
csv_bom = buf.getvalue().encode("utf-8-sig")

query = urllib.parse.urlencode({"city": CITY}).encode("ascii")
fixed = utf8.ljust(10)[:10]

rows = [
    ("the text itself", f"{len(CITY)} characters", CITY),
    ("UTF-8 bytes", f"{len(utf8)} bytes", hexs(utf8)),
    ("JSON, default", f"{len(json_ascii)} bytes", json_ascii.decode()),
    ("JSON, ensure_ascii=False", f"{len(json_raw)} bytes", json_raw.decode()),
    ("CSV, no BOM", f"{len(csv_plain)} bytes", repr(csv_plain.decode())),
    ("CSV, utf-8-sig", f"{len(csv_bom)} bytes", repr(csv_bom.decode("utf-8-sig"))),
    ("URL query string", f"{len(query)} bytes", query.decode()),
    ("CHAR(10), byte-counted", f"{len(fixed)} bytes", hexs(fixed)),
]
for label, size, shown in rows:
    print(f"   {label:<26}{size:>13}   {shown}")
print()
sizes = {size for _, size, _ in rows if size.endswith("bytes")}
print(f"   {len(rows)} rows and {len(sizes)} different byte sizes for one name. Every")
print("   pipeline above is correct; each is measuring a different layer.")
print("   A field width, a length limit or a quota applies to exactly ONE")
print("   of these rows, and it is rarely the first -- which is the")
print("   question to ask before sizing a column, not after the insert")
print("   fails in production.")
print()

print("2. WHERE EACH CHANNEL DECLARES THE ENCODING")
print("-" * 72)
channels = [
    ("HTTP", "Content-Type: ...; charset=utf-8", "in the header, and it wins"),
    ("HTML", "<meta charset> -- only if no header", "the header outranks it"),
    ("JSON", "nowhere: RFC 8259 fixes UTF-8", "no charset parameter exists"),
    ("XML", "<?xml version encoding=...?>", "in the document, self-describing"),
    ("CSV", "nowhere at all", "a BOM, or a document, or a guess"),
    ("fixed-width", "nowhere at all", "the interface specification"),
    ("URL query", "nowhere: %XX escapes bytes", "RFC 3986 can only recommend"),
    ("email header", "=?utf-8?B?...?= names it inline", "the only one that always does"),
]
print(f"   {'channel':<14}{'the declaration':<36}{'who decides'}")
for name, where, who in channels:
    print(f"   {name:<14}{where:<36}{who}")
print()
declared = sum(1 for _, where, _ in channels if not where.startswith("nowhere"))
nowhere = [n for n, where, _ in channels if where.startswith("nowhere") and "RFC" not in where]
print(f"   Three groups, not two. {declared} of the {len(channels)} carry the answer INSIDE the")
print("   data, where a reader can find it without being told. JSON has")
print("   nowhere to put it and does not need one, because the format FIXES")
print("   it -- one encoding, no parameter, no negotiation, which is the")
print(f"   design worth copying. And {len(nowhere)} -- {', '.join(nowhere)} --")
print("   have nowhere to put it AND nothing fixing it, so the answer lives")
print("   in a document or in somebody's memory. Those three are the ones")
print("   that produce a ticket saying 'the file is corrupt'.")
print()

print("3. JSON IS UTF-8 BY THE RFC, SO 'JSON IN ANOTHER ENCODING' IS NOT A THING")
print("-" * 72)
doc = json.dumps({"city": CITY}, ensure_ascii=False)
try:
    doc.encode("cp1252")
    print("   encoding this record as cp1252     it worked?!")
except UnicodeEncodeError as exc:
    print(f"   encoding this record as cp1252     {type(exc).__name__}")
    print(f"     the character it stopped on      {doc[exc.start]!r}  U+{ord(doc[exc.start]):04X}")
PL = "ąćęłńóśźż"


def in_cp1252(ch):
    try:
        ch.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


holds = [c for c in PL if in_cp1252(c)]
print(f"     of Polish's nine letters cp1252 holds  {' '.join(holds)}   ({len(holds)} of {len(PL)})")
print("   So the question 'what if this JSON were cp1252' cannot even be")
print("   asked of this record -- the encode fails before any JSON exists.")
print("   ('ó' survives because it is in the Latin-1 half that cp1252 kept;")
print("   the other eight are the ones Latin-1 never had.) Take a value it")
print("   CAN hold, and the answer arrives one layer later instead:")
print()
cafe = json.dumps({"city": "café"}, ensure_ascii=False)
print(f"     as UTF-8    {hexs(cafe.encode('utf-8'))}")
print(f"     as cp1252   {hexs(cafe.encode('cp1252'))}")
for enc in ("utf-8", "cp1252"):
    payload = cafe.encode(enc)
    try:
        print(f"     json.loads(bytes encoded {enc:<7}) -> {json.loads(payload)}")
    except Exception as exc:
        print(f"     json.loads(bytes encoded {enc:<7}) -> {type(exc).__name__}")
print()
print("   RFC 8259 section 8.1 fixes the encoding of an exchanged JSON text")
print("   to UTF-8, and the media type registration defines no charset")
print("   parameter -- so `Content-Type: application/json; charset=cp1252`")
print("   is not a JSON document in another encoding, it is a broken one")
print("   carrying a parameter nothing is required to read. json.loads")
print("   takes bytes and decodes them itself, which is why the refusal")
print("   above is a DECODE error rather than a syntax error: the parser")
print("   never got far enough to have an opinion about the JSON.")
print()
print("   The escape form is the other half of that. json.dumps defaults to")
print("   ensure_ascii=True, which is not an encoding choice -- it is a")
print("   channel choice, for a pipe that will only carry ASCII:")
print(f"     default             {json.dumps({'city': CITY})}")
print(f"     ensure_ascii=False  {json.dumps({'city': CITY}, ensure_ascii=False)}")
print(f"     same parsed value?  {json.loads(json.dumps({'city': CITY})) == json.loads(json.dumps({'city': CITY}, ensure_ascii=False))}")
print("   Same document, same parsed value, different size on the wire, and")
print("   a \\uXXXX escape that is a UTF-16 code unit inside a UTF-8 format.")
print()

print("4. CSV IS THE ONE WITH NOWHERE TO PUT IT")
print("-" * 72)
print("   Read the BOM'd file with the wrong codec and the damage lands in")
print("   the one place a program will not look -- the first column NAME:")
for enc in ("utf-8", "utf-8-sig"):
    text = csv_bom.decode(enc)
    header = next(csv.reader(io.StringIO(text, newline="")))
    print(f"     decode as {enc:<10} header[0] = {header[0]!r}   len {len(header[0])}")
print()
print("   Both decodes SUCCEEDED. Nothing raised, nothing warned, and one of")
print("   them produced a column called something no lookup will match.")
print("   'utf-8-sig' strips a BOM if there is one and is harmless if there")
print("   is not, so it is the right codec for reading somebody else's CSV;")
print("   plain 'utf-8' is the right one for writing yours.")
print()
print("   The other two arguments that belong on every csv open():")
print("     newline=''       the module handles line endings itself, and a")
print("                      quoted field may CONTAIN one")
print("     encoding='utf-8' because the default is the machine's, and the")
print("                      machine writing the file is not the one reading")
print()

print("5. THE SANDWICH, AND THE ONE HOP THAT USUALLY MISSES IT")
print("-" * 72)
print("   Decode at the boundary, hold text in the middle, encode at the")
print("   boundary. The failure is never the whole program -- it is one hop")
print("   where a value stayed bytes and got treated as text anyway:")
print()
raw = CITY.encode("utf-8")
print(f"   bytes arriving from a socket    {hexs(raw)}")
print(f"     .upper() on the BYTES         {raw.upper()!r}")
print(f"     .upper() on the TEXT          {CITY.upper()!r}")
print()
changed = sum(1 for a, b in zip(raw, raw.upper()) if a != b)
print("   bytes.upper() did not raise and did not refuse. It is documented")
print("   as ASCII-only, so it changed exactly", changed, "byte of", len(raw), "-- the 'd' --")
print("   and left every byte of 'Ł', 'ó' and 'ź' as it found them. A")
print("   half-uppercased value, no error, no log line, and it will compare")
print("   unequal to the properly uppercased one forever.")
print()
print("   Note what did NOT differ: both answers are the same length here.")
print(f"     {CITY!r}.upper()   {len(CITY)} -> {len(CITY.upper())} characters, {len(raw)} -> {len(CITY.upper().encode())} bytes")
print("   Case mapping is a table lookup and the table is free to change")
print(f"   the length -- {'ß'!r}.upper() is {'ß'.upper()!r}, {len('ß')} character becoming {len('ß'.upper())} --")
print("   so 'uppercasing does not resize a field' is a fact about THIS")
print("   string, not a rule you can size a column with.")
print()

print("6. AND WHAT 'WRITE IT DOWN' ACTUALLY MEANS")
print("-" * 72)
spec = [
    ("encoding", "UTF-8"),
    ("normalization form", f"NFC (this record already is: {unicodedata.is_normalized('NFC', CITY)})"),
    ("line ending", "LF"),
    ("BOM", "absent"),
    ("field width unit", "bytes"),
    ("what happens to a value that does not fit", "reject the record"),
    ("what happens to an undecodable byte", "reject the record"),
]
print("   Seven lines, and every one of them is a question somebody will")
print("   otherwise answer for you, differently, at three in the morning:")
print()
for k, v in spec:
    print(f"     {k:<44}{v}")
print()
print("   Note the last two. 'Which encoding' is the famous question and it")
print("   is the easy one; the ones that decide whether an interface is")
print("   debuggable are what it does when the rule is broken. An")
print("   errors='ignore' nobody wrote down is a policy too -- it is just a")
print("   policy chosen by whoever typed fastest.")
