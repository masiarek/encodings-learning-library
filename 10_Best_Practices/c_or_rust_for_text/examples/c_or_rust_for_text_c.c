/* C for text: bytes, a NUL, and a locale you have to ask for.
 *
 * C has no string type and no character type. `char` is the machine's byte,
 * with a sign the standard leaves to the compiler, and a "string" is a run
 * of those up to the first zero. Everything that can tell a byte from a
 * character lives in the C library's locale machinery, which is off by
 * default, process-global once it is on, and not the same machinery on
 * every libc. This is the C half of the page; the Rust half asks the same
 * questions and gets its answers from a type instead of from a setting.
 *
 * Runs under LC_ALL=C like every example here. Section 2 switches to a UTF-8
 * locale itself, on purpose and in view.
 *
 * Build: cc -std=c11 -Wall -Wextra c_or_rust_for_text_c.c -o /tmp/cort && /tmp/cort
 */
#include <ctype.h>
#include <errno.h>
#include <locale.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include <wctype.h>

static void hex(const char *s, size_t n)
{
    for (size_t i = 0; i < n; i++) printf("%s%02x", i ? " " : "", (unsigned char)s[i]);
}

/* mbrtowc, one step at a time: the C spelling of Rust's Utf8Error. */
static void walk(const char *label, const char *s, size_t len)
{
    mbstate_t st;
    memset(&st, 0, sizeof st);
    size_t i = 0;
    wchar_t wc;
    printf("   %-12s", label);
    while (i < len) {
        size_t r = mbrtowc(&wc, s + i, len - i, &st);
        if (r == (size_t)-1) { printf("  | byte %zu: (size_t)-1, invalid", i); break; }
        if (r == (size_t)-2) { printf("  | byte %zu: (size_t)-2, incomplete", i); break; }
        if (r == 0) r = 1;          /* a NUL decodes to L'\0' and reports 0 bytes */
        printf(" U+%04lX", (unsigned long)wc);
        i += r;
    }
    printf("\n");
}

int main(void)
{
    const char cafe[] = "caf\xc3\xa9";          /* café, spelled as the bytes it is */

    printf("1. A char IS A BYTE, AND A STRING IS BYTES UP TO THE FIRST ZERO\n");
    printf("   char cafe[] = \"caf\\xc3\\xa9\";\n");
    printf("   sizeof cafe = %zu   strlen(cafe) = %zu   bytes: ", sizeof cafe, strlen(cafe));
    hex(cafe, strlen(cafe));
    printf("\n");
    printf("   (signed char)cafe[3] = %d   (unsigned char)cafe[3] = %u\n",
           (signed char)cafe[3], (unsigned char)cafe[3]);
    printf("   Six bytes of storage, five of text, and a NUL that is the only\n");
    printf("   structure the type has. Nothing says UTF-8: the é is two chars\n");
    printf("   because that is how many bytes it takes, and which of those two\n");
    printf("   numbers a plain char gives you is the compiler's choice -- the\n");
    printf("   standard leaves the sign of char to the implementation.\n");

    printf("\n2. NOTHING KNOWS WHAT THE BYTES MEAN UNTIL YOU SET A LOCALE\n");
    printf("   MB_CUR_MAX at startup = %zu   (one byte per character: the C locale)\n",
           (size_t)MB_CUR_MAX);
    const char *names[] = {"C.UTF-8", "en_US.UTF-8", "UTF-8"};
    const char *got = NULL;
    for (size_t i = 0; i < 3 && !got; i++) got = setlocale(LC_ALL, names[i]);
    printf("   setlocale(LC_ALL, a UTF-8 locale): %s   MB_CUR_MAX > 1 now: %s\n",
           got ? "obtained" : "NONE AVAILABLE", MB_CUR_MAX > 1 ? "yes" : "no");
    wchar_t w[8];
    size_t n = mbstowcs(w, cafe, 8);
    printf("   mbstowcs(cafe) = %zu wide characters:", n);
    for (size_t i = 0; i < n; i++) printf(" U+%04lX", (unsigned long)w[i]);
    printf("\n");
    printf("   Same five bytes, and now they are four characters -- because a\n");
    printf("   global setting changed, not because anything about the data did.\n");
    printf("   The setting is per process and reaches every thread. And the C\n");
    printf("   locale it replaced is not even the same locale on every libc: the\n");
    printf("   page's dated fence has this exact mbstowcs call, under LC_ALL=C,\n");
    printf("   returning five on macOS and failing on glibc.\n");

    printf("\n3. DISCOVERY IS A LOOP YOU WRITE, AND TWO NEGATIVE NUMBERS\n");
    walk("cafe", cafe, 5);
    walk("caf c3", "caf\xc3", 4);
    walk("caf c3 28", "caf\xc3(", 5);
    walk("a c0 af", "a\xc0\xaf", 3);
    walk("a ed a0 80", "a\xed\xa0\x80", 4);
    errno = 0;
    n = mbstowcs(w, "caf\xc3", 8);
    printf("   mbstowcs(caf c3) == (size_t)-1: %s   errno == EILSEQ: %s\n",
           n == (size_t)-1 ? "yes" : "no", errno == EILSEQ ? "yes" : "no");
    printf("   That is all the one-shot call says: not where it stopped and not\n");
    printf("   whether more bytes would have helped. mbrtowc, one character per\n");
    printf("   call with an mbstate_t between calls, gives back both. (size_t)-2\n");
    printf("   is a valid prefix that ran out -- keep it, read more. (size_t)-1 is\n");
    printf("   bytes that will never be text -- skip and resynchronise. Those are\n");
    printf("   Rust's error_len() None and Some(n), and Rust hands them to you from\n");
    printf("   the first call.\n");

    printf("\n4. CASE: THE BYTE FUNCTION AND THE CHARACTER FUNCTION ARE NOT THE SAME FUNCTION\n");
    printf("   toupper over the bytes of cafe: ");
    for (size_t i = 0; i < 5; i++) printf("%02x ", (unsigned)toupper((unsigned char)cafe[i]));
    printf("\n");
    printf("   towupper(U+00E9)              : U+%04lX\n", (unsigned long)towupper(0xE9));
    printf("   toupper takes one byte and answered for the three ASCII ones; the\n");
    printf("   two bytes of é came back as they went in. towupper takes the decoded\n");
    printf("   value, so it can only run after sections 2 and 3 have happened. What\n");
    printf("   toupper does with a byte above 0x7F is the locale's business, and\n");
    printf("   the page's dated fence shows the two libcs answering differently.\n");

    printf("\n5. WHAT THIS BOUGHT, AND WHAT IT COST\n");
    printf("   Bought: the bytes are yours. Nothing copied, validated or refused\n");
    printf("   them, so a file of unknown encoding, a Latin-1 record or a filename\n");
    printf("   is a char* with no ceremony -- and iconv(3) converts between more\n");
    printf("   tables than Rust's std will ever ship.\n");
    printf("   Cost: a global setting, a loop, an mbstate_t, and answers that belong\n");
    printf("   to whichever libc the program was linked against.\n");
    return 0;
}
