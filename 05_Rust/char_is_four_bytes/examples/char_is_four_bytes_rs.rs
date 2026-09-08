// A `char` is one Unicode scalar value, always four bytes wide in memory, and
// one to four bytes wide inside a String. Both numbers are right; they answer
// different questions.
//
// Build & run:  rustc --edition 2024 char_is_four_bytes_rs.rs && ./char_is_four_bytes_rs

/// The cast, in code-point order. Glyphs go LAST on every row: `😀` is two
/// terminal columns wide and `{:<n}` pads by chars, so a glyph in the middle of
/// a row would bend the columns to its right.
const CAST: [(char, &str); 4] = [('A', "LATIN CAPITAL LETTER A"), ('é', "LATIN SMALL LETTER E WITH ACUTE"), ('€', "EURO SIGN"), ('😀', "GRINNING FACE")];

fn main() {
    println!("1. FOUR NUMBERS FOR ONE CHARACTER, AND ONLY ONE OF THEM IS FOUR");
    println!("   {:<9} {:>8} {:>9} {:>9} {:>10}   glyph", "code pt", "as u32", "size_of", "len_utf8", "len_utf16");
    for (c, _) in CAST {
        println!(
            "   U+{:<7X} {:>8} {:>9} {:>9} {:>10}   {c}",
            c as u32,
            c as u32,
            size_of::<char>(),
            c.len_utf8(),
            c.len_utf16(),
        );
    }
    println!("   size_of is a property of the TYPE and never moves. len_utf8 is a property");
    println!("   of the VALUE, and it is what the same character costs inside a String.");
    println!();

    println!("2. SO THE SAME FOUR CHARACTERS HAVE TWO SIZES");
    let as_chars: [char; 4] = [CAST[0].0, CAST[1].0, CAST[2].0, CAST[3].0];
    let as_string: String = as_chars.iter().collect();
    println!("   [char; 4]   {:>2} bytes   4 x 4, whatever is in it", size_of_val(&as_chars));
    println!("   String      {:>2} bytes   1 + 2 + 3 + 4, because each one was encoded", as_string.len());
    println!("               {}", as_string.as_bytes().iter().map(|b| format!("{b:02X}")).collect::<Vec<_>>().join(" "));
    println!("               and that String is {as_string:?}");
    println!("   A char is a fixed-width box. UTF-8 is a variable-width encoding. Putting a");
    println!("   char into a String encodes it; taking one out decodes it. Neither is free.");
    println!();

    println!("3. THREE WALKS OVER ONE STRING");
    let s = "café";
    println!("   {s:?}   len() = {} bytes", s.len());
    println!("   bytes()        {}", s.bytes().map(|b| format!("{b:02X}")).collect::<Vec<_>>().join(" "));
    println!("   chars()        {}", s.chars().map(|c| format!("{c}")).collect::<Vec<_>>().join("  "));
    println!("   char_indices() {}", s.char_indices().map(|(i, c)| format!("{i}:{c}")).collect::<Vec<_>>().join("  "));
    println!("   Five bytes, four chars. char_indices() gives the BYTE offset of each char,");
    println!("   which is the only index a String will accept — and why the last one is 3,");
    println!("   not 4. Counting characters to build an index is the bug this prevents.");
    println!();

    println!("4. THE ONE THING A char CANNOT HOLD");
    for n in [0xD7FFu32, 0xD800, 0xDFFF, 0xE000, 0x10FFFF, 0x110000] {
        let got = char::from_u32(n);
        let verdict = match got {
            Some(_) => "Some  — a scalar value",
            None => "None  — not a scalar value",
        };
        println!("   char::from_u32(0x{n:06X})   {verdict}");
    }
    println!("   The hole from D800 to DFFF is the surrogate range, which exists so UTF-16");
    println!("   can reach past U+FFFF. A char is a Unicode SCALAR VALUE, and that phrase");
    println!("   means exactly 'code point, minus those two thousand and forty-eight'.");
    println!("   char::MAX = {:?}, so the widest value is 21 bits — which is why 4 bytes,", char::MAX);
    println!("   not 3: there is no 24-bit integer to be addressed on any machine here.");
    println!();

    println!("5. AND THE HOLE PAYS FOR ITSELF");
    println!("   size_of::<char>()          {}", size_of::<char>());
    println!("   size_of::<Option<char>>()  {}   <- the None is stored INSIDE the gap", size_of::<Option<char>>());
    println!("   size_of::<u32>()           {}", size_of::<u32>());
    println!("   size_of::<Option<u32>>()   {}   <- a u32 has no spare bit patterns", size_of::<Option<u32>>());
    println!("   Every u32 from 0 to 0xFFFFFFFF is a valid u32, so Option needs a separate");
    println!("   byte to say which case it is (and then 3 more for alignment). A char has");
    println!("   over four billion invalid patterns, so None can be one of them, for free.");
    println!("   The restriction that makes char awkward is the same one that makes it cheap.");
    println!();

    println!("6. WRITING ONE, AND READING IT BACK");
    let grin = '\u{1F600}';
    println!("   '\\u{{1F600}}'            is {grin}, and {} == {}", grin as u32, 0x1F600);
    println!("   .escape_unicode()      {}", grin.escape_unicode());
    println!("   'é'.escape_unicode()   {}", 'é'.escape_unicode());
    println!("   b'A'                   {}   <- a byte literal: u8, not char, no Unicode at all", b'A');
    println!("   'A' as u32             {}   <- and here the two agree, which is why ASCII hides this", 'A' as u32);
    println!();
    println!("   And one cast that compiles and lies. `as u8` on a char TRUNCATES:");
    for (c, _) in CAST {
        println!("     U+{:<6X} as u32 = {:<6} as u8 = {:<3} {}", c as u32, c as u32, c as u8,
            if c as u32 == c as u8 as u32 { "same value" } else { "TRUNCATED" });
    }
    println!("   Only `as u32` is lossless. u8 keeps the low eight bits and says nothing.");
    println!();

    println!("7. NONE OF THESE COUNTS WHAT A PERSON CALLS A CHARACTER");
    // The last column is COUNTED BY A HUMAN, and labelled as such: std has no
    // method for it, so a number computed here would be a guess wearing a cast.
    println!("   {:<15} {:>7} {:>9} {:>10} {:>10}", "written as", "bytes", "chars", "utf-16", "graphemes");
    println!("   {:<15} {:>7} {:>9} {:>10} {:>10}", "", "len()", ".count()", "len_utf16", "(by eye)");
    for (label, s, by_eye) in [("\"café\"", "café", 4), ("\"cafe\\u{301}\"", "cafe\u{301}", 4), ("\"\\u{1F600}\"", "😀", 1)] {
        println!(
            "   {label:<15} {:>7} {:>9} {:>10} {:>10}",
            s.len(),
            s.chars().count(),
            s.chars().map(|c| c.len_utf16()).sum::<usize>(),
            by_eye,
        );
    }
    println!("   Rows 1 and 2 are the same word. One is written with a combining acute, and");
    println!("   chars() counts it as a character of its own — correctly, because it IS a");
    println!("   scalar value. What a cursor moves over is a GRAPHEME CLUSTER, and there is");
    println!("   no method for it in std: the tables move with every Unicode release, so the");
    println!("   unicode-segmentation crate carries them and the standard library does not.");
}
