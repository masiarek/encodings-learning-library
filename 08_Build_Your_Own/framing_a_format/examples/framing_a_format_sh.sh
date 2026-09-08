#!/usr/bin/env bash
# What the ASCII armour buys, on a real pipe.
#
# The same seven payload bytes twice: raw, and wrapped in Intel HEX records.
# Everything run here is byte-identical on macOS and Ubuntu -- `file`'s MIME
# output rather than its English, `iconv -f X -t X` as a yes/no validator,
# `cut -c` on pure ASCII under LC_ALL=C, and `wc -c` with its padding stripped.
#
# Run:  bash framing_a_format_sh.sh

set -u

say() { printf '\n%s\n%s\n\n' "$1" "------------------------------------------------------------------------"; }

work=$(mktemp -d) || exit 1
trap 'rm -rf "$work"' EXIT
cd "$work" || exit 1

# The tribit packing of 'café', straight from the tribit page.
PAYLOAD_HEX='543305e1d83740'

printf '%s' "$PAYLOAD_HEX" | xxd -r -p > payload.t3

# The same bytes as Intel HEX: one data record and the end-of-file record.
# Written out rather than computed, so this file is the fixture and the
# arithmetic behind it lives in the Python and Rust examples.
cat > payload.hex <<'RECORDS'
:07000000543305E1D837403D
:00000001FF
RECORDS

say "1. TWO FILES, ONE PAYLOAD"
printf '   %-16s %s\n' 'raw bytes' "$(xxd -p payload.t3)"
printf '   %s\n' 'as Intel HEX'
sed 's/^/       /' payload.hex
printf '\n   %-16s %s\n' 'file(1) says' "$(file --mime-type -b payload.t3)"
printf '   %-16s %s\n' 'and' "$(file --mime-type -b payload.hex)"
printf '\n   That verdict is the whole point of the armour: the same payload,\n'
printf '   and only one of the two files is something a text tool will open.\n'

say "2. ONLY ONE OF THEM SURVIVES A 7-BIT CHANNEL"
# iconv -f X -t X is a validator: it answers yes or no and agrees on both
# platforms, exit status included.
for f in payload.t3 payload.hex; do
    iconv -f US-ASCII -t US-ASCII < "$f" > /dev/null 2>&1
    status=$?
    if [ "$status" -eq 0 ]; then
        printf '   %-14s is US-ASCII    exit %d    goes through a 7-bit channel intact\n' "$f" "$status"
    else
        printf '   %-14s is NOT ASCII   exit %d    a 7-bit channel mangles or drops it\n' "$f" "$status"
    fi
done
printf '\n   In 1988 that channel was paper tape and a CRT terminal. Today it is\n'
printf '   a JSON string, a YAML block, a git diff, an email body and a copy\n'
printf '   and paste. The channel changed; the reason for the armour did not.\n'

say "3. FIXED-WIDTH ASCII MEANS cut IS A RECORD PARSER"
printf '   %-14s %s\n' 'record marks' "$(grep -c '^:' payload.hex)"
printf '   %-14s %s\n' 'RECLEN  (2-3)' "$(cut -c2-3   payload.hex | tr '\n' ' ')"
printf '   %-14s %s\n' 'OFFSET  (4-7)' "$(cut -c4-7   payload.hex | tr '\n' ' ')"
printf '   %-14s %s\n' 'RECTYP  (8-9)' "$(cut -c8-9   payload.hex | tr '\n' ' ')"
printf '   %-14s %s\n' 'CHKSUM  (last)' "$(sed 's/.*\(..\)$/\1/' payload.hex | tr '\n' ' ')"
printf '\n   No parser, no library, no program -- four column ranges. The fields\n'
printf '   are fixed width because they are counts of hex digits, so `cut`,\n'
printf '   `grep` and `sed` read this format as well as anything written for\n'
printf '   it. That is the second thing the armour buys, and it is the reason\n'
printf '   a format nobody would design today is still easy to debug.\n'
printf '\n   Find the end-of-file record with no tool that knows the format:\n'
printf '       %s\n' "$(grep -n '^:00000001FF$' payload.hex)"

say "4. THE DATA FIELD IS BASE16, SO xxd PUTS IT BACK"
data=$(sed -n '1s/^:........\(.*\)..$/\1/p' payload.hex)
printf '   %-16s %s\n' 'data field' "$data"
printf '%s' "$data" | xxd -r -p > back.bin
printf '   %-16s %s\n' 'xxd -r -p' "$(xxd -p back.bin)"
if cmp -s payload.t3 back.bin; then
    printf '   %-16s identical to the original bytes\n' 'cmp'
else
    printf '   %-16s DIFFERENT\n' 'cmp'
fi
printf '\n   Intel HEX has no encoding of its own. The DATA field is plain\n'
printf '   base16 -- the same rewriting `xxd -p` performs -- and everything\n'
printf '   else in the record is the frame. Separating those two is the\n'
printf '   point: an encoding turns values into bytes, a frame turns bytes\n'
printf '   into something a stranger can read back.\n'

say "5. WHAT IT COST"
raw=$(wc -c < payload.t3 | tr -d ' ')
body=$(tr -d '\n' < payload.hex | wc -c | tr -d ' ')
whole=$(wc -c < payload.hex | tr -d ' ')
printf '   %-30s %s\n' 'payload bytes'                 "$raw"
printf '   %-30s %s\n' 'characters, newlines stripped' "$body"
printf '   %-30s %s\n' 'file size with newlines'       "$whole"
printf '   %-30s %s%%\n' 'growth'                      "$(( body * 100 / raw ))"
printf '\n   Two costs, and only one of them scales. The base16 is 2x forever.\n'
printf '   The frame is a constant 11 characters a record, plus one 11-byte\n'
printf '   end-of-file record per file -- so it dominates a seven-byte payload\n'
printf '   and disappears into a long one:\n\n'
for n in 7 16 32 255; do
    printf '   %3d data bytes -> %4d characters   frame is %2d%% of the record\n' \
        "$n" "$(( n * 2 + 11 ))" "$(( 11 * 100 / (n * 2 + 11) ))"
done
printf '\n   255 is the largest RECLEN the 1988 specification allows. Real\n'
printf '   toolchains emit 16 or 32, which buys a line that fits in an editor\n'
printf '   at a frame cost of a quarter to a seventh.\n'
