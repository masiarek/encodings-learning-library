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
    println!("   print!(..)    does not — and Rust wraps stdout in a LineWriter, so");
    println!("                 the flush happens ON the newline. Text from a bare");
    println!("                 print! sits in the buffer looking like nothing ran.");
    println!("   This does NOT depend on being a terminal, which is the part worth");
    println!("   knowing: C and Python switch to block buffering when stdout is a");
    println!("   pipe, and lose a completed line if they die unflushed. Rust line-");
    println!("   buffers either way. The page has the measurement.");
    print!("   this line was printed with print! and an explicit \\n\n");

    println!();
    println!("6. WHICH CHARACTERS END A LINE — AND WHY THIS IS NOT splitlines()");
    let breaks = [
        ("LF     000a", "a\nb"),
        ("CRLF   000d000a", "a\r\nb"),
        ("CR     000d", "a\rb"),
        ("VT     000b", "a\u{0b}b"),
        ("FF     000c", "a\u{0c}b"),
        ("FS     001c", "a\u{1c}b"),
        ("NEL    0085", "a\u{85}b"),
        ("LS     2028", "a\u{2028}b"),
        ("PS     2029", "a\u{2029}b"),
    ];
    for (name, s) in breaks {
        let n = s.lines().count();
        println!("   {name:<16} lines() -> {n} line(s){}", if n == 1 { "   (not a break)" } else { "" });
    }
    println!("   Only LF ends a line, with an optional CR allowed in front of it.");
    println!("   Python's splitlines() breaks on ALL NINE of these. So lines() and");
    println!("   splitlines() are not the same reading: they agree on LF and CRLF");
    println!("   and part company on the other seven: four ASCII control codes");
    println!("   (CR, VT, FF, FS) and three that are not ASCII at all (NEL, LS, PS).");
}
