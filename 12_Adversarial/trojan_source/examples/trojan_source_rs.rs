// A scanner for the nine bidi controls, and the reason Rust needs one anyway.
//
// This file contains no raw control character and no non-ASCII identifier:
// rustc would refuse to compile the first (deny by default) and warn about the
// second. Every control below is written as an escape, which is what rustc's
// own error message suggests you do when you meant to keep one.

/// The nine explicit bidirectional formatting characters of UAX #9.
const BIDI: [(u32, &str); 9] = [
    (0x202A, "LRE  LEFT-TO-RIGHT EMBEDDING"),
    (0x202B, "RLE  RIGHT-TO-LEFT EMBEDDING"),
    (0x202C, "PDF  POP DIRECTIONAL FORMATTING"),
    (0x202D, "LRO  LEFT-TO-RIGHT OVERRIDE"),
    (0x202E, "RLO  RIGHT-TO-LEFT OVERRIDE"),
    (0x2066, "LRI  LEFT-TO-RIGHT ISOLATE"),
    (0x2067, "RLI  RIGHT-TO-LEFT ISOLATE"),
    (0x2068, "FSI  FIRST STRONG ISOLATE"),
    (0x2069, "PDI  POP DIRECTIONAL ISOLATE"),
];

fn name_of(c: char) -> Option<&'static str> {
    BIDI.iter().find(|(cp, _)| *cp == c as u32).map(|(_, n)| *n)
}

/// Line, column and name for every bidi control in `text`.
fn scan(text: &str) -> Vec<String> {
    let mut hits = Vec::new();
    for (lineno, line) in text.lines().enumerate() {
        for (col, c) in line.chars().enumerate() {
            if let Some(name) = name_of(c) {
                hits.push(format!("line {} col {}: {}", lineno + 1, col + 1, name));
            }
        }
    }
    hits
}

fn main() {
    println!("1. WHAT AN ESCAPE HOLDS");
    let s = "admin\u{202E} user";
    println!("   let s = \"admin\\u{{202E}} user\";");
    println!("   chars {}   bytes {}", s.chars().count(), s.len());
    let cps: Vec<String> = s.chars().map(|c| format!("U+{:04X}", c as u32)).collect();
    println!("   code points  {}", cps.join(" "));
    println!("   The override is the sixth character and it draws nothing at all.");
    println!("   Written as an escape it is six visible ASCII characters in the");
    println!("   source, greppable and diffable. Written as itself it is nothing,");
    println!("   and it reorders the line it sits in.");
    println!();

    println!("2. WHY THIS FILE COULD NOT HOLD THE RAW ONE");
    println!("   rustc denies text-direction-codepoint-in-literal and");
    println!("   text-direction-codepoint-in-comment BY DEFAULT -- not warn, deny.");
    println!("   So a Trojan Source commit does not compile here, and the error");
    println!("   offers the escape above as the fix. The page quotes both.");
    println!("   Three more lints (confusable-idents, mixed-script-confusables,");
    println!("   uncommon-codepoints) cover the homoglyph half, and those only");
    println!("   WARN -- so the confusable identifier still builds.");
    println!();

    println!("3. THE SCANNER YOU STILL NEED");
    let samples = [
        ("a clean line", "let admin = true;".to_string()),
        ("a filename from a zip", format!("photo_ann{}gnp.exe", '\u{202E}')),
        ("a display name", format!("{}Alice{}", '\u{2066}', '\u{2069}')),
    ];
    for (label, text) in &samples {
        let hits = scan(text);
        println!("   {label}:");
        if hits.is_empty() {
            println!("     clean");
        } else {
            for h in hits {
                println!("     {h}");
            }
        }
    }
    println!("   The second one renders as \"photo_annexe.png\" in a file manager");
    println!("   and is an executable. rustc protected your SOURCE; it has no");
    println!("   opinion about a string your program reads at run time, and that");
    println!("   is where these characters actually arrive.");
    println!();

    println!("4. THE RULE");
    println!("   Source: let the compiler deny them, and keep the deny on.");
    println!("   Data:   scan on the way in, and render on the way out with");
    println!("           escapes rather than glyphs -- a name, a filename or a");
    println!("           commit message from outside is not source code, and it");
    println!("           is not protected by anything that checks source code.");
}
