// Kata answers for `OsStr`, `Path`, and WTF-8.  Unix-only, for the reason the
// lesson's section 7 gives.
//
// Build & run:  rustc --edition 2024 osstr_path_and_wtf8_kata_rs.rs && ./osstr_path_and_wtf8_kata_rs

use std::borrow::Cow;
use std::ffi::{OsStr, OsString};
use std::os::unix::ffi::{OsStrExt, OsStringExt};
use std::path::Path;

const RAW: &[u8] = b"caf\xe9.txt";

fn hex(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02x}")).collect::<Vec<_>>().join(" ")
}

fn main() {
    let name = OsStr::from_bytes(RAW);
    println!("THE NAME: {}   'caf', a Latin-1 e-acute, and '.txt'", hex(RAW));
    println!();

    println!("1. to_str()  ->  Option<&str>");
    println!("   value          {:?}", name.to_str());
    println!("   still holding  the OsStr, if you kept it. The None itself carries nothing —");
    println!("                  it does not tell you which byte was wrong, or what the name");
    println!("                  was. Use it to FILTER, where dropping the name is the point.");
    println!();

    println!("2. to_string_lossy()  ->  Cow<'_, str>");
    let lossy = name.to_string_lossy();
    println!("   value          {lossy:?}");
    println!("   its bytes      {}", hex(lossy.as_bytes()));
    println!("   Cow variant    {}", match lossy { Cow::Borrowed(_) => "Borrowed", Cow::Owned(_) => "Owned — so a substitution happened" });
    println!("   still holding  a String that is NOT this file. e9 became ef bf bd, so the");
    println!("                  name is three bytes longer and opening it gives ENOENT.");
    println!();

    println!("3. into_string()  ->  Result<String, OsString>");
    match OsString::from_vec(RAW.to_vec()).into_string() {
        Ok(s) => println!("   value          Ok({s:?})"),
        Err(back) => {
            println!("   value          Err(OsString)");
            println!("   the Err holds  {} — byte-identical to the input? {}", hex(back.as_bytes()), back.as_bytes() == RAW);
            println!("   still holding  THE NAME. This is the only one of the three whose");
            println!("                  failure path leaves you able to carry on.");
        }
    }
    println!();

    println!("4. SO: WHICH ONE FOR WHICH JOB");
    println!("   into the error message   to_string_lossy(). Its output is for a person to");
    println!("                            read, and a person can read caf<?>.txt. Never pass");
    println!("                            that string to anything that will open a file.");
    println!("   to keep processing       neither — keep the OsStr or the Path and never");
    println!("                            convert at all. Path will join, split, compare,");
    println!("                            open and rename it as it stands. If a String is");
    println!("                            genuinely required, into_string(), because its Err");
    println!("                            gives the name back so the fallback still has it.");
    println!();

    println!("5. Path EQUALITY COMPARES COMPONENTS, AND EACH COMPONENT AS BYTES");
    let a = Path::new("\u{17c}\u{f3}\u{142}w.txt");      // żółw.txt, composed
    let b = Path::new("z\u{307}o\u{301}\u{142}w.txt");   // the same word, decomposed
    println!("   a  {} bytes  {}", a.as_os_str().len(), hex(a.as_os_str().as_bytes()));
    println!("   b  {} bytes  {}", b.as_os_str().len(), hex(b.as_os_str().as_bytes()));
    println!("   a == b   {}", a == b);
    println!("   Both draw the word zolw with its Polish diacritics, and Path calls them");
    println!("   different — because Path::eq compares components() and each component is");
    println!("   compared as BYTES. No Unicode normalization, and no case folding.");
    println!();
    println!("   What components() DOES normalize is separator syntax, and only that:");
    for (l, r) in [("a/b", "a//b"), ("a/b", "a/b/"), ("a/b", "a/./b"), ("a/b", "./a/b"), ("a/c", "a/b/../c"), ("a.txt", "A.TXT")] {
        println!("     {:<9} == {:<11} {}", format!("{l:?}"), format!("{r:?}"), Path::new(l) == Path::new(r));
    }
    println!("   Repeated and trailing separators collapse, and so does an inner '.'; a");
    println!("   leading './' does not, and '..' is left alone on purpose — 'b' might be a");
    println!("   symbolic link, so 'a/b/..' need not be 'a' and std will not pretend it is.");
    println!();
    println!("   Every false above except the case one names two spellings that may well be");
    println!("   the same file, and the case one is the same file on a default macOS or");
    println!("   Windows volume. So the honest summary is that Path equality answers a");
    println!("   question about NAMES, tidying only the syntax it can be certain about.");
    println!("   If you meant to ask about FILES, ask the OS: fs::canonicalize.");
}
