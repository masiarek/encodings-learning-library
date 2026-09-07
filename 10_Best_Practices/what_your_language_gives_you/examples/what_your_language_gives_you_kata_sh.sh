#!/usr/bin/env bash
# The kata's answer, run rather than typed.
#
# Six one-line conversions, each asked the same question: does it raise, does
# it lose something, or does the text come back? Then the second half, which
# is about the page's headline: which of the six could a browser do at all.
#
# Nothing here reads the machine -- no $USER, no date, no hostname, no tool
# whose flags differ between BSD and GNU. The shell is only a harness; every
# measurement is made by the python3 that is already on the reader's machine.
#
# Run:  bash what_your_language_gives_you_kata_sh.sh
set -u

rule() { printf '\n%s\n%s\n\n' "$1" "------------------------------------------------------------------------"; }

rule "PART ONE -- SIX ROUND TRIPS"

python3 - <<'PY'
WORD = "żółw"          # zolw, the Polish for turtle: z-dot o-acute l-stroke w
BYTES = b"caf\xe9.txt"                # a Latin-1 e-acute loose in a stream declared UTF-8

def show(n, label, fn):
    try:
        out = fn()
    except UnicodeError as exc:
        print(f"   {n}  {label:52} {type(exc).__name__}")
        return
    verdict = "round-trips" if out.same else f"LOSES  -> {out.got!r}"
    print(f"   {n}  {label:52} {verdict}")

class R:
    def __init__(self, got, same): self.got, self.same = got, same

def rt(text, enc, errors="strict"):
    back = text.encode(enc, errors).decode(enc, errors)
    return R(back, back == text)

def rt_bytes(raw, enc, errors="strict"):
    back = raw.decode(enc, errors).encode(enc, errors)
    return R(back, back == raw)

show(1, f"{WORD!r}.encode('cp1250')", lambda: rt(WORD, "cp1250"))
show(2, f"{WORD!r}.encode('latin-1')", lambda: rt(WORD, "latin-1"))
show(3, f"{WORD!r}.encode('latin-1', 'replace')", lambda: rt(WORD, "latin-1", "replace"))
show(4, f"{WORD!r}.encode('latin-1', 'backslashreplace')", lambda: rt(WORD, "latin-1", "backslashreplace"))
show(5, "b'caf\\xe9.txt'.decode('utf-8', 'surrogateescape')", lambda: rt_bytes(BYTES, "utf-8", "surrogateescape"))
show(6, "b'caf\\xe9.txt'.decode('latin-1')", lambda: rt_bytes(BYTES, "latin-1"))

esc = WORD.encode("latin-1", "backslashreplace")
print()
print(f"   the word, as characters       {' '.join(f'U+{ord(c):04X}' for c in WORD)}")
print(f"   which of them latin-1 holds   {''.join('y' if ord(c) < 256 else 'n' for c in WORD)}"
      f"   ({sum(ord(c) < 256 for c in WORD)} of {len(WORD)})")
print(f"   line 1 wrote                  {WORD.encode('cp1250').hex(' ')}")
print(f"   line 3 wrote                  {WORD.encode('latin-1', 'replace').hex(' ')}"
      f"   = {WORD.encode('latin-1', 'replace').decode('latin-1')!r}")
print(f"   line 4 wrote                  {len(esc)} bytes: {esc.decode('latin-1')}")
print(f"   line 5 held the byte as       U+{ord(BYTES.decode('utf-8', 'surrogateescape')[3]):04X}")
print(f"   line 6 held the byte as       U+{ord(BYTES.decode('latin-1')[3]):04X}")
PY

cat <<'TEXT'

   Only one of the six raises. Lines 3 and 4 lose the word and report
   nothing at all, and they lose it PARTLY, which is the shape this
   actually takes in a live system: latin-1 holds two of the four
   letters. It has an o-acute, so o survives; it has no z-dot and no
   l-stroke, so those two become question marks in line 3 -- and the
   result is still printable, still four characters long, and still
   half right. A field like that passes every length check you have.

   Line 4 keeps the information and stops being the word: fourteen
   characters where there were four, the two casualties spelled out as
   the escapes a person can read back and no program will match on.

   Lines 5 and 6 both round-trip, and that is the sting. The one
   nobody expects is 6: decoding unknown bytes as LATIN-1 preserves
   them perfectly, because latin-1 maps bytes 0..255 onto code points
   0..255 and back -- the identity map the Rust section is about. It
   is the oldest trick in this field and it is not the same as line 5.

   Line 5 says "this was a byte I could not read" in the code point
   itself, U+DCE9, which no encoder will accept by accident. Line 6
   says "this was e-acute", which is a claim, and a false one: nothing
   in the file said latin-1. Both give the bytes back; only one of
   them is still honest about what it does not know.
TEXT

rule "PART TWO -- WHICH OF THE SIX COULD A BROWSER DO?"

cat <<'TEXT'
   Reading is not the question. TextDecoder handles cp1250 and
   latin-1 both, so the DECODE halves of lines 5 and 6 are fine.

   Every ENCODE in the list is impossible. Lines 1 to 4 all ask for
   bytes in a table that is not UTF-8, and TextEncoder emits UTF-8
   and nothing else -- so line 1, the only one of the six that both
   round-trips and stays honest about its encoding, is exactly the
   one a browser cannot perform.

   Which is the page in one line. The platform will read all forty
   tables and write one, so "we convert it in the front end" is a
   sentence that has to say which direction before it means anything.
TEXT
