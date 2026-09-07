/* The NUL byte means "the string stops here" to C and nothing at all to a
 * length-prefixed format. Hand the same bytes to both and they disagree about
 * what name you asked for.
 *
 * cc -std=c11 -Wall -Wextra
 */
#include <stdio.h>
#include <string.h>

static void hex(const char *label, const char *p, size_t n)
{
    printf("   %-14s", label);
    for (size_t i = 0; i < n; i++)
        printf("%02X ", (unsigned char)p[i]);
    printf("\n");
}

int main(void)
{
    /* One field, as it travels: the whole thing is what was signed. */
    static const char name[] = "www.paypal.com\0.thoughtcrime.org";
    const size_t stored = sizeof name - 1;   /* minus the compiler's own NUL */

    puts("1. ONE FIELD, TWO LENGTHS");
    printf("   bytes stored   %zu   (the length the format carries)\n", stored);
    printf("   strlen(name)   %zu   (the length C computes by searching)\n", strlen(name));
    hex("first 20", name, 20);
    printf("   The 0x00 at offset 14 is a byte like any other to whoever counted\n");
    printf("   to %zu. To strlen it is the end of the world.\n\n", stored);

    puts("2. WHAT EACH PARTY CHECKS, AND BOTH ARE RIGHT");
    printf("   the issuer walks all %zu bytes and asks: does this end in\n", stored);
    printf("   \".thoughtcrime.org\", a domain the requester controls?\n");
    printf("     answer: %s\n",
           memcmp(name + stored - 17, ".thoughtcrime.org", 17) == 0 ? "yes -- issue it" : "no");
    printf("   the client reads the same field with str* and asks: is this\n");
    printf("   \"www.paypal.com\"?\n");
    printf("     answer: %s\n",
           strcmp(name, "www.paypal.com") == 0 ? "yes -- trust it" : "no");
    printf("   Neither party has a bug. They are reading two different strings\n");
    printf("   out of one buffer, because they disagree about where it ends.\n\n");

    puts("3. THE SAME SHAPE, WITHOUT CERTIFICATES");
    {
        static const char upload[] = "/etc/passwd\0.jpg";
        const size_t whole = sizeof upload - 1;
        printf("   the field      \"/etc/passwd\\0.jpg\"   (%zu bytes)\n", whole);
        printf("   the CHECK is length-prefixed: does it end in \".jpg\"?  %s\n",
               memcmp(upload + whole - 4, ".jpg", 4) == 0 ? "yes -- allowed" : "no");
        printf("   the OPEN is NUL-terminated:   what file is that?      \"%s\"\n", upload);
        printf("   That is the PHP null-byte bug, and note which way round it is:\n");
        printf("   the strict reader is the one that gets FOOLED, because it reads\n");
        printf("   past the end of the name the weak reader will actually use.\n");
        printf("   PHP stopped accepting a NUL in a path argument in 5.3.4.\n");
    }
    printf("   Anywhere a length-prefixed world meets a NUL-terminated one --\n");
    printf("   a database column, a protocol field, a filename from a zip, an\n");
    printf("   environment variable, a Java String handed to a C library --\n");
    printf("   the same two readings are available and somebody picks each.\n\n");

    puts("4. WHAT ACTUALLY FIXES IT");
    printf("   not: search harder for the NUL\n");
    printf("   but: REJECT the field. A NUL inside a domain name, a filename or\n");
    printf("        a header is not data that needs handling -- it is a claim\n");
    printf("        that two readings exist, and the only safe answer is no.\n");
    printf("   memchr(name, 0, stored) != NULL  ->  %s\n",
           memchr(name, 0, stored) != NULL ? "contains an embedded NUL: refuse" : "clean");
    return 0;
}
