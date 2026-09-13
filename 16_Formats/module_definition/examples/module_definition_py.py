#!/usr/bin/env python3
"""DEF: a text file in a list of binary formats -- EXPORTS, one name per
line with an optional ordinal and flags -- read by Ghidra through a
reader with no charset named, which means the JVM's default.

Run:  python3 module_definition_py.py
"""

DEF = """; a module-definition file, as the MSVC linker reads it
LIBRARY café
EXPORTS
    Foo
    Bar @2
    Baz @ 3 NONAME
    Qux=Foo
    Data1 DATA
    Secret PRIVATE
    Fwd=other.Func
    Fwd2=other.#5
"""


def parse_export(line):
    """DefExportLine, as Ghidra 12.1.3 tokenises it."""
    name = internal = other = None
    other_ordinal = ordinal = None
    flags = []
    tokens = line.split()
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if name is None:
            name, _, rhs = tok.partition("=")
            if rhs:
                mod, _, rest = rhs.partition(".")
                if not rest:
                    internal = rhs
                else:
                    other = mod
                    if rest.startswith("#"):
                        other_ordinal = int(rest[1:])
                    else:
                        internal = rest
        elif ordinal is None and tok.startswith("@"):
            if tok == "@":
                i += 1
                ordinal = int(tokens[i])
            else:
                ordinal = int(tok[1:])
        elif tok in ("NONAME", "PRIVATE", "DATA"):
            flags.append(tok)
        i += 1
    return name, internal, other, other_ordinal, ordinal, flags


def parse(text):
    exports, in_exports = [], False
    for line in text.splitlines():
        if line.startswith(";") or not line:
            continue
        if line.startswith("LIBRARY"):
            continue
        if line.startswith("EXPORTS"):
            in_exports = True
            continue
        if in_exports:
            exports.append(parse_export(line))
    return exports


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    section(1, "TEXT: A KEYWORD, THEN ONE EXPORT PER LINE")
    print(f"   {'name':<8} {'ordinal':<8} {'flags':<10} {'internal name':<14} other module")
    for name, internal, other, other_ordinal, ordinal, flags in parse(DEF):
        via = f"{other}.#{other_ordinal}" if other_ordinal else (other or "")
        print(f"   {name:<8} {str(ordinal) if ordinal is not None else '-':<8} {' '.join(flags) or '-':<10} {internal or '-':<14} {via}")
    print()
    print("   The loader skips ';' comments and empty lines, ignores LIBRARY,")
    print("   starts at EXPORTS, and tokenises each line after it: the name,")
    print("   with =internal or =module.name or =module.#ordinal glued on; then")
    print("   an @ordinal, or an @ followed by a separate number; then flags.")
    print()

    section(2, "THE LINE IS SPLIT ON WHITESPACE, SO THESE ARE THE SAME EXPORT")
    for line in ("Bar @2", "Bar   @2", "Bar\t@2", "Bar @ 2", "Bar@2"):
        name, *_, ordinal, flags = parse_export(line)
        print(f"   {line!r:<12} -> name {name!r:<8} ordinal {ordinal}")
    print()
    print("   Except the last: with no whitespace the '@2' is part of the name")
    print("   token, and the ordinal is never seen. Whitespace is the grammar.")
    print()

    section(3, "THE CHARSET IS THE JVM'S DEFAULT, WHICH IS UTF-8 SINCE JAVA 18")
    for label, raw in (("written as UTF-8", DEF.encode("utf-8")), ("written as Windows-1252", DEF.encode("cp1252"))):
        text = raw.decode("utf-8", errors="replace")          # what an InputStreamReader with the default charset does
        library = next(l for l in text.splitlines() if l.startswith("LIBRARY"))
        names = [e[0] for e in parse(text)]
        print(f"   {label:<26} LIBRARY line reads {library[8:]!r:<10} exports {names[:3]}...")
    print()
    print("   Ghidra opens the file with new InputStreamReader(stream) and no")
    print("   charset, so the JVM's default applies -- UTF-8 on every platform")
    print("   since JEP 400, and Ghidra 12 runs on Java 21. A .def saved by an")
    print("   old Visual Studio in the ANSI code page decodes its accented")
    print("   comment and library name to U+FFFD, and every export is untouched,")
    print("   because export names are ASCII. The failure is invisible exactly")
    print("   where it does not matter.")
    print()

    section(4, "LINE ENDINGS DO NOT MATTER, AND ONE THING DOES")
    for ending, label in (("\n", "LF"), ("\r\n", "CRLF"), ("\r", "CR alone")):
        text = DEF.replace("\n", ending)
        print(f"   {label:<10} {len(parse(text))} exports")
    print()
    bom = "﻿" + DEF
    print(f"   with a BOM   {len(parse(bom))} exports   -- the first line no longer starts with ';', but nothing before EXPORTS is read anyway")
    bom_exports = "﻿EXPORTS\nFoo\n"
    print(f"   BOM then EXPORTS as the first line   {len(parse(bom_exports))} exports   -- 'EXPORTS' is not at the start of the line any more")
    print()
    print("   readLine() ends a line at LF, CRLF or a bare CR, so the three files")
    print("   parse alike. A byte-order mark is not whitespace and startsWith")
    print("   does not skip it: a file whose first line is EXPORTS, saved as")
    print("   UTF-8 with BOM, has no exports at all to this reader.")


if __name__ == "__main__":
    main()
