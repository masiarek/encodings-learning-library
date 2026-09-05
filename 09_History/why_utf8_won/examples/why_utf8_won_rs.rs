// UTF-8's structure, held as a type invariant.
//
// Python can ask "are these bytes valid UTF-8?"; Rust makes it the difference
// between two types. `&[u8]` is bytes; `&str` is bytes that have already been
// checked. The check is the only door between them, and this program walks
// through it — and gets turned away — six times.
//
// Run:  rustc --edition 2024 why_utf8_won_rs.rs -o /tmp/utf8won && /tmp/utf8won

fn bar() {
    println!("{}", "-".repeat(72));
}

fn head(n: u8, title: &str) {
    println!();
    println!("{n}. {title}");
    bar();
}

fn try_decode(label: &str, bytes: &[u8]) {
    match std::str::from_utf8(bytes) {
        Ok(s) => println!("   {label:34} -> Ok({s:?})"),
        Err(e) => {
            let len = match e.error_len() {
                Some(n) => format!("{n} byte(s) rejected there"),
                None => "ended mid-character".to_string(),
            };
            println!(
                "   {label:34} -> Err: valid up to byte {}, {len}",
                e.valid_up_to()
            );
        }
    }
}

fn main() {
    head(1, "A &str IS BYTES PLUS A PROMISE");
    let s = "Łódź";
    println!("   {s:?}");
    println!("   s.len()          = {}   <- BYTES, not characters", s.len());
    println!("   s.chars().count()= {}   <- characters", s.chars().count());
    println!("   s.as_bytes()     = {:02x?}", s.as_bytes());
    println!("   The promise is the whole difference between &str and &[u8]:");
    println!("   every &str in a running program is already valid UTF-8, because");
    println!("   there is no way to make one that is not without saying `unsafe`.");

    head(2, "THE DOOR: from_utf8 CHECKS, AND SAYS WHERE IT FAILED");
    try_decode("b\"caf\\xc3\\xa9\" (real UTF-8)", b"caf\xc3\xa9");
    try_decode("b\"caf\\xe9 au lait\" (Latin-1)", b"caf\xe9 au lait");
    try_decode("b\"caf\\xc3\" (truncated)", b"caf\xc3");
    println!("   `valid_up_to` is the byte offset where the file stops making");
    println!("   sense — which is how a tool can report the LINE of the problem");
    println!("   instead of 'this file is not UTF-8, good luck'.");

    head(3, "TWO REJECTIONS THAT ARE SECURITY, NOT PEDANTRY");
    try_decode("c0 80  (overlong NUL)", &[0xC0, 0x80]);
    try_decode("2f              (a real slash)", &[0x2F]);
    try_decode("c0 af  (overlong slash)", &[0xC0, 0xAF]);
    println!("   Every code point has exactly ONE valid UTF-8 spelling. A decoder");
    println!("   that accepts the padded spellings lets `c0 af` slip a '/' past a");
    println!("   filter that was looking for 2f — which is how directory-traversal");
    println!("   attacks worked in 2001. Rust's `from_utf8` refuses them.");
    println!();
    try_decode("ed a0 80  (a lone surrogate)", &[0xED, 0xA0, 0x80]);
    println!("   Surrogates are UTF-16's plumbing, not characters. UTF-8 has no");
    println!("   room for them, so text that came from a careless UTF-16 system");
    println!("   is caught here rather than three systems later.");

    head(4, "WHEN YOU CANNOT REFUSE: from_utf8_lossy");
    let dirty = b"Sales report: caf\xe9 \xff totals";
    println!("   bytes  {:02x?}", &dirty[..24]);
    println!("   lossy  {:?}", String::from_utf8_lossy(dirty));
    println!("   Each bad byte becomes U+FFFD, the replacement character. Use it");
    println!("   for a log line a human will read; never for data you will write");
    println!("   back out, because the original bytes are gone for good.");

    head(5, "SELF-SYNCHRONISING, IN THE TYPE SYSTEM");
    let s = "Łódź";
    print!("   char_indices():");
    for (i, c) in s.char_indices() {
        print!(" {i}:{c}");
    }
    println!();
    print!("   is_char_boundary:");
    for i in 0..=s.len() {
        print!(" {i}:{}", if s.is_char_boundary(i) { "Y" } else { "n" });
    }
    println!();
    println!("   Slicing at a boundary works; slicing inside a character does not.");
    println!("   `get` asks instead of panicking, which is how to do it in a tool:");
    for range in [0..2, 0..1, 2..4] {
        println!("     s.get({:?}) = {:?}", range.clone(), s.get(range));
    }

    head(6, "AND ASCII STILL COSTS ONE BYTE");
    for t in ["hello", "Łódź", "日本語"] {
        println!(
            "   bytes {:2}   chars {:2}   ascii-only {:5}   {t:?}",
            t.len(),
            t.chars().count(),
            t.is_ascii()
        );
    }
    println!("   `is_ascii()` is a fast path a great deal of real code takes: if a");
    println!("   string is ASCII, byte indexing and character indexing are the same");
    println!("   thing, and UTF-8 is what makes that shortcut safe to check for.");
}
