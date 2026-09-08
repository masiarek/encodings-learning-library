/* The C view: the layout is in the declaration, and the declaration is about
 * memory rather than about a file.
 *
 * C is where the other three languages get their vocabulary. Python's 'I', 'h'
 * and 'd' are C's types; the padding Python's unprefixed format inserts is
 * C's padding; "network byte order" is a C library's four functions. And C is
 * the only one of the four with no serialiser at all -- no pack, no
 * to_be_bytes -- so the record has to be written out a byte at a time, or not
 * written out honestly.
 *
 * The shortcut is the reason this page exists. `fwrite(&r, sizeof r, 1, fp)`
 * compiles, runs, produces a file, and round-trips perfectly on the machine
 * that wrote it. What it actually emitted is the struct's MEMORY IMAGE: this
 * compiler's field order, this ABI's padding bytes, this CPU's byte order.
 * Change any of the three and the reader gets numbers rather than an error.
 *
 * Numbers that belong to this machine are printed as comparisons rather than
 * as values, so the recorded answer key does not depend on who ran it. The
 * hand-written serialiser below has no such problem: it produces the same
 * fourteen bytes everywhere, which is the entire argument for writing it.
 *
 * Build:  cc -std=c11 -Wall -Wextra packing_a_record_c.c -o /tmp/pack_c && /tmp/pack_c
 */

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

static const char *RULE =
    "------------------------------------------------------------------------";

struct order {
    uint32_t id;
    int16_t qty;
    double price;
};

static void head(int n, const char *title)
{
    printf("\n%d. %s\n%s\n\n", n, title, RULE);
}

static void show(const char *label, const unsigned char *b, size_t n, const char *note)
{
    printf("   %-32s", label);
    char hex[128];
    size_t at = 0;
    for (size_t i = 0; i < n && at + 3 < sizeof hex; i++)
        at += (size_t)snprintf(hex + at, sizeof hex - at, "%s%02x", i ? " " : "", b[i]);
    printf("%-50s %s\n", hex, note);
}

/* Big-endian by construction: shift the value, mask a byte, store it. No
 * memcpy, no cast, no union, and no dependence on this CPU's byte order --
 * arithmetic on a uint32_t means the same thing on every machine C runs on. */
static void put_u32_be(unsigned char *p, uint32_t v)
{
    p[0] = (unsigned char)(v >> 24);
    p[1] = (unsigned char)(v >> 16);
    p[2] = (unsigned char)(v >> 8);
    p[3] = (unsigned char)v;
}

static void put_i16_be(unsigned char *p, int16_t v)
{
    uint16_t u = (uint16_t)v;          /* two's complement, no sign shifting */
    p[0] = (unsigned char)(u >> 8);
    p[1] = (unsigned char)u;
}

/* A double has no shift operator, so the only portable route to its bytes is
 * memcpy -- which hands back THIS machine's order and then has to be fixed. */
static void put_f64_be(unsigned char *p, double v)
{
    unsigned char tmp[8];
    memcpy(tmp, &v, sizeof tmp);
    uint16_t probe = 1;
    unsigned char first;
    memcpy(&first, &probe, 1);
    int little = (first == 1);
    for (int i = 0; i < 8; i++)
        p[i] = little ? tmp[7 - i] : tmp[i];
}

static uint32_t get_u32_be(const unsigned char *p)
{
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16)
         | ((uint32_t)p[2] << 8) | (uint32_t)p[3];
}

int main(void)
{
    struct order r = {4711, -3, 19.5};
    const size_t sum = sizeof(uint32_t) + sizeof(int16_t) + sizeof(double);

    /* ------------------------------------------------------------ 1 */
    head(1, "THE STRUCT IS A MEMORY LAYOUT, AND IT HAS HOLES IN IT");

    printf("   struct order { uint32_t id; int16_t qty; double price; };\n\n");
    printf("   sizeof(struct order)            -- not printed: it is this\n");
    printf("   offsetof(struct order, price)      compiler and this ABI, not\n");
    printf("                                      the record. The comparisons\n");
    printf("                                      below are the portable part.\n\n");
    printf("   4 + 2 + 8, the fields alone              %zu\n", sum);
    printf("   sizeof(struct order) == that sum         %s\n",
           sizeof(struct order) == sum ? "true" : "false");
    printf("   sizeof(struct order) >  that sum         %s\n",
           sizeof(struct order) > sum ? "true" : "false");
    printf("   offsetof(price) == 6, where a file wants it   %s\n",
           offsetof(struct order, price) == 6 ? "true" : "false");
    printf("\n");
    printf("   The struct is bigger than its fields and the third field does\n");
    printf("   not start where the wire wants it. The difference is ALIGNMENT\n");
    printf("   PADDING: a double has to begin at an address divisible by its\n");
    printf("   ALIGNMENT, so the compiler inserts unnamed bytes after `qty`\n");
    printf("   until it does. You cannot see them, you did not ask for them,\n");
    printf("   and their contents are indeterminate.\n");
    printf("\n");
    printf("   That alignment is the ABI's number rather than the standard's,\n");
    printf("   and _Alignof is how you ask this machine instead of guessing.\n");
    printf("   It is not printed here for the usual reason -- but the page\n");
    printf("   carries it measured on four targets, including one where a\n");
    printf("   double aligns to four rather than eight.\n");
    printf("\n");
    printf("   This is exactly what Python's unprefixed 'Ihd' inherits -- the\n");
    printf("   `struct` module's native mode asks the C compiler these same\n");
    printf("   two questions and answers with the same padding.\n");

    /* ------------------------------------------------------------ 2 */
    head(2, "SO THE ONE-LINE WRITE IS THE BUG");

    printf("   fwrite(&r, sizeof r, 1, fp);\n\n");
    printf("   That compiles, runs, and writes a file that reads back\n");
    printf("   perfectly -- with the same program, on the same machine, built\n");
    printf("   by the same compiler. It writes:\n\n");
    printf("     * this CPU's byte order, chosen for you by the hardware\n");
    printf("     * this ABI's padding, in bytes whose values C does not define\n");
    printf("     * this compiler's field order and widths\n\n");
    printf("   None of the three is in the file, so a reader cannot check any\n");
    printf("   of them. Padding is the one worth pausing on: those bytes are\n");
    printf("   INDETERMINATE, so two records with identical fields can differ\n");
    printf("   byte for byte, which breaks memcmp, hashing and any signature\n");
    printf("   taken over the struct -- and it is why they are not printed\n");
    printf("   here. There is nothing stable to print.\n");

    /* ------------------------------------------------------------ 3 */
    head(3, "THE PORTABLE ANSWER IS TO WRITE THE BYTES YOURSELF");

    unsigned char wire[14];
    put_u32_be(wire + 0, r.id);
    put_i16_be(wire + 4, r.qty);
    put_f64_be(wire + 6, r.price);

    show("shift and mask, field by field", wire, sizeof wire, "14 bytes");
    printf("\n");
    printf("     0..4   id     >> 24, >> 16, >> 8, & 0xff\n");
    printf("     4..6   qty    cast to uint16_t first, then shift\n");
    printf("     6..14  price  memcpy, then reversed if this CPU is little\n");
    printf("\n");
    printf("   Fourteen bytes, no padding, byte order stated in the code. The\n");
    printf("   same fourteen bytes Python's struct.pack('>Ihd') and Rust's\n");
    printf("   three to_be_bytes calls produce, which is what \"agreeing on a\n");
    printf("   format\" looks like when nobody shares a library.\n");
    printf("\n");
    printf("   Two details the shifts are carrying quietly. `qty` is cast to\n");
    printf("   uint16_t before shifting, because shifting a negative signed\n");
    printf("   value right is implementation-defined and the cast is the only\n");
    printf("   way to say \"the two's complement bits, please\". And `price`\n");
    printf("   needs a memcpy because C has no shift operator for a double --\n");
    printf("   which means the float field is the one place where you have to\n");
    printf("   ask what this machine does before you can write a portable file.\n");

    /* ------------------------------------------------------------ 4 */
    head(4, "READING IT BACK, AND WHERE C WILL NOT HELP YOU");

    struct order back;
    back.id = get_u32_be(wire);
    printf("   get_u32_be(wire)            id = %u\n", back.id);
    printf("   round trips                 %s\n", back.id == r.id ? "true" : "false");
    printf("\n");
    printf("   And the mistake with no diagnostic anywhere in this file:\n\n");
    uint32_t swapped = ((uint32_t)wire[3] << 24) | ((uint32_t)wire[2] << 16)
                     | ((uint32_t)wire[1] << 8) | (uint32_t)wire[0];
    printf("     the same four bytes read the other way round   %u\n", swapped);
    printf("\n");
    printf("   Both are valid uint32_t values, so there is no error to report\n");
    printf("   and nothing to test against. C has no type that means \"a\n");
    printf("   big-endian 32-bit field\" -- Rust's from_be_bytes and Python's\n");
    printf("   '>' both name the order in the call, and C names it only in\n");
    printf("   whichever helper you remembered to write.\n");
    printf("\n");
    printf("   The name field is worse again, and this page's other half:\n");
    printf("   `char buf[10]` is ten bytes and C has no opinion at all about\n");
    printf("   what encoding they hold, so nothing here can tell you that a\n");
    printf("   strncpy landed in the middle of a UTF-8 sequence. There is no\n");
    printf("   equivalent of Rust's str::from_utf8 refusing, or of Python's\n");
    printf("   decode raising. The bytes just go out.\n");
    printf("\n");

    return 0;
}
