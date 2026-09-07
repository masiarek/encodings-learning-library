#!/usr/bin/env python3
"""Python translates line endings on exactly one path, and people assume it is everywhere.

Read a Windows file in text mode and the CRs are gone before your code sees
them -- which is why this bug is invisible for years and then arrives all at
once, on the day the text comes from somewhere that is not a text-mode read.
This program walks the three reading paths, shows the field that silently
stops matching, and then does the writing side, where `newline=` is a second
and completely separate decision.

Nothing is written to disk: every file here is bytes in memory, so the bytes
shown are the bytes discussed. No CR is ever printed raw -- a carriage return
on this page is always hex or a repr, because a raw one would move the cursor
and be invisible in the very output that is about it.

Run:  python3 crlf_vs_lf_py.py
"""

import csv
import io

BAR = "-" * 72


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


def read_as(raw: bytes, newline):
    """What open(path, encoding='utf-8', newline=NEWLINE).read() would give back."""
    return io.TextIOWrapper(io.BytesIO(raw), encoding="utf-8", newline=newline).read()


UNIX = b"id,name,active\n1,Ada,Y\n"
WIN = b"id,name,active\r\n1,Ada,Y\r\n"
MAC = b"id,name,active\r1,Ada,Y\r"

# ------------------------------------------------------------------ 1
head(1, "THREE FILES, ONE TABLE")
for label, ending, raw in (("Unix", "LF", UNIX), ("Windows", "CRLF", WIN), ("classic Mac", "CR", MAC)):
    print(f"   {label:<12} {ending:<4} {len(raw):>2} bytes   {raw[14:22].hex(' ')} ...")
print()
print("   Same two lines of text. The middle file is one byte per line longer,")
print("   and that byte -- 0d, carriage return -- is the entire subject.")

# ------------------------------------------------------------------ 2
head(2, "READING: PYTHON TRANSLATES, AND ONLY ON THIS ONE PATH")
for label, raw in (("CRLF", WIN), ("CR", MAC)):
    print(f"   {label:<4} file, open(...) default   {read_as(raw, None)!r}")
print("                                   ^ both arrive as \\n. That is")
print("   'universal newlines': a text-mode read turns \\r\\n, \\r and \\n into \\n")
print("   before your code sees anything. It is why a Windows CSV usually just")
print("   works, and why the day it does not comes as a surprise.")
print()
print("   Now the same file down the other two paths:")
print(f"   CRLF file, newline=''           {read_as(WIN, '')!r}")
print(f"   CRLF file, open(..., 'rb')      {WIN!r}")
print()
print("   Nothing translated. Those are not exotic: newline='' is what the csv")
print("   module asks for. And on every other path nothing is translated at")
print("   all: a socket, a zipfile member, an HTTP body, a subprocess with")
print("   text=False, a database column. Some of those hand you bytes and")
print("   some hand you str -- what they have in common is that none of them")
print("   touches a \\r. The protection covers one path, and the CR is waiting")
print("   on all the others.")

# ------------------------------------------------------------------ 3
head(3, "THE FIELD THAT QUIETLY STOPS MATCHING")
row = read_as(WIN, "").split("\n")[1]
fields = row.split(",")
print(f"   text.split(chr(10))[1]     {row!r}")
print(f"   .split(',')                {fields}")
print(f"   fields[-1] == 'Y'          {fields[-1] == 'Y'}   <- the CR is inside the last field")
print(f"   len(fields[-1])            {len(fields[-1])}   <- two characters, and it prints as one")
print()
print("   And here is why the interface half-works rather than failing:")
print(f"   int('42\\r')                {int('42' + chr(13))}      numbers survive -- int() strips whitespace")
print(f"   float('3.5\\r')             {float('3.5' + chr(13))}     so does float()")
print(f"   '42\\r' == '42'             {'42' + chr(13) == '42'}   strings do not")
print()
print("   Quantities reconcile. Keys, codes, flags and dates-as-text do not.")
print("   A report that adds up correctly and matches nothing is this bug.")
print()
print("   Stripping it, and the near-miss:")
print(f"   'Y\\r'.rstrip()             {('Y' + chr(13)).rstrip()!r}    removes any trailing whitespace")
print(f"   'Y\\r'.rstrip(chr(10))      {('Y' + chr(13)).rstrip(chr(10))!r}  <- asked for \\n, left the \\r")
print("   The second is the line people write when they think 'strip the")
print("   newline'. It is exactly correct and it removes the wrong byte.")

# ------------------------------------------------------------------ 4
head(4, "WRITING: newline= IS A SECOND, SEPARATE DECISION")


def written(newline) -> bytes:
    buf = io.BytesIO()
    f = io.TextIOWrapper(buf, encoding="utf-8", newline=newline, write_through=True)
    w = csv.writer(f)
    w.writerow(["id", "name"])
    w.writerow(["1", "Ada"])
    f.flush()
    return buf.getvalue()


print("   csv.writer always emits \\r\\n of its own. What open() then does to it:")
print()
CRLF = chr(13) + chr(10)
for shown, arg in (("''", ""), (r"'\r\n'", CRLF)):
    print(f"   newline={shown:<8}  {written(arg).hex(' ')}")
print()
print("   Look at the second one: 0d 0d 0a. TWO carriage returns. On write, a")
print("   newline= of \\r\\n means 'translate every \\n I write into \\r\\n' -- and")
print("   the \\n the csv module wrote already had a \\r in front of it.")
print()
print("   That second line IS Windows' default. newline=None on Windows")
print("   translates to os.linesep, which is \\r\\n, so the famous blank row")
print("   between every record of an Excel-bound CSV is 0d 0d 0a, and this is")
print("   it reproduced on a Unix machine by naming the ending by hand.")
print(f"   as text:            {written(CRLF).decode()!r}")
print()
print("   newline='' does not mean 'no newlines'. It means 'translate nothing")
print("   in either direction' -- and that is why it is the right argument for")
print("   a csv file on every platform, reading and writing.")

# ------------------------------------------------------------------ 5
head(5, "AND WHY csv ASKS FOR IT: A NEWLINE INSIDE A FIELD")
quoted = b'id,note\r\n1,"first\r\nsecond"\r\n'
print(f"   the file            {quoted!r}")
print("   One record. Its second field is a quoted string containing a real")
print("   line break -- legal CSV, and common in any free-text column.")
print()
for newline in ("", None):
    got = list(csv.reader(io.TextIOWrapper(io.BytesIO(quoted), encoding="utf-8", newline=newline)))
    print(f"   newline={newline!r:<5} -> {got}")
print()
print("   Both parse into one record, so nothing errors and nothing looks")
print("   wrong. But the field's CONTENT is different: the default read")
print("   rewrote the bytes INSIDE the value before csv ever saw them. Read a")
print("   file that way and write it back and you have edited somebody's data")
print("   without touching it. That is the whole reason the csv docs ask for")
print("   newline='': line splitting is the parser's job, not open()'s.")

# ------------------------------------------------------------------ 6
head(6, "THE RULE")
print("   reading text you will parse yourself   the default is right: it")
print("                                          normalises everything to \\n")
print()
print("   reading or writing csv                 newline='' -- always, both")
print("                                          directions, every platform")
print()
print("   comparing, hashing, or byte-counting   open in 'rb'. Text mode has")
print("                                          already changed the bytes.")
print()
print("   text that did NOT come from open()     assume it has CRs. Sockets,")
print("                                          zips, HTTP, subprocesses and")
print("                                          database columns translate")
print("                                          nothing at all.")
print()
print("   And when you strip: .rstrip() with no argument, or splitlines(),")
print("   or .rstrip('\\r\\n'). Never .rstrip('\\n') and never [:-1].")
