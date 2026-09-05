/* The C view: a string is bytes up to the first NUL, and nothing else.
 *
 * Build & run:  cc -std=c11 -Wall -Wextra control_characters_c.c -o nul && ./nul
 */
#include <stdio.h>
#include <string.h>

int main(void) {
    char s[] = "ab\0cd";           /* six bytes: a b NUL c d NUL */

    printf("1. THE ARRAY AND THE STRING ARE DIFFERENT LENGTHS\n");
    printf("   sizeof(s) = %zu   (the compiler stored six bytes, terminator included)\n", sizeof s);
    printf("   strlen(s) = %zu   (strlen counted until the first NUL)\n", strlen(s));
    printf("   printf(\"%%s\") -> \"%s\"   (so does printf)\n", s);
    printf("\n");

    printf("2. THE BYTES ARE ALL STILL THERE\n   ");
    for (size_t i = 0; i < sizeof s; i++) {
        printf("%s%02x", i ? " " : "", (unsigned char)s[i]);
    }
    printf("\n   Only the C string functions stop early. The memory does not.\n\n");

    printf("3. A 'char' IS A BYTE, NOT A CHARACTER\n");
    const char *cafe = "caf\xc3\xa9";
    printf("   \"caf\\xc3\\xa9\" has strlen %zu: C counts bytes and has never heard of \xc3\xa9\n", strlen(cafe));
    printf("\n");

    printf("4. THE CONTROL CHARACTERS C CAN SPELL\n");
    const char *names[] = {"\\a", "\\b", "\\t", "\\n", "\\v", "\\f", "\\r", "\\e (not standard)", "\\0"};
    const char values[] = {'\a', '\b', '\t', '\n', '\v', '\f', '\r', 27, '\0'};
    for (size_t i = 0; i < sizeof values; i++) {
        printf("   %-18s = %2d = 0x%02X\n", names[i], values[i], values[i]);
    }
    return 0;
}
