# Escaping into ASCII

**Level:** 201 · for interface work

**One line:** A JSON string, a URL, an email header and a domain name are channels that carry ASCII and nothing else, so text crossing one of them is encoded **twice** — and the four schemes you will meet disagree about what that second layer wraps: JSON escapes UTF-16 code units, `%XX` escapes bytes and never says whose, a MIME encoded-word wraps bytes of a charset it names, and punycode re-spells code points and touches no bytes at all.

## Four channels that will not carry your bytes

Everything so far in this chapter has been about writing a code point as bytes. This page is about the places you are not allowed to send the bytes.

Each of the four has a different reason and all four are historical. A **URL** is defined by [RFC 3986 ↗](https://www.rfc-editor.org/rfc/rfc3986#section-2.1) as a sequence of characters from a small ASCII set, because in 1994 a URL had to survive being read down a telephone and typed into a terminal of unknown make. An **email header** is US-ASCII by [RFC 5322 ↗](https://www.rfc-editor.org/rfc/rfc5322), because SMTP was a seven-bit protocol and the mail relays of the day would cheerfully strip the eighth bit off every byte in transit. A **domain name** label is letters, digits and hyphen, because DNS is older than both and its resolvers are everywhere and unpatchable. And a **JSON** document is UTF-8 by [RFC 8259 ↗](https://www.rfc-editor.org/rfc/rfc8259#section-8.1) — so JSON is the odd one, a channel that *can* carry your bytes and still has an ASCII escape form, because JavaScript's strings were UTF-16 in 1999 and the notation kept it.

Four committees, four decades, four answers. What makes this a lesson rather than a list is that the answers are not variations on one idea: **they escape four different things.**

## What each scheme actually escapes

One word — `żółw`, four letters, seven UTF-8 bytes — through all four:

| scheme | it escapes | `żółw` becomes | names the encoding? |
|---|---|---|---|
| JSON `\uXXXX` | **UTF-16 code units** | `"\u017c\u00f3\u0142w"` | no — the file is UTF-8, the escape is UTF-16 |
| percent `%XX` | **bytes** | `%C5%BC%C3%B3%C5%82w` | **no**, and that is its one real weakness |
| MIME encoded-word | **bytes of a named charset** | `=?utf-8?b?xbzDs8WCdw==?=` | **yes** — the only one of the four |
| punycode | **code points** | `xn--w-uga1v8h` | not applicable — no bytes are involved |

No two of those outputs share a single character, and the differences are not cosmetic. Read the second column and the rest of the page follows from it.

## An escape is a second encoding, wrapped around the first

That is the whole mental model, and it is why layer confusion is the characteristic bug here rather than mojibake.

[Mojibake](../mojibake/README.md) is one layer decoded with the wrong table. This is the same layer decoded the wrong *number of times*. Escaping something already escaped gives `%25C5%25BC` — the `%25` is a percent sign that itself needed escaping — and one `unquote` of that does not return text, it returns the previous layer, `%C5%BC`, which still looks like a bug and invites a second guess at the table. The fix is never another `unquote`; it is counting how many wrappings the value has and taking off exactly that many. `%C3%83%C2%A9` is the classic sighting: UTF-8 bytes of `Ã©`, which are themselves UTF-8 bytes of `é` read as [Latin-1](../../02_Characters/code_pages/README.md) — two layers of damage, percent-encoded, and perfectly reversible once you can name them.

The same shape appears with the other three. A subject line that arrives reading `=?utf-8?B?PT91dGYtOD9C...?=` has been encoded twice by two well-meaning mail libraries. A JSON string containing `\\u017c` — a literal backslash, then `u017c` — is a `ż` that was escaped a second time on its way into a nested document.

## Only one of the four says what it wrapped

Look again at the last column of the table. Percent-encoding gives you bytes with no statement of what produced them, and [RFC 3986 §2.5 ↗](https://www.rfc-editor.org/rfc/rfc3986#section-2.5) can only *recommend* UTF-8 for new schemes — the syntax has nowhere to record the answer, so `%BF%F3%B3w` from an old Latin-2 form is exactly as well-formed as `%C5%BC%C3%B3%C5%82w` and means the same word. The server has to know, or guess.

The MIME encoded-word of [RFC 2047 ↗](https://www.rfc-editor.org/rfc/rfc2047) is the one design that fixed this, and it fixed it the simple way: the charset is written into the header, between the first two question marks, ahead of the payload. `=?iso-8859-2?B?v/Ozdw==?=` still decodes correctly today, thirty years after anyone chose that code page, with no convention to agree on and nothing to sniff. It is worth noticing what that costs — nothing — and what its absence costs everywhere else.

`B` is base64 and `Q` is quoted-printable, a Latin-1-flavoured cousin of percent-encoding that writes `=C5` where a URL writes `%C5`. The letter is case-insensitive, which is why Python emits `?b?` and most mail clients emit `?B?`.

## The surrogate that leaks into a UTF-8 format

A JSON `\uXXXX` is one **UTF-16 code unit**, so a character above `U+FFFF` is written as a [surrogate pair](../utf16_and_surrogates/README.md): `😀` is `\ud83d\ude00`. There are no surrogates in the document that carries it — JSON files are UTF-8, and UTF-8 cannot encode a surrogate at all — so the escape form is the last place in a modern stack where UTF-16 still shows through.

It has a sharp edge. **Half a pair is valid JSON syntax.** `"\ud83d"` parses; Python hands back a one-character `str` that no encoder will accept, so the failure surfaces at whatever line eventually writes UTF-8 — a database insert, a log, a response — and not at the parse that let it in. Rust will not construct the string at all (`String::from_utf16` refuses a lone surrogate, and `char::decode_utf16` names the unit), which is the same [boundary](../validation_is_a_boundary/README.md) argument in a different type system: check at the door, and the rest of the program cannot hold a broken value.

The practical rule is one line: **reject lone surrogates where you parse, not where you encode.**

## Punycode is the odd one out

Punycode ([RFC 3492 ↗](https://www.rfc-editor.org/rfc/rfc3492)) is not a rewriting of bytes at all. It works on code points, re-spelling a label as ASCII: the ASCII characters keep their order at the front, a hyphen follows, and the rest is a base-36 description of which characters were removed and where they belong. `żółw` becomes `w-uga1v8h`, and `xn--` in front marks the label as encoded rather than a domain that really is called that.

Because no bytes are involved, punycode cannot produce mojibake — there is no table to get wrong. Two other things follow, one useful and one not:

**IDNA normalises before it encodes, and the stdlib's version of "normalise" is twenty years old.** `'straße.de'.encode('idna')` returns `strasse.de` — a *different domain*, not another spelling of the same one. That is IDNA2003's nameprep, which treated `ß` as a way of writing `ss`; [IDNA2008 ↗](https://www.rfc-editor.org/rfc/rfc5891) treats it as a letter and gives `xn--strae-oqa.de`. Python's built-in codec implements the 2003 rules, the `idna` package on PyPI the 2008 ones, and neither call site mentions a version.

**And it preserves the differences a person cannot see.** Latin `a` and Cyrillic `а` are different code points, so they are different labels, so they are different domains — which is the mechanism behind homograph attacks, and the reason a browser shows you `xn--` when a name mixes scripts.

## Which layer is your field width on?

The closing table of the Python run is the practical payoff: four letters, six representations, six sizes — 4 characters, 7 bytes, 21 characters of JSON, 19 of percent-encoding, 24 of encoded-word, 9 of punycode.

Every limit you will meet is measured on exactly one of those rows, and it is rarely the first. A DNS label is 63 characters **after** encoding. A [fixed-width interface field](../../07_Real_Data/fixed_width_byte_fields/README.md) is bytes. A URL length limit counts escaped characters, so a Polish query string hits it at a third of the words an English one does. Ask which row the limit is on before sizing the column, and say which row you meant when you write the specification.

## In Python

<!-- output:escaping_into_ascii_py -->
*Verified output of [`escaping_into_ascii_py.py`](examples/escaping_into_ascii_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. ONE WORD, FOUR CHANNELS, FOUR ANSWERS
------------------------------------------------------------------------
   the text                'żółw'   4 characters
   its UTF-8 bytes         c5 bc c3 b3 c5 82 77   7 bytes

   in a JSON string        "\u017c\u00f3\u0142w"
   in a URL                %C5%BC%C3%B3%C5%82w
   in an email header      =?utf-8?b?xbzDs8WCdw==?=
   in a domain name        xn--w-uga1v8h.pl

   Four channels that carry ASCII only, four schemes invented
   separately to get the same four letters through them. None of the
   four outputs shares a single character with any other, and that is
   not cosmetic: they are escaping different things.

2. JSON ESCAPES UTF-16 CODE UNITS -- IN A FORMAT THAT IS UTF-8
------------------------------------------------------------------------
   json.dumps('😀ż')
     default              "\ud83d\ude00\u017c"
     ensure_ascii=False   "😀ż"

   the same string as UTF-16BE   d8 3d de 00 01 7c
   escapes in the default form   3
   UTF-16 code units in it       3

   The same number, because they are the same thing. A JSON \uXXXX is
   one UTF-16 code unit, so a character above U+FFFF is written as a
   SURROGATE PAIR -- \ud83d\ude00 for one emoji. JSON itself is UTF-8
   by RFC 8259, which has no surrogates in it at all; the escape form
   is the one place UTF-16 still leaks into a modern UTF-8 stack, and
   it is there because JavaScript strings were UTF-16 in 1999.

   The leak has a sharp edge. Half a pair is valid JSON syntax:
     json.loads('"\ud83d"')  ->  '\ud83d'   1 character
     .encode('utf-8')        ->  UnicodeEncodeError: surrogates not allowed

   So a parser accepts it, a str holds it, and the very next encode
   raises -- a payload that is legal JSON and cannot be written to a
   UTF-8 file. Reject lone surrogates at the parse boundary, not later.

3. PERCENT-ENCODING ESCAPES BYTES, AND NEVER SAYS WHICH KIND
------------------------------------------------------------------------
   urllib.parse.quote('żółw')      %C5%BC%C3%B3%C5%82w
   'żółw'.encode().hex()           c5 bc c3 b3 c5 82 77

   Line up the two rows: %C5%BC%C3%B3%C5%82w is the hex dump with a %
   in front of every byte, and the ASCII 'w' left alone because it did
   not need one. A URL is bytes; the escape says nothing whatever about
   which encoding produced them. RFC 3986 recommends UTF-8 for new
   schemes and cannot enforce it, so a %F3 from a Latin-2 form is just
   as well-formed and decodes to a different letter.

   Two details that cause real bugs:
     quote('a b')            a%20b   a path: space becomes %20
     quote_plus('a b')       a+b     a form field: space becomes +
     quote('a/b')            a/b     safe='/' by default, so a path survives
     quote('a/b', safe='')   a%2Fb   for ONE path segment

   And the one that fills bug trackers -- escaping something already escaped:
     encoded once              %C5%BC%C3%B3%C5%82w
     encoded twice             %25C5%25BC%25C3%25B3%25C5%2582w
     unquote(twice)            %C5%BC%C3%B3%C5%82w
     unquote(unquote(twice))   żółw

   The %25 is a percent sign that was itself escaped. One unquote
   returns the string to its previous layer, not to text -- which is
   why the fix is counting layers, not adding another unquote.

4. A MIME ENCODED-WORD IS THE ONE THAT NAMES ITS CHARSET
------------------------------------------------------------------------
   as utf-8        =?utf-8?b?xbzDs8WCdw==?=
   as iso-8859-2   =?iso-8859-2?B?v/Ozdw==?=

   the payload is base64 of the bytes:  c5 bc c3 b3 c5 82 77   (utf-8, 7 bytes)
                                        bf f3 b3 77            (latin-2, 4 bytes)

   =?charset?encoding?payload?= -- and the charset is IN the header,
   which none of the other three schemes manage. That is why an email
   subject in a code page nobody uses any more still decodes correctly
   thirty years later, and a URL from the same era does not.

   Reading one back gives you bytes plus the name to decode them with:
     decode_header  ->  b'\xc5\xbc\xc3\xb3\xc5\x82w', 'utf-8'
     raw.decode(charset)  ->  'żółw'

   'B' is base64 and 'Q' is quoted-printable, a Latin-1-flavoured cousin
   of percent-encoding that uses = instead of %. The letter is
   case-insensitive, which is why Python writes ?b? and most mail
   clients write ?B?.

5. PUNYCODE MOVES CODE POINTS, AND TOUCHES NO BYTES AT ALL
------------------------------------------------------------------------
   'żółw.pl'.encode('idna')   xn--w-uga1v8h.pl
   'żółw'.encode('punycode')   w-uga1v8h

   Read the output: 'w-uga1v8h'. The 'w' is the one ASCII letter of
   żółw, kept in place and in order; everything after the hyphen is a
   base-36 description of which characters were removed and where they
   go back. Nothing here is a byte -- punycode is defined over code
   points, so there is no encoding to guess and no mojibake to have.
   The 'xn--' prefix is what marks a label as encoded rather than a
   domain that really is called that.

   IDNA normalises the label it has to encode, and passes an ASCII
   label through untouched -- case included, since DNS ignores case:
     'żółw.pl'    -> xn--w-uga1v8h.pl
     'ŻÓŁW.pl'    -> xn--w-uga1v8h.pl
     'Żółw.PL'    -> xn--w-uga1v8h.PL

   Normalising is not always harmless. The stdlib codec implements
   IDNA2003, whose nameprep step rewrites ß as ss before encoding:
     'straße.de'.encode('idna')      -> strasse.de
     the same name under IDNA2008    -> xn--strae-oqa.de

   Those are two different domains -- not two spellings of one. Under
   IDNA2008 ß is a letter and survives into the label; under IDNA2003
   it was a way of writing ss and does not. Python's built-in codec
   gives the 2003 answer, the `idna` package on PyPI gives the 2008
   one, and neither call site mentions a version.

   Which is the useful half and the dangerous half at once: two names
   that a person cannot tell apart can still be two different domains,
   because 'a' and the Cyrillic 'а' are different code points and
   punycode preserves the difference perfectly.

6. THE SAME FOUR LETTERS, SIX SIZES
------------------------------------------------------------------------
   the text itself        żółw                                4 characters
   UTF-8 bytes            c5 bc c3 b3 c5 82 77                7 bytes
   JSON, ensure_ascii     "\u017c\u00f3\u0142w"              21 characters
   percent-encoded        %C5%BC%C3%B3%C5%82w                19 characters
   MIME encoded-word      =?utf-8?b?xbzDs8WCdw==?=           24 characters
   punycode label         w-uga1v8h                           9 characters

   A database column, a fixed-width field or a 63-character DNS label
   is measured on ONE of those rows, and it is rarely the first. Ask
   which layer the limit applies to before you size the field.
```
<!-- /output -->

## In the terminal

<!-- output:escaping_into_ascii_sh -->
*Verified output of [`escaping_into_ascii_sh.sh`](examples/escaping_into_ascii_sh.sh) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. PERCENT-ENCODING IS THE HEX DUMP WITH A % IN FRONT
------------------------------------------------------------------------

   the text               żółw
   xxd -p                 c5bcc3b3c58277
   sed s/../%&/g          %C5%BC%C3%B3%C5%82%77

   That is the whole scheme: every byte becomes three characters,
   %XX. This pipe escapes all seven, including the ASCII w -- a real
   encoder leaves the unreserved set (letters, digits, - . _ ~) alone,
   which is why Python printed %C5%BC%C3%B3%C5%82w with a bare w on the
   end. RFC 3986 asks for upper-case hex digits, which is the tr.

2. AND BACK, WITH printf
------------------------------------------------------------------------

   %C5%BC                 -> ż
   %63%61%66%C3%A9        -> café

   The pipe turns every % into \x and lets printf write the bytes.
   Note what did NOT happen: nothing checked that those bytes are
   valid UTF-8, and nothing could have -- a URL does not say what
   encoding its bytes came from. The terminal is doing the decoding,
   and it is guessing.

3. THE SAME WORD, TWO CHARSETS, ONE URL SYNTAX
------------------------------------------------------------------------

   as utf-8       %C5%BC%C3%B3%C5%82%77
   as iso-8859-2  %BF%F3%B3%77

   Two different URLs for one word, both well-formed, and no part of
   either says which table produced it. A server that guesses wrong
   gets mojibake out of a perfectly valid query string. This is the
   one real weakness of percent-encoding and it is a design choice:
   the syntax has nowhere to put the answer.

4. AN ENCODED-WORD PUTS THE ANSWER IN THE HEADER
------------------------------------------------------------------------

   =?utf-8?B?xbzDs8WCdw==?=
   =?iso-8859-2?B?v/Ozdw==?=

   Same two byte strings as section 3, base64 instead of %XX, and
   the charset written in between the question marks. That is the
   difference that matters: a mail client reading either line knows
   what to decode it with, thirty years later, with no convention to
   agree on and nothing to guess.

   Reading one back is the same pipe in reverse:
     c5bcc3b3c58277
     ^ the payload decoded to the bytes we started from
```
<!-- /output -->

## In Rust

<!-- output:escaping_into_ascii_rs -->
*Verified output of [`escaping_into_ascii_rs.rs`](examples/escaping_into_ascii_rs.rs) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. TWO ITERATORS, TWO SCHEMES, ONE STRING
------------------------------------------------------------------------
   "żółw" -- chars 4, bytes 7, utf-16 units 4
     .bytes()          -> %C5%BC%C3%B3%C5%82w
     .encode_utf16()   -> \u017c\u00f3\u0142w
   "😀" -- chars 1, bytes 4, utf-16 units 2
     .bytes()          -> %F0%9F%98%80
     .encode_utf16()   -> \ud83d\ude00

   Same text, two escapes, and neither can be turned into the
   other without decoding first. `len()` is bytes and is what a
   URL counts; `encode_utf16().count()` is code units and is what
   a JSON escape counts; `chars().count()` is neither, and is the
   only one of the three a person would call the length.

2. ABOVE U+FFFF THE PAIR BECOMES VISIBLE
------------------------------------------------------------------------
   U+0041   1 byte(s)  1 unit(s)   json A              "A"
   U+00E9   2 byte(s)  1 unit(s)   json \u00e9         "é"
   U+017C   2 byte(s)  1 unit(s)   json \u017c         "ż"
   U+20AC   3 byte(s)  1 unit(s)   json \u20ac         "€"
   U+1F600  4 byte(s)  2 unit(s)   json \ud83d\ude00   "😀"

   One `char` is always one Unicode scalar value and always four
   bytes wide in memory, but it is one OR TWO code units on the
   wire. \ud83d\ude00 is not two characters sitting together; it
   is one character UTF-16 cannot hold in a single unit, written
   into a format whose files are UTF-8 and contain no surrogates
   anywhere.

3. STD REFUSES HALF A PAIR -- A JSON PARSER WILL HAND YOU ONE
------------------------------------------------------------------------
   String::from_utf16(&[d83d, de00])  -> Ok("😀")
   String::from_utf16(&[d83d])        -> Err("invalid utf-16: lone surrogate found")

   char::decode_utf16 names the offending unit rather than the string:
     unit 0: unpaired surrogate U+D83D

   That is the guard the escape form itself does not have.
   "\ud83d" alone is valid JSON syntax, so a parser may legally
   hand a program half a character. In Rust it cannot become a
   `String`, so the failure lands at the parse boundary instead of
   three layers later at somebody else's encode.

4. UNESCAPING A URL ENDS AT THE VALIDATOR EVERY OTHER READ ENDS AT
------------------------------------------------------------------------
   %C5%BC      -> [c5, bc] -> String::from_utf8 Ok("ż")
   %C5         -> [c5] -> String::from_utf8 Err(valid_up_to = 0)
   caf%C3%A9   -> [63, 61, 66, c3, a9] -> String::from_utf8 Ok("café")

   `percent_decode` returns `Vec<u8>` because that is honestly all
   it knows: percent-decoding produces bytes, and the URL never
   said what encoding made them. A truncated escape leaves a lead
   byte with nothing behind it -- the same truncation case as a
   short read from a file, arriving through a query string, and
   caught by the same one line of validation.
```
<!-- /output -->

## If you are coming from Python or ABAP

**Python.** Four modules, one each: `json` (`ensure_ascii=False` when you control both ends and the transport is UTF-8 — it is smaller, readable in a diff, and skips the surrogate question entirely), `urllib.parse` (`quote` for a path, `quote_plus` for a form field, and `safe=''` when the value is one path *segment* and its slashes are data), `email.header` (build with `Header(value, 'utf-8')`, read with `decode_header`, which hands back bytes plus the charset to decode them with — decode them *with that*, never with a guess), and the `idna` / `punycode` codecs, with the version caveat above. The one habit worth forming: escape at the moment of transmission, never earlier. A value that is percent-encoded three functions before it reaches the URL is a value somebody will escape again.

**ABAP** *(Not machine-checked — CI cannot run ABAP.)* `cl_http_utility=>escape_url( )` and `unescape_url( )` are the percent-encoding pair, and `escape_html( )` the entity one; both are old enough that you should check on your release what they do with a code point above `U+FFFF` before trusting them with one. For mail, let `cl_bcs` build the headers rather than assembling an encoded-word by hand — getting `=?charset?B?…?=` right by string concatenation is a job with no upside. JSON serialisation differs by release (`/ui2/cl_json` where it exists, an XSLT or a hand-rolled writer where it does not), so confirm what your system produces for a non-ASCII value: the two plausible answers, a literal UTF-8 character or a `\uXXXX` escape, are both valid JSON and only one of them will match a partner's test file. And the code page belongs to the interface agreement, not to the tool — see [SAP code pages](../../07_Real_Data/sap_code_pages/README.md).

## Try it

```bash
cd 03_Encodings/escaping_into_ascii/examples
python3 escaping_into_ascii_py.py
bash escaping_into_ascii_sh.sh
rustc --edition 2024 escaping_into_ascii_rs.rs -o /tmp/escapes && /tmp/escapes
```

Without the machine: a partner's REST call is rejected by your service with "invalid character in name", and the value in their log reads `Zamo%C5%82%C4%99`. Say how many layers that value is wrapped in, which of them your service is unwrapping, and what you would ask the partner to send instead.

## See also

- [UTF-16 and surrogates](../utf16_and_surrogates/README.md) — where `😀` comes from, and why it is one character
- [Validation is a boundary](../validation_is_a_boundary/README.md) — the check that a percent-decoded byte string still has to pass
- [Mojibake](../mojibake/README.md) — the wrong-table failure this page's wrong-layer failure is so often mistaken for
- [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) — `%C5` is a hex byte with a sign in front, and nothing more
- [Code pages](../../02_Characters/code_pages/README.md) — the `iso-8859-2` an encoded-word can name and a URL cannot
- [Interfaces and storage](../../10_Best_Practices/interfaces_and_storage/README.md) — where the encoding is declared, protocol by protocol
- [Fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md) — the other place a length is measured on the wrong row
