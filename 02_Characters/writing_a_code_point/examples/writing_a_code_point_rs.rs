// One escape form, and three ways std spells a character back at you.
//
// Rust has a single Unicode escape, `\u{...}`, taking one to six hex digits.
// The braces do the job Python's fixed widths do, which means `\u{41}` and
// `\u{000041}` are the same character and neither has to be padded.
//
// The second half is the part worth stealing: `char` carries THREE escapers
// that disagree on purpose, and the one `{:?}` uses arrives at the same rule
// Python's repr() does, from a different language and a different decade.
//
// This file contains no raw invisible character. Every one below is written
// as an escape -- which is the lesson, and also the reason the file is safe
// to read.

fn main() {
    let bar = "-".repeat(72);

    println!("\n1. ONE FORM, ONE TO SIX DIGITS\n{bar}");
    // All four of these are the same character. The braces mean the escape
    // needs no fixed width, so leading zeros are optional rather than required.
    let four = ['\u{20ac}', '\u{20AC}', '\u{020ac}', '\u{0020ac}'];
    println!("   '\\u{{20ac}}'   '\\u{{20AC}}'   '\\u{{020ac}}'   '\\u{{0020ac}}'");
    println!("   all the same char: {}", four.iter().all(|c| *c == four[0]));
    println!("   and that char is: {:?}   U+{:04X}", four[0], four[0] as u32);
    println!();
    println!("   Hex digits are case-insensitive and leading zeros are free,");
    println!("   because the closing brace is what ends the escape. Python");
    println!("   spells the same character \\u20ac and counts the digits.");

    println!("\n2. WHAT GOES IN THE BRACES IS A SCALAR VALUE\n{bar}");
    println!("   The escape does not take 'a number'. It takes a Unicode");
    println!("   SCALAR VALUE, which is every code point except the 2,048");
    println!("   surrogates -- exactly what a `char` is allowed to hold.");
    println!();
    for cp in [0x41u32, 0x20AC, 0x1F600, 0x10FFFF, 0xD800, 0x110000] {
        match char::from_u32(cp) {
            Some(c) => println!(
                "   U+{:06X}  char::from_u32 -> Some   UTF-8 bytes {}   {:?}",
                cp,
                c.len_utf8(),
                c
            ),
            None => println!("   U+{cp:06X}  char::from_u32 -> None   not a scalar value"),
        }
    }
    println!();
    println!("   The last two are the two ways to be outside the range: a");
    println!("   surrogate, which belongs to UTF-16's machinery and is not a");
    println!("   character, and a number above the top of Unicode. Written as");
    println!("   escapes, `\\u{{D800}}` and `\\u{{110000}}` do not compile at all --");
    println!("   the page quotes what rustc says. char::from_u32 is the same");
    println!("   check moved to run time, which is why it returns an Option.");

    println!("\n3. THREE ESCAPERS THAT DISAGREE ON PURPOSE\n{bar}");
    println!("   {:<12}{:<14}{:<14}{}", "code point", "escape_", "escape_", "escape_");
    println!("   {:<12}{:<14}{:<14}{}", "", "unicode()", "default()", "debug()");
    for cp in [0x41u32, 0xE9, 0x20AC, 0x1F600, 0x0A, 0x202E] {
        let c = char::from_u32(cp).unwrap();
        println!(
            "   U+{:<10}{:<14}{:<14}{}",
            format!("{cp:04X}"),
            c.escape_unicode().to_string(),
            c.escape_default().to_string(),
            c.escape_debug().to_string()
        );
    }
    println!();
    println!("   Read the three columns as three different answers to 'who is");
    println!("   going to read this?'. escape_unicode() escapes everything, so");
    println!("   its output is pure ASCII and survives any channel. Nobody can");
    println!("   read it. escape_default() keeps ASCII and escapes the rest --");
    println!("   the old, safe, unfriendly choice. escape_debug() escapes only");
    println!("   what would not draw, so an accented letter, a currency sign");
    println!("   and an emoji all come through as themselves.");

    println!("\n4. {{:?}} IS escape_debug, AND PYTHON'S repr() AGREES WITH IT\n{bar}");
    let s = "caf\u{e9} \u{20ac} \u{ca0}";
    println!("   {{}}    {s}");
    println!("   {{:?}}  {s:?}");
    println!();
    let hidden = "admin\u{202E} user";
    println!("   a string with an invisible character in it, Debug-printed:");
    println!("   {hidden:?}");
    println!();
    println!("   Eleven characters, and Debug printed ten of them as themselves");
    println!("   and one as an escape. Python's repr() makes the same split on");
    println!("   the same string, by asking str.isprintable(); Rust asks its own");
    println!("   printability table. Two standard libraries, no shared code, one");
    println!("   rule: a character that draws something is printed as itself, and");
    println!("   a character that draws nothing is printed as an escape.");
    println!();
    println!("   Display ({{}}) does NOT do this. Printing that string with {{}}");
    println!("   would reorder the rest of the line, which is why this program");
    println!("   does not do it.");

    println!("\n5. ONE ESCAPE, THREE LENGTHS\n{bar}");
    println!(
        "   {:<10}{:>6}{:>7}{:>8}{:>8}   {}",
        "escape", "chars", "bytes", "utf-16", "plane", "as itself"
    );
    for (esc, c) in [
        ("\\u{41}", 'A'),
        ("\\u{E9}", '\u{e9}'),
        ("\\u{20AC}", '\u{20ac}'),
        ("\\u{CA0}", '\u{ca0}'),
        ("\\u{1F600}", '\u{1f600}'),
    ] {
        let plane = (c as u32) >> 16;
        println!(
            "   {:<10}{:>6}{:>7}{:>8}{:>8}   {}",
            esc,
            1,
            c.len_utf8(),
            c.len_utf16(),
            plane,
            c
        );
    }
    println!();
    println!("   One escape is always one `char`. It is one to four bytes in");
    println!("   UTF-8, and one OR TWO units in UTF-16 -- and the last column");
    println!("   says why. Unicode is cut into 17 planes of 65,536 code points.");
    println!("   Plane 0 is the Basic Multilingual Plane, the BMP, and it holds");
    println!("   everything up to U+FFFF; a character in it is one UTF-16 unit.");
    println!("   Planes 1 to 16 are the supplementary planes, informally the");
    println!("   ASTRAL planes, and a character there needs a surrogate PAIR --");
    println!("   two UTF-16 units, which is why JSON, Java and JavaScript spell");
    println!("   the emoji \\uD83D\\uDE00 and Rust spells it \\u{{1F600}}.");
}
