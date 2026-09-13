#!/usr/bin/env bash
# Answer key: six bytes, five questions, two languages -- and the one question
# only the page's dated fence can answer. Compiles a C program and a Rust
# program of its own, so the two columns come from the two compilers and not
# from anybody's memory.
#
# Run:  bash c_or_rust_for_text_kata_sh.sh
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

cat > "$tmp/k.c" <<'CEOF'
#include <ctype.h>
#include <locale.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <wchar.h>
int main(void) {
    const char s[] = "a\xc3\xa9\xe2\x82\xac";                 /* a é € */
    printf("   C    strlen(s)                     = %zu\n", strlen(s));
    printf("   C    toupper over the bytes        :");
    for (size_t i = 0; i < strlen(s); i++) printf(" %02x", (unsigned)toupper((unsigned char)s[i]));
    printf("\n");
    const char *names[] = {"C.UTF-8", "en_US.UTF-8", "UTF-8"};
    const char *got = NULL;
    for (int i = 0; i < 3 && !got; i++) got = setlocale(LC_ALL, names[i]);
    wchar_t w[8];
    printf("   C    mbstowcs(s), UTF-8 locale     = %zu\n", mbstowcs(w, s, 8));
    mbstate_t st; memset(&st, 0, sizeof st);
    wchar_t wc; size_t i = 0, r = 0;
    while (i < 4) { r = mbrtowc(&wc, s + i, 4 - i, &st); if (r == (size_t)-1 || r == (size_t)-2) break; i += r; }
    printf("   C    mbrtowc on the first 4 bytes  : stopped at byte %zu with %s\n", i,
           r == (size_t)-2 ? "(size_t)-2, incomplete" : r == (size_t)-1 ? "(size_t)-1, invalid" : "no error");
    return 0;
}
CEOF

cat > "$tmp/k.rs" <<'REOF'
fn main() {
    let b: &[u8] = b"a\xc3\xa9\xe2\x82\xac"; // a é €
    let s = std::str::from_utf8(b).unwrap();
    println!("   Rust s.len()                       = {}", s.len());
    println!("   Rust s.chars().count()             = {}", s.chars().count());
    let e = std::str::from_utf8(&b[..4]).unwrap_err();
    println!("   Rust from_utf8(&b[..4])            : valid_up_to {}, error_len {:?}", e.valid_up_to(), e.error_len());
    let up = s.to_uppercase();
    let hex: Vec<String> = up.bytes().map(|x| format!("{x:02x}")).collect();
    println!("   Rust s.to_uppercase()              = {:?}  bytes {}", up, hex.join(" "));
}
REOF

cc -std=c11 -Wall -Wextra "$tmp/k.c" -o "$tmp/kc"
rustc --edition 2024 "$tmp/k.rs" -o "$tmp/krs"
"$tmp/kc" > "$tmp/c.out"
"$tmp/krs" > "$tmp/r.out"
c() { sed -n "${1}p" "$tmp/c.out"; }
r() { sed -n "${1}p" "$tmp/r.out"; }

echo "1. HOW LONG IS IT: SIX AND SIX, AND ONLY ONE SIDE CAN ALSO SAY THREE UNASKED"
c 1; r 1; r 2; c 3
echo "   Both count bytes without being told anything. Rust's three came from"
echo "   the type; C's three came from a setlocale call that had to run first,"
echo "   and before it ran the same call had no portable answer (question 5)."
echo
echo "2. THE FIRST FOUR BYTES: A CHARACTER CUT SHORT, SEEN FROM BOTH SIDES"
r 3; c 4
echo "   Same verdict at the same position: three good bytes, then the lead"
echo "   byte of € with nothing after it. None and (size_t)-2 both mean"
echo "   'read more' -- neither is the answer for bytes that are simply wrong."
echo
echo "3. UPPERCASE UNDER LC_ALL=C"
c 2; r 4
echo "   C changed the one ASCII byte and nothing else: the C locale has no"
echo "   opinion above 0x7F on either libc, which is the only reason this"
echo "   line could be recorded. Rust changed é to É from its own table, and"
echo "   would have printed the same under any environment at all."
echo
echo "4. WHAT EACH ONE NEEDED TO GET HERE"
echo "   C    : a locale name that exists on this machine, one global call,"
echo "          an mbstate_t, and a loop"
echo "   Rust : a slice and a function"
echo
echo "5. THE ONE WITH NO ANSWER"
echo "   C    mbstowcs(s) under LC_ALL=C     : (not recorded)"
echo "   Six on a Mac -- its C locale is a single-byte table where every byte"
echo "   is a character -- and (size_t)-1 on glibc, whose C locale is ASCII"
echo "   and stops at the first byte above 0x7F. The standard picks neither."
echo "   A key that held either number would be red on the other runner, so"
echo "   the page's dated fence holds both and this key holds a sentence."
