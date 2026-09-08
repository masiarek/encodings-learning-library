// Kata answers for Slicing by byte.
//
// Build & run:  rustc --edition 2024 slicing_by_byte_kata_rs.rs && ./slicing_by_byte_kata_rs

use std::panic;

const S: &str = "żółw";

fn truncate_to_bytes(s: &str, budget: usize) -> &str {
    if budget >= s.len() {
        return s;
    }
    let mut end = budget;
    while !s.is_char_boundary(end) {
        end -= 1;
    }
    &s[..end]
}

fn main() {
    println!("THE STRING {S:?}");
    println!("   chars    {}", S.chars().map(|c| format!("{c}")).collect::<Vec<_>>().join("  "));
    println!("   bytes    {}", S.as_bytes().iter().map(|b| format!("{b:02x}")).collect::<Vec<_>>().join(" "));
    println!("   len()    {} bytes for {} characters", S.len(), S.chars().count());
    println!("   Three of the four letters cost two bytes; only 'w' is one.");
    println!();

    println!("WHERE YOU MAY CUT");
    let good: Vec<usize> = (0..=S.len()).filter(|i| S.is_char_boundary(*i)).collect();
    let bad: Vec<usize> = (0..=S.len()).filter(|i| !S.is_char_boundary(*i)).collect();
    println!("   boundaries      {good:?}");
    println!("   not boundaries  {bad:?}");
    println!("   Five legal indices for a seven-byte string. The odd ones below 6 are all");
    println!("   inside a two-byte letter, and 7 is the end, which always counts.");
    println!();

    println!("THE FOUR EXPRESSIONS");
    panic::set_hook(Box::new(|_| {}));
    let attempts: [(&str, Box<dyn Fn() -> String + std::panic::UnwindSafe>); 4] = [
        ("&s[0..2]", Box::new(|| S[0..2].to_string())),
        ("s.get(0..2)", Box::new(|| format!("{:?}", S.get(0..2)))),
        ("&s[..s.len()]", Box::new(|| S[..S.len()].to_string())),
        ("&s[..s.len() - 1]", Box::new(|| S[..S.len() - 1].to_string())),
    ];
    for (label, f) in attempts {
        match panic::catch_unwind(f) {
            Ok(v) => println!("   {label:<20} {v}"),
            Err(_) => println!("   {label:<20} PANICS"),
        }
    }
    let _ = panic::take_hook();
    println!();
    println!("   &s[0..2]           byte 2 is the START of 'ó', so this is legal — it is");
    println!("                      the whole of 'ż' and nothing else. Legal by luck: the");
    println!("                      same expression on \"café\" would have been fine too, and");
    println!("                      on a string starting with a three-byte character it is not.");
    println!("   s.get(0..2)        the same answer, wrapped in Some. On a bad index it is");
    println!("                      None instead of a panic, which is the entire difference.");
    println!("   &s[..s.len()]      always legal, for every string. The end of a string is a");
    println!("                      boundary by definition, so this can never fail.");
    println!("   &s[..s.len() - 1]  works HERE and is the one that can fail. 'w' is one");
    println!("                      byte, so len()-1 lands on a boundary; on a string ending");
    println!("                      in any non-ASCII character the same expression panics.");
    println!();

    println!("AND THAT LAST PAIR IS THE LESSON");
    println!("   len()-1 is {} here, and is_char_boundary({}) is {}.", S.len() - 1, S.len() - 1, S.is_char_boundary(S.len() - 1));
    println!("   \"żółw\" ends in 'w', a one-byte character, so cutting one byte off the end");
    println!("   removes exactly one character and is safe. Reverse the word and it is not:");
    let rev: String = S.chars().rev().collect();
    println!("     {rev:?}  len {}  boundary at len-1? {}", rev.len(), rev.is_char_boundary(rev.len() - 1));
    println!("   Same expression, same four letters, different answer — because the question");
    println!("   was never about the string's length. It was about its LAST CHARACTER, and");
    println!("   the expression does not mention that.");
    println!();

    println!("FIVE BYTES OF FIELD");
    let cut = truncate_to_bytes(S, 5);
    println!("   truncate_to_bytes({S:?}, 5) = {cut:?}   {} bytes, {} characters", cut.len(), cut.chars().count());
    println!("   Two characters survive, in four bytes. Byte 5 is inside 'ł', so the honest");
    println!("   answer is to stop at 4 and leave the field one byte short.");
    println!();
    println!("   The naive &s[..5] does not get an answer at all:");
    panic::set_hook(Box::new(|_| {}));
    match panic::catch_unwind(|| S[..5].to_string()) {
        Ok(v) => println!("     &s[..5] = {v:?}"),
        Err(_) => println!("     &s[..5] PANICS — byte 5 is not a char boundary"),
    }
    let _ = panic::take_hook();
    println!("   And the version people actually write, in a language with no such check,");
    println!("   is the byte slice — which does not panic and does not work either:");
    let raw = &S.as_bytes()[..5];
    println!("     &s.as_bytes()[..5]  = {}   valid UTF-8? {}",
        raw.iter().map(|b| format!("{b:02x}")).collect::<Vec<_>>().join(" "),
        std::str::from_utf8(raw).is_ok());
    println!("   Five bytes written to a five-byte field, no error anywhere, and the file is");
    println!("   no longer text. That is the bug this page exists to make loud.");
}
