#!/usr/bin/env bash
# One command tells you whether a CSV has a signature. The rest is consequences.
#
# The reason this bug survives a morning is that every tool which shows you the
# file shows you text, and in text the three bytes are nothing at all. So the
# first move is always the same: look at the bytes.
#
# Run:  bash bom_in_a_csv_sh.sh

set -u

BOM='\xef\xbb\xbf'
excel() { printf "${BOM}id,name\n1,Ada\n2,Ben\n"; }   # saved from Excel as "CSV UTF-8"
clean() { printf 'id,name\n1,Ada\n2,Ben\n'; }         # written by a script

say() { printf '\n%s\n%s\n\n' "$1" "------------------------------------------------------------------------"; }

say "1. THE DIAGNOSIS, IN ONE COMMAND"
printf '   xxd on the file from Excel:\n'
excel | xxd | head -1 | sed 's/^/     /'
printf '\n   xxd on the file from a script:\n'
clean | xxd | head -1 | sed 's/^/     /'
printf '\n   Or just the first three bytes, which is the whole question:\n'
printf '     from Excel      %s\n' "$(excel | head -c 3 | xxd -p)"
printf '     from a script   %s\n' "$(clean | head -c 3 | xxd -p)"
printf '\n   efbbbf means a signature is present. Anything else means there is\n'
printf '   none. On screen the two files are identical, and they will stay\n'
printf '   identical in every editor, viewer and paste into a chat window.\n'

say "2. WHAT IT DOES TO A SHELL PIPELINE"
printf '   grep -c "^id"      clean %s   signed %s\n' \
    "$(clean | grep -c '^id')" "$(excel | grep -c '^id')"
printf '   first field, cut   clean %s   signed %s\n' \
    "$(clean | head -1 | cut -d, -f1 | xxd -p)" "$(excel | head -1 | cut -d, -f1 | xxd -p)"
printf '   awk "$1==\\"id\\""    clean %s   signed %s\n' \
    "$(clean | head -1 | awk -F, '{print ($1=="id") ? "match" : "no match"}')" \
    "$(excel | head -1 | awk -F, '{print ($1=="id") ? "match" : "no match"}')"
printf '\n   Three pipelines, three silent wrong answers. Not one of them\n'
printf '   errors; grep returns 0 matches, cut hands back a field with three\n'
printf '   extra bytes, awk compares two strings that print the same and are\n'
printf '   not equal. A pipeline built on any of these produces an empty\n'
printf '   report and no complaint.\n'

say "3. STRIP IT ON THE WAY IN"
printf '   sed "1s/^<bom>//" then the same three checks:\n'
strip() { sed "1s/^$(printf '\xef\xbb\xbf')//"; }
printf '     grep -c "^id"    %s\n' "$(excel | strip | grep -c '^id')"
printf '     first field      %s\n' "$(excel | strip | head -1 | cut -d, -f1 | xxd -p)"
printf '     awk compare      %s\n' \
    "$(excel | strip | head -1 | awk -F, '{print ($1=="id") ? "match" : "no match"}')"
printf '\n   ..and on the file that never had one, the same sed is a no-op:\n'
printf '     grep -c "^id"    %s\n' "$(clean | strip | grep -c '^id')"
printf '\n   Line 1 only, and conditional. That is `encoding="utf-8-sig"` for\n'
printf '   a shell pipeline, and it is safe to put in front of any CSV.\n'

say "4. THE OTHER DIRECTION, WHICH IS WHY THE THING EXISTS"
printf '   a UTF-8 row with an em dash, no signature:\n'
printf '1,before\xe2\x80\x94after\n' | xxd | sed 's/^/     /'
printf '\n   handed to a reader that guesses a one-byte table instead:\n'
printf '     as Mac Roman   %s\n' "$(printf '1,before\xe2\x80\x94after' | iconv -f MAC -t UTF-8)"
printf '     as CP1252      %s\n' "$(printf '1,before\xe2\x80\x94after' | iconv -f CP1252 -t UTF-8)"
printf '\n   Both are what Excel shows on a double-click when nothing declared\n'
printf '   the encoding -- a Mac guesses one, Windows the other, and the shape\n'
printf '   of the garbage says which. Three bytes at the front remove the\n'
printf '   guess. That is the entire argument for writing one, and it applies\n'
printf '   only to files whose reader is a person.\n'
