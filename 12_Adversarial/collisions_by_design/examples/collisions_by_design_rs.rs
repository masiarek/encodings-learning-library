// Rust never folds anything behind your back -- and that is why the fold is a
// decision you have to make in the open, and why the collision it creates is
// silent unless you look for it.

use std::collections::HashMap;

fn cps(s: &str) -> String {
    s.chars().map(|c| format!("U+{:04X}", c as u32)).collect::<Vec<_>>().join(" ")
}

/// A registry that considers two names the same when `fold` maps them together.
fn register(fold: fn(&str) -> String, names: &[&str]) -> (HashMap<String, String>, Vec<String>) {
    let mut by_key: HashMap<String, String> = HashMap::new();
    let mut lost = Vec::new();
    for name in names {
        let key = fold(name);
        if let Some(previous) = by_key.insert(key.clone(), name.to_string()) {
            lost.push(format!("{previous:?} was replaced by {name:?} under key {key:?}"));
        }
    }
    (by_key, lost)
}

fn main() {
    println!("1. String EQUALITY IS BYTE EQUALITY, ALWAYS");
    let composed = "caf\u{e9}";
    let decomposed = "cafe\u{301}";
    println!("   composed    {composed:?}  {} bytes  {}", composed.len(), cps(composed));
    println!("   decomposed  {decomposed:?}  {} bytes  {}", decomposed.len(), cps(decomposed));
    println!("   ==          {}", composed == decomposed);
    println!("   Same word on screen, different bytes, and Rust says no. There is");
    println!("   no locale, no collation and no hidden normalisation anywhere in");
    println!("   std -- which means Rust will never merge two users for you, and");
    println!("   never split two rows a database has already merged.");
    println!();

    println!("2. SO THE FOLD IS A DECISION, AND THERE IS MORE THAN ONE");
    let names = ["ss", "\u{df}", "SS"];
    for (label, fold) in [
        ("to_lowercase", str::to_lowercase as fn(&str) -> String),
        ("to_uppercase", str::to_uppercase as fn(&str) -> String),
    ] {
        let (by_key, _) = register(fold, &names);
        let mut keys: Vec<_> = by_key.keys().cloned().collect();
        keys.sort();
        println!("   registry keyed by {label:<13} {} record(s): {:?}",
                 by_key.len(), keys);
    }
    println!("   The three names are \"ss\", \"\\u{{df}}\" and \"SS\". Lowercasing keeps the");
    println!("   sharp s apart from the double s; uppercasing folds all three into");
    println!("   one. Both registries are case-insensitive. They disagree about how");
    println!("   many people signed up.");
    println!();

    println!("3. AND THE ONE THAT LOSES A USER SAYS NOTHING");
    let (_, lost) = register(str::to_uppercase, &names);
    for line in &lost {
        println!("   {line}");
    }
    println!("   HashMap::insert returns the value it displaced. That Option is the");
    println!("   only notice you will ever get, and `map.insert(k, v);` -- with the");
    println!("   semicolon and no binding -- throws it away without a warning.");
    println!("   #[must_use] is not on it, because overwriting is usually the point.");
    println!();

    println!("4. WHAT TO DO INSTEAD");
    println!("   let key = fold(input);                       // one fold, chosen once");
    println!("   match registry.entry(key) {{                   // ask before writing");
    println!("       Occupied(_) => return Err(NameTaken),");
    println!("       Vacant(slot) => slot.insert(record),");
    println!("   }}");
    println!("   `entry` is the difference between 'this name is taken' and");
    println!("   'this name is now yours', and it is the same one line of code.");
}
