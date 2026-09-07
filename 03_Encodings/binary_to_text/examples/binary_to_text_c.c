/* The C view: a binary-to-text encoder is one integer and four shifts.
 *
 * Everything else on this page -- alphabets, padding rules, which base is
 * fashionable -- is decoration on these six lines. Three bytes are loaded into
 * one 24-bit accumulator and read back out in four 6-bit slices, and C is the
 * language that will not let you look away from that.
 *
 * Build:  cc -std=c11 -Wall -Wextra binary_to_text_c.c -o /tmp/btt_c && /tmp/btt_c
 */

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static const char ALPHABET[65] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

static const char *RULE =
    "------------------------------------------------------------------------";

static void encode_group(const unsigned char *in, size_t n, char out[5])
{
    /* Load: the three bytes become one 24-bit number, high byte first.
       A short group is zero-filled, which is what the padding then hides. */
    uint32_t v = (uint32_t)in[0] << 16;
    if (n > 1) v |= (uint32_t)in[1] << 8;
    if (n > 2) v |= (uint32_t)in[2];

    /* Store: read it back six bits at a time, most significant first. */
    out[0] = ALPHABET[(v >> 18) & 63];
    out[1] = ALPHABET[(v >> 12) & 63];
    out[2] = (n > 1) ? ALPHABET[(v >> 6) & 63] : '=';
    out[3] = (n > 2) ? ALPHABET[v & 63] : '=';
    out[4] = '\0';
}

int main(void)
{
    const unsigned char word[] = {0x63, 0x61, 0x66, 0xc3, 0xa9}; /* "café" in UTF-8 */
    const size_t len = sizeof word;

    printf("\n1. ONE ACCUMULATOR, FOUR SHIFTS\n%s\n\n", RULE);

    printf("   %-14s ", "the bytes");
    for (size_t i = 0; i < len; i++) printf("%02x ", word[i]);
    printf("  (%zu bytes)\n\n", len);

    char all[16] = {0};
    for (size_t off = 0; off < len; off += 3) {
        size_t n = (len - off < 3) ? len - off : 3;
        uint32_t v = (uint32_t)word[off] << 16;
        if (n > 1) v |= (uint32_t)word[off + 1] << 8;
        if (n > 2) v |= (uint32_t)word[off + 2];

        char out[5];
        encode_group(word + off, n, out);
        strcat(all, out);

        printf("   group %zu: %zu byte%s\n", off / 3 + 1, n, n == 1 ? "" : "s");
        printf("     v = 0x%06x        the 24-bit accumulator%s\n", v,
               n < 3 ? " (zero-filled)" : "");
        printf("     (v >> 18) & 63 = %2u -> %c\n", (v >> 18) & 63, out[0]);
        printf("     (v >> 12) & 63 = %2u -> %c\n", (v >> 12) & 63, out[1]);
        printf("     (v >>  6) & 63 = %2u -> %c%s\n", (v >> 6) & 63, out[2],
               n > 1 ? "" : "   (dropped: only one real byte, so '=')");
        printf("      v        & 63 = %2u -> %c%s\n", v & 63, out[3],
               n > 2 ? "" : "   (dropped: '=' says so)");
        printf("\n");
    }

    printf("   %-14s %s\n", "encoded", all);

    printf("\n2. WHY THE SHIFTS ARE THE WHOLE STORY\n%s\n\n", RULE);
    printf("   There is no string type here, no encoding, no locale and no\n");
    printf("   allocation. `unsigned char` in, ASCII out, and the only\n");
    printf("   arithmetic is masking six bits at a time out of a number that\n");
    printf("   was three bytes a moment ago.\n\n");
    printf("   That is why base64 costs exactly 4/3: %zu bytes is %zu group%s\n",
           len, (len + 2) / 3, (len + 2) / 3 == 1 ? "" : "s");
    printf("   of 24 bits, and each group is spent on four characters whether\n");
    printf("   it was full or not -- %zu characters out, %zu of them padding.\n",
           4 * ((len + 2) / 3), (size_t)(len % 3 ? 3 - len % 3 : 0));
    printf("\n   Change 6 to 5 and the alphabet to 32 characters and this is\n");
    printf("   Base32. Change it to 4 and 16 and it is a hex dump. The base\n");
    printf("   is a parameter; the loop is the encoding.\n");

    return 0;
}
