"""Ask the implementation what it accepts, instead of reading what is listed.

iconv(1)'s man page lists five flags and no conversion suffixes, yet the
command accepts //TRANSLIT and //IGNORE.  The general shape of that problem is
here in miniature: Python's manual prints a table of about a hundred codecs,
and codecs.lookup() answers to several hundred names.  The registry is the
authority; the table is a summary of it.
"""
import codecs

print("1. ONE CODEC, MANY SPELLINGS -- lookup() NORMALISES BEFORE IT SEARCHES")
for name in ["utf-8", "utf8", "utf_8", "UTF-8", "U8", "utf 8"]:
    print(f"   codecs.lookup({name!r:9}).name -> {codecs.lookup(name).name!r}")
print()
print("   Six spellings, one codec.  Punctuation and case are folded away, so")
print("   a name absent from the documented table may still be a live alias.")
print()

print("2. NAMES THE TUTORIALS DO NOT PRINT, ASKED DIRECTLY")
for name in ["latin1", "l1", "cp819", "iso8859-1", "utf-8-sig", "punycode",
             "idna", "undefined", "mbcs", "cp65001", "utf-9"]:
    try:
        print(f"   {name:<11} -> {codecs.lookup(name).name}")
    except LookupError:
        print(f"   {name:<11} -> LookupError: unknown encoding")
print()
print("   'l1' and 'cp819' are Latin-1 under names no page here has ever used.")
print("   'mbcs' is real, and Windows-only -- a documented codec that is a")
print("   LookupError on this machine.  So the answer is a fact about the")
print("   interpreter you are running, not about the language.")
print()

print("3. THE PROBE, AS A FUNCTION YOU CAN KEEP")
def supported(name: str) -> bool:
    try:
        codecs.lookup(name)
        return True
    except LookupError:
        return False

wanted = ["utf-8", "shift_jis", "koi8-r", "cp1250", "big5", "euc-kr", "utf-7",
          "iso2022_jp", "tis-620", "kz1048", "utf-2", "ebcdic"]
have = [n for n in wanted if supported(n)]
miss = [n for n in wanted if not supported(n)]
print(f"   asked for {len(wanted)} names")
print(f"   present:  {', '.join(have)}")
print(f"   absent:   {', '.join(miss)}")
print()
print("   Three lines, and no documentation was consulted.  Write the same")
print("   probe for any tool: try the flag, read the exit status, and believe")
print("   the machine over the page -- in both directions.")
