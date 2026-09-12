#!/usr/bin/env python3
"""One string of digits, several readers, and no two of them agree.

`010` is ten to `int()`, eight to `int(s, 8)`, a refusal to `int(s, 0)`, and --
inside one dotted quad -- eight to `socket.inet_aton` and a refusal to
`ipaddress`. Every one of those is correct. The base was never in the string.

Run:  python3 which_base_did_you_mean_py.py
"""

import ipaddress
import socket


def show(label: str, fn) -> None:
    """Print what a reader did with the string, or the name of its refusal."""
    try:
        print(f"   {label:<34} -> {fn()}")
    except Exception as e:  # noqa: BLE001 -- the KIND is the result here
        print(f"   {label:<34} -> {type(e).__name__}   (refused)")


print("1. ONE FIELD OF FOUR CHARACTERS, AND FIVE READERS IN ONE STANDARD LIBRARY")
show("int('010')", lambda: int("010"))
show("int('010', 8)", lambda: int("010", 8))
show("int('010', 2)", lambda: int("010", 2))
show("int('010', 0)", lambda: int("010", 0))
show("inet_ntoa(inet_aton('010.0.0.1'))", lambda: socket.inet_ntoa(socket.inet_aton("010.0.0.1")))
show("ipaddress.ip_address('010.0.0.1')", lambda: ipaddress.ip_address("010.0.0.1"))
print("   Ten, eight, two, a refusal, 8.0.0.1 and a refusal. Nothing in '010' picked")
print("   one of those; each reader brought its own base and none of them said so.")

print()
print("2. AND inet_aton TAKES FOUR MORE SPELLINGS NOBODY TYPED ON PURPOSE")
for s in ("010.0.0.1", "0x8.0.0.1", "134744072", "10.1", "0177.1", "8.8.8.8"):
    show(f"inet_aton({s!r})", lambda s=s: socket.inet_ntoa(socket.inet_aton(s)))
print("   A leading zero is octal, 0x is hex, a bare number is the whole 32-bit")
print("   address, and a dotted address may have four parts, three, two or one --")
print("   all of it documented in inet_aton(3), and all of it older than DNS.")
print("   The last two are the ones that end up in a security report: 0177.1 is")
print("   127.0.0.1, so an allow-list that compares the STRING and a connect()")
print("   that PARSES it are two readers of one field, disagreeing about a base")
print("   nobody wrote down. That is the classic SSRF filter bypass.")

print()
print("3. WHICH IS WHY ipaddress REFUSES EVERY ONE OF THEM")
for s in ("010.0.0.1", "0x8.0.0.1", "134744072"):
    show(f"ip_address({s!r})", lambda s=s: ipaddress.ip_address(s))
print("   Not an oversight in the older function and not a fix to it -- the two")
print("   have different jobs. CPython's own comment in ipaddress.py says which")
print("   standard it chose to be as strict as, and names the bug that made it:")
print("      # Handle leading zeros as strict as glibc's inet_pton()")
print("      # See security bug bpo-36384")

print()
print("4. A PREFIX IS ACCEPTED ONLY WHERE IT AGREES WITH THE BASE YOU NAMED")
show("int('0xFF', 16)", lambda: int("0xFF", 16))
show("int('0xFF')", lambda: int("0xFF"))
show("int('0xFF', 10)", lambda: int("0xFF", 10))
show("int('FF', 16)", lambda: int("FF", 16))
show("int('0b1010', 2)", lambda: int("0b1010", 2))
show("int('0o377', 8)", lambda: int("0o377", 8))
show("int('0x41', 0)", lambda: int("0x41", 0))
print("   So the prefix is never the argument -- `base` is. int(s, 0) is the one")
print("   reading that asks the string, and it is also the one that refuses '010',")
print("   because a leading zero was octal in C and Python 3 declined to inherit it.")

print()
print("5. 'IS IT DIGITS' IS A DIFFERENT QUESTION FROM 'WILL int() TAKE IT'")
print(f"   {'string':<10} {'isdigit()':<11} {'isdecimal()':<13} int()")
for s in ("42", "٤٢", "²"):
    try:
        got = str(int(s))
    except ValueError:
        got = "ValueError"
    print(f"   {s!r:<10} {str(s.isdigit()):<11} {str(s.isdecimal()):<13} {got}")
print("   Row 2 is two ARABIC-INDIC digits and int() reads them as 42. Row 3 is")
print("   SUPERSCRIPT TWO: isdigit() says yes and int() refuses it, so the guard")
print("   everyone writes -- `if s.isdigit(): int(s)` -- raises on a string it just")
print("   approved. isdecimal() is the one that matches int(); better still, try it.")
