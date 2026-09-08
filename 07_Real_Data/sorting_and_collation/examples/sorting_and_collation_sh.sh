#!/usr/bin/env bash
# `sort` is a collation engine, and the tie-break it does for you has a flag.
#
# The Python examples beside this one show which order a locale gives and what
# a comparison is made of. This one is about the tool, and about the two things
# the tool does that nobody reads the man page for: it silently accepts a
# collation that does not exist, and it silently repairs the ties its own
# comparison creates -- until you pass --stable, which is the flag that sounds
# like it makes things more reproducible and does the opposite.
#
# Every command names its own locale in view, and every one of them names C:
# C is the only collation identical on both machines this library is checked
# on, so it is the only one whose ORDER may be recorded. What is recorded here
# is machinery, not an alphabet.
#
# Run:  bash sorting_and_collation_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

echo "1. A COLLATION THAT IS NOT INSTALLED IS NOT AN ERROR"
echo "------------------------------------------------------------------------"
# Zebra / Lodz with a stroked L / Ant / Zeromski, as octal escapes -- a
# multibyte literal in a script is a bet on the editor that saved it.
printf 'Zebra\n\305\201odz\nAnt\n\305\273eromski\n' > ./_names.txt
show "LC_ALL=zz_ZZ.UTF-8 sort ./_names.txt 2>/dev/null; echo \"exit=\$?\""
LC_ALL=zz_ZZ.UTF-8 sort ./_names.txt 2>./_err.txt >./_a.txt || true
LC_ALL=C sort ./_names.txt > ./_b.txt
printf '\n  bytes written to stderr: %s\n' "$(wc -c < ./_err.txt | tr -d ' ')"
printf '  same output as LC_ALL=C: %s\n' \
  "$(cmp -s ./_a.txt ./_b.txt && echo yes || echo no)"
echo "   Byte order, exit 0, and an empty stderr. This is the mirror of what"
echo "   Python does with the same request: section 2 of the other example"
echo "   shows locale.setlocale RAISING for a locale nobody has, and here the"
echo "   shell tool takes it, says nothing, and sorts by bytes. One of those"
echo "   two failures you can catch; the other reaches production as a list"
echo "   that is merely wrong. A container is where you meet it, because a"
echo "   stock image ships no human-language locales at all."

echo
echo "2. sort ALREADY CARRIES A COLLATION, AND -f IS A TOY ONE"
echo "------------------------------------------------------------------------"
printf 'bravo\nBravo\nalpha\n' > ./_case.txt
printf 'Bravo\nbravo\nalpha\n' > ./_case2.txt
echo "   -f folds case, so 'bravo' and 'Bravo' become EQUAL to the comparison"
echo "   without becoming equal as strings. Every real collation does that at"
echo "   some level -- it is what ignoring case, or an accent, or a joiner"
echo "   means. Here it gives us a tie we can hold still and look at."
show "LC_ALL=C sort -f ./_case.txt | tr '\n' ' '; echo"

echo
echo "3. THE TIE-BREAK sort DOES FOR YOU, AND THE FLAG THAT REMOVES IT"
echo "------------------------------------------------------------------------"
echo "   The same three lines, in two input orders:"
echo "     A:  bravo Bravo alpha"
echo "     B:  Bravo bravo alpha"
printf '\n     default   A -> %s\n' "$(LC_ALL=C sort -f ./_case.txt  | tr '\n' ' ')"
printf     '     default   B -> %s\n' "$(LC_ALL=C sort -f ./_case2.txt | tr '\n' ' ')"
printf     '     with -s   A -> %s\n' "$(LC_ALL=C sort -f -s ./_case.txt  | tr '\n' ' ')"
printf     '     with -s   B -> %s\n' "$(LC_ALL=C sort -f -s ./_case2.txt | tr '\n' ' ')"
echo
echo "   The default gives ONE answer for both inputs. -s gives two, which is"
echo "   backwards from how the flag reads: -s is --stable, and stability is"
echo "   the promise that equal lines keep the order they ARRIVED in -- so it"
echo "   is the route by which the input order reaches the output."
echo "   Without it, sort applies a LAST-RESORT COMPARISON: when the keys tie"
echo "   it compares the whole lines bytewise. That is UTS #10 A.3.2's recipe"
echo "   for a deterministic comparison, already wired into the tool, and -s"
echo "   is the switch that takes it out."

echo
echo "4. AND -u THROWS AWAY A LINE THAT IS NOT A DUPLICATE"
echo "------------------------------------------------------------------------"
printf '\n     -f -u     A -> %s\n' "$(LC_ALL=C sort -f -u ./_case.txt  | tr '\n' ' ')"
printf     '     -f -u     B -> %s\n' "$(LC_ALL=C sort -f -u ./_case2.txt | tr '\n' ' ')"
echo
echo "   Three lines in, two out, both times -- and a different survivor each"
echo "   time. -u means 'unique according to the comparison', not 'byte"
echo "   identical', so a comparison that ignores case makes bravo and Bravo"
echo "   one line and the input order picks which one lives. Under a real"
echo "   collation the same flag merges rows differing by an accent, a soft"
echo "   hyphen or a zero-width joiner nobody can see. SELECT DISTINCT is the"
echo "   same statement in the other language."

echo
echo "5. THE SAME THING ON A KEY FIELD, WHICH IS WHERE IT ACTUALLY HAPPENS"
echo "------------------------------------------------------------------------"
printf '2 b\n1 b\n3 a\n' > ./_recs.txt
printf '\n     sort -k2,2       %s\n' "$(LC_ALL=C sort -k2,2    ./_recs.txt | tr '\n' '/')"
printf     '     sort -k2,2 -s    %s\n' "$(LC_ALL=C sort -k2,2 -s ./_recs.txt | tr '\n' '/')"
echo
echo "   Sorting records on one column is the everyday case, and no locale is"
echo "   involved: the two rows whose column 2 is 'b' simply have no order of"
echo "   their own. The default breaks the tie on the whole line and gets 1"
echo "   before 2; -s keeps the file order and gets 2 before 1. Neither is"
echo "   wrong, and only one of them is the same tomorrow if the file is"
echo "   regenerated in a different order. Name a second key -- sort -k2,2"
echo "   -k1,1 -- and the question does not arise, which is the shell's"
echo "   spelling of ORDER BY name, id."

rm -f ./_names.txt ./_case.txt ./_case2.txt ./_recs.txt ./_err.txt ./_a.txt ./_b.txt
