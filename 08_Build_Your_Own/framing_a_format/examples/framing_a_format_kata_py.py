#!/usr/bin/env python3
"""Answers to the framing kata: four records, one lie.

Four Intel HEX records, read with nothing but addition. The last question
needs no arithmetic at all, and it is the one that says what a per-record
checksum is worth.
"""

RECORDS = [
    ":020000040000FA",
    ":03001000E282ACDD",
    ":02002000C4BC5D",
    ":00000001FF",
]

TYPES = {
    0x00: "Data",
    0x01: "End of File",
    0x02: "Extended Segment Address",
    0x03: "Start Segment Address",
    0x04: "Extended Linear Address",
    0x05: "Start Linear Address",
}


def fields(rec: str) -> tuple[int, int, int, bytes, int]:
    """RECLEN, LOAD OFFSET, RECTYP, DATA, CHKSUM."""
    raw = bytes.fromhex(rec[1:])
    return raw[0], int.from_bytes(raw[1:3], "big"), raw[3], raw[4:-1], raw[-1]


print("THE FOUR RECORDS")
print()
for i, rec in enumerate(RECORDS, 1):
    print(f"   {i}  {rec}")
print()

# --------------------------------------------------------------------------
print("1. WHAT EACH ONE IS -- read RECTYP, characters 8 and 9")
print()
print(f"   {'#':<3}{'record':<20}{'RECLEN':<8}{'OFFSET':<9}{'RECTYP':<8}name")
for i, rec in enumerate(RECORDS, 1):
    reclen, offset, rectyp, data, chk = fields(rec)
    print(
        f"   {i:<3}{rec:<20}{f'{reclen:02X}':<8}"
        f"{f'0x{offset:04X}':<9}{f'{rectyp:02X}':<8}{TYPES[rectyp]}"
    )
print()
print("   Two Data records between an address record and an end-of-file")
print("   record. RECTYP is the third field and it is always in the same two")
print("   columns, which is why `cut -c8-9` reads it straight out of the file.")
print()

# --------------------------------------------------------------------------
print("2. RECORD 2 -- how many bytes, and where")
print()
reclen, offset, rectyp, data, chk = fields(RECORDS[1])
print(f"   RECLEN  {reclen:02X}    = {reclen} data bytes")
print(f"   OFFSET  {offset:04X}  = {offset} decimal, where the loader puts the first one")
print(f"   DATA    {data.hex(' ')}  = {data.decode('utf-8')!r} in UTF-8")
print()
print("   RECLEN counts BYTES, not characters of the record -- three data")
print("   bytes are six hex characters. The frame is eleven characters, the")
print("   record mark included, and it does not change with the payload:")
print(f"   len(record) = {len(RECORDS[1])} = 11 + {reclen * 2}")
print()

# --------------------------------------------------------------------------
print("3. WHICH ONE IS THE LIE")
print()
print("   Add up every byte from RECLEN to CHKSUM. A good record sums to 0.")
print()
print(f"   {'#':<3}{'record':<20}sum mod 256")
bad = []
for i, rec in enumerate(RECORDS, 1):
    total = sum(bytes.fromhex(rec[1:])) & 0xFF
    if total:
        bad.append((i, rec, total))
    note = "ok" if total == 0 else f"FAILS -- got {total} = 0x{total:02X}"
    print(f"   {i:<3}{rec:<20}{total:>3}   {note}")
print()
i, rec, total = bad[0]
reclen, offset, rectyp, data, chk = fields(rec)
short_by = 256 - total
print(f"   Record {i} is the lie. The reader gets {total} back, and in eight bits")
print(f"   {total} is -{short_by}: the record's content is {short_by} less than whatever the")
print("   checksum was computed over. The number it hands you IS the damage.")
print()
repaired = bytes([data[0] + short_by]) + data[1:]
print(f"   {'stored':<16}{data.hex(' ')}")
print(f"   {f'+{short_by} on byte 0':<16}{repaired.hex(' ')}   = {repaired.decode('utf-8')!r}")
print()
print("   The character 5 in the file became a 4 -- one bit of one byte, the")
print("   damage a bad cable or a careless edit actually does -- and ż became")
print("   a byte that starts a UTF-8 sequence nothing finishes.")
print()
print(f"   But the checksum never said WHICH byte. +{short_by} on the other one satisfies")
print("   it exactly as well:")
alt = data[:1] + bytes([data[1] + short_by])
body = bytes([reclen, offset >> 8, offset & 0xFF, rectyp]) + alt + bytes([chk])
print(f"   {alt.hex(' ')} sums to {sum(body) & 0xFF} as well -- and it is not the right answer.")
print(f"   Eight bits of check over the {len(rec) - 1} characters after the mark can")
print("   detect, and have nothing left over to locate with.")
print()

# --------------------------------------------------------------------------
print("4. NOW DELETE RECORD 3 -- the question with no arithmetic in it")
print()
short = RECORDS[:2] + RECORDS[3:]
print("   the file that is left:")
for rec in short:
    print(f"      {rec}")
print()


def all_verify(recs: list[str]) -> bool:
    return all(sum(bytes.fromhex(r[1:])) & 0xFF == 0 for r in recs)


print(f"   every remaining checksum verifies: {all_verify(short)}")
print()
print("   Nothing complains. The corrupt record is gone, and so is the only")
print("   thing in the file that objected to it -- what a reader now has is a")
print("   clean file missing two bytes of somebody's data, and it says so")
print("   nowhere. Deleting the damage repaired the file's self-report.")
print()
print("   And it is not one blind spot, it is the whole class. Take the good")
print("   file -- records 1, 2 and 4 -- and damage it four different ways")
print("   without touching a single record's own bytes:")
print()
good = [RECORDS[0], RECORDS[1], RECORDS[3]]
damage = [
    ("the original, undamaged", good),
    ("record 2 deleted", [good[0], good[2]]),
    ("record 2 sent twice", [good[0], good[1], good[1], good[2]]),
    ("records 1 and 2 swapped", [good[1], good[0], good[2]]),
    ("cut off before end-of-file", good[:2]),
]
for what, recs in damage:
    print(f"   {what:<28}{len(recs)} records   every checksum verifies: {all_verify(recs)}")
print()
print("   Four kinds of damage and not one of them is visible, because none")
print("   of them is inside a record. That is the shape of the answer: a")
print("   checksum is scoped to a RECORD, so it can say a record is damaged")
print("   and can never say the FILE is. Catching these wants a different")
print("   field -- a count, a sequence number, or a hash over the whole")
print("   stream -- and which one you want is a decision to make at the")
print("   start, because a field added later is a field every existing")
print("   reader has never heard of.")
print()
print("   Unless, of course, the format left itself somewhere to put one.")
print("   That is the record type, one field along: a reader that can skip a")
print("   record it does not recognise is a reader that survives the version")
print("   of the format nobody has written yet.")
