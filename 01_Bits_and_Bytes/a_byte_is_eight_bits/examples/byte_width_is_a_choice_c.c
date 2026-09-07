/* The C view: the language still refuses to promise that a byte is eight bits.
 *
 * Build and run:  cc -std=c11 -Wall -Wextra byte_width_is_a_choice_c.c -o /tmp/bw && /tmp/bw
 */
#include <limits.h>
#include <stdio.h>

int main(void) {
    printf("1. C HAS A NAME FOR THE NUMBER EVERYONE THINKS IS SETTLED\n");
    printf("   CHAR_BIT   = %-6d <limits.h> -- the bits in a char, on THIS machine\n", CHAR_BIT);
    printf("   UCHAR_MAX  = %-6u so an unsigned char holds 0..%u\n", (unsigned)UCHAR_MAX, (unsigned)UCHAR_MAX);
    printf("   The C standard requires CHAR_BIT >= 8 and no more. POSIX requires exactly 8,\n");
    printf("   which is why every machine you will meet says 8 -- by a promise the operating\n");
    printf("   system makes, not one the language does.\n\n");

    printf("2. WHICH IS WHY sizeof(char) IS 1 BY DEFINITION, NOT BY MEASUREMENT\n");
    printf("   sizeof(char)  = %-3zu <- 1 always, on every machine C has ever targeted\n", sizeof(char));
    printf("   sizeof(int)   = %-3zu <- and this one is measured, in units of char\n", sizeof(int));
    printf("   On a machine with 9-bit chars, sizeof(char) would still be 1 and a char would\n");
    printf("   still hold 9 bits. sizeof counts CHARS, and a char is whatever this machine's\n");
    printf("   byte is. That is the whole reason the network standards say 'octet' instead.\n\n");

    printf("3. THE BITS IN AN int, WORKED OUT RATHER THAN ASSUMED\n");
    printf("   sizeof(int) * CHAR_BIT = %zu * %d = %zu bits\n", sizeof(int), CHAR_BIT, sizeof(int) * CHAR_BIT);
    printf("   That multiplication is the portable spelling. Writing 32 is a guess that has\n");
    printf("   been right for a long time on the machines that are left.\n");
    return 0;
}
