// The control group: a language that watched the whole story and refused.
//
// Rust is the counterfactual for this page. It was designed long after 1996,
// with the surrogate mess fully visible, and it is the one language here that
// had the option to store 16-bit code units and did not take it. UTF-16 is in
// std only as a *conversion*; there is no type that holds it, and every door
// back from it is fallible. This program walks that boundary four times.
//
// Run:  rustc --edition 2024 why_utf16_stayed_rs.rs -o /tmp/utf16stayed && /tmp/utf16stayed

fn head(n: u8, title: &str) {
    println!();
    println!("{n}. {title}");
    println!("{}", "-".repeat(72));
}

fn main() {
    // ------------------------------------------------------------ 1
    head(1, "THERE IS NO UTF-16 STRING TYPE, AND THAT IS THE POINT");
    println!(
        "   size_of::<char>() = {}   a char is a CODE POINT, not a 16-bit unit",
        std::mem::size_of::<char>()
    );
    println!(
        "   size_of::<u16>()  = {}   the unit Java, JavaScript and ABAP count",
        std::mem::size_of::<u16>()
    );
    println!();
    println!("   std has String (UTF-8) and OsString (the platform's bytes). It has");
    println!("   no Utf16String at all — on Windows, where the OS speaks UTF-16,");
    println!("   the conversion happens at the system call and not in the type.");

    // ------------------------------------------------------------ 2
    head(2, "UTF-16 IS A CONVERSION HERE, NEVER A STORAGE FORMAT");
    println!(
        "   {:<10} {:<12} {:>5} {:>7} {:>7}   char",
        "label", "code point", "chars", "u16 len", "u8 len"
    );
    let cast = [
        ("ascii", 'A'),
        ("accent", 'é'),
        ("polish", 'ż'),
        ("cjk", '日'),
        ("astral", '😀'),
    ];
    for (label, ch) in cast {
        println!(
            "   {:<10} {:<12} {:>5} {:>7} {:>7}   {}",
            label,
            format!("U+{:04X}", ch as u32),
            1,
            ch.len_utf16(),
            ch.len_utf8(),
            ch
        );
    }
    println!();
    println!("   len_utf16() is a question you have to ASK. In a language whose");
    println!("   strings are UTF-16 it is the answer you get by default, which is");
    println!("   why their `length` is a unit count and nobody chose that.");

    // ------------------------------------------------------------ 3
    head(3, "THE DOOR BACK IS FALLIBLE, BECAUSE UTF-16 CAN HOLD NON-TEXT");
    let cases: [(&str, &[u16]); 3] = [
        ("a valid pair", &[0xD83D, 0xDE00]),
        ("a lone lead surrogate", &[0xD83D]),
        ("a lone trail surrogate", &[0xDE00]),
    ];
    for (label, units) in cases {
        let shown: Vec<String> = units.iter().map(|u| format!("{u:04X}")).collect();
        match String::from_utf16(units) {
            Ok(s) => println!("   {label:<24} [{}]  -> Ok({s:?})", shown.join(" ")),
            Err(e) => println!("   {label:<24} [{}]  -> Err({e})", shown.join(" ")),
        }
    }
    println!();
    println!("   A lone surrogate is a perfectly ordinary u16, so any UTF-16 buffer");
    println!("   can contain one — a truncated string, a bad concatenation, a file");
    println!("   cut at the wrong byte. Rust makes you handle it:");
    println!(
        "   from_utf16_lossy([D83D]) -> {:?}",
        String::from_utf16_lossy(&[0xD83D])
    );

    // ------------------------------------------------------------ 4
    head(4, "AND A char CANNOT BE A SURROGATE AT ALL");
    for cp in [0x0041u32, 0xD7FF, 0xD800, 0xDFFF, 0xE000, 0x1F600] {
        let verdict = match char::from_u32(cp) {
            Some(c) => format!("Some({c:?})"),
            None => "None   <- reserved for UTF-16's sake".to_string(),
        };
        println!("   char::from_u32(0x{cp:04X}) = {verdict}");
    }
    println!();
    println!("   Those 2,048 code points are not characters and never will be. They");
    println!("   exist only so that a 16-bit encoding can reach past 16 bits — a");
    println!("   permanent hole punched in Unicode itself, in 1996, to rescue the");
    println!("   encoding this page is about. Rust declines to represent them, which");
    println!("   is a choice only a language that does not store UTF-16 can make.");
}
