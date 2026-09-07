/* The C view: strtol answers a question you did not ask, and hides the answer
 * you needed in a pointer.
 *
 * Every language on this page has to decide where a hex string stops. C's
 * decision is the oldest and the loudest about its consequences: strtol
 * converts as much as it can, returns that, and reports nothing. Where it
 * stopped is written into `endptr`, and if you do not read `endptr` you cannot
 * tell a clean parse from a truncated one -- they return the same type, and
 * often the same value.
 *
 * Build:  cc -std=c11 -Wall -Wextra hex_number_or_bytes_c.c -o /tmp/hnb_c && /tmp/hnb_c
 */

#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

static const char *RULE =
    "------------------------------------------------------------------------";

int main(void)
{
    const char *cases[] = {"41", "0x41", "  41", "+41", "-41",
                           "4_1", "4G", "41xyz", "zz", "",
                           "FFFFFFFFFFFFFFFFFF"};
    const size_t n = sizeof cases / sizeof *cases;

    printf("\n1. IT CONVERTS WHAT IT CAN AND RETURNS IT\n%s\n\n", RULE);
    printf("   %-22s %20s  %-9s %s\n", "input", "strtol(.., 16)", "consumed", "left over");
    for (size_t i = 0; i < n; i++) {
        char *end;
        long v = strtol(cases[i], &end, 16);
        printf("   %-22s %20ld  %-9td %s\n", cases[i], v, end - cases[i],
               *end ? end : "(nothing)");
    }
    printf("\n   Only the first column is a return value. Rows 6, 7 and 8 all\n");
    printf("   succeeded as far as C is concerned -- 4, 4 and 65 -- and the\n");
    printf("   only trace of the rest of the string is the pointer. Row 9 and\n");
    printf("   row 10 return 0, which is also what a correct parse of \"0\"\n");
    printf("   returns, so the value alone cannot tell you they failed.\n");

    printf("\n2. AND IT ACCEPTS THREE THINGS A BYTE FIELD SHOULD NOT\n%s\n\n", RULE);
    printf("   %-22s %s\n", "\"0x41\"", "the prefix is part of base 16 in C, by the standard");
    printf("   %-22s %s\n", "\"  41\"", "leading whitespace is skipped before anything else");
    printf("   %-22s %s\n", "\"-41\"", "a sign is allowed, so a hex FIELD can arrive negative");
    printf("\n   The third is the one that surprises people. A two-digit hex\n");
    printf("   field is a byte, bytes have no sign, and strtol will hand you\n");
    printf("   -65 for \"-41\" without a murmur -- into a long, which is signed,\n");
    printf("   so the assignment to an unsigned char later is where it wraps.\n");

    printf("\n3. THE CHECKS THAT ARE PORTABLE\n%s\n\n", RULE);
    printf("   %-22s %-12s %-12s %s\n", "input", "no digits", "trailing", "ERANGE");
    for (size_t i = 0; i < n; i++) {
        char *end;
        errno = 0;
        long v = strtol(cases[i], &end, 16);
        (void)v;
        int no_digits = (end == cases[i]);
        int trailing = (!no_digits && *end != '\0');
        int range = (errno == ERANGE);
        printf("   %-22s %-12s %-12s %s\n", cases[i],
               no_digits ? "yes" : "no", trailing ? "yes" : "no", range ? "yes" : "no");
    }
    printf("\n   Three questions, three answers, and none of them is the return\n");
    printf("   value. `end == input` is the only portable way to learn that\n");
    printf("   nothing was converted, and ERANGE on overflow is the only errno\n");
    printf("   the standard promises: after a failed conversion errno is\n");
    printf("   implementation-defined, and macOS and glibc genuinely differ.\n");
    printf("   This program therefore prints the pointer comparison and never\n");
    printf("   errno itself -- the same discipline the rest of the library\n");
    printf("   applies to any answer that belongs to the machine.\n");

    printf("\n4. WHAT THE OVERFLOW ROW IS REALLY SAYING\n%s\n\n", RULE);
    printf("   LONG_MAX on this build is %ld, %zu bytes wide.\n", LONG_MAX, sizeof(long));
    printf("   \"FFFFFFFFFFFFFFFFFF\" is 18 hex digits, so 9 bytes of data --\n");
    printf("   perfectly ordinary as a field, and unrepresentable as a long.\n");
    printf("   The number door has a ceiling and the byte door does not, which\n");
    printf("   is the same distinction one more time: a hex string that is\n");
    printf("   DATA has no maximum, and a hex string that is a QUANTITY is\n");
    printf("   bounded by a type it never mentions.\n");

    return 0;
}
