/* The C view: nothing checks, so here is the check you have to write.
 *
 * Build & run:  cc -std=c11 -Wall -Wextra validation_is_a_boundary_c.c -o v && ./v
 */
#include <stdio.h>
#include <string.h>
#include <stddef.h>

typedef enum { UTF8_OK, UTF8_BAD, UTF8_INCOMPLETE } utf8_status;

/* The whole of RFC 3629, as a range table. This is the function Rust's core
 * library runs once at the boundary, and the function Bob Steagall's CppCon
 * talk rewrites as a DFA and then as SSE intrinsics. It is not big. It is
 * just never written for you. */
static utf8_status utf8_validate(const unsigned char *v, size_t len, size_t *valid_up_to)
{
    size_t i = 0;
    while (i < len) {
        const size_t start = i;
        const unsigned char c = v[i];

        if (c < 0x80) { i++; continue; }            /* plain ASCII */

        size_t need;                                 /* continuation bytes required */
        if      (c >= 0xC2 && c <= 0xDF) need = 1;
        else if (c >= 0xE0 && c <= 0xEF) need = 2;
        else if (c >= 0xF0 && c <= 0xF4) need = 3;
        else { *valid_up_to = start; return UTF8_BAD; }   /* 80..C1 and F5..FF cannot lead */

        const size_t avail = len - i - 1;
        for (size_t k = 1; k <= need && k <= avail; k++) {
            const unsigned char b = v[i + k];
            int ok;
            if (k > 1)              ok = (b >= 0x80 && b <= 0xBF);
            else if (c == 0xE0)     ok = (b >= 0xA0 && b <= 0xBF);  /* no overlong 3-byte */
            else if (c == 0xED)     ok = (b >= 0x80 && b <= 0x9F);  /* no surrogates */
            else if (c == 0xF0)     ok = (b >= 0x90 && b <= 0xBF);  /* no overlong 4-byte */
            else if (c == 0xF4)     ok = (b >= 0x80 && b <= 0x8F);  /* nothing above U+10FFFF */
            else                    ok = (b >= 0x80 && b <= 0xBF);
            if (!ok) { *valid_up_to = start; return UTF8_BAD; }
        }
        if (avail < need) { *valid_up_to = start; return UTF8_INCOMPLETE; }
        i += need + 1;
    }
    *valid_up_to = len;
    return UTF8_OK;
}

static void show_bytes(const unsigned char *v, size_t len)
{
    for (size_t i = 0; i < len; i++) printf("%s%02x", i ? " " : "", v[i]);
}

int main(void)
{
    /* U+D800 as UTF-8 would be ED A0 80 - a sequence Unicode forbids outright. */
    const char surrogate[] = "\xed\xa0\x80";
    const char overlong[]  = "\xc0\xaf";

    printf("1. C HOLDS WHAT UNICODE FORBIDS, AND NOTHING OBJECTS\n");
    printf("   char surrogate[] = \"\\xed\\xa0\\x80\";   strlen = %zu, sizeof = %zu\n",
           strlen(surrogate), sizeof surrogate);
    printf("   char overlong[]  = \"\\xc0\\xaf\";        strlen = %zu, sizeof = %zu\n",
           strlen(overlong), sizeof overlong);
    printf("   Both compiled. Both have a length. printf(\"%%s\") would write those bytes to your\n");
    printf("   terminal unchanged. No function in the C library has an opinion about UTF-8,\n");
    printf("   because a char* is a run of bytes and that is the entire type.\n\n");

    printf("2. SO YOU WRITE THE CHECK YOURSELF - THE SAME INPUTS AS THE OTHER TWO EXAMPLES\n");
    struct { const unsigned char *v; size_t len; const char *why; } cases[] = {
        { (const unsigned char *)"\x7d",             1, "U+007D, the slide's line 1"      },
        { (const unsigned char *)"\xc2\xa9",         2, "U+00A9, the slide's line 2"      },
        { (const unsigned char *)"\xe2\x89\xa0",     3, "U+2260, the slide's line 3"      },
        { (const unsigned char *)"\x89",             1, "lone continuation byte"          },
        { (const unsigned char *)"\xe2\x89",         2, "truncated 3-byte sequence"       },
        { (const unsigned char *)"\xc0\xaf",         2, "overlong '/'"                    },
        { (const unsigned char *)"\xed\xa0\x80",     3, "UTF-16 surrogate U+D800"         },
        { (const unsigned char *)"\xf5\x80\x80\x80", 4, "above U+10FFFF"                  },
        { (const unsigned char *)"\xe0\x80\xaf",     3, "overlong '/' the 3-byte way"     },
    };
    const char *names[] = { "OK", "BAD", "INCOMPLETE" };
    for (size_t i = 0; i < sizeof cases / sizeof cases[0]; i++) {
        size_t up_to = 0;
        const utf8_status st = utf8_validate(cases[i].v, cases[i].len, &up_to);
        printf("   ");
        show_bytes(cases[i].v, cases[i].len);
        printf("%*s%-11s valid_up_to=%zu  %s\n",
               (int)(14 - 3 * cases[i].len), "", names[st], up_to, cases[i].why);
    }
    printf("\n");

    printf("3. THE TWO ANSWERS THAT ARE NOT THE SAME ANSWER\n");
    printf("   BAD        = these bytes are not UTF-8 and never will be. Resynchronise.\n");
    printf("   INCOMPLETE = a valid prefix that ran out. Keep it and read more.\n");
    printf("   That is Rust's Some(n) and None, and the distinction a 'return false' validator loses.\n\n");

    printf("4. WHAT THE TALK IS ACTUALLY ABOUT\n");
    printf("   The loop above is ~30 lines and branches once per byte. A DFA replaces the branches\n");
    printf("   with a table lookup per byte; SSE intrinsics check 16 bytes per iteration.\n");
    printf("   Same rules, same verdicts - only the throughput changes.\n");
    return 0;
}
