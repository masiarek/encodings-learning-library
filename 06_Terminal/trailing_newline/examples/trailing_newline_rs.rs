//! The last byte of a text file, from Rust.
//!
//! Rust makes the terminator-versus-separator distinction visible in the type
//! system's own vocabulary: `lines()` is the terminator reading and `split('\n')`
//! is the separator reading, and they are different iterators on purpose.

fn main() {
    let no_nl = "ż";
    let with_nl = "ż\n";

    println!("1. TWO STRINGS, ONE CHARACTER, ONE BYTE APART");
    for (name, s) in [("no_nl  ", no_nl), ("with_nl", with_nl)] {
        let hex: Vec<String> = s.bytes().map(|b| format!("{b:02x}")).collect();
        println!("   {name}  {:<12}  {} bytes", hex.join(" "), s.len());
    }
    println!("   len() is bytes, always — the letter is two of them.");

    println!();
    println!("2. lines() CANNOT SEE THE DIFFERENCE");
    println!("   {:<8}.lines() -> {:?}", "\"ż\"", no_nl.lines().collect::<Vec<_>>());
    println!("   {:<8}.lines() -> {:?}", "\"ż\\n\"", with_nl.lines().collect::<Vec<_>>());
    println!("   Identical, and the docs say so: the final line ending is optional.");
    println!("   lines() also strips a \\r before the \\n, so it reads CRLF files too.");

    println!();
    println!("3. split('\\n') CAN");
    println!("   {:<8}.split() -> {:?}", "\"ż\"", no_nl.split('\n').collect::<Vec<_>>());
    println!("   {:<8}.split() -> {:?}", "\"ż\\n\"", with_nl.split('\n').collect::<Vec<_>>());
    println!("   The trailing newline opens an empty last field. Same split as Python's.");

    println!();
    println!("4. THE TEST TO WRITE");
    for (name, s) in [("no_nl  ", no_nl), ("with_nl", with_nl)] {
        println!("   {name}  ends_with('\\n') -> {:<5}  lines().count() -> {}",
                 s.ends_with('\n'), s.lines().count());
    }
    println!("   Ask the bytes. Both strings have one line.");

    println!();
    println!("5. WRITING IT");
    println!("   println!(..)  adds it");
    println!("   print!(..)    does not — and stdout is line-buffered when it is a");
    println!("                 terminal, so a print! with no newline may sit in the");
    println!("                 buffer looking like nothing happened until you flush.");
    print!("   this line was printed with print! and an explicit \\n\n");
}
