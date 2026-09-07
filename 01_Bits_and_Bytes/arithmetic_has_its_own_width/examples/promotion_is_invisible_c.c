/* The C view: the variable is eight bits wide and the arithmetic is not.
 *
 * Build and run:  cc -std=c11 -Wall -Wextra promotion_is_invisible_c.c -o /tmp/pi && /tmp/pi
 */
#include <limits.h>
#include <stdio.h>

int main(void) {
    unsigned char c = 255;
    signed char s = -5;

    printf("1. THE STORE IS EIGHT BITS. THE OPERATOR IS NOT.\n");
    printf("   sizeof(c)               = %-3zu the variable really is one byte\n", sizeof(c));
    printf("   sizeof(c << 2)          = %-3zu the EXPRESSION is an int, %zu bytes wide here\n",
           sizeof(c << 2), sizeof(int));
    printf("   Before any arithmetic operator runs, C converts every operand narrower\n");
    printf("   than int to int. It is called integer promotion, it is not optional, and\n");
    printf("   there is no syntax for it -- nothing in `c << 2` says a widening happened.\n\n");

    printf("2. WHICH IS WHY A SHIFT CAN OUTGROW THE VARIABLE IT CAME FROM\n");
    unsigned char d = c << 2;
    printf("   c                       = %-6u 1111 1111\n", c);
    printf("   c << 2                  = %-6d <- what the operator produced, as an int\n", c << 2);
    printf("   (unsigned char)(c << 2) = %-6u <- what survives the store back into a byte\n", d);
    printf("   Both numbers are right. The narrowing happens at the STORE, not in the\n");
    printf("   shift, so ((c << 2) > 255) is %d while d is only %u.\n\n", (c << 2) > 255, d);

    printf("3. TWO OPERATORS THAT LOOK LIKE DIVISION AND DISAGREE ON NEGATIVES\n");
    printf("   s                       = %-6d 1111 1011 read as a signed byte\n", s);
    printf("   s >> 3                  = %-6d <- shifts round DOWN, toward minus infinity\n", s >> 3);
    printf("   s / 8                   = %-6d <- division rounds toward ZERO (C99 onward)\n", s / 8);
    printf("   s %% 8                   = %-6d <- and the remainder carries the sign of s\n", s % 8);

    int differ = 0;
    for (int x = -8; x <= -1; x++) {
        if ((x >> 3) != (x / 8)) {
            differ++;
        }
    }
    int agree_unsigned = 0;
    for (unsigned x = 0; x < 256u; x++) {
        if ((x >> 3) == (x / 8u)) {
            agree_unsigned++;
        }
    }
    printf("   Counted, not assumed: over the 8 values -8..-1 the two answers differ on\n");
    printf("   %d of them, and over the 256 values 0..255 they agree on %d. So `>> 3` is a\n",
           differ, agree_unsigned);
    printf("   fast `/ 8` exactly while the value cannot be negative.\n\n");

    printf("4. ONE BYTE, TWO READINGS -- AND ONLY ONE DIRECTION IS PROMISED\n");
    signed char neg = -100;
    printf("   signed char neg         = %-6d the value stored\n", neg);
    printf("   (unsigned char)neg      = %-6u the same eight bits, read unsigned\n",
           (unsigned)(unsigned char)neg);
    printf("   Converting TO an unsigned type is defined by the standard: reduce modulo\n");
    printf("   2^%d and you are done. Going back the other way -- putting 156 into a signed\n", CHAR_BIT);
    printf("   char -- is implementation-defined in C11, so this program does not do it.\n\n");

    printf("5. THE ONE THING THIS PROGRAM DELIBERATELY WILL NOT PRINT\n");
    printf("   Whether plain `char` is signed. C leaves that to the implementation, so it\n");
    printf("   is a property of the machine and the compiler rather than of the language,\n");
    printf("   and an answer key here could only be right on the machine that recorded it.\n");
    printf("   Ask your own compiler with one line -- printf(\"%%d\\n\", CHAR_MIN); -- and\n");
    printf("   until you have, write `signed char` or `unsigned char` whenever the byte is\n");
    printf("   a NUMBER. Plain `char` is for text, where the question does not arise.\n");
    return 0;
}
