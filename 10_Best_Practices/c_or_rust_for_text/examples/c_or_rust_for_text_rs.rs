// Rust for text: bytes, a promise, and no locale anywhere.
//
// Rust has two types where C has one. &[u8] is bytes; &str is bytes that
// have been checked to be UTF-8; and the check is a function whose error
// says where it stopped and whether more bytes would have helped. Nothing
// here asks a locale, because there is no locale to ask -- the answers come
// from the type and from the Unicode tables compiled into std. This is the
// Rust half of the page; the C half asks the same questions of a char*.
//
// Run:  rustc --edition 2024 c_or_rust_for_text_rs.rs -o /tmp/cort_rs && /tmp/cort_rs

use std::ffi::OsStr;
use std::os::unix::ffi::OsStrExt;

fn hex(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02x}")).collect::<Vec<_>>().join(" ")
}

fn main() {
    let bytes: &[u8] = b"caf\xc3\xa9"; // café, spelled as the bytes it is

    println!("1. TWO TYPES, AND THE BOUNDARY BETWEEN THEM IS A FUNCTION");
    println!("   let bytes: &[u8] = b\"caf\\xc3\\xa9\";   len {}   {}", bytes.len(), hex(bytes));
    let s: &str = std::str::from_utf8(bytes).expect("these five bytes are UTF-8");
    println!(
        "   let s: &str = from_utf8(bytes)?         len {}   chars {}   {:?}",
        s.len(),
        s.chars().count(),
        s
    );
    println!(
        "   bytes[3] = {}   s.as_bytes()[3] = {}   (a u8 is 0..=255; no sign to argue about)",
        bytes[3],
        s.as_bytes()[3]
    );
    println!("   Same five bytes. One value knows nothing about them; the other exists");
    println!("   only because from_utf8 said yes, and every method on it -- chars(),");
    println!("   to_uppercase(), slicing -- is written on that promise.");

    println!("\n2. DISCOVERY IS IN THE ERROR, FROM THE FIRST CALL");
    let inputs: [&[u8]; 4] = [b"caf\xc3", b"caf\xc3(", b"a\xc0\xaf", b"a\xed\xa0\x80"];
    for input in inputs {
        match std::str::from_utf8(input) {
            Ok(ok) => println!("   {:<14} Ok({ok:?})", hex(input)),
            Err(e) => println!(
                "   {:<14} Err: valid_up_to {}  error_len {:?}   lossy {:?}",
                hex(input),
                e.valid_up_to(),
                e.error_len(),
                String::from_utf8_lossy(input)
            ),
        }
    }
    println!("   error_len None is a prefix that ran out -- keep it, read more. Some(n)");
    println!("   is n bytes that will never be text -- skip them. C's mbrtowc says the");
    println!("   same two things as (size_t)-2 and (size_t)-1, one character per call,");
    println!("   after a locale has been set and an mbstate_t kept between calls.");

    println!("\n3. NO LOCALE ANYWHERE");
    for w in ["café", "straße", "Łódź"] {
        let up = w.to_uppercase();
        println!(
            "   {w:?}.to_uppercase() = {up:?}   bytes {} -> {}   chars {} -> {}",
            w.len(),
            up.len(),
            w.chars().count(),
            up.chars().count()
        );
    }
    println!("   The tables are in std, so they are the same on every machine that ran");
    println!("   this binary. Nothing was set first, so nothing elsewhere in the process");
    println!("   can have set it differently. It is also why there is no");
    println!("   to_uppercase_in(locale): the Turkish dotless i is a crate's job.");

    println!("\n4. BYTES THAT ARE NOT TEXT HAVE A TYPE TOO");
    let name = OsStr::from_bytes(b"caf\xe9.txt"); // Latin-1 é, as a Unix filename may be
    println!("   OsStr::from_bytes(b\"caf\\xe9.txt\") = {name:?}   len {}", name.len());
    println!("   .to_str()          = {:?}", name.to_str());
    println!("   .to_string_lossy() = {:?}", name.to_string_lossy());
    println!("   The byte survives, the &str never comes into being, and the lossy view");
    println!("   says so with U+FFFD. That is C's char* with the decision made visible:");
    println!("   the place where bytes become text is a method call you can read.");

    println!("\n5. WHAT std WILL NOT DO, AND SAYS SO");
    println!(
        "   String::from_utf16(&[0x63, 0x61, 0x66, 0xE9]) = {:?}",
        String::from_utf16(&[0x63, 0x61, 0x66, 0xE9])
    );
    println!(
        "   char::from_u32(0xD800)                       = {:?}   (a surrogate is not a char)",
        char::from_u32(0xD800)
    );
    println!("   Latin-1 in: (b as char) is the whole decoder, because Latin-1 IS code");
    println!("   points 0..=255. Windows-1250, Shift_JIS, an EBCDIC page: no table in std");
    println!("   at all -- encoding_rs is the crate, and iconv is a C library you bind.");
    println!("   Graphemes, collation, locale-aware case: crates too, and they are good");
    println!("   precisely because std declined to guess.");
}
