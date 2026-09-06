// Rust knows even less about scripts than Python does -- and the little it
// knows is in the compiler, not in `std`.
//
// So this program does the honest thing: it asks `char` every question it has,
// shows that none of them separates a Latin letter from its Cyrillic twin, and
// then hand-rolls the block ranges to show why that is not the easy fix it
// looks like. Block boundaries never move once assigned, so the table below is
// a literal that cannot rot -- the same licence RFC 3454's table B.1 has on
// the previous page.

/// A few Unicode blocks, transcribed. Note how many rows LATIN needs.
const BLOCKS: [(u32, u32, &str); 8] = [
    (0x0041, 0x005A, "LATIN (basic, upper)"),
    (0x0061, 0x007A, "LATIN (basic, lower)"),
    (0x00C0, 0x024F, "LATIN (1 Supplement + Extended-A/B)"),
    (0x0370, 0x03FF, "GREEK"),
    (0x0400, 0x04FF, "CYRILLIC"),
    (0x0500, 0x052F, "CYRILLIC (Supplement)"),
    (0x2C60, 0x2C7F, "LATIN (Extended-C)"),
    (0xA720, 0xA7FF, "LATIN (Extended-D)"),
];

fn block_of(c: char) -> &'static str {
    let n = c as u32;
    for (lo, hi, name) in BLOCKS {
        if n >= lo && n <= hi {
            return name;
        }
    }
    "not in the transcribed table"
}

fn bar() {
    println!("{}", "-".repeat(72));
}

fn main() {
    let lat = 'a';
    let cyr = 'а'; // U+0430

    println!("\n1. TWO chars THAT std CANNOT TELL APART");
    bar();
    println!("   {:<22} {:<12} {}", "", "latin a", "cyrillic a");
    println!("   {:<22} U+{:04X}       U+{:04X}", "code point", lat as u32, cyr as u32);
    println!("   {:<22} {:<12} {}", "len_utf8()", lat.len_utf8(), cyr.len_utf8());
    println!("   {:<22} {:<12} {}", "is_alphabetic()", lat.is_alphabetic(), cyr.is_alphabetic());
    println!("   {:<22} {:<12} {}", "is_lowercase()", lat.is_lowercase(), cyr.is_lowercase());
    println!("   {:<22} {:<12} {}", "is_ascii()", lat.is_ascii(), cyr.is_ascii());
    println!("   {:<22} {:<12} {}", "is_alphanumeric()", lat.is_alphanumeric(), cyr.is_alphanumeric());
    println!();
    println!("   is_ascii() is the only one that splits them, and it is not a");
    println!("   script test -- it would put 'é' on the Cyrillic side. `char`");
    println!("   has no script method, no block method, and no name method:");
    println!("   Rust ships the classification tables and not the names.");

    println!("\n2. BLOCKS, TRANSCRIBED -- AND WHY IT IS NOT THE EASY FIX");
    bar();
    for c in ['a', 'A', 'é', 'ż', 'а', 'ο', 'ᶜ', '0', '.'] {
        println!("   U+{:04X}  {}  {}", c as u32, c, block_of(c));
    }
    println!();
    println!("   Read the LATIN rows in the table above: the alphabet needs");
    println!("   FIVE ranges and this transcription still misses several, so");
    println!("   'ᶜ' comes back unknown though it is plainly a Latin letter.");
    println!("   And the last two rows are in no script at all -- a digit and");
    println!("   a full stop belong to every alphabet at once, which is why");
    println!("   any real mixed-script check has to special-case them.");
    println!();
    println!("   So a block table is easy to write, easy to verify, and");
    println!("   wrong in two directions at once: incomplete for one script,");
    println!("   and silent about the characters that have none.");

    println!("\n3. WHERE RUST DOES KNOW -- AND IT IS THE COMPILER");
    bar();
    let zolw = 3; // an ASCII binding, for contrast
    let żółw = 4; // a non-ASCII one: legal since 1.53
    println!("   let żółw = 4;  compiles       {}", żółw == 4);
    println!("   let zolw = 3;  also compiles  {}", zolw == 3);
    println!();
    println!("   rustc accepts non-ASCII identifiers and then does exactly");
    println!("   what this page argues for: it declines to FOLD them, and");
    println!("   warns instead. Three lints ship for it --");
    println!("      uncommon_codepoints");
    println!("      confusable_idents");
    println!("      mixed_script_confusables");
    println!("   -- which is the UTS #39 machinery, in a compiler, aimed at");
    println!("   the one place where two names that look identical do real");
    println!("   damage: a diff nobody can read.");
    println!();
    println!("   Note where that leaves the two languages. Python NORMALIZES");
    println!("   identifiers and so cannot warn about them; Rust preserves");
    println!("   them and so must. Same trade as IDNA2003 against IDNA2008,");
    println!("   one floor down.");
}
