/* The C view: an escape that is not a string feature at all.
 *
 * C calls `\uXXXX` a UNIVERSAL CHARACTER NAME, and the name is the point.
 * It is part of the source character set, translated in phase 1 of
 * translation, long before anything knows it is inside a string. Two
 * consequences no other language on this page has: a UCN works in an
 * IDENTIFIER, and C refuses to let you write one for an ASCII character.
 *
 * Build: cc -std=c11 -Wall -Wextra writing_a_code_point_c.c
 */

#include <stdio.h>
#include <string.h>

/* A UCN in an identifier. This is one variable, spelled two ways: the
 * declaration escapes the letter, the uses below do not have to. */
static int caf\u00e9 = 7;

static void row(const char *what, const char *s)
{
    size_t n = strlen(s);
    printf("   %-22s %2zu   ", what, n);
    for (size_t i = 0; i < n; i++)
        printf("%s%02x", i ? " " : "", (unsigned char)s[i]);
    printf("\n");
}

int main(void)
{
    const char *bar = "------------------------------------------------------------------------";

    printf("\n1. A UCN NAMES A CODE POINT; \\x NAMES A BYTE\n%s\n", bar);
    printf("   %-22s %s   %s\n", "literal", "n", "bytes");
    row("\"\\u00e9\"", "\u00e9");
    row("\"\\xc3\\xa9\"", "\xc3\xa9");
    row("\"\\xe9\"", "\xe9");
    printf("\n");
    printf("   The first two are the same two bytes and got there by different\n");
    printf("   routes. \\u00e9 names code point U+00E9 and lets the COMPILER\n");
    printf("   encode it, in whatever the execution character set is -- UTF-8\n");
    printf("   for clang and gcc today. \\xc3\\xa9 names those two bytes directly.\n");
    printf("   \\xe9 is one byte and is not the same character at all: it is what\n");
    printf("   Latin-1 would have used, sitting in a UTF-8 string where it is\n");
    printf("   not valid.\n");

    printf("\n2. THE ESCAPE IS WIDER THAN THE STRING IT IS IN\n%s\n", bar);
    printf("   caf\\u00e9 = %d\n", caf\u00e9);
    printf("\n");
    printf("   That is a UCN in an IDENTIFIER, declared with the escape and\n");
    printf("   used with it too. C translates universal character names in\n");
    printf("   phase 1, before tokenising, so by the time anything asks what a\n");
    printf("   string literal contains the escape is long gone. Python and Rust\n");
    printf("   both handle their escapes inside the string literal, and neither\n");
    printf("   lets you spell an identifier that way.\n");

    printf("\n3. AND C IS THE ONE THAT REFUSES TO ESCAPE ASCII\n%s\n", bar);
    printf("   These three compile, because $ @ and ` are the named exceptions:\n");
    row("\"\\u0024\\u0040\\u0060\"", "\u0024\u0040\u0060");
    printf("\n");
    printf("   This one does not compile at all:\n");
    printf("       const char *a = \"\\u0041\";   /* the letter A */\n");
    printf("\n");
    printf("   C11 6.4.3 forbids a UCN below U+00A0 except those three, and\n");
    printf("   forbids the surrogates D800-DFFF. The reason is the phase it\n");
    printf("   runs in: if \\u0022 became a quotation mark before tokenising,\n");
    printf("   an escape could close a string literal, and a comment could end\n");
    printf("   somewhere the reader cannot see. The rule exists so that the\n");
    printf("   text a compiler tokenises is the text a person read.\n");
    printf("\n");
    printf("   Which is the same worry as the invisible-character section of\n");
    printf("   this lesson, answered in 1999 by a standards committee, in the\n");
    printf("   only language here whose escape runs early enough to need it.\n");

    return 0;
}
