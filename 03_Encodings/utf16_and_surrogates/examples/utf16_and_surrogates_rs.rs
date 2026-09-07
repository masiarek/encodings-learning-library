// The pair mechanism, one explicit call at a time.
//
// Rust never stores UTF-16, so nothing here happens implicitly: encoding to
// units, reading them back, and failing on a half are three separate calls you
// can watch. That makes it a better place to see the mechanism than a language
// where UTF-16 is the string type and the pair is assembled behind your back.
//
// Run:  rustc --edition 2024 utf16_and_surrogates_rs.rs -o /tmp/surro && /tmp/surro

fn head(n: u8, title: &str) {
    println!();
    println!("{n}. {title}");
    println!("{}", "-".repeat(72));
}

fn units_of(s: &str) -> Vec<u16> {
    s.encode_utf16().collect()
}

fn show(units: &[u16]) -> String {
    units
        .iter()
        .map(|u| format!("{u:04X}"))
        .collect::<Vec<_>>()
        .join(" ")
}

fn main() {
    // ------------------------------------------------------------ 1
    head(1, "ONE char IN, ONE OR TWO UNITS OUT");
    let mut buf = [0u16; 2];
    for ch in ['A', 'é', 'ż', '日', '😀'] {
        let units = ch.encode_utf16(&mut buf);
        println!(
            "   {ch}  U+{cp:04X}  len_utf16 = {n}   units [{u}]",
            cp = ch as u32,
            n = ch.len_utf16(),
            u = show(units)
        );
    }
    println!();
    println!("   The buffer has to be two long. That is the whole difference: a");
    println!("   char is one code point, and asking for its UTF-16 form can give");
    println!("   you back two of the things UTF-16 calls a character.");

    // ------------------------------------------------------------ 2
    head(2, "READING THE UNITS BACK");
    let text = "A😀B";
    let units = units_of(text);
    println!("   {text:?}");
    println!("     chars().count()        = {}", text.chars().count());
    println!("     encode_utf16().count() = {}", units.len());
    println!("     units                  = [{}]", show(&units));
    println!();
    print!("   char::decode_utf16 ->");
    for r in char::decode_utf16(units.iter().copied()) {
        match r {
            Ok(c) => print!(" Ok({c:?})"),
            Err(e) => print!(" Err({:04X})", e.unpaired_surrogate()),
        }
    }
    println!();
    println!("   Three code points out of four units, and the pair was rejoined.");

    // ------------------------------------------------------------ 3
    head(3, "THE SAME STRING, CUT ONE UNIT SHORT");
    let cut = &units[..2];
    println!("   Keeping the first 2 of {} units: [{}]", units.len(), show(cut));
    print!("   char::decode_utf16 ->");
    for r in char::decode_utf16(cut.iter().copied()) {
        match r {
            Ok(c) => print!(" Ok({c:?})"),
            Err(e) => print!(" Err(unpaired {:04X})", e.unpaired_surrogate()),
        }
    }
    println!();
    println!();
    println!("   That error IS the failure SAP warns about for ABAP — a string");
    println!("   truncated in the middle of a surrogate representation. The cut");
    println!("   landed at a legal unit boundary and an illegal character");
    println!("   boundary, and only a decoder that knows about pairs can tell.");
    println!("   In UTF-8 the equivalent cut is detectable from the bytes alone.");

    // ------------------------------------------------------------ 4
    head(4, "THE RESERVED BLOCK IS A HOLE IN THE char TYPE");
    for cp in [0xD7FFu32, 0xD800, 0xDBFF, 0xDC00, 0xDFFF, 0xE000] {
        match char::from_u32(cp) {
            Some(c) => println!("   U+{cp:04X}  Some({c:?})"),
            None => println!("   U+{cp:04X}  None"),
        }
    }
    println!();
    println!("   2,048 numbers with no character behind them, reserved so that a");
    println!("   UTF-16 decoder can never be in doubt about where a pair starts.");
    println!("   Rust spends a type invariant to keep them out; the languages");
    println!("   that store UTF-16 cannot, because in UTF-16 they are just units.");
}
