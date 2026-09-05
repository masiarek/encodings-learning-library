/* The shortest-form rule, derived rather than quoted.
 *
 * C is where this bug actually shipped, because in C the decoder is yours.
 * Part 1 writes the decoder straight off the template table and watches it
 * accept an overlong brace. Part 2 derives the three boundary bytes from
 * arithmetic -- the numbers on Steagall's "Boundary Conditions" slide are
 * not conventions to memorise, they are the smallest second byte that is
 * not already spellable in fewer bytes. Part 3 is the fix, in three tests.
 */
#include <stdint.h>
#include <stdio.h>

/* Decode one sequence off the templates. No validation of any kind. */
static uint32_t naive_decode(const unsigned char *b, int *len)
{
    if (b[0] < 0x80) { *len = 1; return b[0]; }
    if ((b[0] >> 5) == 0x06) { *len = 2; return (uint32_t)(b[0] & 0x1F) << 6
                                             | (uint32_t)(b[1] & 0x3F); }
    if ((b[0] >> 4) == 0x0E) { *len = 3; return (uint32_t)(b[0] & 0x0F) << 12
                                             | (uint32_t)(b[1] & 0x3F) << 6
                                             | (uint32_t)(b[2] & 0x3F); }
    *len = 4; return (uint32_t)(b[0] & 0x07) << 18
                  | (uint32_t)(b[1] & 0x3F) << 12
                  | (uint32_t)(b[2] & 0x3F) << 6
                  | (uint32_t)(b[3] & 0x3F);
}

/* The smallest code point each template is ALLOWED to carry. */
static uint32_t floor_for(int len)
{
    return len == 1 ? 0x0u : len == 2 ? 0x80u : len == 3 ? 0x800u : 0x10000u;
}

int main(void)
{
    static const unsigned char brace1[] = { 0x7D };
    static const unsigned char brace2[] = { 0xC1, 0xBD };
    static const unsigned char brace3[] = { 0xE0, 0x81, 0xBD };
    static const unsigned char brace4[] = { 0xF0, 0x80, 0x81, 0xBD };
    const unsigned char *forms[4] = { brace1, brace2, brace3, brace4 };
    int len;
    uint32_t cp;

    printf("1. THE DECODER WITH NOTHING BUT THE TEMPLATES\n");
    for (int n = 0; n < 4; n++) {
        cp = naive_decode(forms[n], &len);
        printf("   %d byte%s -> U+%04X  '%c'\n", len, len == 1 ? " " : "s",
               cp, (char)cp);
    }
    printf("   Four different byte strings, one character. C will not stop you:\n");
    printf("   there is no str type here, only a pointer, and no library ran a check.\n");

    printf("\n2. WHERE THE BOUNDARY FALLS, BY ARITHMETIC\n");
    printf("   For each template, walk the second byte upward and ask the only\n");
    printf("   question that matters: is this code point already spellable shorter?\n");
    for (len = 2; len <= 4; len++) {
        unsigned char probe[4] = { 0, 0x80, 0x80, 0x80 };
        unsigned int first_ok = 0;
        unsigned char lead = len == 2 ? 0xC0 : len == 3 ? 0xE0 : 0xF0;
        int dummy;
        if (len == 2) {
            /* For two bytes the LEAD byte is what moves; the payload is in it. */
            for (unsigned int b0 = 0xC0; b0 <= 0xDF; b0++) {
                probe[0] = (unsigned char)b0; probe[1] = 0x80;
                if (naive_decode(probe, &dummy) >= floor_for(2)) { first_ok = b0; break; }
            }
            printf("   2 bytes: lead 0x%02X 0x80 is the first that reaches U+%04X\n",
                   first_ok, floor_for(2));
            printf("            so 0xC0 and 0xC1 lead nothing legal, ever.\n");
            continue;
        }
        for (unsigned int b1 = 0x80; b1 <= 0xBF; b1++) {
            probe[0] = lead; probe[1] = (unsigned char)b1;
            probe[2] = 0x80; probe[3] = 0x80;
            if (naive_decode(probe, &dummy) >= floor_for(len)) { first_ok = b1; break; }
        }
        printf("   %d bytes: 0x%02X 0x%02X ... is the first that reaches U+%04X\n",
               len, lead, first_ok, floor_for(len));
        printf("            so after 0x%02X, a second byte below 0x%02X is overlong.\n",
               lead, first_ok);
    }

    printf("\n3. THE FIX, IN THREE COMPARISONS\n");
    printf("   if (b0 == 0xC0 || b0 == 0xC1)                 return REJECT;\n");
    printf("   if (b0 == 0xE0 && b1 <  0xA0)                 return REJECT;\n");
    printf("   if (b0 == 0xF0 && b1 <  0x90)                 return REJECT;\n");
    for (int n = 0; n < 4; n++) {
        const unsigned char *b = forms[n];
        int reject = (b[0] == 0xC0 || b[0] == 0xC1)
                  || (b[0] == 0xE0 && b[1] < 0xA0)
                  || (b[0] == 0xF0 && b[1] < 0x90);
        cp = naive_decode(b, &len);
        printf("   %d byte%s U+%04X  %s\n", len, len == 1 ? " " : "s", cp,
               reject ? "REJECT" : "accept");
    }
    printf("   Three lines. That is the entire cost of the rule, and leaving them\n");
    printf("   out is what a decade of directory-traversal advisories was about.\n");
    return 0;
}
