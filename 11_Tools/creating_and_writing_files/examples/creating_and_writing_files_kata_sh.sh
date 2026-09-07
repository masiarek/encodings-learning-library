#!/usr/bin/env bash
# The answer key for this page's kata. Everything the folded block claims is
# printed by this program, so a solution cannot rot into one that no longer
# says what the page says.
#
# Two things it has to pin, or the key would not be an answer at all:
#
#   * USER. The kata's fifth line is an unquoted heredoc containing $USER,
#     whose whole point is that it expands -- so on the reader's machine it
#     expands to something else. It is set to `ada` here and the page says so.
#   * stat. -f is the format string on BSD and "show the filesystem" on GNU,
#     and BOTH succeed, so a try-one-then-the-other fallback is silently wrong
#     on Linux. Probe once, commit to an answer. (Same helper as the lesson's
#     own example; the two files are run separately, so it is repeated rather
#     than shared.)
#
# Run:  bash creating_and_writing_files_kata_sh.sh
set -eu

if stat -c '%i' . >/dev/null 2>&1; then STATFMT=-c; MOD='%a'
else                                    STATFMT=-f; MOD='%Lp'; fi
mode() { stat "$STATFMT" "$MOD" "$1"; }
size() { wc -c < "$1" | tr -d ' '; }
hex()  { xxd -p < "$1" | tr -d '\n'; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

USER=ada    # pinned: the reader's own run will differ on line 5, and only there

echo "PART ONE — THE SIX WRITES, AS BYTES"
echo
echo hello         > f; w1=$(hex f)
printf hello       > f; w2=$(hex f)
printf 'hello\n'   > f; w3=$(hex f)
cat <<< hello      > f; w4=$(hex f)
cat << EOF         > f
hello $USER
EOF
w5=$(hex f)
cat << 'EOF'       > f
hello $USER
EOF
w6=$(hex f)
printf '   %-24s %s\n' "echo hello"         "$w1"
printf '   %-24s %s\n' "printf hello"       "$w2"
printf '   %-24s %s\n' "printf 'hello\\n'"   "$w3"
printf '   %-24s %s\n' "cat <<< hello"      "$w4"
printf '   %-24s %s\n' "<< EOF   (\$USER=ada)" "$w5"
printf '   %-24s %s\n' "<< 'EOF'"           "$w6"
echo
echo "   68 65 6c 6c 6f is hello. Rows 1, 3 and 4 are the SAME FILE: echo is"
echo "   printf with an 0a glued on and an argument parser you did not ask"
echo "   for, and <<< supplies the newline too. Row 2 is the only one of the"
echo "   four that stops where you stopped typing."
[ "$w1" = "$w3" ] && [ "$w3" = "$w4" ] || { echo "   BUG: rows 1/3/4 differ"; exit 1; }
echo "   Rows 5 and 6 differ by the length of a username, and row 6 holds a"
echo "   literal dollar sign — 24 55 53 45 52 is \$USER, five characters that"
echo "   are in the file rather than a name that was looked up."
echo
echo "   The reader's row 5 will not match this one, and that is the answer:"
echo "   an unquoted delimiter makes the heredoc a double-quoted string, so"
echo "   what lands in the file depends on who ran it."

echo
echo "PART TWO — EMPTYING A FILE THAT SOMEBODY ELSE IS HOLDING"
echo
setup() {          # 12 bytes, mode 600, a second NAME, and an open DESCRIPTOR
  rm -f f g
  printf 'old content\n' > f
  ln f g
  chmod 600 f
  exec 3< f
}
report() {
  held=$(cat <&3 | tr -d '\n')          # what the pre-blanking descriptor still sees
  exec 3<&-
  printf '   %-32s g: %2s bytes   mode: %s   fd 3 reads: %s\n' \
    "$1" "$(size g)" "$(mode f)" "${held:-(nothing)}"
}
setup; : > f                              ; report ": > f"
setup; install -m 644 /dev/null f         ; report "install -m 644 /dev/null f"
echo
echo "   Three questions, and the two commands disagree on all three."
echo
echo "   ': >' TRUNCATES. There is one file, both names see it, and the"
echo "   descriptor opened before the blanking is still on that same file —"
echo "   which is now empty, so it reads nothing. The mode was never touched."
echo
echo "   install REPLACES. The name f now points at a new file; g and fd 3"
echo "   still hold the old one, twelve bytes of it, and will go on holding it"
echo "   until the last reference goes away. -m set the mode because setting"
echo "   the mode is what install is for. This is the shape of the classic"
echo "   log-rotation bug: the daemon's descriptor keeps a nameless file"
echo "   growing on a disk where nothing can be found to delete."
echo
echo "   And the inode number predicted none of the three. Unlinking returns"
echo "   it to the pool, so the replacement may be handed the same number"
echo "   back — the lesson's own section 3 measures both outcomes. What"
echo "   answers the question is something that HOLDS the file: the second"
echo "   link, or the descriptor."
