#!/usr/bin/env bash
# The locale is not one setting. It is six variables, they are independent, and
# they decide what "a character" means to every tool that asks.
#
# This is a lesson ABOUT the locale, so unlike every other example here it sets
# its own instead of inheriting the pinned LC_ALL=C — in view, on every line.
#
# Run:  bash locale_and_lc_ctype_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

# A UTF-8 locale, whatever this machine calls it. The name differs per platform
# (macOS ships en_US.UTF-8, a bare Linux may have only C.UTF-8), so pick by
# asking each candidate what its charmap is and keep the NAME out of the output
# — otherwise this page's answer key would only match one machine.
utf8_locale() {
  local c
  for c in C.UTF-8 en_US.UTF-8 en_US.utf8; do
    if LC_ALL="$c" locale charmap 2>/dev/null | grep -qi 'utf-\?8'; then printf '%s' "$c"; return; fi
  done
  printf 'C'
}
U=$(utf8_locale)

# Ask the environment, not the name: is the character type UTF-8 right now?
isutf8() { if locale charmap 2>/dev/null | grep -qi 'utf-\?8'; then echo "UTF-8"; else echo "not UTF-8"; fi; }
ASK="$(declare -f isutf8); isutf8"

printf 'caf\303\251\n' > ./_demo.txt        # café + newline: 5 characters, 6 bytes

echo "1. THREE VARIABLES, ONE ANSWER — and the order they are consulted in"
printf '     LANG=<utf8>                        -> %s\n' "$(env -u LC_ALL -u LC_CTYPE LANG=$U    bash -c "$ASK")"
printf '     LANG=<utf8>  LC_CTYPE=C            -> %s   <- LC_CTYPE beats LANG\n' "$(env -u LC_ALL LANG=$U LC_CTYPE=C bash -c "$ASK")"
printf '     LANG=C  LC_CTYPE=C  LC_ALL=<utf8>  -> %s       <- LC_ALL beats everything\n' "$(LANG=C LC_CTYPE=C LC_ALL=$U bash -c "$ASK")"
echo "     LANG is the fallback, LC_CTYPE is the specific setting, LC_ALL is the"
echo "     override. Set LC_ALL in a script and nothing else can be consulted."

echo
echo "2. IN THE C LOCALE THERE IS NO SUCH THING AS A CHARACTER"
show "LC_ALL=C     wc -c < ./_demo.txt | tr -d ' '"
show "LC_ALL=C     wc -m < ./_demo.txt | tr -d ' '"
echo "   ^ two different flags, the same answer. 'Character' means 'byte' here,"
echo "     so the question wc -m exists to ask cannot be asked."
show "LC_ALL=\$U    wc -m < ./_demo.txt | tr -d ' '"
echo "   ^ same file, same tool, same second. One byte of it is now half a letter."

echo
echo "3. LC_CTYPE IS NOT LC_COLLATE — the variables really are independent"
printf 'b\naz\nA\nB\naa\n' > ./_sort.txt
show "LC_ALL=C           sort ./_sort.txt | tr '\n' ' '; echo"
show "LC_CTYPE=\$U        sort ./_sort.txt | tr '\n' ' '; echo"
echo "   ^ identical. Switching the CHARACTER TYPE to UTF-8 says nothing about"
echo "     sort order, which is LC_COLLATE's job and was never asked to change."
echo "     'The locale' is six variables; a tool reads the one it needs."

echo
echo "4. SO WHICH TOOLS CHANGE?"
echo "     wc -m      yes   it is a question about characters"
echo "     wc -c      no    a byte is a byte in every locale"
echo "     sort       yes, but to LC_COLLATE, not to LC_CTYPE"
echo "     od -a      yes   it asks isprint() -- see 'Inspecting a file'"
echo "     tr         it depends on WHOSE tr, which is the point of the table"
echo "                on the page: BSD tr obeys the locale and GNU tr cannot."

rm -f ./_demo.txt ./_sort.txt
