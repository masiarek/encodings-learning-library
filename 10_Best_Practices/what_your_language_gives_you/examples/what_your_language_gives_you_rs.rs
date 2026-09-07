//! Rust's answers to the same four questions, and the one it answers best.
//!
//! Rust's standard library ships **no** legacy encodings at all -- a fact that
//! reads as a gap until you see what it buys on question four. This program
//! counts what `std` has, shows why Latin-1 looks like an exception and is not,
//! and ends on the thing no amount of library code gives you: a string type
//! that cannot hold bytes that are not text.
//!
//! Everything here is arithmetic over a table written out in the source. No
//! Unicode property is looked up, so the output does not depend on which
//! Unicode version this rustc was built against.
//!
//! Build and run:  rustc --edition 2024 what_your_language_gives_you_rs.rs
//!                 ./what_your_language_gives_you_rs

// windows-1250, bytes 0x80..=0xFF -> code point. 0xFFFD marks the five byte
// values the table leaves undefined. This is the kind of data `std` has none of.
const CP1250_HIGH: [u32; 128] = [
    0x20AC, 0xFFFD, 0x201A, 0xFFFD, 0x201E, 0x2026, 0x2020, 0x2021,
    0xFFFD, 0x2030, 0x0160, 0x2039, 0x015A, 0x0164, 0x017D, 0x0179,
    0xFFFD, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2013, 0x2014,
    0xFFFD, 0x2122, 0x0161, 0x203A, 0x015B, 0x0165, 0x017E, 0x017A,
    0x00A0, 0x02C7, 0x02D8, 0x0141, 0x00A4, 0x0104, 0x00A6, 0x00A7,
    0x00A8, 0x00A9, 0x015E, 0x00AB, 0x00AC, 0x00AD, 0x00AE, 0x017B,
    0x00B0, 0x00B1, 0x02DB, 0x0142, 0x00B4, 0x00B5, 0x00B6, 0x00B7,
    0x00B8, 0x0105, 0x015F, 0x00BB, 0x013D, 0x02DD, 0x013E, 0x017C,
    0x0154, 0x00C1, 0x00C2, 0x0102, 0x00C4, 0x0139, 0x0106, 0x00C7,
    0x010C, 0x00C9, 0x0118, 0x00CB, 0x011A, 0x00CD, 0x00CE, 0x010E,
    0x0110, 0x0143, 0x0147, 0x00D3, 0x00D4, 0x0150, 0x00D6, 0x00D7,
    0x0158, 0x016E, 0x00DA, 0x0170, 0x00DC, 0x00DD, 0x0162, 0x00DF,
    0x0155, 0x00E1, 0x00E2, 0x0103, 0x00E4, 0x013A, 0x0107, 0x00E7,
    0x010D, 0x00E9, 0x0119, 0x00EB, 0x011B, 0x00ED, 0x00EE, 0x010F,
    0x0111, 0x0144, 0x0148, 0x00F3, 0x00F4, 0x0151, 0x00F6, 0x00F7,
    0x0159, 0x016F, 0x00FA, 0x0171, 0x00FC, 0x00FD, 0x0163, 0x02D9,
];

fn say(title: &str) {
    println!("\n{title}\n{}", "-".repeat(72));
}

fn main() {
    say("1. QUESTION ONE: WHAT ENCODINGS DOES `std` KNOW?");

    println!("   the encodings `std` can decode, in full:");
    println!("       UTF-8    str::from_utf8 / _mut, String::from_utf8, _lossy");
    println!("       UTF-16   String::from_utf16, _lossy, and since rustc 1.98");
    println!("                the explicit-endian from_utf16le / from_utf16be");
    println!(
        "
   Two encodings, and both of them are Unicode. There is no third,
   and no registry to ask for one: no `from_latin1`, no lookup by
   name, no `windows-1250` anywhere in the standard library. Where
   Python answered question one with thirty-odd tables in both
   directions, Rust answers it with none, and points at a crate."
    );

    say("2. LATIN-1 LOOKS LIKE AN EXCEPTION, AND IS ARITHMETIC");

    // `u8 as char` is the only integer-to-char cast the language allows.
    let all_256_round_trip = (0u8..=255).all(|b| (b as char) as u32 == b as u32);
    println!("   `b as char` is the only integer-to-char cast Rust permits,");
    println!("   and for all 256 byte values it agrees with Latin-1: {all_256_round_trip}");
    println!("       0x41 -> {:?}      0xE9 -> {:?}", 0x41u8 as char, 0xE9u8 as char);
    println!(
        "
   That one-liner is a complete, correct Latin-1 decoder, and it is
   not a feature anybody implemented. Latin-1's 256 characters ARE
   code points 0 to 255, by construction, so the decode is the
   identity function and a cast is enough."
    );

    say("3. windows-1250 IS NOT ARITHMETIC, AND THAT IS THE GENERAL CASE");

    let mut agree = 0usize;
    let mut undefined = 0usize;
    for i in 0..128usize {
        let byte = 0x80 + i as u32;
        match CP1250_HIGH[i] {
            0xFFFD => undefined += 1,
            cp if cp == byte => agree += 1,
            _ => {}
        }
    }
    println!("   of the 256 byte values, how many `b as char` gets right");
    println!("   for windows-1250:                     {}", 128 + agree);
    println!("   bytes the table maps somewhere else:  {}", 128 - agree - undefined);
    println!("   bytes the table leaves undefined:     {undefined}");
    println!();
    let z_dot = char::from_u32(CP1250_HIGH[0xBF - 0x80]).unwrap();
    println!("       byte 0xBF   `as char` says {:?}   U+{:04X}", 0xBFu8 as char, 0xBF);
    println!("       byte 0xBF   the table says {z_dot:?}   U+{:04X}", z_dot as u32);
    println!(
        "
   The lower half is ASCII and free. The upper half is a decision
   somebody wrote down decades ago, and there is nothing in it to
   compute -- which is what a legacy encoding mostly IS.

   Latin-1 is not the easy case in a family of easy cases. It is the
   only case. Of the twenty-eight single-byte tables in the browser
   standard, NONE is the identity map, and Latin-1 itself is not
   among them -- the standard gives its name to windows-1252 instead.
   The closest is ISO-8859-15, which agrees on 120 of the 128 high
   bytes and puts a euro sign in one of the other eight. Shipping
   these is shipping data, which is why they live in a crate."
    );

    say("4. QUESTION FOUR: CAN THE TYPE SYSTEM STOP YOU?");

    let bad = vec![b'c', b'a', b'f', 0xE9, b'.', b't', b'x', b't'];
    match std::str::from_utf8(&bad) {
        Ok(s) => println!("   unexpectedly decoded: {s:?}"),
        Err(e) => println!(
            "   str::from_utf8 on the same caf-0xE9-.txt bytes: Err, valid up to byte {}",
            e.valid_up_to()
        ),
    }
    let lossy = String::from_utf8_lossy(&bad);
    println!("   String::from_utf8_lossy:                        {lossy:?}");
    println!("   the 0xE9 is gone, replaced:                     {}", !lossy.contains('\u{E9}'));
    println!(
        "   the only signal that anything changed:          {}",
        if matches!(lossy, std::borrow::Cow::Owned(_)) { "Cow::Owned" } else { "none" }
    );
    println!(
        "
   Rust's answer here is different in kind, and it is a refusal: in
   safe Rust there is no way to put those bytes in a `String` at all.
   Python's `str` will hold them under `surrogateescape`, which is a
   different and equally deliberate answer -- one language made the
   invalid state unrepresentable, the other made it representable on
   purpose so that a filename survives.

   Both are right. They are answers to different questions, which is
   the whole point of asking four."
    );
}
