// Rust takes non-ASCII identifiers too -- and makes the opposite choice about
// what to do with them, which is the whole content of this page.
//
// The three lints named at the bottom are the subject here, so they are
// ALLOWED at the top: with them on, every run of this example would print
// warnings into CI forever. Their real output is on the page, in a dated fence,
// because lint wording is not stable enough to record.
#![allow(uncommon_codepoints, confusable_idents, mixed_script_confusables)]

fn bar() {
    println!("{}", "-".repeat(72));
}

fn main() {
    println!("\n1. RUST TAKES THEM TOO");
    bar();
    let żółw = 4;
    println!("   let żółw = 4;   ->   {}", żółw);
    println!();
    println!("   Stable since Rust 1.53, from the same UAX #31 rule Python");
    println!("   uses. So far the two languages agree completely.");

    println!("\n2. AND NORMALIZES THEM -- TO NFC, NOT NFKC");
    bar();
    let café = 1;              // bound with the COMPOSED spelling
    println!("   bound as   caf\\u{{e9}}       (composed, 4 chars)");
    println!("   read as    cafe\\u{{301}}     (e + COMBINING ACUTE U+0301, 5 chars)");
    println!("   value      {}", café);
    println!();
    println!("   Two spellings, one binding -- the compiler put the source");
    println!("   into NFC before it looked at any name. This is the half");
    println!("   Rust and Python agree on, and it is the uncontroversial");
    println!("   half: the two spellings really are the same character.");

    println!("\n3. BUT THE LIGATURE IS A DIFFERENT NAME");
    bar();
    let ﬁle = 1;
    let file = 2;
    println!("   let ﬁle  = 1;   (U+FB01 LATIN SMALL LIGATURE FI)   ->  {}", ﬁle);
    println!("   let file = 2;   (f, i as ASCII)                    ->  {}", file);
    println!("   they are the same binding                          ->  {}", ﬁle == file);
    println!();
    println!("   Python binds ONE variable here, because NFKC expands the");
    println!("   ligature. Rust binds TWO, because NFC does not. Neither is");
    println!("   wrong; they answer different questions about what a name is.");

    println!("\n4. AND SO IS THE CYRILLIC LOOK-ALIKE");
    bar();
    let а = "cyrillic";
    let a = "latin";
    println!("   let а = ...;   (U+0430)   ->  {}", а);
    println!("   let a = ...;   (U+0061)   ->  {}", a);
    println!("   same binding              ->  {}", а == a);
    println!();
    println!("   Here the two languages AGREE on the outcome -- two");
    println!("   variables -- and disagree completely about what to do next.");

    println!("\n5. THE DIFFERENCE THAT MATTERS IS THE WARNING");
    bar();
    println!("   With the allow() at the top of this file removed, rustc");
    println!("   emits three lints, all warn-by-default:");
    println!();
    println!("      uncommon_codepoints        the ligature is Not_NFKC");
    println!("      confusable_idents          two names that look alike");
    println!("      mixed_script_confusables   a script used only for these");
    println!();
    println!("   That is UTS #39 machinery, shipped in a compiler, on by");
    println!("   default. Python has no equivalent and cannot easily have");
    println!("   one -- having normalized the ligature away, there are no");
    println!("   longer two names for it to compare.");
    println!();
    println!("   So the trade runs: NORMALIZE and the surprise is silent,");
    println!("   PRESERVE and you owe the user a warning. Rust chose to owe");
    println!("   the warning. It is the same argument IDNA2008 had with");
    println!("   IDNA2003 about a domain name, one floor down.");
}
