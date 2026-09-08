"""Answer key: the same guard, two orders, one of them wrong."""
import os, unicodedata as ud, urllib.parse

BLOCKED = "/etc/passwd"

def check_then_canon(path):
    if path == BLOCKED: return "REFUSED"
    return "opened " + os.path.normpath(urllib.parse.unquote(path))

def canon_then_check(path):
    real = os.path.normpath(urllib.parse.unquote(path))
    if real == BLOCKED: return "REFUSED"
    return "opened " + real

ATTEMPTS = ["/etc/passwd", "/etc/./passwd", "/var/../etc/passwd", "/etc/%70asswd", "/tmp/ok"]
print(f"{'input':<24} {'check first':<26} {'canonicalise first'}")
for a in ATTEMPTS:
    print(f"{a:<24} {check_then_canon(a):<26} {canon_then_check(a)}")
print()
print("   Four of the five reach /etc/passwd, and the guard that runs FIRST")
print("   stops exactly one of them -- the one spelled the obvious way. The")
print("   check was not wrong: it told the truth about the string it was given.")
print("   Everything after it handed the next stage a different string.")
print()
print("THE RULE, AND WHY IT IS NOT 'CHECK HARDER'")
print("   You cannot enumerate the spellings. Percent-encoding, dot segments,")
print("   symlinks, case folding, Unicode normalization and overlong UTF-8 all")
print("   produce the same resource from different bytes, and a blocklist has")
print("   to be right about all of them at once. Canonicalising first makes the")
print("   check compare ONE value against ONE value.")
print()
print("THE UNICODE VERSION OF THE SAME BUG")
name = "ADMIN"
print(f"   stored user   {name!r}")
for spelling in ["admin", "ADMIN", "ａdmin", "Ⓐdmin"]:
    folded = ud.normalize("NFKC", spelling).casefold()
    print(f"   {spelling:<8} -> NFKC+casefold {folded!r:<10} "
          f"{'MATCHES the reserved name' if folded == name.casefold() else 'distinct'}")
print("   If you compare before folding, all four are different users. If you")
print("   fold before comparing, all four are one. Neither is 'safe' on its")
print("   own -- what makes it safe is that ONE of them is the stored form and")
print("   everything is converted to it before any comparison happens.")
print()
print("AND THE ORDER THAT IS STILL WRONG")
print("   canonicalise -> check -> canonicalise again is not belt and braces;")
print("   the second canonicalisation can move the value again. Do it once, as")
print("   early as possible, and pass the CANONICAL value downstream -- never")
print("   the original alongside it, or something will use the wrong one.")

assert canon_then_check("/etc/%70asswd") == "REFUSED"
assert check_then_canon("/etc/%70asswd") != "REFUSED"
