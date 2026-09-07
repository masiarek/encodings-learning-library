# Anki cards: hexadecimal, from the digit up to the two readings of one hex
# string.  Every `code` block is run by verify.py under LC_ALL=C / PYTHONUTF8=1
# and its stdout must match `expect` exactly; a card with `fails_msg` must NOT
# compile, with that text in stderr.
#
# NOTE ON STRING LITERALS: any front/back/code text containing a backslash is a
# RAW string.  Python eats `\x41` into `A` silently, which is a mistake this
# deck is partly about, and which ate three snippets of the sibling Rust deck
# before it was caught.

SITE = "https://masiarek.github.io/encodings-learning-library/"
BITS = SITE + "01_Bits_and_Bytes/"
COUNT = BITS + "counting_in_hex/index.html"

DECK = "Encodings::Hex"

CARDS = [

# ------------------------------------------------- the digit, and why 16 --

dict(id="hex_why_sixteen",
 front="Hexadecimal has sixteen symbols. <b>Where does the 16 come from</b> &mdash; and why not a base with ten symbols, or eight?",
 back="<b>16 = 2<sup>4</sup>, so one hex digit is exactly four bits &mdash; half a byte &mdash; and a byte is therefore "
      "<i>always</i> two digits.</b> That is the whole reason the notation exists."
      "<br><br>The tempting wrong answer is <i>&ldquo;to write big numbers with fewer digits.&rdquo;</i> Compactness cannot be "
      "the reason: <b>decimal is also far shorter than binary</b>, and decimal is useless here &mdash; 65, 200 and 255 "
      "look nothing like their bits, and a byte in decimal is one, two or three characters long, so a row of them has "
      "no rhythm. Hex is not chosen for being <i>short</i>; it is chosen for <b>dividing the byte</b>."
      "<br><br>Everything else follows: a hex dump is a grid, the seam between two bytes never falls inside a digit, "
      "and you can read the bits off the digit without arithmetic.",
 lang="py",
 code='''for n in (65, 200, 255):
    print(f"{n:3} = {n:08b} = {n:02X}")''',
 code_on="back",
 expect=""" 65 = 01000001 = 41
200 = 11001000 = C8
255 = 11111111 = FF""",
 bridge="<b>ABAP:</b> a field of <code>TYPE x</code> has no decimal view and no character view &mdash; it is written in "
        "source and shown in the debugger as hex digits, two per byte, always. The language offers exactly the base "
        "that divides a byte, and no octal literal at all. <i>(Not machine-checked; CI cannot run ABAP.)</i>",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html"),
 tags="encodings hex bits why"),

dict(id="hex_af_values",
 front="Say the sixteen hex symbols out loud, in order. What decimal value is <code>A</code>? <code>F</code>?",
 back="<b><code>0</code>&ndash;<code>9</code> then <code>A B C D E F</code> &mdash; A is <b>10</b>, F is <b>15</b>.</b>"
      "<br><br>The letters are not decoration; they are what lets a value from 10 to 15 stay <i>one character wide</i>, "
      "which is the property the whole grid depends on. Case is free: <code>0xff</code> and <code>0xFF</code> are the "
      "same byte, and only the prefix letter is always lowercase."
      "<br><br>The four to actually memorise are the ones you will read every day: <b>A = 10, C = 12, E = 14, F = 15</b>. "
      "The odd letters are then one less than the even one after them.",
 lang="py",
 code='''print(" ".join(f"{n:X}" for n in range(16)))''',
 code_on="back",
 expect="0 1 2 3 4 5 6 7 8 9 A B C D E F",
 bridge="<b>Python:</b> <code>format(n, 'X')</code> is uppercase and <code>'x'</code> lowercase, and that choice is "
        "yours everywhere &mdash; but pick one per output stream. A dump that mixes <code>c3</code> and <code>A9</code> "
        "is harder to scan than either.",
 link=("Counting in hexadecimal", COUNT),
 tags="encodings hex digits"),

dict(id="hex_counting_carry",
 front="Count. What comes after <code>F</code>? After <code>19</code>? After <code>9F</code>? After <code>FF</code>?",
 back="<b><code>F</code>&rarr;<code>10</code> &middot; <code>19</code>&rarr;<code>1A</code> &middot; "
      "<code>9F</code>&rarr;<code>A0</code> &middot; <code>FF</code>&rarr;<code>100</code></b>"
      "<br><br>It is ordinary counting with a column that holds sixteen instead of ten. You run out of symbols after "
      "<code>F</code>, so the column resets to <code>0</code> and carries one to the left."
      "<br><br>The trap is <b>reading <code>10</code> as &ldquo;ten&rdquo;</b>. It is <i>one-zero</i>, and it is 16. "
      "Say hex numbers digit by digit &mdash; <i>&ldquo;one-A&rdquo;</i>, not <i>&ldquo;nineteen&rdquo;</i> &mdash; and "
      "the mistake stops being available."
      "<br><br><code>FF</code>&rarr;<code>100</code> is the one worth keeping: it is 255 &rarr; 256, which is the first "
      "number that does not fit in a byte.",
 lang="py",
 code='''for n in (0x0E, 0x0F, 0x19, 0x1F, 0x9F, 0xFF):
    print(f"{n:>3X} + 1 = {n + 1:<3X}   ({n} + 1 = {n + 1})")''',
 code_on="back",
 expect="""  E + 1 = F     (14 + 1 = 15)
  F + 1 = 10    (15 + 1 = 16)
 19 + 1 = 1A    (25 + 1 = 26)
 1F + 1 = 20    (31 + 1 = 32)
 9F + 1 = A0    (159 + 1 = 160)
 FF + 1 = 100   (255 + 1 = 256)""",
 link=("Counting in hexadecimal", COUNT),
 tags="encodings hex counting"),

dict(id="hex_ff_and_100",
 front="<code>0xFF</code> in decimal, in bits, and in one sentence &mdash; why is it the hex number everyone remembers? "
      "And what is <code>0x100</code>?",
 back="<b><code>0xFF</code> = 255 = <code>1111 1111</code> &mdash; every switch on, the biggest value a byte holds.</b> "
      "<b><code>0x100</code> = 256 &mdash; the first number that needs a second byte.</b>"
      "<br><br>Those two are the edge of the byte, seen from each side, and they are why <code>FF</code> turns up as "
      "&ldquo;all ones&rdquo; everywhere: <code>0xFF</code> as a mask keeps the low byte, <code>0xFFFF</code> is 65535, "
      "and a screenful of <code>FF</code> in a dump is usually erased flash or padding rather than data."
      "<br><br>Worth having alongside it: <b><code>0x7F</code> = 127</b>, the last ASCII code point, so a byte with the "
      "top bit clear is exactly a byte <code>&le; 0x7F</code>.",
 lang="py",
 code='''print(0xFF, f"{0xFF:08b}", 0xFF == 255)
print(0x100, f"{0x100:09b}", 0x100 == 256)
print(0x7F, "last ASCII", 0xFF & 0x1234, "= 0x1234 masked to its low byte")''',
 code_on="back",
 expect="""255 11111111 True
256 100000000 True
127 last ASCII 52 = 0x1234 masked to its low byte""",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html"),
 tags="encodings hex bytes"),

# ---------------------------------------- the prefix: 0x means "not decimal" --

dict(id="hex_four_bases",
 front="Write <b>195</b> in all four bases a modern language accepts. What is the rule behind the three prefixes?",
 back="<b><code>0b1100_0011</code> &middot; <code>0o303</code> &middot; <code>195</code> &middot; <code>0xC3</code></b>"
      "<br><br>The rule: <b>the leading <code>0</code> means &lsquo;not decimal&rsquo;, and the letter after it is the "
      "first letter of the base&rsquo;s English name</b> &mdash; he<b>x</b>adecimal, <b>o</b>ctal, <b>b</b>inary. "
      "Decimal is the only base with no prefix, because it is the default."
      "<br><br>Python, Rust and (since C23) C all spell it this way, so this half transfers with no edits. The prefix "
      "is not decoration: it is the only thing on the line that says which base the digits are in.",
 lang="py",
 code='''print(0b1100_0011, 0o303, 195, 0xC3)''',
 code_on="back",
 expect="195 195 195 195",
 bridge="<b>Python:</b> the underscore is a separator the parser throws away (since 3.6), so a literal can draw its own "
        "grouping &mdash; <code>0b1100_0011</code> by nibble, <code>0xC3_A9</code> by <b>byte</b>, which is the grouping "
        "that matters for bytes. <b>Rust</b> is looser still: underscores anywhere, any number of times.",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html#writing-the-literal"),
 tags="encodings hex literals prefix"),

dict(id="hex_prefix_is_for_humans",
 front=r"Does <code>&quot;0x41&quot;</code> parse as hex? Answer for <b>Python</b> <code>int(s,16)</code>, "
       r"<b>Rust</b> <code>from_str_radix</code>, <b>C</b> <code>strtol</code>, <b>bash</b> <code>$((16#s))</code>.",
 back="<b>Python yes &middot; Rust <b>no</b> &middot; C yes &middot; bash yes.</b> Three of the four accept the prefix "
      "and one refuses it, which is the point: <b>the prefix is for humans, and each parser decides separately whether "
      "to humour you.</b>"
      "<br><br>Rust&rsquo;s <code>from_str_radix</code> wants digits only &mdash; you already said the base in the "
      "argument, so the prefix is redundant input, and Rust treats redundant input as an error. C&rsquo;s "
      "<code>strtol</code> goes the other way and treats <code>0x</code> as part of base 16 by definition."
      "<br><br>So <i>&ldquo;the field is hex&rdquo;</i> does not say whether a leading <code>0x</code> is allowed in it. "
      "Somebody has to decide, in the open, next to the code that reads the field.",
 lang="rs",
 code=r'''fn main() {
    println!("{:?}", u8::from_str_radix("41", 16));
    println!("{:?}", u8::from_str_radix("0x41", 16));
}''',
 code_on="back",
 expect="""Ok(65)
Err(ParseIntError { kind: InvalidDigit })""",
 bridge="<b>Python:</b> <code>int(s, 0)</code> is the third behaviour again &mdash; base 0 means <i>read the prefix and "
        "obey it</i>, so <code>int('0x41', 0)</code> is 65 and <code>int('41', 0)</code> is forty-one, decimal.",
 link=("Hex: a number, or a picture of bytes", BITS + "hex_number_or_bytes/index.html"),
 tags="encodings hex parsing prefix gotcha"),

dict(id="hex_leading_zero_c",
 front="What does this C program print? (The habit from every other language is the trap.)",
 lang="c",
 code='''#include <stdio.h>
int main(void) { printf("%d %d %d\\n", 0755, 755, 0x1ED); return 0; }''',
 code_on="front",
 expect="493 755 493",
 back="<b>In C a bare leading zero <i>is</i> the octal prefix.</b> <code>0755</code> is 493; <code>755</code> is 755. "
      "One character apart, 262 apart in value &mdash; which is why <code>chmod(path, 0755)</code> is correct and "
      "<code>chmod(path, 755)</code> compiles and is not."
      "<br><br>It is the only prefix you cannot see: <code>0x</code> / <code>0o</code> / <code>0b</code> are two "
      "characters, one of them a letter, while C&rsquo;s octal prefix is <i>a single character that is also a digit</i>, "
      "in a language where zero-padding a number is ordinary."
      "<br><br><b>Python 3 removed the rule</b> &mdash; <code>0755</code> in source is a SyntaxError, not a different "
      "number, which is the right way to retire a trap: fail, do not reinterpret. <b>Rust never adopted it</b>: "
      "<code>0755</code> is 755 and the zero is inert padding.",
 bridge=r"<b>Python:</b> the live version is text you did not write. <code>int('0755')</code> is <b>755</b>, "
        r"<code>int('0755', 8)</code> is <b>493</b>, <code>int('0755', 0)</code> raises. Three answers from seven "
        r"characters, and the string does not say which was meant.",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html#writing-the-literal"),
 tags="encodings hex octal literals gotcha"),

# --------------------------------------------------- the escape: \x is a byte --

dict(id="hex_0x_versus_backslash_x",
 front=r"<code>0x41</code> and <code>\x41</code> both name 65 in hex. <b>What is the difference?</b>",
 back=r"<b><code>0x41</code> is a <i>number</i> written in source. <code>\x41</code> is a <i>byte inside a string</i>.</b>"
      r"<br><br>They live in different places and you cannot swap them: <code>0x41 + 1</code> is arithmetic; "
      r"<code>&quot;\x41&quot;</code> is text you can print, index and encode. One is a value, the other is a way of "
      r"typing a character or a byte you cannot easily type."
      r"<br><br>The same byte has more spellings still, and each tool picks one:"
      r"<br>&bull; <code>0x41</code> &mdash; the number 65, in hex (Python, Rust, C, bash arithmetic)"
      r"<br>&bull; <code>\x41</code> &mdash; the byte 65 in a literal (Python, Rust, <code>printf</code>)"
      r"<br>&bull; <code>41</code> &mdash; one byte in a hex dump, or an ABAP <code>x</code> field"
      r"<br>&bull; <code>%41</code> &mdash; the byte 65 in a URL"
      r"<br>&bull; <b><code>U+0041</code> &mdash; the <i>code point</i> 65, which is not a byte at all</b>"
      r"<br><br>The last one is the odd one out and the one worth flagging: a code point is a number in the Unicode "
      r"table, and how it becomes bytes is a separate question with more than one answer.",
 lang="py",
 code=r'''n = 0x41
s = "\x41"
print(n, n + 1, type(n).__name__)
print(s, s * 3, type(s).__name__)''',
 code_on="back",
 expect="""65 66 int
A AAA str""",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html#the-spellings"),
 tags="encodings hex escapes spelling"),

dict(id="hex_backslash_x_str_vs_bytes",
 front=r"Python. <code>&quot;\xc3&quot;</code> and <code>b&quot;\xc3&quot;</code> are both one item long. "
       r"<b>Encode the first one &mdash; how many bytes come out, and why?</b>",
 lang="py",
 code=r'''s = "\xc3"
b = b"\xc3"
print(len(s), len(b))
print(s.encode("utf-8"))
print(b)''',
 code_on="front",
 expect="""1 1
b'\\xc3\\x83'
b'\\xc3'""",
 back=r"<b>Two bytes, because <code>&quot;\xc3&quot;</code> was never a byte.</b> Inside a <code>str</code>, "
      r"<code>\xNN</code> names the <i>code point</i> U+00C3 &mdash; &Atilde; &mdash; and UTF-8 spells that code point "
      r"with two bytes, <code>c3 83</code>. Inside a <code>bytes</code> literal the same escape names the byte itself."
      r"<br><br>So the escape does not have one meaning; it has the meaning of the container it is in. This is the "
      r"text-versus-bytes line drawn through a single piece of syntax, and it is the reason a &lsquo;fix&rsquo; like "
      r"<code>s.encode('latin-1')</code> sometimes appears to work &mdash; latin-1 maps the first 256 code points "
      r"straight onto the first 256 byte values, so it undoes exactly this confusion and nothing else."
      r"<br><br>Rust removes the ambiguity by refusing it: <code>&quot;\xc3&quot;</code> does not compile at all.",
 bridge=r"<b>Rust:</b> in a <code>str</code> literal <code>\xNN</code> accepts only <code>00</code>&ndash;<code>7F</code> "
        r"&mdash; ASCII, where byte and code point still agree. Above that you must say which you meant: "
        r"<code>b&quot;\xc3&quot;</code> for the byte, <code>&quot;\u{c3}&quot;</code> for the character.",
 link=("Writing a code point", SITE + "02_Characters/writing_a_code_point/index.html"),
 tags="encodings hex escapes python bytes gotcha"),

dict(id="hex_rust_str_escape_range",
 front=r"Does this compile?",
 lang="rs",
 code=r'''fn main() {
    let s = "\xC3";
    println!("{}", s);
}''',
 code_on="front",
 fails_msg="out of range hex escape",
 back=r"<b>No.</b> <code>error: out of range hex escape &mdash; must be a character in the range [\x00-\x7f]</code>."
      r"<br><br>Rust will not let <code>\xNN</code> above <code>7F</code> into a <code>str</code>, because above 7F the "
      r"question <i>&ldquo;is this a byte or a character?&rdquo;</i> has two different answers and the literal does not "
      r"say. So it makes you say:"
      r"<br>&bull; <code>b&quot;\xC3&quot;</code> &mdash; the <b>byte</b> 0xC3, in a <code>&amp;[u8]</code>"
      r"<br>&bull; <code>&quot;\u{C3}&quot;</code> &mdash; the <b>character</b> &Atilde;, which UTF-8 stores as two bytes"
      r"<br><br>rustc prints both of those as help lines, so the error is also the answer key. Python allows the same "
      r"literal and quietly gives you the second reading &mdash; which is the previous card.",
 link=("Writing a code point", SITE + "02_Characters/writing_a_code_point/index.html"),
 tags="encodings hex escapes rust compile-error"),

dict(id="hex_c_greedy_escape",
 front=r"C. You want a BEL byte followed by the letter <code>f</code>, so you write <code>&quot;\x7f&quot;</code>. "
       r"<b>What did you actually get?</b>",
 lang="c",
 code=r'''#include <stdio.h>
#include <string.h>
int main(void) {
    const char *want = "\x7" "f";   /* BEL, then the letter f */
    const char *oops = "\x7f";      /* one byte: DEL */
    printf("%zu %zu %02X %02X\n", strlen(want), strlen(oops),
           (unsigned char)want[0], (unsigned char)oops[0]);
    return 0;
}''',
 code_on="front",
 expect="2 1 07 7F",
 back=r"<b>One byte, <code>0x7F</code> &mdash; DEL &mdash; because C&rsquo;s <code>\x</code> is <i>greedy</i>.</b> It "
      r"consumes as many hex digits as follow it, with no limit, so the <code>f</code> you meant as a letter was eaten "
      r"as a digit."
      r"<br><br>Python and Rust both take <b>exactly two</b> digits, so you can see where the escape ends by counting. "
      r"C is the only one of the three where <b>you cannot tell where an escape stops without looking at the next "
      r"character</b> &mdash; and where <code>&quot;\x41&quot; &quot;2&quot;</code>, two adjacent literals, is the "
      r"portable way to say what you meant."
      r"<br><br>Greed also overflows silently in principle: <code>&quot;\x411&quot;</code> is a hex escape out of range, "
      r"which is a diagnostic in clang and gcc but a value you should never rely on.",
 bridge=r"<b>Python:</b> the opposite failure &mdash; too <i>few</i> digits is refused. <code>&quot;\x7&quot;</code> is "
        r"a SyntaxError (<i>truncated \xXX escape</i>), not a BEL. The fixed width is what makes it checkable.",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html#the-spellings"),
 tags="encodings hex escapes c gotcha"),

# ------------------------------------------- the picture versus the thing --

dict(id="hex_text_is_not_the_byte",
 front=r"A hex dump shows you <code>41</code>. <b>Is the file made of the characters <code>4</code> and "
       r"<code>1</code>?</b> Write the two calls that convert each way.",
 back=r"<b>No. The file holds <i>one</i> byte; <code>41</code> is a picture of it.</b>"
      r"<br><br>The text <code>'41'</code> is two characters, and as bytes those are <code>0x34</code> and "
      r"<code>0x31</code> &mdash; the ASCII digits four and one. The byte the dump is describing is <code>0x41</code>, "
      r"which is <code>A</code>."
      r"<br><br><b>The two calls:</b> <code>bytes.fromhex('41')</code> turns the picture into the thing, and "
      r"<code>b'A'.hex()</code> turns the thing into the picture. Everything in a hex dump is a picture."
      r"<br><br>This is the single most useful sentence in the chapter, because the confusion is invisible: both "
      r"readings look like &lsquo;hex&rsquo; and only one of them is the file.",
 lang="py",
 code=r'''print("41".encode())
print(bytes.fromhex("41"))
print(b"A".hex())''',
 code_on="back",
 expect="""b'41'
b'A'
41""",
 bridge=r"<b>Python:</b> <code>bytes.hex(' ')</code> takes a separator since 3.8, which is a one-call hex dump: "
        r"<code>'caf\xc3\xa9'.encode().hex(' ')</code> &rarr; <code>63 61 66 c3 a9</code>.",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html#in-python"),
 tags="encodings hex dump picture-vs-thing"),

dict(id="hex_text_is_not_the_byte_sh",
 front=r"Same question in the shell. <b>What do these four print?</b>",
 lang="sh",
 code=r'''printf '41'          | xxd -p    # the TEXT "41": two characters
printf '\x41'        | xxd -p    # the BYTE 0x41: one byte
printf '\303\251'    | xxd -p    # octal escape -- POSIX printf
printf '\xc3\xa9'    | xxd -p    # hex escape -- a bash extension''',
 code_on="front",
 expect="""3431
41
c3a9
c3a9""",
 back=r"<b>The text <code>41</code> dumps as <code>3431</code>; the byte <code>\x41</code> dumps as <code>41</code>.</b> "
      r"Two characters versus one byte, from the shell."
      r"<br><br>The last two lines are the same two bytes &mdash; the e-acute of <code>caf&eacute;</code> in UTF-8 "
      r"&mdash; written two ways, and the difference is portability: <b><code>\NNN</code> (octal) is in POSIX "
      r"<code>printf</code>; <code>\xHH</code> (hex) is a bash extension.</b> A script that must run under "
      r"<code>/bin/sh</code> writes its bytes in octal."
      r"<br><br>That is the one place octal is still load-bearing rather than legacy, and it is worth knowing before "
      r"you reach for a hex escape in a shebang you did not choose.",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html#in-the-terminal"),
 tags="encodings hex shell printf octal"),

dict(id="hex_padding_02x",
 front=r"You are printing bytes. <b><code>{:x}</code> or <code>{:02x}</code>?</b> Show what goes wrong with the other one.",
 back=r"<b><code>{:02x}</code>, always, when the value is a byte.</b> A byte is <i>always</i> two hex digits &mdash; "
      r"that is the whole property hex is chosen for &mdash; and <code>{:x}</code> prints one digit for anything under "
      r"16, which silently breaks the grid."
      r"<br><br>So <code>format(5, 'x')</code> is <code>'5'</code>, which is not a byte; <code>format(5, '02x')</code> "
      r"is <code>'05'</code>, which is. In a run of bytes the difference is not cosmetic: the columns stop lining up, "
      r"and worse, the output is no longer reversible &mdash; you cannot tell <code>5 05</code> from <code>50 5</code>."
      r"<br><br>The <code>#</code> flag adds the prefix and the width <i>counts</i> it: <code>f'{65:#04x}'</code> is "
      r"<code>0x41</code>, four characters including the <code>0x</code>. Getting that wrong gives you <code>0x1</code> "
      r"where you wanted <code>0x01</code>.",
 lang="py",
 code=r'''print(format(5, "x"), format(5, "02x"), format(65, "02X"), f"{65:#04x}")''',
 code_on="back",
 expect="5 05 41 0x41",
 bridge=r"<b>Rust:</b> the same four, spelled <code>{:x}</code>, <code>{:02x}</code>, <code>{:02X}</code>, "
        r"<code>{:#04x}</code> &mdash; and <code>{:08b}</code> for the eight bits behind them.",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html#in-rust"),
 tags="encodings hex formatting"),

# -------------------------------------- a number, or a picture of bytes (201) --

dict(id="hex_two_readings",
 front=r"<code>0041</code>. <b>What is it?</b> Give both answers, and say what decides between them.",
 back=r"<b>Either 65, or the two bytes <code>00 41</code> &mdash; and nothing in the string chooses.</b>"
      r"<br><br>As a <b>number</b>: leading zeros are noise, <code>0041</code> equals <code>41</code>, there is no width, "
      r"and byte order is a meaningless question."
      r"<br><br>As a <b>byte string</b>: the leading zero is <i>data</i> &mdash; the first byte is NUL &mdash; the width "
      r"<i>is</i> the field, and byte order is a real question the digits do not answer."
      r"<br><br>Both readings are correct. The choice lives in the field the string came out of, which is why "
      r"<i>&ldquo;the field is hex&rdquo;</i> is not a specification and <i>&ldquo;the field is four hex digits, two "
      r"bytes, big-endian&rdquo;</i> is."
      r"<br><br>The reflex to distrust is <code>int(s, 16)</code> on an identifier: the value is never wrong and the "
      r"<b>length is destroyed</b>, and nothing raises until several layers downstream.",
 lang="py",
 code=r'''s = "0041"
print("as a number:", int(s, 16))
print("as bytes:   ", bytes.fromhex(s), len(bytes.fromhex(s)))
print("41 == 0041 as numbers:", int("41", 16) == int("0041", 16))
print("41 == 0041 as bytes:  ", bytes.fromhex("41") == bytes.fromhex("0041"))''',
 code_on="back",
 expect="""as a number: 65
as bytes:    b'\\x00A' 2
41 == 0041 as numbers: True
41 == 0041 as bytes:   False""",
 bridge=r"<b>Python:</b> <code>int.to_bytes</code> has no default byte order and Rust has two separate methods "
        r"(<code>to_be_bytes</code> / <code>to_le_bytes</code>) rather than one with a flag &mdash; both are the same "
        r"refusal to guess, at the moment you cross from one reading to the other.",
 link=("Hex: a number, or a picture of bytes", BITS + "hex_number_or_bytes/index.html"),
 tags="encodings hex bytes 201"),

dict(id="hex_odd_length",
 front=r"A field arrives holding <code>123</code> &mdash; three hex digits. <b>What do "
       r"<code>int(s,16)</code>, <code>bytes.fromhex(s)</code> and <code>xxd -r -p</code> each do?</b>",
 back=r"<b>291 &middot; ValueError &middot; one byte <code>0x12</code>, silently, exit 0.</b>"
      r"<br><br>Only the middle one tells you anything. An odd-length hex field is nearly always a <i>truncated</i> one "
      r"&mdash; a log line cut at a column limit, a copy-paste that lost a character &mdash; so the error is the answer "
      r"you want and the silent halving is the one that ships."
      r"<br><br><code>xxd -r -p</code> behaves the same way on a non-hex character: it stops, keeps what it had, exits 0. "
      r"<b>It is an excellent encoder of hex you produced and a poor validator of hex somebody sent you.</b>"
      r"<br><br>Do not quote the ValueError&rsquo;s wording: CPython reworded it in 3.14, so the sentence you get is a "
      r"fact about which interpreter ran, not about your data. Catch the class.",
 lang="py",
 code=r'''print(int("123", 16))
try:
    bytes.fromhex("123")
except ValueError as e:
    print(type(e).__name__, "- not a whole number of bytes")''',
 code_on="back",
 expect="""291
ValueError - not a whole number of bytes""",
 link=("Hex: a number, or a picture of bytes", BITS + "hex_number_or_bytes/index.html"),
 tags="encodings hex validation 201 gotcha"),

dict(id="hex_int_is_not_validation",
 front=r"<code>int(s, 16)</code> returned 65, so the field is two ASCII hex digits. <b>True?</b>",
 lang="py",
 code=r'''print(int("٤١", 16))''',
 code_on="front",
 expect="65",
 back=r"<b>False.</b> Those are <code>&#x664;&#x661;</code> &mdash; two ARABIC-INDIC digits, U+0664 and U+0661. They are "
      r"not ASCII and not in <code>0123456789abcdefABCDEF</code>, and Python returns 65 anyway."
      r"<br><br><code>int()</code> accepts any character carrying a Unicode decimal digit value, in every base. So a "
      r"field &lsquo;validated&rsquo; by <code>int(s, 16)</code> succeeding will accept digits your regex, your database "
      r"and your partner&rsquo;s parser all reject &mdash; a <b>parser differential</b> hiding inside a one-line type check."
      r"<br><br>The habit: <b><code>int(s, 16)</code> succeeding is not a validation.</b> If the field has a fixed width, "
      r"check the length and the character set yourself, <i>then</i> decode &mdash; in that order, because after decoding "
      r"the evidence is gone.",
 bridge=r"<b>Rust:</b> <code>from_str_radix</code> rejects them, along with a leading space, a sign, an underscore and a "
        r"trailing anything. That strictness is the reason it feels annoying and the reason it is safe.",
 link=("Hex: a number, or a picture of bytes", BITS + "hex_number_or_bytes/index.html"),
 tags="encodings hex validation unicode 201 gotcha"),

dict(id="hex_c_strtol_partial",
 front=r"C. <code>strtol(&quot;4G&quot;, &amp;end, 16)</code> &mdash; what comes back, and how do you find out it went wrong?",
 lang="c",
 code=r'''#include <stdio.h>
#include <stdlib.h>
int main(void) {
    char s[] = "4G";
    char *end;
    long v = strtol(s, &end, 16);
    printf("%ld rest=%s converted_nothing=%d\n", v, end, end == s);
    return 0;
}''',
 code_on="front",
 expect="4 rest=G converted_nothing=0",
 back=r"<b>It returns 4, and says nothing.</b> <code>strtol</code> is not a validator; it is a longest-prefix parser. "
      r"<code>4G</code> gives 4, <code>41xyz</code> gives 65, and the only record of the rest is <code>endptr</code>."
      r"<br><br>Worse: <code>zz</code> and the empty string both return <b>0</b> &mdash; which is also what a correct "
      r"parse of <code>&quot;0&quot;</code> returns, so <b>the return value alone cannot distinguish success from total "
      r"failure</b>."
      r"<br><br><code>end == input</code> is the portable test for <i>nothing was converted</i>. Do not reach for "
      r"<code>errno</code>: after a failed conversion it is implementation-defined, and macOS and glibc genuinely differ.",
 link=("Hex: a number, or a picture of bytes", BITS + "hex_number_or_bytes/index.html"),
 tags="encodings hex parsing c 201 gotcha"),

# ------------------------------------------------ the road not taken: octal --

dict(id="hex_why_not_octal",
 front=r"Octal is the same trick at three bits per digit, and it was the standard first. <b>Why did hex win?</b> "
       r"(The answer is not about hexadecimal.)",
 back=r"<b>Three does not divide eight.</b> A byte is 8 bits, so it is exactly two hex digits and never a whole number "
      r"of octal digits &mdash; and once digits stop lining up with bytes, a dump stops being a grid."
      r"<br><br>Seen close up: the top octal digit of a byte is not a whole digit. <code>0o377</code> is 255, the biggest "
      r"byte, and that leading digit runs <code>0</code>&ndash;<code>3</code> and no further, because three octal digits "
      r"would be 9 bits. Both hex digits are full digits."
      r"<br><br>And across two bytes it is fatal: <code>&eacute;</code> in UTF-8 is <code>c3 a9</code>, and in octal it is "
      r"<code>0o141651</code> where one digit is <b>three bits taken from both bytes at once</b>. There is nowhere to put "
      r"the gap. That is why no octal tool has ever had the shape of a hex dump."
      r"<br><br>The history follows rather than explains: octal-era machines had <b>six-bit</b> characters, and 6 &divide; 3 "
      r"= 2 exactly &mdash; the same tidy property hex has now. Octal did not lose an argument; its word size stopped "
      r"being manufactured.",
 lang="py",
 code=r'''print("one hex digit = 4 bits, one octal digit = 3 bits")
print("a byte is 8 bits:", 8 / 4, "hex digits exactly;", round(8 / 3, 2), "octal digits")
print("biggest byte:", 0xFF, "=", oct(0xFF), "=", bin(0xFF))''',
 code_on="back",
 expect="""one hex digit = 4 bits, one octal digit = 3 bits
a byte is 8 bits: 2.0 hex digits exactly; 2.67 octal digits
biggest byte: 255 = 0o377 = 0b11111111""",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html#why-hex-and-not-octal"),
 tags="encodings hex octal why"),

dict(id="hex_octal_still_fits",
 front=r"Where is <b>octal</b> still the right base and hex the awkward one? Give the case and the arithmetic.",
 back=r"<b>Unix permissions.</b> Three <code>rwx</code> triples is 9 bits, and 9 &divide; 3 = 3 exactly, so "
      r"<code>0o755</code> is one digit per triple and says <i>rwx r-x r-x</i> out loud. The same nine bits in hex are "
      r"<code>0x1ED</code>, where no digit lines up and which says nothing at all."
      r"<br><br>So the base is not a matter of taste or era: <b>it is whichever one divides the field you are reading.</b> "
      r"Four bits per digit fits a byte; three fits a permission triple; and that is the entire rule, applied twice."
      r"<br><br>Which is also the honest form of the previous card &mdash; octal is not obsolete, it is <i>specialised</i>. "
      r"Reach for it on the <code>mode</code> argument of <code>os.chmod</code> and, per the shell card, on "
      r"<code>printf '\NNN'</code> when the script must run under <code>/bin/sh</code>.",
 lang="py",
 code=r'''print("chmod 755:", 0o755, "=", oct(0o755), "=", hex(0o755))
print("nine bits: ", f"{0o755:09b}", "->", "111 101 101")''',
 code_on="back",
 expect="""chmod 755: 493 = 0o755 = 0x1ed
nine bits:  111101101 -> 111 101 101""",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html#why-hex-and-not-octal"),
 tags="encodings hex octal"),

# ------------------------------------------------------------ the toolchain --

dict(id="hex_rust_byte_string",
 front=r"Rust. <code>let n = 0x1A;</code> and <code>let b = b&quot;\x1A&quot;;</code> &mdash; "
       r"<b>what is each one, and what does each print?</b>",
 lang="rs",
 code=r'''fn main() {
    let hex_number = 0x1A;
    let byte_literal = b"\x1A";
    println!("{} {:?} {}", hex_number, byte_literal, byte_literal.len());
}''',
 code_on="front",
 expect="26 [26] 1",
 back=r"<b><code>0x1A</code> is the integer 26. <code>b&quot;\x1A&quot;</code> is a <i>byte string</i> &mdash; "
      r"<code>&amp;[u8; 1]</code> &mdash; holding one byte whose value is 26.</b>"
      r"<br><br>The <code>{:?}</code> gives it away: a byte string prints as <code>[26]</code>, a list, because that is "
      r"what it is. The number has no length; the byte string has length 1, and that length is the difference the whole "
      r"chapter turns on."
      r"<br><br>Rust also has <code>b'A'</code>, a byte <i>literal</i>, which really is the number 65 &mdash; a "
      r"<code>u8</code>, not a container. Three spellings, three types: <code>0x41</code> (integer), <code>b'A'</code> "
      r"(<code>u8</code>), <code>b&quot;A&quot;</code> (<code>&amp;[u8; 1]</code>).",
 bridge=r"<b>Python:</b> <code>b'A'</code> is the <i>plural</i> &mdash; a one-element <code>bytes</code> container, "
        r"matching Rust&rsquo;s <code>b&quot;A&quot;</code>. Same spelling, different thing: Rust&rsquo;s "
        r"<code>b'A'</code> <i>is</i> the number 65. The familiar syntax maps to the other form.",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html#in-rust"),
 tags="encodings hex rust literals"),

dict(id="hex_shell_bases",
 front=r"In the shell, with no language: <b>convert 65 to hex, 5 to two-digit uppercase hex, and "
       r"<code>0x41</code> back to decimal.</b> Then read <code>41</code> as base 16 without a prefix.",
 back=r"<b><code>printf '%x' 65</code> &middot; <code>printf '%02X' 5</code> &middot; <code>printf '%d' 0x41</code> "
      r"&middot; <code>$(( 16#41 ))</code></b>"
      r"<br><br>Two different mechanisms, worth keeping apart. <b><code>printf</code> converts a number for display</b> "
      r"and accepts <code>0x</code> on the way in. <b><code>$(( base#digits ))</code> is bash arithmetic</b> and takes any "
      r"base from 2 to 64 &mdash; <code>2#01000001</code>, <code>8#101</code>, <code>16#41</code> are all 65 &mdash; but "
      r"it wants the base <i>before</i> the <code>#</code>, not a prefix."
      r"<br><br>And neither one shows you bytes. For that it is <code>xxd</code>, which is the next tool along and a "
      r"different question entirely.",
 lang="sh",
 code=r'''echo $(( 16#41 )) $(( 2#01000001 )) $(( 8#101 ))
printf '%x %02X %d\n' 65 5 0x41''',
 code_on="back",
 expect="""65 65 65
41 05 65""",
 link=("Hex is a shorthand", BITS + "hex_is_a_shorthand/index.html#in-the-terminal"),
 tags="encodings hex shell"),
]
