// Writing a number in source, in Rust: the same four bases, and a leading zero
// that means nothing at all.
//
// Run:  rustc --edition 2024 writing_the_literal_rs.rs -o /tmp/lit && /tmp/lit

fn main() {
    println!("1. THE SAME FOUR BASES, THE SAME PREFIXES");
    println!("   0b1100_0011 = {}      0o303 = {}      195 = {}      0xC3 = {}",
             0b1100_0011, 0o303, 195, 0xC3);
    println!("   Rust took Python's prefixes unchanged, so this half transfers with no edits.");
    println!();

    println!("2. THE UNDERSCORE IS LOOSER HERE: ANYWHERE, ANY NUMBER OF TIMES");
    println!("   0xC3_A9    = {}   grouped by byte, the reading that matters", 0xC3_A9);
    println!("   0x_C3_A9_  = {}   legal too -- leading and trailing, and Rust does not mind", 0x_C3_A9_);
    println!("   1_000_000  = {}", 1_000_000);
    println!();

    println!("3. AND A LITERAL MAY NAME ITS OWN TYPE, WHICH PYTHON HAS NO WAY TO DO");
    println!("   0xC3u8     = {}     a u8, so the width is in the literal", 0xC3u8);
    println!("   0xC3_A9u16 = {}   a u16, and the compiler checks it fits", 0xC3_A9u16);
    println!("   That suffix is the whole difference in one character: in Python 195 is an");
    println!("   integer of no particular width, and in Rust you have said which byte count");
    println!("   you meant before the program runs.");
    println!();

    println!("4. AND THE LEADING ZERO? IT IS JUST A ZERO");
    println!("   0755 = {}    decimal, not octal -- Rust has no leading-zero rule at all", 0755);
    println!("   One seven-character literal, and each language on this page gives it a");
    println!("   different reading -- each from its own program, above and below. The");
    println!("   prefix exists so that sentence can stop being true of new code.");
}
