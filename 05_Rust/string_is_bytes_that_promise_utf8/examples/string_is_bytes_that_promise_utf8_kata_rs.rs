// Answer key: five things Rust refuses, and the one promise behind all of them.
fn main() {
    let s = String::from("café");

    println!("THE VALUE");
    println!("   {:?}", s);
    println!("   len()          {}   <- BYTES, and the method says so", s.len());
    println!("   chars().count() {}   <- code points", s.chars().count());
    println!("   as_bytes()     {:02x?}", s.as_bytes());
    println!();

    println!("1. THERE IS NO s[0]");
    println!("   Index<usize> is not implemented for String, at all. A byte");
    println!("   index may land inside a character, so the operation that");
    println!("   looks free in every other language is the one Rust removed.");
    println!();

    println!("2. SLICING IS ALLOWED, AND CHECKED AT RUNTIME");
    println!("   &s[0..3] = {:?}", &s[0..3]);
    // Silence the panic hook: the message goes to stderr, which no answer
    // key records, and an unsilenced abort message is noise in the log.
    let hook = std::panic::take_hook();
    std::panic::set_hook(Box::new(|_| {}));
    let bad = std::panic::catch_unwind(|| {
        let s = String::from("café");
        s[0..4].to_string()
    });
    std::panic::set_hook(hook);
    println!("   &s[0..4] -> {}", if bad.is_err() { "PANIC: byte index 4 is not a char boundary" } else { "ok" });
    println!("   The promise cannot be checked at compile time here, so it is");
    println!("   checked at run time -- and breaking it aborts rather than");
    println!("   producing half a character.");
    println!();

    println!("3. THE PROMISE IS WHAT MAKES from_utf8 RETURN A Result");
    let good = String::from_utf8(vec![0x63, 0x61, 0x66, 0xc3, 0xa9]);
    let bad2 = String::from_utf8(vec![0x63, 0x61, 0x66, 0xe9]);
    println!("   from_utf8(63 61 66 c3 a9) -> {:?}", good);
    println!("   from_utf8(63 61 66 e9)    -> {}", if bad2.is_err() { "Err(FromUtf8Error)" } else { "Ok" });
    println!("   Vec<u8> is bytes. String is bytes PLUS a proof. The only way");
    println!("   across is a function that can fail, or one that repairs:");
    println!("   from_utf8_lossy(63 61 66 e9) = {:?}",
             String::from_utf8_lossy(&[0x63, 0x61, 0x66, 0xe9]));
    println!();

    println!("4. WHY &str AND String ARE TWO TYPES");
    println!("   String owns its bytes and can grow; &str is a borrowed view of");
    println!("   bytes that already keep the promise. Take &str in a signature");
    println!("   and every caller can pass either; return String when you made");
    println!("   the bytes yourself. That is the whole convention.");
    println!();

    println!("5. WHAT THE PROMISE BUYS");
    println!("   chars() cannot fail. Every &str is displayable. No function");
    println!("   anywhere has to ask 'is this valid?' again, because the only");
    println!("   door into the type already asked. Python checks at the same");
    println!("   boundary and then forgets; Rust puts the answer in the type.");

    assert_eq!(s.len(), 5);
    assert_eq!(s.chars().count(), 4);
}
