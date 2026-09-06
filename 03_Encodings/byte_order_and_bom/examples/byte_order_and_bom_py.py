#!/usr/bin/env python3
"""The mark that says which end came first -- and the three bytes it became.

A number wider than one byte has to be written in some order, and the two
orders are both in use. The byte order mark is one code point, U+FEFF, put at
the front so a reader can work the order out from the file instead of being
told. UTF-8 has no order to resolve and gets the mark anyway, as a signature
meaning "this is UTF-8" -- which is useful to a guessing reader and is three
bytes of content to everyone else.

In Python the choice is made by the codec NAME: a name with a byte-order
suffix writes no mark, a name without one picks an order for you and writes a
mark to say which -- and the same name on the way back decides who eats it.

Run:  python3 byte_order_and_bom_py.py
"""

import codecs
import io
import json
import re
import unicodedata

BAR = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


# ------------------------------------------------------------------ 1
head(1, "A NUMBER WIDER THAN A BYTE HAS TWO SPELLINGS")
n = 258
print(f"   the number                {n}   = 0x{n:08x}")
print(f"   .to_bytes(4, 'big')       {n.to_bytes(4, 'big').hex(' ')}   most significant end first")
print(f"   .to_bytes(4, 'little')    {n.to_bytes(4, 'little').hex(' ')}   least significant end first")
print()
print("   Same number, same four bytes, opposite order. Both are correct and")
print("   neither is detectable from the bytes alone: 00 00 01 02 read the")
print("   other way round is 33,619,968, and nothing in the file objects.")
print("   Big-endian is the order the internet standards chose, which is why")
print("   it is called network byte order; x86 and ARM run little-endian, so")
print("   every packet header crossing a socket is being swapped.")
print()
print("   A single byte has no order. This whole question only exists for")
print("   values stored in more than one byte -- which is what UTF-16 makes")
print("   every character, and what UTF-8 makes none of.")

# ------------------------------------------------------------------ 2
head(2, "THE MARK: ONE CODE POINT, WRITTEN IN THE FILE'S OWN ORDER")
mark = "﻿"
print(f"   U+FEFF is {unicodedata.name(mark)}")
print(f"   as utf-16-be   {mark.encode('utf_16_be').hex(' ')}")
print(f"   as utf-16-le   {mark.encode('utf_16_le').hex(' ')}")
print()
print("   The reader does not have to be told the order; it reads the mark and")
print("   deduces it. Both of these decode to the same two letters:")
for raw in (b"\xfe\xff\x00I\x00D", b"\xff\xfeI\x00D\x00"):
    print(f"     {raw.hex(' '):<20} .decode('utf-16') -> {raw.decode('utf-16')!r}")
print()
print("   And here is why the trick is sound rather than merely conventional.")
print("   Read the little-endian bytes as if they were big-endian:")
wrong = b"\xff\xfeI\x00D\x00".decode("utf_16_be")
print(f"     b'\\xff\\xfeI\\x00D\\x00'.decode('utf-16-be') -> {wrong!r}")
print(f"     first code point: U+{ord(wrong[0]):04X}, "
      f"{unicodedata.name(wrong[0], 'no name -- a PERMANENT NONCHARACTER')}")
print()
print("   U+FFFE is reserved forever and can never be assigned. So the mirror")
print("   image of the mark is not some other letter that might legitimately")
print("   open a file -- it is a value guaranteed never to mean anything, and")
print("   a reader that sees it knows for certain it has the order backwards.")

# ------------------------------------------------------------------ 3
head(3, "THE CODEC NAME DECIDES WHETHER A MARK IS WRITTEN")
face = "\U0001F600"
print("   one code point, U+1F600, written seven ways:")
for name in ("utf-8", "utf-16be", "utf-16le", "utf-32be", "utf-32le"):
    raw = face.encode(name)
    print(f"     {name:<9} {len(raw)} bytes   {raw.hex(' ')}")
raw16, raw32 = face.encode("utf-16"), face.encode("utf-32")
print(f"     {'utf-16':<9} {len(raw16)} bytes   "
      f"starts with codecs.BOM_UTF16: {raw16[:2] == codecs.BOM_UTF16}")
print(f"     {'utf-32':<9} {len(raw32)} bytes   "
      f"starts with codecs.BOM_UTF32: {raw32[:4] == codecs.BOM_UTF32}")
print()
print("   The bytes of those last two are not printed, on purpose: the mark")
print("   is followed by whichever order THIS machine runs, so the answer")
print("   depends on who ran the script and a recorded key must not. What")
print("   holds everywhere is the shape --")
print(f"     the rest of the utf-16 form is one of the two suffixed forms: "
      f"{raw16[2:] in (face.encode('utf-16le'), face.encode('utf-16be'))}")
print(f"     the rest of the utf-32 form is one of the two suffixed forms: "
      f"{raw32[4:] in (face.encode('utf-32le'), face.encode('utf-32be'))}")
print()
print("   So the rule is the name, and that is the whole of it:")
print("     WITH a suffix (utf-16le, utf-32be) -- you have already said which")
print("       order, there is nothing left to announce, and no mark is added")
print("     WITHOUT one (utf-16, utf-32) -- the codec picks an order for you")
print("       and writes a mark at the front to say which one it picked")
print()
print("   The mark is a header, not text, and it is written even when there")
print("   is no text at all:")
for name in ("utf-16le", "utf-16", "utf-32le", "utf-32"):
    call = f"len(''.encode({name!r}))"
    print(f"     {call:<26} = {len(''.encode(name))}")

# ------------------------------------------------------------------ 4
head(4, "AND THE NAME HAS TO SURVIVE THE ALIAS TABLE")
for name in ("utf-16le", "utf-16-le", "utf_16_le", "UTF 16 LE", "utf16-le", "utf16le"):
    try:
        print(f"   {name!r:<12} -> codecs.lookup(..).name = {codecs.lookup(name).name!r}")
    except LookupError as e:
        print(f"   {name!r:<12} -> LookupError: {e}")
print()
print("   Four spellings work and two do not, and the difference is not the")
print("   hyphen -- 'UTF 16 LE' is fine. Python turns every run of")
print("   non-alphanumeric characters into a single underscore and looks the")
print("   result up in encodings.aliases, so 'utf-16le', 'utf 16le' and")
print("   'utf_16_le' all arrive as a name that table knows. 'utf16-le' has")
print("   nothing at all between 'utf' and '16', so it normalises to a name")
print("   the table has never contained. Two spellings that look equally")
print("   reasonable, and only one of them exists.")

# ------------------------------------------------------------------ 5
head(5, "READING BACK: THE SAME NAME DECIDES WHO EATS THE MARK")
marked = codecs.BOM_UTF16_LE + face.encode("utf_16_le")
print(f"   a little-endian file with a mark   {marked.hex(' ')}")
print(f"     .decode('utf-16')     -> {marked.decode('utf_16')!r}")
print(f"     .decode('utf-16le')   -> {marked.decode('utf_16_le')!r}")
print()
print("   The unsuffixed codec consumes the mark; the suffixed one hands it")
print("   back as a character, because you told it the order and it has no")
print("   reason to think the first two bytes are anything but text. That is")
print("   the utf-8-sig asymmetry of section 8, one encoding up -- and it is")
print("   where an invisible U+FEFF welded to your first field comes from.")
print()
print("   The other way round is worse, and cannot be shown here for the")
print("   same reason as section 3: a file with NO mark, decoded by the")
print("   unsuffixed 'utf-16', is read in this machine's order. Right half")
print("   the time, silently wrong the other half, and the half you get")
print("   depends on the hardware -- which is the exact bug the mark was")
print("   invented to prevent, reintroduced by a codec default.")

# ------------------------------------------------------------------ 6
head(6, "FF FE IS NOT ENOUGH TO IDENTIFY A FILE")
print(f"   codecs.BOM_UTF16_LE   {codecs.BOM_UTF16_LE.hex(' ')}")
print(f"   codecs.BOM_UTF32_LE   {codecs.BOM_UTF32_LE.hex(' ')}"
      f"   <- the line above, plus two NULs")
utf32_file = codecs.BOM_UTF32_LE + "A~".encode("utf_32_le")
print(f"   a UTF-32LE file       {utf32_file.hex(' ')}")
print(f"     .decode('utf-32')   -> {utf32_file.decode('utf_32')!r}")
print(f"     .decode('utf-16')   -> {utf32_file.decode('utf_16')!r}")
print()
print("   No exception. A sniffer that tests the two-byte mark first calls")
print("   every little-endian UTF-32 file UTF-16, and what it hands back is")
print("   the right letters with a NUL welded to each one -- which then")
print("   survives a strip(), fails every comparison, and looks like a")
print("   database problem. Test the four-byte mark before the two-byte one.")

# ------------------------------------------------------------------ 7
head(7, "UTF-8 HAS NO BYTE ORDER, AND GETS THE MARK ANYWAY")
print(f"   the same code point as UTF-8   {mark.encode('utf_8').hex(' ')}")
print(f"   codecs.BOM_UTF8                {codecs.BOM_UTF8!r}")
print()
print("   UTF-8 is a stream of single bytes; a three-byte character has one")
print("   spelling and there is no end to put first. So EF BB BF resolves")
print("   nothing. It was repurposed as a SIGNATURE: a flag at the front")
print("   meaning 'read me as UTF-8', for a reader that would otherwise fall")
print("   back to a local code page and guess wrong. Python spells that codec")
print("   'utf-8-sig' -- sig for signature, not for byte order.")
print()
for label, data in (("plain UTF-8   ", "id,name\n"), ("with signature", "﻿id,name\n")):
    print(f"   {label}  {data.encode('utf_8').hex(' ')}")
print()
print("   Same file. Three bytes of difference, and they are content.")

# ------------------------------------------------------------------ 8
head(8, "utf-8-sig: FORGIVING ON THE WAY IN, LOUD ON THE WAY OUT")
for raw in (b"\xef\xbb\xbfid", b"id"):
    got_plain = raw.decode("utf_8")
    got_sig = raw.decode("utf_8_sig")
    print(f"   {raw.hex(' '):<14} as utf-8: {got_plain!r:<12} as utf-8-sig: {got_sig!r}")
print()
print("   That asymmetry is the whole rule. Reading with utf-8-sig strips a")
print("   signature if there is one and does nothing at all if there is not,")
print("   so it is the safe reader for a file of unknown origin. Writing with")
print("   it always adds one -- so write plain 'utf-8' unless you have decided")
print("   on purpose that the consumer needs the flag.")

# ------------------------------------------------------------------ 9
head(9, "WHAT THE THREE BYTES BREAK")
bom_text = "﻿"
print("   Invisible to a reader that expects it. To everyone else it is just")
print("   the first three bytes of the file:")
print()
print(f"   a ^-anchored match   re.match('^id', {bom_text + 'id'!r}) -> "
      f"{re.match('^id', bom_text + 'id')}")
try:
    json.loads(bom_text + "{}")
except json.JSONDecodeError as e:
    print(f"   a JSON parser        {type(e).__name__}: {e}")
print(f"   a shebang            {(bom_text + '#!/usr/bin/env python3').encode('utf_8')[:6].hex(' ')} ..."
      "   the kernel looks at offset 0 and does not find '#!'")
print(f"   an exact key match   {bom_text + 'id'!r} == 'id' -> {bom_text + 'id' == 'id'}")
print(f"   a strip()            {(bom_text + 'id').strip()!r}   "
      f"-- U+FEFF.isspace() is {bom_text.isspace()}, so strip() leaves it")
joined = (bom_text + "a\n") + (bom_text + "b\n")
print(f"   concatenation        {joined.encode('utf_8').hex(' ')}")
print("                        a signature in the MIDDLE of a file is not a")
print("                        signature, it is garbage on line 2")
print()
print("   Only the JSON parser complains, and it is the only one that names")
print("   the fix in its own error message. The rest fail silently: the match")
print("   returns None, the comparison returns False, the strip does nothing,")
print("   and a header that looks identical on screen goes on not matching.")

# ------------------------------------------------------------------ 10
head(10, "THE DECISION, IN ONE QUESTION")
print("   Who reads this file?")
print()
print("     a program, by exact bytes    -> plain 'utf-8'. A parser, a config,")
print("       (JSON, a shell script,        a shebang and a diff all read from")
print("        a diff, a build)             offset 0 and the mark is content.")
print()
print("     a guessing GUI               -> 'utf-8-sig'. Excel has no other")
print("       (Excel, Notepad)             way to know, and guesses the local")
print("                                    code page when there is no flag.")
print()
print("     both                         -> write plain, and make the reader")
print("                                    forgiving with 'utf-8-sig'.")
print()
print("   The question is answerable: grep for who opens the file before you")
print("   change what you write into it.")
