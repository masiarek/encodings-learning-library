#!/usr/bin/env bash
# Writing a code point at a shell prompt, and reading one back.
#
# The shell has no idea what a code point is. `printf` writes BYTES, so the
# escapes that work everywhere are the ones that name bytes: \xHH and \NNN.
# The one that names a code point, \uXXXX, is the least portable escape on
# this page -- it depends on your bash version AND your locale, so this
# script records only its SHAPE and the lesson page carries the measurement.
#
# Then the other direction: three tools, three spellings, one set of bytes.
#
# Run: bash writing_a_code_point_sh.sh

# The house od helper: BSD od pads its lines and adds a trailing blank one,
# GNU od does neither, so no single recorded key matches both raw.
tidy() { awk '{ for (i = 1; i <= NF; i++) printf "%4s", $i; print "" }' | sed -e '/^$/d'; }

bar="------------------------------------------------------------------------"

echo
echo "1. THE ESCAPES THAT NAME BYTES WORK EVERYWHERE"
echo "$bar"
printf '   %-26s' 'printf "\xe2\x82\xac"'; printf '\xe2\x82\xac' | od -An -tx1 | tidy
printf '   %-26s' 'printf "\342\202\254"'; printf '\342\202\254' | od -An -tx1 | tidy
printf '   %-26s' 'the character, pasted in'; printf '€' | od -An -tx1 | tidy
echo
echo "   Three bytes, three ways of asking for them, and none of the three"
echo "   mentions Unicode. \\xHH is hex and \\NNN is octal; both name a byte"
echo "   and stop there. It is the same E2 82 AC either way because the"
echo "   file this script is written in is UTF-8, not because printf knows"
echo "   that U+20AC is a euro sign. It does not."

echo
echo "2. THE ESCAPE THAT NAMES A CODE POINT IS THE ONE THAT TRAVELS BADLY"
echo "$bar"
n=$(printf '\u20ac' | wc -c | tr -d ' ')
echo "   printf '\\u20ac' | wc -c   ->  $n"
echo
echo "   Three, if that escape had produced a euro sign. It produced $n --"
echo "   the six characters of the escape itself, handed back unchanged."
echo "   Under LC_ALL=C there is no euro sign to produce, so printf gives up"
echo "   and prints what it was given. Which six bytes it hands back is not"
echo "   the same on every machine, so this script counts them and the page"
echo "   prints the measurement with a date. Three configurations, three"
echo "   answers, is the summary."

echo
echo "3. AND THREE TOOLS SPELL THE SAME BYTES THREE WAYS"
echo "$bar"
euro() { printf '\xe2\x82\xac'; }
printf '   %-17s' 'od -An -tx1'; euro | od -An -tx1 | tidy
printf '   %-18s' 'xxd -p'; euro | xxd -p
printf '   %-18s' 'cat -v'; euro | cat -v; echo
printf '   %-18s' 'wc -c'; euro | wc -c | tr -d ' '
echo
echo "   Same three bytes, four renderings. cat -v is the odd one: M- means"
echo "   'the high bit is set', so M-b is 0x62 with the top bit on, which is"
echo "   0xE2 -- an ASCII spelling of a non-ASCII byte, which is why it"
echo "   survives a pipe, an email and a bug report intact."
echo
echo "   Every line of this section is a SPELLING of one thing. Nothing here"
echo "   changed the file; the tools disagree about how to say it out loud."
