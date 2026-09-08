//! UTF-8 by hand, from the side where the type does the remembering.
//!
//! The Python example walks the code points and asks what bytes come out. This
//! one walks the BYTES -- every combination the nine rows of Table 3-7 permit --
//! and asks what code point goes in. Two directions, and only together do they
//! say the table is a bijection: 1,112,064 scalar values, 1,112,064 sequences,
//! and nothing on either side without a partner on the other.
//!
//! Both of those walk what the table ALLOWS, so neither ever meets a byte
//! string the table exists to refuse. Section 5 closes that hole by sweeping
//! the whole space instead of the permitted part of it: every three-byte
//! string there is, 2^24 of them, put to a validator written from the nine
//! rows and to `str::from_utf8` side by side.
//!
//! Everything here is arithmetic over the number line. No character is named
//! and nothing is asked about which characters are assigned, so the answers do
//! not depend on the Unicode version this rustc was built against.
//!
//! Build: rustc --edition 2024 utf8_by_hand_rs.rs

/// Table 3-7: a code point range, then one inclusive byte range per position.
const TABLE_3_7: [(u32, u32, &[(u8, u8)]); 9] = [
    (0x0000, 0x007F, &[(0x00, 0x7F)]),
    (0x0080, 0x07FF, &[(0xC2, 0xDF), (0x80, 0xBF)]),
    (0x0800, 0x0FFF, &[(0xE0, 0xE0), (0xA0, 0xBF), (0x80, 0xBF)]),
    (0x1000, 0xCFFF, &[(0xE1, 0xEC), (0x80, 0xBF), (0x80, 0xBF)]),
    (0xD000, 0xD7FF, &[(0xED, 0xED), (0x80, 0x9F), (0x80, 0xBF)]),
    (0xE000, 0xFFFF, &[(0xEE, 0xEF), (0x80, 0xBF), (0x80, 0xBF)]),
    (0x10000, 0x3FFFF, &[(0xF0, 0xF0), (0x90, 0xBF), (0x80, 0xBF), (0x80, 0xBF)]),
    (0x40000, 0xFFFFF, &[(0xF1, 0xF3), (0x80, 0xBF), (0x80, 0xBF), (0x80, 0xBF)]),
    (0x100000, 0x10FFFF, &[(0xF4, 0xF4), (0x80, 0x8F), (0x80, 0xBF), (0x80, 0xBF)]),
];

/// The pencil method in the decode direction: strip each marker, join the rest.
fn decode_by_hand(raw: &[u8]) -> u32 {
    let mask: u32 = match raw.len() {
        1 => 0x7F,
        2 => 0x1F,
        3 => 0x0F,
        _ => 0x07,
    };
    let mut cp = (raw[0] as u32) & mask;
    for &b in &raw[1..] {
        cp = (cp << 6) | ((b as u32) & 0x3F);
    }
    cp
}

/// Every byte combination one row permits, in order, one call per sequence.
fn walk(cols: &[(u8, u8)], buf: &mut [u8; 4], at: usize, visit: &mut impl FnMut(&[u8])) {
    if at == cols.len() {
        visit(&buf[..cols.len()]);
        return;
    }
    for b in cols[at].0..=cols[at].1 {
        buf[at] = b;
        walk(cols, buf, at + 1, visit);
    }
}

/// The nine rows re-read as a decision about ONE lead byte: how long the
/// sequence is and what its second byte may be. Built from TABLE_3_7 rather
/// than typed out again, so a table edit cannot leave this behind -- and built
/// once, because section 5 asks it 2^24 times.
fn lead_byte_table() -> [Option<(usize, u8, u8)>; 256] {
    let mut map = [None; 256];
    for (_, _, cols) in TABLE_3_7 {
        let (first_lo, first_hi) = cols[0];
        let second = if cols.len() > 1 { cols[1] } else { (0, 0) };
        for b in first_lo..=first_hi {
            map[b as usize] = Some((cols.len(), second.0, second.1));
        }
    }
    map
}

/// A whole byte string, one sequence after another: a UTF-8 validator whose
/// every rule came off the table above and nowhere else.
fn scan(raw: &[u8], map: &[Option<(usize, u8, u8)>; 256]) -> bool {
    let mut i = 0;
    while i < raw.len() {
        let Some((n, lo, hi)) = map[raw[i] as usize] else {
            return false; // C0, C1, F5-FF, or a continuation byte in front
        };
        if i + n > raw.len() {
            return false; // the lead byte promised more than the string holds
        }
        if n > 1 {
            if !(lo..=hi).contains(&raw[i + 1]) {
                return false; // the row's second-byte column is the whole rule
            }
            for k in 2..n {
                if !(0x80..=0xBF).contains(&raw[i + k]) {
                    return false;
                }
            }
        }
        i += n;
    }
    true
}

fn hexes(raw: &[u8]) -> String {
    raw.iter()
        .map(|b| format!("{b:02X}"))
        .collect::<Vec<_>>()
        .join(" ")
}

fn main() {
    // ------------------------------------------------------------ section 1
    println!("1. char IS A SCALAR VALUE, AND THAT IS A TYPE");
    println!("   Rust's char is not a byte and not a UTF-16 unit. It is one code");
    println!("   point that is not a surrogate -- exactly the set Table 3-7 covers");
    println!("   -- and the type refuses everything outside it at construction.");
    println!();
    println!(
        "   {:<25}= {} bytes, the same for every char",
        "size_of::<char>()",
        size_of::<char>()
    );
    println!("   {:<25}= U+{:04X}", "char::MAX", char::MAX as u32);
    for probe in [0x0041u32, 0x00E9, 0x017C, 0x20AC, 0x1F600, 0xD800, 0x110000] {
        let call = format!("char::from_u32(0x{probe:X})");
        match char::from_u32(probe) {
            Some(c) => println!(
                "   {call:<25}= Some('{c}')  {} byte(s) in a String",
                c.len_utf8()
            ),
            None => println!(
                "   {call:<25}= None      {}",
                if probe > 0x10FFFF {
                    "above the top of Unicode"
                } else {
                    "a surrogate is not a scalar value"
                }
            ),
        }
    }
    println!();
    println!("   Two numbers that disagree on purpose. A char is always 4 bytes in");
    println!("   memory, because a fixed width is what makes it a type you can put");
    println!("   in an array; len_utf8() is 1 to 4, because that is what it costs");
    println!("   in a String. Neither is wrong and neither answers the other's");
    println!("   question.");
    println!();

    // ------------------------------------------------------------ section 2
    println!("2. THE BUFFER IS FOUR BYTES, AND THAT IS THE WHOLE PROMISE");
    println!("   encode_utf8 writes into a caller's [u8; 4]. The 4 is not a guess:");
    println!("   it is the width of the last template, and the type system is");
    println!("   where this page's table ends up living.");
    println!();
    for cp in [0x0041u32, 0x00E9, 0x017C, 0x20AC, 0x1F600] {
        let c = char::from_u32(cp).expect("scalar value");
        let mut buf = [0u8; 4];
        let s: &str = c.encode_utf8(&mut buf);
        println!(
            "   {:<8} '{c}'  len_utf8() {}   returns {:<12} buf {}",
            format!("U+{cp:04X}"),
            c.len_utf8(),
            hexes(s.as_bytes()),
            hexes(&buf)
        );
    }
    println!();
    println!("   The trailing zeros are the buffer, not the character: encode_utf8");
    println!("   hands back a &str borrowing only the bytes it wrote. len_utf8()");
    println!("   answered the same question before a single byte was written.");
    println!();

    // ------------------------------------------------------------ section 3
    println!("3. TABLE 3-7, CHECKED BY EXHAUSTION -- THE BYTE SIDE");
    println!("   Every byte combination the nine rows permit, decoded by hand, and");
    println!("   checked against the code point range the row claims. Then handed");
    println!("   to str::from_utf8, which is the decoder Rust ships.");
    println!();
    println!("   the row's byte columns                    sequences   decoding into");
    let mut grand_total: u32 = 0;
    for (lo, hi, cols) in TABLE_3_7 {
        let mut count: u32 = 0;
        let mut buf = [0u8; 4];
        walk(cols, &mut buf, 0, &mut |raw: &[u8]| {
            let cp = decode_by_hand(raw);
            assert!(cp >= lo && cp <= hi, "{} outside its row", hexes(raw));
            let s = std::str::from_utf8(raw).expect("row permits it, so Rust must take it");
            let c = s.chars().next().expect("one character");
            assert_eq!(c as u32, cp, "{}: hand decode disagrees with Rust", hexes(raw));
            assert_eq!(c.len_utf8(), raw.len(), "{}: width disagrees", hexes(raw));
            count += 1;
        });
        grand_total += count;
        let columns = cols
            .iter()
            .map(|(a, z)| format!("{a:02X}-{z:02X}"))
            .collect::<Vec<_>>()
            .join(" ");
        println!(
            "   {columns:<40} {count:>9}   U+{lo:04X} - U+{hi:04X}",
        );
    }
    println!();
    println!("   {grand_total} byte sequences -- the same number the Python example");
    println!("   counted from the other end. The rows do not overlap and they leave");
    println!("   nothing out, so the table is a bijection: one sequence per scalar");
    println!("   value, one scalar value per sequence, and no exceptions to learn.");
    println!();

    // ------------------------------------------------------------ section 4
    println!("4. WHAT MAKES A STREAM READABLE FROM THE MIDDLE");
    println!("   Four classes of byte value, and they do not overlap -- so any");
    println!("   byte announces which class it is in with no context at all:");
    println!();
    let (mut ascii, mut lead, mut cont, mut never) = (0u32, 0u32, 0u32, 0u32);
    for b in 0u16..=255 {
        match b as u8 {
            0x00..=0x7F => ascii += 1,
            0x80..=0xBF => cont += 1,
            0xC2..=0xF4 => lead += 1,
            _ => never += 1,
        }
    }
    for (label, n, what) in [
        ("00-7F", ascii, "a whole character by itself"),
        ("C2-F4", lead, "starts a two-, three- or four-byte character"),
        ("80-BF", cont, "continues one, and can never start one"),
        ("C0, C1, F5-FF", never, "appear in no well-formed UTF-8 at all"),
    ] {
        println!("   {label:<15}{n:>3}  {what}");
    }
    println!("   {:<15}---", "");
    println!(
        "   {:<15}{:>3}  every byte value, in exactly one class",
        "",
        ascii + lead + cont + never
    );
    println!();
    println!("   So from any offset, walk backwards over 80-BF and the first byte");
    println!("   that is not one is the start of the character you landed in. It");
    println!("   is never more than three steps, because no template is longer.");
    println!();
    let s = "aż😀b";
    println!("   \"{s}\" is {} bytes: {}", s.len(), hexes(s.as_bytes()));
    println!();
    println!("   offset  byte  is_char_boundary  the character it belongs to");
    for i in 0..s.len() {
        let mut start = i;
        while !s.is_char_boundary(start) {
            start -= 1;
        }
        let c = s[start..].chars().next().expect("a character starts here");
        println!(
            "   {i:>6}  {:02X}    {:<16}  '{c}' starting at offset {start}",
            s.as_bytes()[i],
            s.is_char_boundary(i)
        );
    }
    println!();
    println!("   is_char_boundary is that backward walk with a name. Rust exposes");
    println!("   it because &str indexing is by BYTE offset and the language will");
    println!("   not let you cut a character in half -- so the question the shell");
    println!("   answers with a hex dump is, here, a method on the type.");
    println!();

    // ------------------------------------------------------------ section 5
    println!("5. THE HALF OF THE TABLE NEITHER SWEEP HAS TOUCHED YET");
    println!("   Section 3 walked what the nine rows PERMIT and the Python example");
    println!("   walked the code points, so between them they have never once met a");
    println!("   byte string the table exists to REFUSE. This walks the whole space");
    println!("   instead of the permitted part of it: every three-byte string there");
    println!("   is, put to the validator above and to from_utf8 side by side.");
    println!();
    let map = lead_byte_table();
    let (mut agree, mut valid, mut single) = (0u32, 0u32, 0u32);
    for x in 0..0x0100_0000u32 {
        let raw = [(x >> 16) as u8, (x >> 8) as u8, x as u8];
        let mine = scan(&raw, &map);
        let rust = std::str::from_utf8(&raw).is_ok();
        if mine == rust {
            agree += 1;
        }
        if rust {
            valid += 1;
        }
        if mine && map[raw[0] as usize].expect("scan said yes").0 == 3 {
            single += 1;
        }
    }
    println!("     three-byte strings, 2^24                {:>10}", 0x0100_0000u32);
    println!("     my scanner agrees with from_utf8        {:>10}", agree);
    println!("     disagreements                           {:>10}", 0x0100_0000u32 - agree);
    println!();
    println!("   Nobody had to think of a case. Sweeping the space rather than the");
    println!("   rows puts every overlong, every surrogate, every truncated sequence");
    println!("   and every lone continuation byte in front of both decoders, because");
    println!("   at three bytes there is nowhere else for them to be.");
    println!();
    println!("   And the count of the ones that ARE text is arithmetic before it is a");
    println!("   measurement -- a three-byte string is UTF-8 in exactly four shapes:");
    println!();
    let ascii = 128u32;
    let two = 0x800 - 0x80; // row two of the table: U+0080..U+07FF
    let three = (0x10000 - 0x800) - 2048; // rows three to six, less the surrogates
    println!("     three ASCII bytes           128^3    = {:>10}", ascii.pow(3));
    println!("     ASCII, then a 2-byte char   128*1920 = {:>10}", ascii * two);
    println!("     a 2-byte char, then ASCII   1920*128 = {:>10}", two * ascii);
    println!("     one 3-byte char                      = {:>10}", three);
    println!("                                            {:>10}", "----------");
    println!("     predicted                              {:>10}", ascii.pow(3) + 2 * ascii * two + three);
    println!("     from_utf8 accepted                     {:>10}", valid);
    println!("     of which exactly one character long    {:>10}", single);
    println!();
    println!("   Every term came off Table 3-7 and not off a run: 1920 is row two's");
    println!("   U+0080..U+07FF, and {three} is rows three to six added up -- U+0800");
    println!("   through U+FFFF less the 2,048 surrogates. The table predicted the");
    println!("   number and then the loop went and got it, which is the only order in");
    println!("   which a sweep is a check rather than a description.");
}
