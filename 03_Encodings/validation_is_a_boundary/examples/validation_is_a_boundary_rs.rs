// Where the UTF-8 check happens in Rust, and what the type remembers afterwards.
//
// Build & run:  rustc --edition 2024 validation_is_a_boundary_rs.rs -o /tmp/vb && /tmp/vb

/// One byte as the slide draws it: 1110.0010
fn bits(b: u8) -> String {
    format!("{:04b}.{:04b}", b >> 4, b & 0x0F)
}

fn hexed(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect::<Vec<_>>().join(" ")
}

fn main() {
    println!("1. THE THREE SEQUENCES FROM THE SLIDE, DECODED");
    for (n, raw) in [&b"\x7d"[..], &b"\xc2\xa9"[..], &b"\xe2\x89\xa0"[..]].iter().enumerate() {
        let text = std::str::from_utf8(raw).unwrap(); // the check happens HERE, and only here
        let drawn = raw.iter().map(|&b| bits(b)).collect::<Vec<_>>().join(" ");
        let c = text.chars().next().unwrap();
        println!(
            "   {}: {drawn:<35} U+{:04X}: {:<15} ({text})",
            n + 1,
            c as u32,
            raw.iter().map(|b| format!("0x{b:02X}")).collect::<Vec<_>>().join(" "),
        );
    }
    println!("   Same three sequences, same bits. UTF-8 is UTF-8; only the checking differs.");
    println!();

    println!("2. SIX WAYS TO BE INVALID, AND WHAT Utf8Error KNOWS");
    let bad: [(&[u8], &str); 6] = [
        (b"\x89", "lone continuation byte"),
        (b"\xe2\x89", "truncated 3-byte sequence"),
        (b"\xc0\xaf", "overlong '/' - two bytes for U+002F"),
        (b"\xe0\x80\xaf", "overlong '/' - the three-byte way"),
        (b"\xed\xa0\x80", "UTF-16 surrogate U+D800"),
        (b"\xf5\x80\x80\x80", "above U+10FFFF"),
    ];
    for (raw, why) in bad {
        let e = std::str::from_utf8(raw).unwrap_err();
        println!(
            "   {:<12} valid_up_to={}  error_len={:<7} {why}",
            hexed(raw),
            e.valid_up_to(),
            format!("{:?}", e.error_len()),
        );
    }
    println!("   error_len = Some(n): definitely wrong, skip n bytes and resynchronise.");
    println!("   error_len = None:    the bytes ran out mid-sequence - a valid PREFIX, not an error yet.");
    println!();

    println!("3. WHY THAT None MATTERS: THE SAME BYTES, ONE BYTE LATER");
    let mut buf: Vec<u8> = vec![0xE2, 0x89];
    println!("   {:<12} -> {:?}", hexed(&buf), std::str::from_utf8(&buf).map_err(|e| e.error_len()));
    buf.push(0xA0);
    println!("   {:<12} -> {:?}", hexed(&buf), std::str::from_utf8(&buf).map(|s| s.to_string()));
    println!("   A reader on a socket keeps the tail and waits. A reader that saw Some(n) throws it away.");
    println!();

    println!("4. PAST THE BOUNDARY, THE TYPE REMEMBERS - SO NOTHING CHECKS AGAIN");
    let s: &str = std::str::from_utf8(b"caf\xc3\xa9 \xe2\x89\xa0").unwrap();
    println!("   s                    = {s:?}");
    println!("   s.len()              = {}   (bytes - it is still a byte buffer)", s.len());
    println!("   s.chars().count()    = {}   (a full decode, but no validation)", s.chars().count());
    println!("   s.as_bytes()         = [{}]", hexed(s.as_bytes()));
    println!("   `&str` MEANS valid UTF-8. chars() bottoms out in an unsafe fn whose safety comment");
    println!("   reads \"bytes must produce a valid UTF-8-like string\" - it trusts the type and skips");
    println!("   every range check. That saved scan is what the invariant buys.");
    println!();

    println!("5. AND A char CANNOT HOLD WHAT UTF-8 CANNOT ENCODE");
    println!("   size_of::<char>()        = {}   (a Unicode scalar value, not a code unit)", size_of::<char>());
    println!("   char::from_u32(0xD800)   = {:?}   <- the surrogate Python built happily", char::from_u32(0xD800));
    println!("   char::from_u32(0x110000) = {:?}", char::from_u32(0x110000));
    println!("   char::from_u32(0x10FFFF) = {:?}", char::from_u32(0x10FFFF));
    println!("   The gap Python leaves between decode and encode does not exist here: there is no");
    println!("   value of type char that encode_utf8 could fail on. It is not checked, it is unrepresentable.");
    println!();

    println!("6. WHEN YOU WANT THE BYTES ANYWAY: lossy, AND THE unsafe DOOR");
    for (raw, _) in bad {
        let lossy = String::from_utf8_lossy(raw);
        println!(
            "   {:<12} lossy -> {:<10} {} replacement char(s)",
            hexed(raw),
            format!("{lossy:?}"),
            lossy.chars().filter(|&c| c == '\u{FFFD}').count(),
        );
    }
    println!("   How many U+FFFD you get is error_len, applied repeatedly - the Unicode 'maximal subpart' rule.");
    let owned = String::from_utf8(vec![0xE2, 0x89]);
    println!("   String::from_utf8(vec![E2,89]).unwrap_err().into_bytes() = {:?}",
             owned.unwrap_err().into_bytes());
    println!("   The failed conversion hands the bytes back rather than dropping them.");
    println!("   And str::from_utf8_unchecked is the same conversion with the check removed - `unsafe`,");
    println!("   because a wrong promise here is undefined behaviour, not a panic.");
}
