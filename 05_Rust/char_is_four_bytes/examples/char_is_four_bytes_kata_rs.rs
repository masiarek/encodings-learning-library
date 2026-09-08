// Kata answers for `char` is four bytes.
//
// Build & run:  rustc --edition 2024 char_is_four_bytes_kata_rs.rs && ./char_is_four_bytes_kata_rs

fn main() {
    let c = '€';
    println!("THE FOUR NUMBERS FOR '{c}'");
    println!("   size_of::<char>()   {}   the TYPE's width. Never moves, for any value.", size_of::<char>());
    println!("   '€'.len_utf8()      {}   what it costs inside a String", c.len_utf8());
    println!("   '€'.len_utf16()     {}   what it costs in Java, JavaScript or ABAP", c.len_utf16());
    println!("   '€' as u32          {}   the code point itself, U+{:04X}", c as u32, c as u32);
    println!();

    println!("AND THE FIFTH, WHICH IS THE FIRST AGAIN");
    println!("   size_of::<Option<char>>()   {}", size_of::<Option<char>>());
    println!("   Not 5, and not 8. A char has more invalid bit patterns than valid ones —");
    println!("   everything above 0x10FFFF, and the surrogate block — so None is stored as");
    println!("   one of them. The tag needs no room of its own. Compare a type with no");
    println!("   spare patterns: size_of::<Option<u32>>() = {}, which is 4 for the value,", size_of::<Option<u32>>());
    println!("   1 for the tag and 3 for alignment.");
    println!();

    let s = "€1";
    println!("THE STRING \"{s}\"");
    println!("   len()             {}   BYTES: 3 for the euro sign, 1 for the digit", s.len());
    println!("   chars().count()   {}   scalar values", s.chars().count());
    println!("   char_indices()    {}", s.char_indices().map(|(i, c)| format!("{i}:{c}")).collect::<Vec<_>>().join("  "));
    println!("   The second character starts at byte 3, not byte 1. Every index Rust will");
    println!("   accept is in the first column; every index a person counts is in the second.");
    println!();

    println!("THE COLUMN THAT SAYS \"2 CHARACTERS\"");
    println!("   Almost always len(), the byte count — {} here, so \"€1\" does not fit.", s.len());
    println!("   Oracle VARCHAR2(2) defaults to BYTE semantics and needs CHAR spelled out;");
    println!("   MySQL's utf8mb3 sizes in characters but stores three bytes each; a COBOL or");
    println!("   ABAP fixed field is bytes on disk whatever the program calls it. The rule");
    println!("   that survives all of them: a width with no unit is a byte count.");
    println!();

    println!("char::from_u32(0xDC00)");
    println!("   {:?}", char::from_u32(0xDC00));
    println!("   0xDC00 is a LOW SURROGATE. Surrogates are the 2,048 code points UTF-16");
    println!("   reserves to encode everything above U+FFFF as a pair, so they never stand");
    println!("   for a character alone. A char is a Unicode scalar value, which is defined");
    println!("   as a code point that is not one of these — so the constructor cannot");
    println!("   return one, and returns None rather than a value you would have to check.");
    println!("   For comparison, the code point either side of the block:");
    for n in [0xD7FFu32, 0xDC00, 0xE000] {
        println!("     0x{n:04X}  {:?}", char::from_u32(n));
    }
}
