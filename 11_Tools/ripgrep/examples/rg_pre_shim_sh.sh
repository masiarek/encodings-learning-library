#!/bin/sh
# A ripgrep --pre preprocessor: make PDFs searchable by piping them through
# pdftotext. rg runs this once per file, hands it the filename as $1, and reads
# this program's stdout instead of the file itself. Anything that is not a PDF
# is passed through untouched, so the search result is the same as without it.
#
#     rg --pre <this file> --pre-glob '*.pdf' PATTERN .
#
# --pre-glob is not optional in practice: without it, every file in the search
# pays for a spawned process, not just the PDFs.
#
# Run with no arguments it explains itself, which is also how CI verifies that
# the copy printed on the page is the copy in this file.
case "$1" in
    "")          echo "usage: rg --pre $0 --pre-glob '*.pdf' PATTERN ." ;;
    *.pdf|*.PDF) exec pdftotext -q "$1" - ;;
    *)           exec cat "$1" ;;
esac
