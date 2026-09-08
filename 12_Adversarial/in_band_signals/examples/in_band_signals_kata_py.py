"""Answer key: five bytes that end a field for somebody."""
print("THE SHAPE")
print("   A character that means 'stop here' or 'what follows is an")
print("   instruction' to one program is ordinary data to another. Put it in a")
print("   field and the two disagree about where the field ends -- and one of")
print("   them is the one that acts.")
print()
rows = [
    ("00", "NUL", "ends a C string", "the kernel and every C library"),
    ("0a", "LF", "ends a record", "line-oriented tools, log parsers, HTTP headers"),
    ("2c", ",", "ends a field", "every CSV reader"),
    ("22", '"', "ends a quoted field", "CSV, JSON, shell"),
    ("3d", "=", "ends a formula's name", "a spreadsheet, if it is the FIRST byte"),
]
print(f"   {'byte':<6} {'char':<5} {'means':<26} to")
for b, c, m, who in rows:
    print(f"   {b:<6} {c:<5} {m:<26} {who}")
print()
print("THE ONE THAT IS NOT A BYTE AT ALL")
print("   A leading =, +, - or @ in a CSV cell is data to your program and a")
print("   FORMULA to a spreadsheet. Nothing in the file changed; the meaning")
print("   was assigned by the reader. Prefixing the cell with a quote or a")
print("   space is the fix, and it is a fix in the WRITER, because the reader")
print("   is not yours.")
print()
print("WHY ESCAPING IS NOT ONE PROBLEM")
name = 'O"Brien, Jr.\nadmin'
print(f"   the value  {name!r}")
print("   To put that in a CSV cell you double the quote and wrap the field.")
print("   To put it in a JSON string you backslash the quote and the newline.")
print("   To put it in a shell command you do something different again.")
print("   Three destinations, three escapings, and the value is unchanged in")
print("   all three -- so escaping is a property of the CHANNEL, never of the")
print("   data, and a single 'sanitise' function that runs early is the bug.")
print()
print("THE TWO DEFENCES, AND ONLY ONE OF THEM SCALES")
print("   1. Escape at the boundary, per destination, with the destination's")
print("      own library. csv.writer, json.dumps, shlex.quote, a parameterised")
print("      query -- each knows its own in-band signals.")
print("   2. Get the data out of the band entirely: a length-prefixed field, a")
print("      separate argument, a bound parameter. Then no byte can mean")
print("      'field ends here' because the length already said where.")
print()
print("   Everything else -- stripping, blocklists, replacing quotes on input")
print("   -- is guessing which channel the value will eventually cross, and")
print("   values usually cross more than one.")

assert '"' in 'O"Brien, Jr.\nadmin'
