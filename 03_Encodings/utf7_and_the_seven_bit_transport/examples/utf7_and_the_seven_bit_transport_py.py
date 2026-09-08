#!/usr/bin/env python3
"""UTF-7: a sound answer to a real constraint, and the one clause that ruined it.

In 1997 a mail relay could not be trusted with a byte above 0x7F. UTF-7 answers
that by spelling any Unicode character in printable ASCII: `+` shifts into a
modified Base64 run over UTF-16BE code units, `-` shifts back out. That much is
a good design, and it is what sections 1 and 2 measure.

Sections 3 and 4 are why it is deprecated. RFC 2152 lets an encoder write
certain ASCII characters EITHER directly OR inside a Base64 run, so one string
has many legal spellings -- and a decoder must accept all of them while an
encoder writes one. Section 3 counts the spellings of a single eight-character
string, exhaustively, and puts every one through the decoder shipped with this
Python. Section 4 asks what that decoder refuses, and what it carries.

Everything here is arithmetic and table lookup. Nothing is read out of the
Unicode character database, nothing is random, nothing touches the network.

Run:  python3 utf7_and_the_seven_bit_transport_py.py
"""

import base64
import codecs
import email.header
import itertools
import quopri

RULE = "-" * 72

# RFC 2152's modified Base64 is RFC 2045's alphabet without the pad character.
B64 = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/")

CAFE = "café"
PAYLOAD = "<script>"


def say(title: str) -> None:
    print(f"\n{title}\n{RULE}")


def hi(raw: bytes) -> str:
    """The highest byte value in a byte string, as hex."""
    return f"0x{max(raw):02X}"


def shift(text: str) -> str:
    """One modified-Base64 run: UTF-16BE code units, base64, pad stripped."""
    return "+" + base64.b64encode(text.encode("utf-16-be")).rstrip(b"=").decode()


# ---------------------------------------------------------------------------
say("1. THE CONSTRAINT, AND FOUR ANSWERS TO IT")

print("   SMTP and NNTP in the 1990s were SEVEN-BIT transports: a relay was")
print("   entitled to strip the high bit off every byte it carried. So a")
print("   payload with any byte above 0x7F could not be sent as itself.")
print()
print(f"   the string             {CAFE!r}")
print(f"   as UTF-8               {CAFE.encode().hex(' ')}   highest byte {hi(CAFE.encode())}")
print("   ...which is exactly the byte the transport would not carry.")
print()

rows = [
    ("base64", base64.b64encode(CAFE.encode()).decode(),
     "whole stream, unreadable, +33% always"),
    ("quoted-printable", quopri.encodestring(CAFE.encode()).decode(),
     "per byte, ASCII stays legible"),
    ("MIME encoded-word", email.header.Header(CAFE, "utf-8").encode(),
     "names its own charset -- alone in this table"),
    ("UTF-7", CAFE.encode("utf-7").decode("ascii"),
     "per character, ASCII stays legible, no charset named"),
]
print("   scheme              output                     what it does")
for name, out, note in rows:
    print(f"   {name:<19} {out:<26} {note}")
print()
print(f"   Highest byte across all four outputs: "
      f"{hi(''.join(o for _, o, _ in rows).encode())}. Every one is ASCII,")
print("   which was the whole requirement.")
print("   UTF-7 is the entry that keeps ASCII readable AND carries the rest of")
print("   Unicode without a second header naming a table. That is a genuine")
print("   advantage over the other three, and it is why the format existed.")

# ---------------------------------------------------------------------------
say("2. THE MECHANISM: + SHIFTS IN, - SHIFTS OUT, THE MIDDLE IS UTF-16")

print("   code point   UTF-16BE code units   base64      UTF-7        character")
for ch in ("é", "€", "😀"):
    print(f"   {f'U+{ord(ch):04X}':<12} {ch.encode('utf-16-be').hex(' '):<21}"
          f" {shift(ch)[1:]:<11} {ch.encode('utf-7').decode():<12} {ch}")
print()
print("   The second column is the finding. A UTF-7 run is Base64 of UTF-16")
print("   CODE UNITS -- not of code points, and not of UTF-8 bytes -- so an")
print("   emoji travels through a surrogate pair on its way into a mail body,")
print("   and its run is twice as long as the two BMP characters above it.")
print("   The '=' padding Base64 would add is stripped. A run ends at '-', or")
print("   at the first byte that is not in the Base64 alphabet, or at the end")
print("   of the input; a '-' that ends a run is absorbed and is not output.")

# ---------------------------------------------------------------------------
say("3. THE ASYMMETRY: THE DECODER ACCEPTS WHAT THE ENCODER NEVER WRITES")

escaped = b"+ADw-script+AD4-"
print(f"   decode  {escaped!r:<19}  ->  {escaped.decode('utf-7')!r}")
print(f"   encode  {PAYLOAD!r:<19}  ->  {PAYLOAD.encode('utf-7')!r}   <- unchanged")
print()
print("   Both are correct. RFC 2152 puts '<' and '>' in Set O, the OPTIONAL")
print("   direct characters: an encoder may pass them through or escape them,")
print("   and a decoder must accept either. Round-tripping a payload through")
print("   your own encoder therefore proves nothing about your decoder.")
print()

escapes = [chr(c) for c in range(0x20, 0x7F)
           if chr(c).encode("utf-7") != chr(c).encode("ascii")]
print(f"   printable ASCII this encoder escapes:  {' '.join(escapes)}"
      f"      ({len(escapes)} of {0x7F - 0x20})")
print("   Everything else, angle brackets included, is passed through. That is")
print("   one encoder's policy, not the format's rule.")
print()

print("   Three spellings of one character:")
for cand in (b"<", b"+ADw-", b"+ADw"):
    print(f"     {cand!r:<10} -> {cand.decode('utf-7')!r}")
print("   Direct; shifted in and explicitly out; shifted in and ended by the")
print("   end of the input.")


def spellings(text: str) -> set[bytes]:
    """Every UTF-7 spelling of `text` under one stated rule.

    Cut the string into consecutive groups; write each group either directly
    or as one modified-Base64 run; a run's terminating '-' may be omitted only
    where the next byte is not itself in the Base64 alphabet. Nothing here is
    asserted -- every candidate is put through the decoder before it counts.
    """
    n = len(text)
    found: set[bytes] = set()
    for cuts in itertools.product((0, 1), repeat=n - 1):
        groups, cur = [], [0]
        for i, cut in enumerate(cuts, 1):
            if cut:
                groups.append(cur)
                cur = []
            cur.append(i)
        groups.append(cur)
        for labels in itertools.product("db", repeat=len(groups)):
            opens = ["+" if lab == "b" else text[g[0]] for g, lab in zip(groups, labels)]
            parts = []
            for i, (g, lab) in enumerate(zip(groups, labels)):
                chunk = text[g[0]: g[-1] + 1]
                if lab == "d":
                    parts.append([chunk])
                    continue
                body = shift(chunk)
                nxt = opens[i + 1] if i + 1 < len(groups) else None
                parts.append([body + "-"] + ([body] if nxt not in B64 else []))
            for combo in itertools.product(*parts):
                found.add("".join(combo).encode("ascii"))
    return found


built = spellings(PAYLOAD)
verified = {b for b in built if b.decode("utf-7") == PAYLOAD}
longest = max(verified, key=len)
print()
print(f"   Now the whole string {PAYLOAD!r}, enumerated under that rule:")
print(f"     byte strings constructed                {len(built):>5}")
print(f"     of those, decoded back to the string    {len(verified):>5}")
print(f"     rejected, or decoded to something else  {len(built) - len(verified):>5}")
print(f"     spellings this encoder will ever write  {1:>5}   "
      f"({PAYLOAD.encode('utf-7')!r})")
print(f"     shortest                                {min(verified, key=len)!r}")
print(f"     longest, at {len(longest)} bytes                     {longest!r}")
print()
print("   That ratio IS the security problem. A filter that searches bytes is")
print("   guarding one spelling out of thousands, and the attacker chooses")
print("   which one to send. Compare overlong UTF-8, where the same argument")
print("   ends the other way: one character, one legal spelling, and every")
print("   other candidate ill-formed and rejected on sight.")

# ---------------------------------------------------------------------------
say("4. WHAT THIS DECODER REFUSES, AND WHAT IT CARRIES")

# The class is printed and the codec's own wording is not: a diagnostic
# string is a property of the interpreter, not of these bytes.
REFUSALS = [
    (b"+ADx-", "'ADx' carries '<' plus two padding bits that are not zero"),
    (b"+AGEA-", "22 payload bits: one code unit and six bits of nothing"),
]
print("   refused:")
for cand, why in REFUSALS:
    try:
        got = repr(cand.decode("utf-7"))
    except UnicodeDecodeError as exc:
        got = f"{type(exc).__name__}   {why}"
    print(f"     {cand!r:<12} -> {got}")
print()
print("   carried, and each of these is five printable ASCII bytes:")
for cand, note in ((b"+AAA-", "a NUL, through a channel that takes printable ASCII only"),
                   (b"+AB8-", "U+001F, a C0 control"),
                   (b"+2D0-", "a LONE SURROGATE -- half of the emoji above")):
    print(f"     {cand!r:<12} -> {cand.decode('utf-7')!r:<12} {note}")
print()
lone = b"+2D0-".decode("utf-7")
try:
    lone.encode("utf-8")
    verdict = "encodes"
except UnicodeEncodeError as exc:
    verdict = f"{type(exc).__name__} -- a surrogate is not a scalar value"
print(f"   and that last one, re-encoded to UTF-8:  {verdict}")
print("   So a UTF-7 decode that SUCCEEDS can hand you a string your next")
print("   stage cannot write out at all -- the UTF-16 layer showing through.")
print()
print("   The codec is not lax, though. RFC 2152 calls a run ill-formed when")
print("   the discarded bits are non-zero, and the two refusals above are")
print("   exactly that rule and the incomplete-run rule. The danger was never")
print("   a sloppy implementation; it is the format's own optional escape,")
print("   faithfully implemented. Which is why deprecating the format was the")
print("   fix, and hardening the decoder was not.")

# ---------------------------------------------------------------------------
say("5. AND THE CODEC IS STILL HERE")

print(f"   codecs.lookup('utf-7').name  ->  {codecs.lookup('utf-7').name!r}")
print("   It takes no flag to reach and prints no warning when used. .NET")
print("   marked UTF7Encoding obsolete and browsers stopped sniffing UTF-7,")
print("   but a decoder kept alive for compatibility is still a decoder")
print("   somebody's input can reach. Hence the rule this page ends on: name")
print("   the encoding at the boundary, so nothing downstream is left to")
print("   choose a second reading of the same bytes.")
