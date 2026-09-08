// Answer key: five signatures, and the one the compiler will not let you write.
fn count_chars(s: &str) -> usize { s.chars().count() }
fn shout(s: &str) -> String { s.to_uppercase() }

fn main() {
    let owned = String::from("café");
    println!("1. TAKE &str, RETURN String");
    println!("   count_chars(&owned)  {}", count_chars(&owned));
    println!("   count_chars(\"café\")  {}", count_chars("café"));
    println!("   shout(&owned)        {:?}", shout(&owned));
    println!("   A &str parameter accepts a String, a literal and a slice, so");
    println!("   it costs the caller nothing. Taking String forces every caller");
    println!("   to give up ownership or clone -- the single most common");
    println!("   avoidable allocation in a Rust codebase.");
    println!();

    println!("2. NEVER INVENT A BYTE INDEX");
    println!("   forbidden:  &s[0..4]      -- 4 may be inside a character");
    let first3: String = owned.chars().take(3).collect();
    println!("   correct:    chars().take(3) -> {:?}", first3);
    println!("   char_indices() gives you real boundaries when you need offsets:");
    for (i, c) in owned.char_indices() {
        print!("   ({}, {:?})", i, c);
    }
    println!();
    println!("   Note the gap: the last index is 3 and the string is 5 bytes,");
    println!("   because é occupies 3 and 4. There is no boundary at 4.");
    println!();

    println!("3. ASK FOR THE LENGTH YOU MEANT");
    println!("   len()            {}   bytes -- for buffers and field limits", owned.len());
    println!("   chars().count()  {}   code points -- for most 'how long is this'", owned.chars().count());
    println!("   Neither is 'characters' as a person means it; that needs a");
    println!("   grapheme crate, and needing one is the honest answer.");
    println!();

    println!("4. LET &[u8] MEAN 'NOT CHECKED YET'");
    // Built through an iterator rather than written as a literal slice: rustc
    // lints a from_utf8 call on an invalid LITERAL, and a warning in an
    // answer key is noise about the example rather than about the lesson.
    let owned_bytes: Vec<u8> = [0x63u8, 0x61, 0x66, 0xe9].iter().copied().collect();
    let raw: &[u8] = &owned_bytes;
    match std::str::from_utf8(raw) {
        Ok(s) => println!("   from_utf8 ok: {:?}", s),
        Err(e) => println!("   from_utf8 err at byte {} -- and the type says so", e.valid_up_to()),
    }
    println!("   {:?}", String::from_utf8_lossy(raw));
    println!("   A function taking &[u8] is saying 'these may not be text'. A");
    println!("   function taking &str is saying 'somebody already checked'. The");
    println!("   boundary between them is the only place a decode belongs.");
    println!();

    println!("5. THE SIGNATURE THE COMPILER REFUSES");
    println!("   fn first(s: &str) -> char {{ s[0] }}   // does not compile");
    println!("   String has no Index<usize>, so the O(1) indexing every other");
    println!("   language offers is simply absent -- not slow, absent. That is");
    println!("   the UTF-8-everywhere rules with the compiler holding them:");
    println!("   the operation that would silently split a character is not");
    println!("   available to be written by accident.");

    assert_eq!(owned.len(), 5);
    assert_eq!(count_chars(&owned), 4);
}
