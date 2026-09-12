/* Where "010 means eight" actually comes from: one argument to strtol.
 *
 * `base` 0 means "read the prefix and decide" -- 0x is hex, a leading 0 is
 * octal, anything else decimal -- and it is the mode `xxd -s`, `od -j` and
 * bash's printf are all built on. `base` 10 means "these are decimal digits,
 * whatever they look like". Neither is wrong; they are different questions,
 * and each one mangles a string the other reads correctly, silently, into a
 * number that looks perfectly reasonable.
 *
 * Run:  cc -std=c11 -Wall -Wextra base_zero_reads_the_prefix_c.c -o /tmp/bz && /tmp/bz
 */

#include <stdio.h>
#include <stdlib.h>

static void row(const char *input, int base) {
    char *end;
    long v = strtol(input, &end, base);
    int consumed = (int)(end - input);
    printf("   %-8s %-6d %12ld %9d   %s\n", input, base, v, consumed,
           *end ? end : "(nothing)");
}

int main(void) {
    printf("1. ONE ARGUMENT, AND IT IS THE WHOLE CONVENTION\n");
    printf("   %-8s %-6s %12s %9s   %s\n", "input", "base", "value", "consumed", "left over");
    const char *inputs[] = {"010", "0x10", "10", "09", "0"};
    for (size_t i = 0; i < sizeof inputs / sizeof *inputs; i++) row(inputs[i], 0);
    printf("\n");
    for (size_t i = 0; i < sizeof inputs / sizeof *inputs; i++) row(inputs[i], 10);

    printf("\n2. READ THE TWO BLOCKS AGAINST EACH OTHER\n");
    printf("   010   is 8 under base 0 and 10 under base 10. Same digits, same\n");
    printf("         function, one argument apart -- and no error either way.\n");
    printf("   09    is where base 0 gives up: the leading zero said octal, 9 is\n");
    printf("         not an octal digit, so it returns 0 and leaves \"9\" behind.\n");
    printf("   0x10  is where base 10 gives up, the same way round: it reads the\n");
    printf("         0, stops at the x, and returns 0 with \"x10\" left over.\n");

    printf("\n3. AND BOTH GIVE-UPS RETURN 0, WHICH IS ALSO A CORRECT ANSWER\n");
    printf("   The last row is a real \"0\", parsed in full. Nothing in the return\n");
    printf("   value separates it from the two failures above -- only `consumed`\n");
    printf("   does, and a caller that ignores the endptr cannot tell them apart.\n");
    printf("   That is the same claim the rest of this library keeps making about\n");
    printf("   text: the value is not the whole result, and the base is not in the\n");
    printf("   digits. Here it is one int argument, chosen by whoever wrote the\n");
    printf("   tool, in a call you never see.\n");
    return 0;
}
