/* The C view: where the leading-zero rule came from, and what C still lacks.
 *
 * Build and run:  cc -std=c11 -Wall -Wextra writing_the_literal_c.c -o /tmp/litc && /tmp/litc
 */
#include <stdio.h>

int main(void) {
    printf("1. IN C, A LEADING ZERO *IS* THE OCTAL PREFIX\n");
    printf("   0755 = %d    <- octal. The prefix is a single '0', and it is easy to miss.\n", 0755);
    printf("    755 = %d    <- decimal. One character apart, 262 apart in value.\n", 755);
    printf("   0x1ED = %d   <- the same 493 in hex, where the base is spelled out loud.\n", 0x1ED);
    printf("   This is the rule Python 3 removed and Rust never adopted, and it is why\n");
    printf("   chmod(path, 0755) is correct while chmod(path, 755) compiles and is not.\n\n");

    printf("2. WHICH MAKES THE ZERO THE ONLY PREFIX YOU CANNOT SEE\n");
    printf("   0x / 0b / 0o are two characters and one of them is a letter. C's octal\n");
    printf("   prefix is one character that is also a digit, in a language where a\n");
    printf("   zero-padded number is a completely ordinary thing to write.\n\n");

    printf("3. AND C11 HAS NO BINARY LITERAL AT ALL\n");
    printf("   0b1100_0011 is not C. Neither is the underscore.\n");
    printf("   C++14 added both first, and picked the APOSTROPHE as its separator --\n");
    printf("   0b1100'0011 -- because '_' was already taken by user-defined literals.\n");
    printf("   C23 then matched C++, nine years later. Same idea, a third spelling.\n");
    return 0;
}
