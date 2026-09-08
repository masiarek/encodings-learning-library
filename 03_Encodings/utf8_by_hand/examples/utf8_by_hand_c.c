/* UTF-8 by hand, in the language that hands you nothing.
 *
 * Python has .encode, Rust has char::encode_utf8. C has no character type, no
 * string type and no opinion about text -- so the encoder below IS the pencil
 * method, written in the arithmetic a pencil does: pick a template, shift the
 * payload bits into its slots, or with the markers. Ten lines, and after this
 * page you could write it from the table.
 *
 * Section 4 is C's own stake in the design. Nothing in a multi-byte UTF-8
 * sequence is a zero byte, so strlen, strcpy and strcmp kept working on the
 * day UTF-8 arrived -- which is the concrete form of the compatibility
 * argument on "Why UTF-8 won", in the only language that can show it.
 *
 * Build: cc -std=c11 -Wall -Wextra utf8_by_hand_c.c
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define TOP_OF_UNICODE 0x10FFFFu
#define SURROGATE_LO   0xD800u
#define SURROGATE_HI   0xDFFFu

/* The encoder. This is the whole of UTF-8 in the encode direction. */
static int encode(uint32_t cp, unsigned char out[4]) {
    if (cp < 0x80u) {                       /* 0xxxxxxx                      */
        out[0] = (unsigned char)cp;
        return 1;
    }
    if (cp < 0x800u) {                      /* 110xxxxx 10xxxxxx             */
        out[0] = (unsigned char)(0xC0u | (cp >> 6));
        out[1] = (unsigned char)(0x80u | (cp & 0x3Fu));
        return 2;
    }
    if (cp < 0x10000u) {                    /* 1110xxxx 10xxxxxx 10xxxxxx    */
        out[0] = (unsigned char)(0xE0u | (cp >> 12));
        out[1] = (unsigned char)(0x80u | ((cp >> 6) & 0x3Fu));
        out[2] = (unsigned char)(0x80u | (cp & 0x3Fu));
        return 3;
    }
    out[0] = (unsigned char)(0xF0u | (cp >> 18));   /* 11110xxx + three      */
    out[1] = (unsigned char)(0x80u | ((cp >> 12) & 0x3Fu));
    out[2] = (unsigned char)(0x80u | ((cp >> 6) & 0x3Fu));
    out[3] = (unsigned char)(0x80u | (cp & 0x3Fu));
    return 4;
}

/* The width a lead byte announces, from its leading 1 bits alone. */
static int announced_width(unsigned char b) {
    if (b < 0x80u) return 1;
    if (b < 0xC0u) return 0;                /* a continuation byte, not a lead */
    if (b < 0xE0u) return 2;
    if (b < 0xF0u) return 3;
    return 4;
}

/* The decoder: strip every marker, concatenate what is left. */
static uint32_t decode(const unsigned char *b, int width) {
    static const uint32_t lead_mask[5] = {0, 0x7Fu, 0x1Fu, 0x0Fu, 0x07u};
    uint32_t cp = b[0] & lead_mask[width];
    for (int i = 1; i < width; i++) cp = (cp << 6) | (b[i] & 0x3Fu);
    return cp;
}

/* Three lines, and they are the whole of self-synchronisation. */
static size_t start_of_character(const unsigned char *s, size_t at) {
    while (at > 0 && (s[at] & 0xC0u) == 0x80u) at--;
    return at;
}

static void print_hex(const unsigned char *b, int n) {
    for (int i = 0; i < n; i++) printf("%02X%s", b[i], i + 1 < n ? " " : "");
}

int main(void) {
    static const struct { uint32_t cp; const char *why; } CAST[] = {
        {0x0041u,  "ASCII"},
        {0x00E9u,  "233 needs 8 bits, and 7 fit"},
        {0x017Cu,  "past U+00FF"},
        {0x20ACu,  "14 bits in 16 slots"},
        {0x1F600u, "above U+FFFF"},
    };
    const size_t cast_n = sizeof CAST / sizeof CAST[0];

    puts("1. THE ENCODER IS THE PENCIL METHOD, IN TEN LINES");
    puts("   No character type, no string type, no library. Choose the");
    puts("   template by comparing against 0x80 / 0x800 / 0x10000, shift the");
    puts("   payload bits into place, or with the markers. That is all of it.");
    puts("");
    puts("   code point   bytes  the encoder's answer  as text");
    for (size_t i = 0; i < cast_n; i++) {
        unsigned char buf[5] = {0};
        int n = encode(CAST[i].cp, buf);
        printf("   U+%04X%*s%d      ", CAST[i].cp,
               CAST[i].cp > 0xFFFFu ? 7 : 8, "", n);
        print_hex(buf, n);
        printf("%*s%s   %s\n", (int)(14 - 3 * n), "", (const char *)buf,
               CAST[i].why);
    }
    puts("");

    puts("2. AND THE DECODER IS THE SAME TABLE BACKWARDS");
    puts("   The first byte announces the width; every other byte gives up its");
    puts("   low six bits. Round-tripped over every scalar value below.");
    puts("");
    for (size_t i = 0; i < cast_n; i++) {
        unsigned char buf[4];
        int n = encode(CAST[i].cp, buf);
        int w = announced_width(buf[0]);
        uint32_t back = decode(buf, w);
        printf("   ");
        print_hex(buf, n);
        printf("%*sannounced width %d   decodes to U+%04X%*s%s\n",
               (int)(14 - 3 * n), "", w, back,
               back > 0xFFFFu ? 3 : 4, "",
               back == CAST[i].cp ? "ok" : "WRONG");
    }
    puts("");

    puts("3. THE ROUND TRIP, OVER EVERY SCALAR VALUE UNICODE HAS");
    {
        unsigned long checked = 0, widths[5] = {0, 0, 0, 0, 0};
        int worst_backward_walk = 0;
        for (uint32_t cp = 0; cp <= TOP_OF_UNICODE; cp++) {
            unsigned char buf[4];
            int n;
            if (cp >= SURROGATE_LO && cp <= SURROGATE_HI) continue;
            n = encode(cp, buf);
            if (announced_width(buf[0]) != n) {
                printf("   FAIL: U+%X announces the wrong width\n", cp);
                return 1;
            }
            if (decode(buf, n) != cp) {
                printf("   FAIL: U+%X does not survive the round trip\n", cp);
                return 1;
            }
            /* land on the LAST byte and walk back to the character's start */
            {
                size_t last = (size_t)(n - 1);
                int walk = (int)(last - start_of_character(buf, last));
                if (walk > worst_backward_walk) worst_backward_walk = walk;
            }
            widths[n]++;
            checked++;
        }
        printf("   %lu scalar values encoded, and every one decoded back to\n", checked);
        puts("   the number it came from. No table, no library, no allocation.");
        puts("");
        printf("   1 byte   %8lu   ASCII\n", widths[1]);
        printf("   2 bytes  %8lu\n", widths[2]);
        printf("   3 bytes  %8lu   (the surrogate hole is subtracted here)\n", widths[3]);
        printf("   4 bytes  %8lu\n", widths[4]);
        printf("            %8lu   = 0x110000 - 2048\n",
               widths[1] + widths[2] + widths[3] + widths[4]);
        puts("");
        printf("   Worst backward walk from a byte to its character's start: %d\n",
               worst_backward_walk);
        puts("   -- three, because no template is longer. That loop is the whole");
        puts("   of self-synchronisation and it needs no state at all.");
    }
    puts("");

    puts("4. WHY strlen NEVER HAD TO CHANGE");
    puts("   C strings end at a zero byte, so an encoding that put a zero byte");
    puts("   inside a character would have broken every C program ever written.");
    puts("   UTF-8 does not, and that is checkable rather than promised:");
    puts("");
    {
        unsigned long zero_bytes_inside = 0, low_bytes_inside = 0;
        for (uint32_t cp = 1; cp <= TOP_OF_UNICODE; cp++) {
            unsigned char buf[4];
            int n;
            if (cp >= SURROGATE_LO && cp <= SURROGATE_HI) continue;
            n = encode(cp, buf);
            if (n == 1) continue;                       /* ASCII is itself */
            for (int i = 0; i < n; i++) {
                if (buf[i] == 0x00u) zero_bytes_inside++;
                if (buf[i] < 0x80u) low_bytes_inside++;
            }
        }
        printf("   zero bytes found inside a multi-byte character : %lu\n",
               zero_bytes_inside);
        printf("   bytes below 0x80 found inside one              : %lu\n",
               low_bytes_inside);
    }
    puts("");
    {
        const char *word = "\xc5\xbc\xc3\xb3\xc5\x82w";   /* the Polish for turtle */
        printf("   \"%s\"  strlen = %zu   ", word, strlen(word));
        printf("bytes: ");
        print_hex((const unsigned char *)word, (int)strlen(word));
        puts("");
        printf("   strchr(word, 'w') found the 'w' at byte %ld, and it really is\n",
               (long)(strchr(word, 'w') - word));
        puts("   a 'w' -- not the tail of a letter that happened to end in 0x77.");
    }
    puts("");
    puts("   strlen counts bytes, and on this page that is not a bug: there is");
    puts("   no character type in C to count instead. What matters is that it");
    puts("   terminates in the right place and that a byte search cannot land");
    puts("   inside a character. Both fall out of the templates, and both are");
    puts("   why UTF-8 could be adopted without a flag day.");
}
